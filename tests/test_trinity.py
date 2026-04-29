"""Tests for Trinity client wiring."""
import os, pytest

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("DOME_ROOT", os.path.join(os.path.dirname(__file__), ".."))


def test_trinity_client_init():
    from agents.core.trinity_client import TrinityClient
    tc = TrinityClient()
    assert tc.provider in ("local", "trinity", "mixed")
    assert tc.api_base.startswith("http")


def test_trinity_client_local_fallback():
    os.environ["DOME_PROVIDER"] = "local"
    from agents.core.trinity_client import TrinityClient
    tc = TrinityClient()
    assert tc.provider == "local"
    assert tc.has_credentials() is False or tc.provider == "local"
    os.environ.pop("DOME_PROVIDER", None)


def test_trinity_client_reads_env_vars():
    os.environ["TRINITY_API_BASE"] = "http://test:9999"
    os.environ["HUB_API_SECRET"] = "test-secret"
    os.environ["TRINITY_JWT"] = "test-jwt"
    from agents.core.trinity_client import TrinityClient
    tc = TrinityClient()
    assert tc.api_base == "http://test:9999"
    assert tc.hub_secret == "test-secret"
    assert tc.jwt == "test-jwt"
    # Cleanup
    os.environ.pop("TRINITY_API_BASE")
    os.environ.pop("HUB_API_SECRET")
    os.environ.pop("TRINITY_JWT")
