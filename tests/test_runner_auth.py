"""Tests fuer runner.wp_client.auth_from_env."""
import base64

from runner.wp_client import auth_from_env


def test_wp_auth_trimmed(monkeypatch):
    monkeypatch.setenv("WP_AUTH", "Basic abc123\n")
    assert auth_from_env() == "Basic abc123"


def test_basic_from_user_pass(monkeypatch):
    monkeypatch.delenv("WP_AUTH", raising=False)
    monkeypatch.setenv("WP_USER", "u")
    monkeypatch.setenv("WP_APP_PASSWORD", "p p")
    expected = "Basic " + base64.b64encode(b"u:p p").decode("ascii")
    assert auth_from_env() == expected


def test_none_when_nothing_set(monkeypatch):
    monkeypatch.delenv("WP_AUTH", raising=False)
    monkeypatch.delenv("WP_USER", raising=False)
    monkeypatch.delenv("WP_APP_PASSWORD", raising=False)
    assert auth_from_env() is None
