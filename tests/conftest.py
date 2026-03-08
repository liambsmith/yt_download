"""Test fixtures and configuration."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_urls():
    """Provide sample YouTube URLs for testing."""
    return [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "https://www.youtube.com/playlist?list=PLexample",
    ]


@pytest.fixture
def invalid_urls():
    """Provide invalid URLs for testing."""
    return [
        "https://example.com/video",
        "not-a-url",
        "https://google.com",
    ]


@pytest.fixture
def sample_text_file(temp_dir):
    """Create a temporary file with sample URLs."""
    filepath = os.path.join(temp_dir, "urls.txt")
    with open(filepath, 'w') as f:
        f.write("https://www.youtube.com/watch?v=dQw4w9WgXcQ\n")
        f.write("https://youtu.be/dQw4w9WgXcQ\n")
    return filepath


@pytest.fixture
def output_dir(temp_dir):
    """Create a temporary output directory."""
    output_path = os.path.join(temp_dir, "downloads")
    os.makedirs(output_path)
    return output_path
