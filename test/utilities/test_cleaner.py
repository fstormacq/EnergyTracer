from pathlib import Path

import pytest

from src.utilities.cleaner import (
    clean_artifacts,
    confirm_delete_output,
    get_artifacts_to_remove,
)


@pytest.mark.unit
def test_get_artifacts_to_remove_can_skip_output(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    output_dir = tmp_path / "output"
    htmlcov_dir = tmp_path / "htmlcov"
    output_dir.mkdir()
    htmlcov_dir.mkdir()

    artifacts = get_artifacts_to_remove(delete_output=False)

    assert Path("output") not in {artifact_path for artifact_path, _ in artifacts}
    assert Path("htmlcov") in {artifact_path for artifact_path, _ in artifacts}


@pytest.mark.unit
def test_confirm_delete_output_accepts_yes(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "y")

    assert confirm_delete_output()


@pytest.mark.unit
def test_confirm_delete_output_rejects_no(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "n")

    assert not confirm_delete_output()


@pytest.mark.unit
def test_clean_artifacts_can_keep_output(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    output_dir = tmp_path / "output"
    htmlcov_dir = tmp_path / "htmlcov"
    output_dir.mkdir()
    htmlcov_dir.mkdir()
    (output_dir / "result.txt").write_text("data")
    (htmlcov_dir / "report.txt").write_text("data")

    monkeypatch.setattr("src.utilities.cleaner.confirm_delete_output", lambda: False)
    monkeypatch.setattr("src.utilities.cleaner.confirm_cleanup", lambda: True)

    assert clean_artifacts() == 0
    assert output_dir.exists()
    assert not htmlcov_dir.exists()


@pytest.mark.unit
def test_clean_artifacts_removes_all(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    output_dir = tmp_path / "output"
    htmlcov_dir = tmp_path / "htmlcov"
    output_dir.mkdir()
    htmlcov_dir.mkdir()
    (output_dir / "result.txt").write_text("data")
    (htmlcov_dir / "report.txt").write_text("data")

    monkeypatch.setattr("src.utilities.cleaner.confirm_delete_output", lambda: True)
    monkeypatch.setattr("src.utilities.cleaner.confirm_cleanup", lambda: True)

    assert clean_artifacts() == 0
    assert not output_dir.exists()
    assert not htmlcov_dir.exists()
