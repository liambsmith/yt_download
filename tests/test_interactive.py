"""Tests for interactive mode functionality."""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestInteractiveFunctionality:
    """Tests for interactive mode functionality."""

    def test_download_single_with_valid_url(self):
        """Test download_single with valid URL."""
        with patch('builtins.input') as mock_input:
            with patch('download.validate_url') as mock_validate:
                with patch('download.download_video') as mock_download:
                    mock_input.side_effect = [
                        "https://www.youtube.com/watch?v=abc123",
                        "",
                        "n",
                    ]
                    mock_validate.return_value = True
                    
                    from download import download_single
                    result = download_single()
                    
                    assert result is None
                    mock_download.assert_called_once()

    def test_download_single_audio_only(self):
        """Test audio-only download."""
        with patch('builtins.input') as mock_input:
            with patch('download.validate_url') as mock_validate:
                with patch('download.download_video') as mock_download:
                    mock_input.side_effect = [
                        "https://www.youtube.com/watch?v=abc123",
                        "",
                        "y",
                        "mp3",
                    ]
                    mock_validate.return_value = True
                    
                    from download import download_single
                    download_single()
                    
                    call_args = mock_download.call_args
                    assert call_args[1].get('audio_only', False) is True

    def test_download_playlist_success(self):
        """Test playlist download."""
        with patch('builtins.input') as mock_input:
            with patch('download.validate_url') as mock_validate:
                with patch('download.get_video_info') as mock_get_info:
                    with patch('download.download_video') as mock_download:
                        mock_validate.return_value = True
                        mock_get_info.return_value = {
                            'entries': [{'title': 'Video 1'}]
                        }
                        mock_input.side_effect = [
                            "https://www.youtube.com/playlist?list=PLexample",
                            "",
                            "y",
                        ]
                        
                        from download import download_playlist
                        download_playlist()
                        
                        call_args = mock_download.call_args
                        assert call_args[1].get('playlist', False) is True

    def test_download_audio_success(self):
        """Test audio download."""
        with patch('builtins.input') as mock_input:
            with patch('download.validate_url') as mock_validate:
                with patch('download.download_video') as mock_download:
                    mock_validate.return_value = True
                    mock_input.side_effect = [
                        "https://www.youtube.com/watch?v=abc123",
                        "",
                        "mp3",
                    ]
                    
                    from download import download_audio
                    download_audio()
                    
                    call_args = mock_download.call_args
                    assert call_args[1].get('audio_only', False) is True


class TestInteractiveMenu:
    """Basic tests for menu structure."""

    def test_menu_displays_options(self):
        """Test that menu options are displayed."""
        import inspect
        from download import interactive_menu
        
        source = inspect.getsource(interactive_menu)
        assert 'Menu:' in source or 'menu' in source.lower()
        assert 'Download single video' in source or 'single' in source.lower()
        assert 'Exit' in source

    def test_menu_has_exit_option(self):
        """Test that menu has exit option."""
        import inspect
        from download import interactive_menu
        
        source = inspect.getsource(interactive_menu)
        assert '5' in source or 'exit' in source.lower()


class TestDownloadFromFile:
    """Tests for file-based download."""

    def test_download_from_file_with_valid_urls(self, tmp_path, sample_text_file):
        """Test download from file with valid URLs."""
        with patch('builtins.input') as mock_input:
            with patch('download.validate_url') as mock_validate:
                with patch('download.download_video') as mock_download:
                    mock_validate.return_value = True
                    mock_input.side_effect = [
                        str(sample_text_file),
                        str(tmp_path),
                        "y",
                    ]
                    
                    from download import download_from_file
                    download_from_file()
                    
                    assert mock_download.call_count >= 1

    def test_download_from_file_not_found(self):
        """Test download from non-existent file."""
        with patch('builtins.input') as mock_input:
            mock_input.return_value = "/tmp/nonexistent.txt"
            
            with patch('os.path.exists') as mock_exists:
                mock_exists.return_value = False
                
                from download import download_from_file
                
                # Should print error message
                import io
                import sys
                captured_output = io.StringIO()
                sys.stdout = captured_output
                download_from_file()
                sys.stdout = sys.__stdout__
                
                output = captured_output.getvalue()
                assert "not found" in output.lower() or "❌" in output
