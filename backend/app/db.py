"""SQLite connections and contact storage shared by the API."""

import sqlite3

from flask import current_app, g


# Identifiers below are fixed application data, never request input.
CHILD_FIELDS = {
    "phones": ("label", "number", "is_primary"),
    "emails": ("label", "email", "is_primary"),
    "social_accounts": ("platform", "account"),
    "addresses": ("label", "address", "is_primary"),
}


def get_db() -> sqlite3.Connection:
    """Return the request's connection with foreign-key enforcement enabled."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None) -> None:
    """Close the connection at the end of the application context."""
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db() -> None:
    """Create the schema without deleting existing contacts."""
    with current_app.open_resource("schema.sql", mode="r", encoding="utf-8") as schema:
        get_db().executescript(schema.read())


def serialize_contact(row: sqlite3.Row) -> dict:
    """Return a contact and its ordered child arrays in API format."""
    contact = dict(row)
    contact["is_favorite"] = bool(contact["is_favorite"])
    for table, fields in CHILD_FIELDS.items():
        rows = get_db().execute(
            f"SELECT {', '.join(fields)} FROM {table} "
            "WHERE contact_id = ? ORDER BY id",
            (contact["id"],),
        ).fetchall()
        contact[table] = []
        for child_row in rows:
            child = dict(child_row)
            if "is_primary" in fields:
                child["is_primary"] = bool(child["is_primary"])
            contact[table].append(child)
    return contact


def insert_children(contact_id: int, contact: dict) -> None:
    """Insert validated child arrays inside the caller's transaction."""
    for table, fields in CHILD_FIELDS.items():
        columns = ", ".join(("contact_id", *fields))
        placeholders = ", ".join("?" for _ in range(len(fields) + 1))
        get_db().executemany(
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
            [(contact_id, *(item[field] for field in fields)) for item in contact[table]],
        )


def insert_contact(contact: dict, now: str) -> int:
    """Insert a validated contact and children within the caller's transaction."""
    cursor = get_db().execute(
        'INSERT INTO contacts (name, "group", is_favorite, notes, created_at, updated_at) '
        "VALUES (?, ?, ?, ?, ?, ?)",
        (contact["name"], contact["group"], contact["is_favorite"], contact["notes"], now, now),
    )
    insert_children(cursor.lastrowid, contact)
    return cursor.lastrowid
