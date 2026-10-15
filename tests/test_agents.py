import pytest

from deployment_impact.agents import _client


def test_client_uses_foundry_v1_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://foundry.example.test/")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "test-deployment")

    client, deployment = _client()
    try:
        assert str(client.base_url) == "https://foundry.example.test/openai/v1/"
        assert deployment == "test-deployment"
    finally:
        client.close()


def test_client_reports_missing_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT",
    ):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(RuntimeError, match="Missing required Azure OpenAI configuration"):
        _client()
