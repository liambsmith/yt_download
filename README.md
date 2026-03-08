# 🎬 YouTube Video Downloader

A portable YouTube video downloader with dual interface (CLI and interactive menu).

## Features

- ✅ **Single video download** - Download individual videos in best quality
- ✅ **Playlist download** - Download entire playlists
- ✅ **Audio extraction** - Extract audio in multiple formats (MP3, M4A, WebM, etc.)
- ✅ **Batch downloads** - Download multiple videos from a file list
- ✅ **Interactive mode** - Menu-driven interface for guided downloads
- ✅ **Best quality** - Automatically selects optimal video/audio quality
- ✅ **Progress tracking** - Real-time download progress display
- ✅ **Resume support** - Resume interrupted downloads
- ✅ **Portable setup** - Uses conda environment for easy setup

## Quick Start

### 1. Setup Environment

Run the setup script to create a conda environment with Python 3.14 and FFmpeg:

```bash
./setup.sh
```

This will:
- Create a conda environment named `yt-dl` with Python 3.14
- Install FFmpeg for video processing
- Install yt-dlp and testing dependencies

### 2. Activate Environment

```bash
conda activate yt-dl
```

### 3. Run the Downloader

**Interactive Mode:**
```bash
python download.py
# or
python download.py --interactive
```

**CLI Mode:**
```bash
# Single video
python download.py https://www.youtube.com/watch?v=VIDEO_ID

# Playlist
python download.py --playlist https://www.youtube.com/playlist?list=PLAYLIST_ID

# Audio only (MP3)
python download.py --audio-format mp3 https://www.youtube.com/watch?v=VIDEO_ID

# Batch download from file
python download.py -f urls.txt
```

## Usage Examples

### Download a Single Video

```bash
python download.py https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Default behavior: Downloads best quality video + audio merged into MP4.

### Download a Playlist

```bash
python download.py --playlist https://www.youtube.com/playlist?list=PLexample
```

Downloads all videos in the playlist.

### Extract Audio Only

```bash
# MP3
python download.py --audio-format mp3 https://www.youtube.com/watch?v=VIDEO_ID

# Multiple formats
python download.py --audio-format mp3,m4a,webm https://www.youtube.com/watch?v=VIDEO_ID
```

### Batch Download

Create a file `urls.txt` with one URL per line:

```
https://www.youtube.com/watch?v=VIDEO1
https://www.youtube.com/watch?v=VIDEO2
https://www.youtube.com/watch?v=VIDEO3
```

Then run:

```bash
python download.py -f urls.txt
```

### Custom Output Directory

```bash
python download.py https://www.youtube.com/watch?v=VIDEO_ID -o ./my_videos/
```

## Interactive Mode

When run without arguments or with `--interactive`, the downloader shows a menu:

```
============================================================
🎬 YouTube Video Downloader
============================================================

📋 Menu:
  1. Download single video
  2. Download playlist
  3. Download audio only
  4. Download from file list
  5. Exit

🔹 Select option (1-5):
```

## File Naming

Videos are saved with the format:
```
{Video Title} - {Video ID}.{extension}
```

Example: `Never Gonna Give You Up - dQw4w9WgXcQ.mp4`

- Special characters are removed from titles
- Duplicate files are numbered automatically (e.g., `Video (1).mp4`)
- Files are saved to `./downloads/` by default

## Supported Audio Formats

- MP3
- M4A
- WebM
- OGG
- WAV
- FLAC
- AAC
- And more...

## Testing

Run the test suite:

```bash
pytest tests/ -v
pytest tests/ -v --cov=download
```

Test coverage includes:
- Filename sanitization and generation
- URL validation
- Format selection
- Interactive menu functionality
- Error handling

## Requirements

- Python 3.14+
- FFmpeg (for merging video and audio)
- yt-dlp library

## Git Workflow

This project uses git for version control:

```bash
# Check status
git status

# View changes
git diff

# Create a commit
git add .
git commit -m "feat: description of changes"

# Rollback changes
git revert <commit-hash>
```

## Troubleshooting

### FFmpeg not found

If you see errors about FFmpeg, make sure the conda environment is activated:

```bash
conda activate yt-dl
```

### Download fails

- Check that the URL is valid
- Ensure you have a stable internet connection
- Check disk space availability

### Network errors

yt-dlp automatically retries failed downloads. Try running the command again.

## License

MIT License

## Credits

- **yt-dlp**: https://github.com/yt-dlp/yt-dlp
- Built with ❤️ for easy YouTube video downloading
