import json

import pytest

from tradingagents.run_provenance import build_run_provenance, validate_run_provenance


def _build(config=None):
    return build_run_provenance(
        ticker=" AAPL ",
        trade_date="2026-09-01",
        asset_type="stock",
        selected_analysts=("market", "news"),
        config=config or {
            "max_debate_rounds": 1,
            "max_risk_discuss_rounds": 2,
            "backend_url": "https://relay.invalid/v1?token=secret",
            "llm_provider": "openai",
        },
        route_fingerprint="0123456789abcdef",
    )


def test_manifest_is_json_safe_and_declares_advisory_only():
    manifest = _build()
    json.dumps(manifest)
    assert manifest["schema_version"] == "tradingagents-run-provenance-v1"
    assert manifest["universe"] == ["AAPL"]
    assert manifest["data_cutoff"] == "2026-09-01"
    assert manifest["execution_capability"] is False
    assert manifest["mode"] == "advisory"


def test_hash_is_stable_and_raw_endpoint_never_persisted():
    first = _build()
    second = _build()
    assert first == second
    encoded = json.dumps(first)
    assert "relay.invalid" not in encoded
    assert "secret" not in encoded


def test_graph_hash_changes_for_structural_config():
    first = _build()
    second = _build({"max_debate_rounds": 3, "max_risk_discuss_rounds": 2})
    assert first["graph_config_hash"] != second["graph_config_hash"]


def test_validator_accepts_generated_manifest_and_binds_ticker():
    validate_run_provenance(_build(), expected_ticker="AAPL")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("route_fingerprint", "not-a-digest"),
        ("graph_config_hash", "0123456789ABCDEf"),
        ("data_cutoff", "2026-9-1"),
        ("mode", "execution"),
    ],
)
def test_validator_rejects_unsafe_or_noncanonical_values(field, value):
    manifest = _build()
    manifest[field] = value
    with pytest.raises(ValueError):
        validate_run_provenance(manifest)


def test_validator_rejects_execution_capability_and_ticker_mismatch():
    manifest = _build()
    manifest["execution_capability"] = True
    with pytest.raises(ValueError, match="execution_capability"):
        validate_run_provenance(manifest)

    manifest = _build()
    with pytest.raises(ValueError, match="does not match"):
        validate_run_provenance(manifest, expected_ticker="MSFT")

