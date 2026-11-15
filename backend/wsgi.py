"""WSGI entry point used by production servers such as gunicorn on Render."""

from app import create_app

app = create_app()
