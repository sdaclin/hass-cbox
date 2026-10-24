"""Serve the connbox simulator so a local Home Assistant can be pointed at it."""

from aiohttp import web
from tests.connbox_simulator import CboxSimulator

web.run_app(CboxSimulator().app, port=80)
