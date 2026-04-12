"""
pytest configuration for AXON integration tests.
"""
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        default="https://axon-onld.onrender.com",
        help="Base URL for the AXON backend (default: live deployment)",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: marks tests that hit live endpoints and may take >5s (e.g. Render cold-start)"
    )
    config.addinivalue_line(
        "markers",
        "x402: marks tests that test the x402 payment protocol"
    )
