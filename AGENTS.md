# AGENTS.md - Developer Guidelines

## Environment Setup

```bash
# Activate conda environment (required for all operations)
conda activate yt-dl

# Deactivate when done
conda deactivate
```

## Build & Test Commands

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run single test (by file and function name)
pytest tests/test_download.py::TestFilenameSanitization::test_basic_sanitization -v

# Run single test (by class)
pytest tests/test_download.py::TestFilenameSanitization -v

# Run with coverage report
pytest tests/ -v --cov=download --cov-report=term-missing

# Run specific test file only
pytest tests/test_naming.py -v

# Run tests matching pattern
pytest tests/ -v -k "filename"

# Quick test run (no verbose output)
pytest tests/ --tb=short
```

### Setup Script
```bash
# Create conda environment with Python 3.14 + FFmpeg
./setup.sh

# Activate environment
conda activate yt-dl
```

## Code Style Guidelines

### Imports
```python
# Order: standard library -> third-party -> local
import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

import yt_dlp

from download import sanitize_filename  # local imports (if any)
```

### Type Hints
- **Required** for all function parameters and return types
- Use `Optional[T]` for nullable types
- Use `List[T]` or `dict[str, T]` for collections
- Use `Any` sparingly, prefer specific types

```python
def download_video(
    url: str,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    playlist: bool = False,
    audio_formats: Optional[List[str]] = None,
    audio_only: bool = False
) -> bool:
    """Download video from URL."""
```

### Naming Conventions
- **Functions/variables**: `snake_case` (e.g., `sanitize_filename`, `output_dir`)
- **Classes**: `PascalCase` (e.g., `Colors`, `TestFilenameSanitization`)
- **Constants**: `UPPER_CASE` (e.g., `DEFAULT_OUTPUT_DIR`, `SUPPORTED_AUDIO_FORMATS`)
- **Test functions**: `test_*` (e.g., `test_basic_sanitization`)
- **Test classes**: `Test*` (e.g., `TestDownloadVideo`)

### Docstrings
Use Google-style docstrings:
```python
def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing unsafe characters.
    
    Args:
        filename: Raw filename string
        
    Returns:
        Sanitized filename safe for filesystem
    """
```

### Error Handling
```python
# Use try/except for external operations
try:
    import yt_dlp
except ImportError:
    print_error("Error: yt-dlp is not installed.")
    sys.exit(1)

# Handle specific exceptions
try:
    ydl.download([url])
except yt_dlp.utils.DownloadError as e:
    print_error(f"Download failed: {e}")
    return False

# Use print_error() for user-facing errors (defined in Colors class)
```

### Terminal Output
- Use the `Colors` class for colored output
- Use helper functions: `print_error()`, `print_success()`, `print_warning()`, `print_info()`
- Include progress hooks for long operations

```python
print_success("Download completed successfully!")
print_error(f"Error: {error_message}")
print_info(f"Output directory: {output_dir}")
```

### Testing
- All tests in `tests/` directory
- Use fixtures from `conftest.py` (`temp_dir`, `sample_urls`, `output_dir`)
- Mock external dependencies with `unittest.mock.patch`
- Use `pytest.raises()` for expected exceptions
- Test edge cases and error conditions

```python
from unittest.mock import patch, Mock

@patch('download.yt_dlp.YoutubeDL')
def test_download_video_success(self, mock_ydl):
    """Test successful video download."""
    mock_instance = Mock()
    mock_ydl.return_value.__enter__.return_value = mock_instance
    
    result = download_video("https://youtube.com/watch?v=test")
    
    assert result is True
    mock_instance.download.assert_called_once()
```

### File Operations
- Use `pathlib.Path` for path operations
- Use `tempfile.TemporaryDirectory()` in tests for temporary files
- Create output directories with `Path.mkdir(parents=True, exist_ok=True)`

### Line Length
- Maximum 100 characters per line
- Use parentheses for multi-line function calls
- Break lines before operators

### Comments
- Use `#` for inline comments (one space after #)
- Document complex logic or non-obvious decisions
- No comments needed for self-explanatory code

## Git Workflow

```bash
# Check status
git status

# View changes
git diff

# Stage files
git add <file>

# Commit with conventional commits
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
git commit -m "test: add tests for feature"
git commit -m "docs: update documentation"

# Rollback if needed
git revert <commit-hash>
git reset --hard HEAD~1  # destructive - use with caution
```

## Common Patterns

### Progress Callbacks
```python
def print_progress(d: Dict[str, Any]):
    """Progress callback for yt-dlp."""
    if d['status'] == 'downloading':
        percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
        print(f"\r📥 Downloading: {percent:.1f}%", end='', flush=True)
```

### Sanitization Functions
Always sanitize user input (filenames, titles) to prevent filesystem issues.

### URL Validation
Validate URLs before processing:
```python
if not validate_url(url):
    print_warning("Warning: Invalid YouTube URL")
```

## References
- [pytest documentation](https://docs.pytest.org/)
- [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp)
- PEP 8 (Python Style Guide)
- PEP 484 (Type Hints)
