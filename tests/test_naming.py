"""Tests for filename generation and naming conventions."""

import os
import sys
import pytest
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from download import generate_filename, sanitize_filename


class TestFilenameGeneration:
    """Tests for filename generation logic."""

    def test_basic_filename_generation(self):
        """Test basic filename generation with title and ID."""
        result = generate_filename("Test Video", "abc123xyz", "mp4")
        assert result == "Test Video - abc123xyz.mp4"

    def test_filename_with_special_characters_in_title(self):
        """Test filename generation with special characters in title."""
        result = generate_filename("Video: <Test> | Name?", "abc123", "mp4")
        # Special characters should be removed
        assert "<" not in result
        assert ">" not in result
        assert "?" not in result
        assert "|" not in result

    def test_filename_uses_correct_extension(self):
        """Test that the correct file extension is used."""
        for ext in ['mp4', 'mp3', 'mkv', 'webm', 'm4a']:
            result = generate_filename("Test", "abc123", ext)
            assert result.endswith(f".{ext}")

    def test_filename_contains_separator(self):
        """Test that title and ID are separated correctly."""
        result = generate_filename("My Video", "xyz789", "mp4")
        assert " - " in result


class TestFilenameUniqueness:
    """Tests for filename uniqueness handling."""

    def test_handles_duplicate_filenames(self):
        """Test that duplicate filenames get numbered suffixes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create first file
                Path("Test Video - abc123.mp4").touch()
                
                # Generate second filename
                result = generate_filename("Test Video", "abc123", "mp4")
                
                # Should have (1) suffix
                assert " (1)" in result
                assert result.endswith(".mp4")
            finally:
                os.chdir(old_cwd)

    def test_handles_multiple_duplicates(self):
        """Test handling of multiple duplicate files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Create multiple files
                Path("Test Video - abc123.mp4").touch()
                Path("Test Video - abc123 (1).mp4").touch()
                Path("Test Video - abc123 (2).mp4").touch()
                
                # Generate next filename
                result = generate_filename("Test Video", "abc123", "mp4")
                
                # Should have (3) suffix
                assert " (3)" in result
            finally:
                os.chdir(old_cwd)

    def test_different_ids_dont_conflict(self):
        """Test that different video IDs don't conflict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory for relative path testing
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Create file with one ID
                Path("Test - abc123.mp4").touch()
                
                # Generate with different ID
                result = generate_filename("Test", "xyz789", "mp4")
                
                # Should not have suffix
                assert " (1)" not in result
            finally:
                os.chdir(old_cwd)


class TestFilenameEdgeCases:
    """Tests for edge cases in filename generation."""

    def test_empty_title(self):
        """Test filename with empty title."""
        result = generate_filename("", "abc123", "mp4")
        assert "abc123" in result
        assert result.endswith(".mp4")

    def test_very_long_title(self):
        """Test filename with very long title."""
        long_title = "A" * 300
        result = generate_filename(long_title, "abc123", "mp4")
        # Should be truncated (200 for title + 13 for " - abc123.mp4")
        assert len(result) <= 213

    def test_unicode_characters(self):
        """Test filename with unicode characters."""
        result = generate_filename("视频 测试", "abc123", "mp4")
        assert "视频" in result
        assert "测试" in result
        assert "abc123" in result

    def test_numbers_in_filename(self):
        """Test filename with numbers."""
        result = generate_filename("Video 2024 Part 1", "abc123", "mp4")
        assert "2024" in result
        assert "1" in result


class TestSanitizeFilename:
    """Tests for filename sanitization function."""

    def test_removes_path_separators(self):
        """Test that path separators are removed."""
        result = sanitize_filename("Video/Name")
        assert "/" not in result

        result = sanitize_filename("Video\\Name")
        assert "\\" not in result

    def test_removes_colon(self):
        """Test that colons are removed."""
        result = sanitize_filename("Video: Name")
        assert ":" not in result

    def test_removes_angle_brackets(self):
        """Test that angle brackets are removed."""
        result = sanitize_filename("<Video> Name")
        assert "<" not in result
        assert ">" not in result

    def test_removes_pipe(self):
        """Test that pipe character is removed."""
        result = sanitize_filename("Video | Name")
        assert "|" not in result

    def test_removes_question_mark(self):
        """Test that question mark is removed."""
        result = sanitize_filename("Video? Name")
        assert "?" not in result

    def test_removes_asterisk(self):
        """Test that asterisk is removed."""
        result = sanitize_filename("Video* Name")
        assert "*" not in result

    def test_removes_quotes(self):
        """Test that quotes are removed."""
        result = sanitize_filename('Video "Name"')
        assert '"' not in result

    def test_normalizes_whitespace(self):
        """Test that whitespace is normalized."""
        result = sanitize_filename("Video   Name")
        assert result == "Video Name"

    def test_strips_whitespace(self):
        """Test that leading/trailing whitespace is removed."""
        result = sanitize_filename("  Video Name  ")
        assert result == "Video Name"
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_strips_trailing_dots(self):
        """Test that trailing dots are removed."""
        result = sanitize_filename("Video Name.")
        assert result == "Video Name"

    def test_empty_string_returns_default(self):
        """Test that empty string returns default filename."""
        result = sanitize_filename("")
        assert result == "video"

    def test_only_whitespace_returns_default(self):
        """Test that whitespace-only string returns default."""
        result = sanitize_filename("   ")
        assert result == "video"

    def test_preserves_letters_and_numbers(self):
        """Test that letters and numbers are preserved."""
        result = sanitize_filename("Video123 Test")
        assert result == "Video123 Test"

    def test_preserves_underscores(self):
        """Test that underscores are preserved."""
        result = sanitize_filename("Video_Name")
        assert "_" in result

    def test_preserves_hyphens(self):
        """Test that hyphens are preserved."""
        result = sanitize_filename("Video-Name")
        assert "-" in result
