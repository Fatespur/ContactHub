"""Run the local backend on the contract's port."""

from app import create_app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000)
