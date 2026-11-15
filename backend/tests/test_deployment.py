"""Deployment configuration and WSGI entry point checks."""

import importlib

import pytest

from app import create_app


@pytest.mark.parametrize("origins,origin", [
    (" https://frontend.example, https://second.example ", "https://second.example"),
    ("*", "https://any.example"),
    (" , ", "http://localhost:5173"),
])
def test_environment_configuration(monkeypatch, tmp_path, origins, origin):
    database = tmp_path / "persistent" / "contacts.sqlite3"
    monkeypatch.setenv("DATABASE", str(database))
    monkeypatch.setenv("CORS_ORIGINS", origins)
    app = create_app()
    assert database.is_file()
    response = app.test_client().get(
        "/api/v1/contacts", headers={"Origin": origin},
    )
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == origin
    if "*" not in origins:
        denied = app.test_client().get(
            "/api/v1/contacts", headers={"Origin": "https://denied.example"},
        )
        assert "Access-Control-Allow-Origin" not in denied.headers


def test_test_config_overrides_database_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE", str(tmp_path / "unused.sqlite3"))
    database = tmp_path / "test" / "contacts.sqlite3"
    app = create_app({"TESTING": True, "DATABASE": str(database)})
    assert app.config["DATABASE"] == str(database)
    assert database.is_file()
    assert not (tmp_path / "unused.sqlite3").exists()


def test_wsgi_entry_point(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE", str(tmp_path / "wsgi.sqlite3"))
    module = importlib.import_module("wsgi")
    assert module.app.test_client().get("/api/v1/contacts").status_code == 200
