"""Fixtures for testing."""

import pytest


@pytest.fixture(autouse=True)
def _auto_enable_custom_integrations(
    enable_custom_integrations: bool,  # noqa: ARG001, FBT001
) -> None:
    """Auto enable custom integration."""
    return
