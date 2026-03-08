"""Tests for download.py core functionality."""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from download import (
    sanitize_filename,
    generate_filename,
    format_size,
    validate_url,
    get_video_info,
    print_progress,
    download_video,
)


class TestFilenameSanitization:
    """Tests for filename sanitization."""

    def test_basic_sanitization(self):
        """Test basic filename sanitization."""
        result = sanitize_filename("My Video Title")
        assert result == "My Video Title"

    def test_removes_invalid_characters(self):
        """Test that invalid characters are removed."""
        result = sanitize_filename("Video: <test> | file?name*")
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result
        assert '"' not in result
        assert "\\" not in result
        assert "/" not in result

    def test_replaces_multiple_spaces(self):
        """Test that multiple spaces are replaced with single space."""
        result = sanitize_filename("Video   Title   Here")
        assert result == "Video Title Here"

    def test_strips_leading_trailing_spaces(self):
        """Test that leading and trailing spaces are removed."""
        result = sanitize_filename("  Video Title  ")
        assert result == "Video Title"

    def test_strips_trailing_dots(self):
        """Test that trailing dots are removed (Windows issue)."""
        result = sanitize_filename("Video Title.  ")
        assert result == "Video Title"

    def test_handles_empty_filename(self):
        """Test that empty filename gets default value."""
        result = sanitize_filename("")
        assert result == "video"

    def test_limits_length(self):
        """Test that filename length is limited."""
        long_title = "a" * 300
        result = sanitize_filename(long_title)
        assert len(result) <= 200


class TestFilenameGeneration:
    """Tests for filename generation."""

    def test_generates_filename_with_title_and_id(self):
        """Test basic filename generation."""
        result = generate_filename("Test Video", "abc123", "mp4")
        assert "Test Video" in result
        assert "abc123" in result
        assert result == "Test Video - abc123.mp4"

    def test_sanitizes_title_in_filename(self):
        """Test that title is sanitized in filename."""
        result = generate_filename("Video: <test>", "abc123", "mp4")
        assert "<" not in result
        assert ">" not in result

    def test_handles_duplicate_files(self):
        """Test that duplicate filenames are handled."""
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
            finally:
                os.chdir(old_cwd)


class TestSizeFormatting:
    """Tests for file size formatting."""

    def test_formats_bytes(self):
        """Test formatting of bytes."""
        result = format_size(1024)
        assert "KB" in result

    def test_formats_kb(self):
        """Test formatting of kilobytes."""
        result = format_size(1500)
        assert "KB" in result

    def test_formats_mb(self):
        """Test formatting of megabytes."""
        result = format_size(1500000)
        assert "MB" in result

    def test_formats_gb(self):
        """Test formatting of gigabytes."""
        result = format_size(1500000000)
        assert "GB" in result


class TestURLValidation:
    """Tests for URL validation."""

    def test_valid_standard_url(self):
        """Test valid standard YouTube URL."""
        assert validate_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    def test_valid_short_url(self):
        """Test valid short YouTube URL."""
        assert validate_url("https://youtu.be/dQw4w9WgXcQ")

    def test_valid_shorts_url(self):
        """Test valid Shorts URL."""
        assert validate_url("https://www.youtube.com/shorts/dQw4w9WgXcQ")

    def test_valid_playlist_url(self):
        """Test valid playlist URL."""
        assert validate_url("https://www.youtube.com/playlist?list=PLexample")

    def test_invalid_url(self):
        """Test invalid URL."""
        assert not validate_url("https://example.com/video")

    def test_invalid_google_url(self):
        """Test non-YouTube URL."""
        assert not validate_url("https://google.com")


class TestProgressCallback:
    """Tests for progress callback."""

    def test_progress_download_status(self):
        """Test progress callback with downloading status."""
        data = {
            'status': 'downloading',
            'downloaded_bytes': 500,
            'total_bytes': 1000,
        }
        # Should not raise exception
        print_progress(data)

    def test_progress_finished_status(self):
        """Test progress callback with finished status."""
        data = {'status': 'finished'}
        # Should not raise exception
        print_progress(data)

    def test_progress_error_status(self):
        """Test progress callback with error status."""
        data = {
            'status': 'error',
            'error_message': 'Test error'
        }
        # Should not raise exception
        print_progress(data)


class TestVideoInfo:
    """Tests for video info retrieval."""

    @patch('download.yt_dlp.YoutubeDL')
    def test_get_video_info_success(self, mock_ydl):
        """Test successful video info retrieval."""
        mock_instance = Mock()
        mock_instance.extract_info.return_value = {
            'title': 'Test Video',
            'id': 'abc123',
            'uploader': 'Test Channel'
        }
        mock_ydl.return_value.__enter__.return_value = mock_instance
        
        result = get_video_info("https://www.youtube.com/watch?v=abc123")
        
        assert result is not None
        assert result['title'] == 'Test Video'

    @patch('download.yt_dlp.YoutubeDL')
    def test_get_video_info_failure(self, mock_ydl):
        """Test failed video info retrieval."""
        mock_ydl.side_effect = Exception("Test error")
        
        result = get_video_info("https://www.youtube.com/watch?v=abc123")
        
        assert result is None


class TestDownloadVideo:
    """Tests for download functionality."""

    @patch('download.yt_dlp.YoutubeDL')
    def test_download_video_success(self, mock_ydl):
        """Test successful video download."""
        mock_instance = Mock()
        mock_ydl.return_value.__enter__.return_value = mock_instance
        
        result = download_video(
            "https://www.youtube.com/watch?v=abc123",
            output_dir="/tmp/test",
            playlist=False,
            audio_formats=None,
            audio_only=False
        )
        
        assert result is True
        mock_instance.download.assert_called_once()

    @patch('download.yt_dlp.YoutubeDL')
    def test_download_video_with_audio_formats(self, mock_ydl):
        """Test download with audio format specification."""
        mock_instance = Mock()
        mock_ydl.return_value.__enter__.return_value = mock_instance
        
        result = download_video(
            "https://www.youtube.com/watch?v=abc123",
            audio_formats=['mp3', 'm4a'],
            audio_only=True
        )
        
        assert result is True

    @patch('download.yt_dlp.YoutubeDL')
    def test_download_playlist(self, mock_ydl):
        """Test playlist download."""
        mock_instance = Mock()
        mock_ydl.return_value.__enter__.return_value = mock_instance
        
        result = download_video(
            "https://www.youtube.com/playlist?list=PLexample",
            playlist=True
        )
        
        assert result is True

    @patch('download.yt_dlp.YoutubeDL')
    def test_download_video_error(self, mock_ydl):
        """Test download error handling."""
        from yt_dlp.utils import DownloadError
        
        mock_instance = Mock()
        mock_instance.download.side_effect = DownloadError("Test error")
        mock_ydl.return_value.__enter__.return_value = mock_instance
        
        result = download_video(
            "https://www.youtube.com/watch?v=abc123"
        )
        
        assert result is False


# Import Path for duplicate test
from pathlib import Path
import tempfile
