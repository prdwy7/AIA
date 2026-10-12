"""core_api — AI Kiosk central API (sessions, cases, inputs)."""

from core_api._version import __version__
from core_api.app import create_app

__all__ = ["create_app", "__version__"]
