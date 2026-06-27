from pathlib import Path

from pmpp.utils.config import load_config


def test_load_config_defaults(tmp_path: Path):
    cfg = load_config(tmp_path)
    assert "llm" in cfg
    assert cfg["llm"]["provider"] == "none"


def test_load_config_from_toml(tmp_path: Path):
    p = tmp_path / ".pmpp.toml"
    p.write_text('llm = { provider = "suggest", budget = 2 }\n')
    cfg = load_config(tmp_path)
    assert cfg["llm"]["provider"] == "suggest"
    assert cfg["llm"]["budget"] == 2
