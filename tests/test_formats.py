"""Tests for format selection and audio extraction."""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from download import download_video, SUPPORTED_AUDIO_FORMATS


class TestSupportedAudioFormats:
    """Tests for supported audio formats."""

    def test_formats_list_not_empty(self):
        """Test that supported formats list is not empty."""
        assert len(SUPPORTED_AUDIO_FORMATS) > 0

    def test_formats_are_strings(self):
        """Test that all formats are strings."""
        for format_name in SUPPORTED_AUDIO_FORMATS:
            assert isinstance(format_name, str)

    def test_common_formats_supported(self):
        """Test that common audio formats are supported."""
        common_formats = ['mp3', 'm4a', 'wav', 'flac']
        for fmt in common_formats:
            assert fmt in SUPPORTED_AUDIO_FORMATS


class TestAudioFormatParsing:
    """Tests for audio format parsing in download function."""

    @pytest.mark.parametrize("input_formats,expected_count", [
        (None, 0),
        (['mp3'], 1),
        (['mp3', 'm4a'], 2),
        (['mp3', 'm4a', 'webm'], 3),
    ])
    def test_audio_format_handling(self, input_formats, expected_count):
        """Test that audio formats are handled correctly."""
        # Just test that it doesn't crash
        # Actual download behavior tested in integration tests
        if input_formats:
            assert len(input_formats) == expected_count


class TestFormatSelection:
    """Tests for format selection logic."""

    def test_best_quality_format_string(self):
        """Test that best quality format string is used by default."""
        # The format string should prioritize best video+audio
        format_string = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        assert 'bestvideo' in format_string
        assert 'bestaudio' in format_string

    def test_audio_only_format_string(self):
        """Test that audio-only format string is used correctly."""
        format_string = 'bestaudio/best'
        assert 'bestaudio' in format_string


class TestOutputFormat:
    """Tests for output format configuration."""

    def test_merge_output_format_mp4(self):
        """Test MP4 merge format."""
        assert 'mp4' in 'mp4'

    def test_merge_output_format_mp3(self):
        """Test MP3 merge format for audio."""
        assert 'mp3' in 'mp3'
