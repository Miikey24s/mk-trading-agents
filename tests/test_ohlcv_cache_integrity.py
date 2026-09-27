"""Cache writes must not publish a partial OHLCV snapshot."""
from __future__ import annotations

import os

import pandas as pd
import pytest

from tradingagents.dataflows import stockstats_utils as su


@pytest.mark.unit
def test_write_ohlcv_cache_replaces_target_from_same_directory(tmp_path, monkeypatch):
    target = tmp_path / "AAPL-YFin-data.csv"
    frame = pd.DataFrame({"Date": ["2026-07-18"], "Close": [123.45]})
    replacements = []
    replace = os.replace

    def _record_replace(source, destination):
        replacements.append((source, destination))
        replace(source, destination)

    monkeypatch.setattr(su.os, "replace", _record_replace)
    su._write_ohlcv_cache(frame, target)

    assert target.read_text(encoding="utf-8").endswith("2026-07-18,123.45\n")
    assert len(replacements) == 1
    source, destination = replacements[0]
    assert destination == os.fspath(target)
    assert os.path.dirname(source) == os.fspath(tmp_path)
    assert source != os.fspath(target)
    assert not list(tmp_path.glob("*.tmp"))


@pytest.mark.unit
def test_write_ohlcv_cache_cleans_temporary_file_when_replace_fails(tmp_path, monkeypatch):
    target = tmp_path / "AAPL-YFin-data.csv"
    frame = pd.DataFrame({"Date": ["2026-07-18"], "Close": [123.45]})

    def _fail_replace(source, destination):
        raise OSError("simulated cache replace failure")

    monkeypatch.setattr(su.os, "replace", _fail_replace)
    with pytest.raises(OSError, match="simulated cache replace failure"):
        su._write_ohlcv_cache(frame, target)

    assert not target.exists()
    assert not list(tmp_path.glob("*.tmp"))
