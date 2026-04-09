"""Tests for path traversal prevention in PDF upload (CWE-22).

Validates that PDFService._sanitize_filename strips directory components
(both POSIX and Windows separators) and that the resulting file path
always stays within the storage directory.
"""
import os
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath

import pytest


def _sanitize_filename(filename: str) -> str:
    """Mirror of PDFService._sanitize_filename (no FastAPI dependency)."""
    sanitized = PureWindowsPath(filename).name
    sanitized = PurePosixPath(sanitized).name
    if not sanitized or sanitized in (".", ".."):
        raise ValueError("Invalid filename")
    return sanitized


def _is_within(file_path: Path, storage_dir: Path) -> bool:
    """Check resolved path stays inside storage_dir."""
    norm_fp = os.path.normpath(file_path)
    norm_sd = os.path.normpath(storage_dir)
    return norm_fp.startswith(norm_sd + os.sep) or norm_fp == norm_sd


class TestSanitizeFilename:
    """Unit tests for filename sanitization."""

    def test_strips_parent_traversal(self):
        assert _sanitize_filename("../../evil.pdf") == "evil.pdf"

    def test_strips_absolute_path(self):
        assert _sanitize_filename("/etc/passwd.pdf") == "passwd.pdf"

    def test_strips_nested_dirs(self):
        assert _sanitize_filename("foo/bar/baz.pdf") == "baz.pdf"

    def test_normal_filename_unchanged(self):
        assert _sanitize_filename("report.pdf") == "report.pdf"

    def test_empty_filename_raises(self):
        with pytest.raises(ValueError):
            _sanitize_filename("")

    def test_dot_only_raises(self):
        with pytest.raises(ValueError):
            _sanitize_filename(".")

    def test_dotdot_only_raises(self):
        with pytest.raises(ValueError):
            _sanitize_filename("..")

    def test_windows_backslash(self):
        """Windows-style backslash separators are stripped."""
        result = _sanitize_filename("..\\..\\evil.pdf")
        assert result == "evil.pdf"

    def test_mixed_separators(self):
        result = _sanitize_filename("..\\../foo/bar\\baz.pdf")
        assert result == "baz.pdf"


class TestPathContainment:
    """Integration-style tests: sanitized name -> file path -> containment."""

    @pytest.mark.parametrize("payload", [
        "../../../tmp/evil.pdf",
        "foo/../../bar/../../tmp/evil.pdf",
        "/etc/shadow.pdf",
        "....//....//tmp/evil.pdf",
        "..\\..\\..\\tmp\\evil.pdf",
        "..\\../foo\\..\\..\\tmp/evil.pdf",
    ])
    def test_sanitized_path_stays_in_storage(self, payload):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_dir = Path(tmpdir) / "uploads"
            storage_dir.mkdir()

            safe = _sanitize_filename(payload)
            file_path = storage_dir / f"pdf_99999_{safe}"
            assert _is_within(file_path, storage_dir), (
                f"Traversal with {payload!r}: "
                f"{os.path.normpath(file_path)} escapes {storage_dir}"
            )

    def test_normal_upload_works(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_dir = Path(tmpdir) / "uploads"
            storage_dir.mkdir()

            safe = _sanitize_filename("my_report.pdf")
            file_path = storage_dir / f"pdf_12345_{safe}"
            assert _is_within(file_path, storage_dir)
            assert file_path.name == "pdf_12345_my_report.pdf"
