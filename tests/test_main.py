import logging

import pytest

from app.main import shutdown_event, startup_event

pytestmark = pytest.mark.asyncio


async def test_startup_event_logging(caplog):
    caplog.set_level(logging.INFO)
    await startup_event()
    assert "Starting up..." in caplog.text


async def test_shutdown_event_logging(caplog):
    caplog.set_level(logging.INFO)
    await shutdown_event()
    assert "Shutting down..." in caplog.text
