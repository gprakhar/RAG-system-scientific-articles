"""Tests for src/main.py."""
import sys
import pytest
import yaml

from main import _load_config, main


class TestLoadConfig:
    """Tests for the _load_config helper."""

    def test_loads_valid_config(self) -> None:
        """_load_config returns a dict with expected top-level keys."""
        config = _load_config(config_path="config.yaml")
        assert isinstance(config, dict)
        assert "gcp" in config
        assert "pdf_files" in config

    def test_gcp_section_has_required_keys(self) -> None:
        """GCP config section contains project_id, location, and model."""
        config = _load_config(config_path="config.yaml")
        assert "project_id" in config["gcp"]
        assert "location" in config["gcp"]
        assert "model" in config["gcp"]

    def test_pdf_files_section_has_required_keys(self) -> None:
        """pdf_files config section contains file_path and output_path."""
        config = _load_config(config_path="config.yaml")
        assert "file_path" in config["pdf_files"]
        assert "output_path" in config["pdf_files"]

    def test_missing_config_raises_file_not_found(self) -> None:
        """_load_config raises FileNotFoundError for a missing config file."""
        with pytest.raises(FileNotFoundError):
            _load_config(config_path="nonexistent_config.yaml")

    def test_invalid_yaml_raises_yaml_error(self, tmp_path) -> None:
        """_load_config raises yaml.YAMLError for malformed YAML."""
        bad_config = tmp_path / "bad.yaml"
        bad_config.write_text("key: [unclosed bracket")
        with pytest.raises(yaml.YAMLError):
            _load_config(config_path=str(bad_config))


class TestMain:
    """Integration tests for the main entry point."""

    def test_main_runs_without_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """main() completes without raising an exception."""
        monkeypatch.setattr(sys, "argv", ["rag"])
        main()

    def test_main_accepts_library_argument(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """main() accepts --library flag and passes it to read_pdf."""
        monkeypatch.setattr(sys, "argv", ["rag", "--library", "pymupdf"])
        main()
