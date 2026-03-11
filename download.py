#!/usr/bin/env python3
"""
YouTube Video Downloader

A dual-interface YouTube video downloader supporting:
- Single video download (best quality)
- Playlist download
- Audio-only extraction (all formats)
- Batch downloads from file
- Interactive menu-driven mode

Usage:
    CLI Mode:
        python download.py <url>
        python download.py --playlist <url>
        python download.py --audio-format mp3,m4a <url>
        python download.py -f urls.txt

    Interactive Mode:
        python download.py
        python download.py --interactive
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed.")
    print("Please run: pip install yt-dlp")
    sys.exit(1)


# Configuration
DEFAULT_OUTPUT_DIR = "./downloads"
SUPPORTED_AUDIO_FORMATS = ["mp3", "m4a", "webm", "ogg", "wav", "flac", "aac", "mp4", "m4p", "m4b", "mp2", "wma", "mka"]

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_colored(text: str, color: str = Colors.ENDC):
    """Print colored text to terminal."""
    print(f"{color}{text}{Colors.ENDC}")


def print_success(text: str):
    print_colored(text, Colors.GREEN)


def print_error(text: str):
    print_colored(text, Colors.FAIL)


def print_warning(text: str):
    print_colored(text, Colors.WARNING)


def print_info(text: str):
    print_colored(text, Colors.CYAN)


def print_header(text: str):
    print_colored(f"\n{'='*60}\n{text}\n{'='*60}", Colors.HEADER)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing unsafe characters.
    
    Args:
        filename: Raw filename string
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    # Strip leading/trailing spaces and dots (Windows issue)
    filename = filename.strip(' .')
    # Limit length (Windows max is 255, leave room for extension)
    if len(filename) > 200:
        filename = filename[:200]
    # Handle empty filename
    if not filename:
        filename = "video"
    return filename


def generate_filename(title: str, video_id: str, ext: str) -> str:
    """
    Generate a safe filename for downloaded video.
    
    Args:
        title: Video title
        video_id: YouTube video ID
        ext: File extension
        
    Returns:
        Complete filename with extension
    """
    sanitized_title = sanitize_filename(title)
    filename = f"{sanitized_title} - {video_id}.{ext}"
    
    # Check for duplicates and add number if needed
    counter = 1
    while Path(filename).exists():
        filename = f"{sanitized_title} - {video_id} ({counter}).{ext}"
        counter += 1
        
    return filename


def print_progress(d: Dict[str, Any]):
    """
    Progress callback for yt-dlp.
    Prints download progress to terminal.
    """
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        downloaded = d.get('downloaded_bytes', 0)
        speed = d.get('speed', 0)
        eta = d.get('eta', 0)
        
        if total and total > 0:
            percent = downloaded / total * 100
            bar_length = 40
            filled = int(bar_length * downloaded / total)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r📥 Downloading: [{bar}] {percent:.1f}%", end='', flush=True)
        elif speed and speed > 0:
            print(f"\r📥 Downloading at {format_size(speed)}/s...", end='', flush=True)
            
    elif d['status'] == 'finished':
        print("\r📥 Download complete! Processing...")
        
    elif d['status'] == 'error':
        print_error(f"\n❌ Download error: {d.get('error_message', 'Unknown error')}")


def format_size(size: float) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def validate_url(url: str) -> bool:
    """
    Validate YouTube URL format.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid YouTube URL, False otherwise
    """
    patterns = [
        r'youtube\.com/watch\?v=',
        r'youtu\.be/',
        r'youtube\.com/shorts/',
        r'youtube\.com/playlist\?list=',
    ]
    return any(re.search(pattern, url) for pattern in patterns)


def get_video_info(url: str) -> Optional[Dict[str, Any]]:
    """
    Get video information without downloading.
    
    Args:
        url: YouTube URL
        
    Returns:
        Dictionary with video info or None if failed
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        print_error(f"Failed to get video info: {e}")
        return None


def download_video(
    url: str,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    playlist: bool = False,
    audio_formats: Optional[List[str]] = None,
    audio_only: bool = False
) -> bool:
    """
    Download video from URL.
    
    Args:
        url: YouTube URL
        output_dir: Output directory path
        playlist: Download entire playlist if True
        audio_formats: List of audio formats to extract
        audio_only: Download audio only
        
    Returns:
        True if download successful, False otherwise
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Build format selection
    if audio_only:
        format_select = 'bestaudio/best'
        post_processors = []
    else:
        format_select = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        # Add FFmpeg post-processor if available
        post_processors = [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]
    
    # Build audio format options
    if audio_formats:
        # Convert list to comma-separated string
        audio_format_str = ','.join(audio_formats)
    else:
        audio_format_str = 'all'
    
    # Configure yt-dlp options
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s - %(id)s.%(ext)s'),
        'format': format_select,
        'format_sort': 'br',
        'format_sort_force': True,
        'verbose': True,
        'progress_hooks': [print_progress],
        'merge_output_format': 'mp4' if not audio_only else 'mp3',
        'postprocessors': post_processors,
        'continue': True,
        'nopartial': True,
        'writethumbnail': True,
        'writeautomaticsub': True,
        'skip_download': audio_only,
        'ignoreerrors': True,
        'subtitles': ['en', 'hu', ''],
        'writesubtitles': True,
        'subtitleslangs': ['en', 'hu'],
    }
    
    # Add audio extraction options if needed
    if audio_only or audio_formats:
        ydl_opts['extractaudio'] = True
        ydl_opts['audioformat'] = audio_format_str if audio_formats else 'mp3'
    
    # Handle playlist mode
    if playlist:
        ydl_opts['playlist_items'] = '0'  # Download all items
    
    try:
        print_info(f"🎬 Downloading from: {url}")
        print_info(f"📁 Output directory: {output_dir}")
        print_info(f"🎵 Audio formats: {audio_format_str if audio_formats else 'N/A'}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        print_success("\n✅ Download completed successfully!")
        return True
        
    except yt_dlp.utils.DownloadError as e:
        print_error(f"\n❌ Download failed: {e}")
        return False
    except Exception as e:
        print_error(f"\n❌ Unexpected error: {e}")
        return False


def interactive_menu():
    """
    Run interactive menu-driven interface.
    """
    print_header("🎬 YouTube Video Downloader")
    
    while True:
        print("\n📋 Menu:")
        print("  1. Download single video")
        print("  2. Download playlist")
        print("  3. Download audio only")
        print("  4. Download from file list")
        print("  5. Exit")
        
        choice = input("\n🔹 Select option (1-5): ").strip()
        
        if choice == '1':
            download_single()
        elif choice == '2':
            download_playlist()
        elif choice == '3':
            download_audio()
        elif choice == '4':
            download_from_file()
        elif choice == '5':
            print_info("👋 Goodbye!")
            break
        else:
            print_warning("❌ Invalid option. Please try again.")


def download_single():
    """Download a single video."""
    print_header("📹 Download Single Video")
    
    url = input("🔗 Enter YouTube URL: ").strip()
    
    if not validate_url(url):
        print_warning("⚠️  Warning: This doesn't look like a valid YouTube URL.")
    
    output_dir = input(f"📁 Output directory (default: {DEFAULT_OUTPUT_DIR}): ").strip()
    if not output_dir:
        output_dir = DEFAULT_OUTPUT_DIR
    
    quality = input("🎵 Download audio only? (y/n, default: n): ").strip().lower()
    audio_formats = None
    if quality == 'y':
        format_choice = input(f"Audio formats ({', '.join(SUPPORTED_AUDIO_FORMATS[:5])}...): ").strip()
        if format_choice:
            audio_formats = [f.strip() for f in format_choice.split(',')]
    
    if validate_url(url):
        download_video(url, output_dir, audio_only=bool(audio_formats), audio_formats=audio_formats)


def download_playlist():
    """Download an entire playlist."""
    print_header("📋 Download Playlist")
    
    url = input("🔗 Enter YouTube playlist URL: ").strip()
    
    if not validate_url(url) or 'playlist' not in url and 'list=' not in url:
        print_warning("⚠️  Warning: This doesn't look like a valid playlist URL.")
    
    output_dir = input(f"📁 Output directory (default: {DEFAULT_OUTPUT_DIR}): ").strip()
    if not output_dir:
        output_dir = DEFAULT_OUTPUT_DIR
    
    # Get video info first
    print_info("\n📊 Getting playlist info...")
    info = get_video_info(url)
    
    if info:
        if 'entries' in info and info['entries']:
            print(f"📋 Found {len(list(info['entries']))} videos in playlist")
        else:
            print(f"🎬 Title: {info.get('title', 'Unknown')}")
            print(f"👤 Uploader: {info.get('uploader', 'Unknown')}")
            print(f"👁️ Views: {info.get('view_count', 0):,}")
    
    download = input("\n⬇️  Download playlist? (y/n): ").strip().lower()
    
    if download == 'y':
        download_video(url, output_dir, playlist=True)


def download_audio():
    """Download audio only."""
    print_header("🎵 Download Audio Only")
    
    url = input("🔗 Enter YouTube URL: ").strip()
    
    if not validate_url(url):
        print_warning("⚠️  Warning: This doesn't look like a valid YouTube URL.")
    
    output_dir = input(f"📁 Output directory (default: {DEFAULT_OUTPUT_DIR}): ").strip()
    if not output_dir:
        output_dir = DEFAULT_OUTPUT_DIR
    
    print(f"\nAvailable formats: {', '.join(SUPPORTED_AUDIO_FORMATS)}")
    format_choice = input("Audio format (default: mp3): ").strip()
    
    if not format_choice:
        format_choice = 'mp3'
    
    if validate_url(url):
        download_video(url, output_dir, audio_only=True, audio_formats=[format_choice])


def download_from_file():
    """Download videos from a file list."""
    print_header("📄 Download from File List")
    
    filepath = input("📁 Path to file with URLs (one per line): ").strip()
    
    if not os.path.exists(filepath):
        print_error(f"❌ File not found: {filepath}")
        return
    
    output_dir = input(f"📁 Output directory (default: {DEFAULT_OUTPUT_DIR}): ").strip()
    if not output_dir:
        output_dir = DEFAULT_OUTPUT_DIR
    
    # Read URLs from file
    with open(filepath, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print_info(f"\n📋 Found {len(urls)} URLs in file")
    
    download_all = input("\n⬇️  Download all videos? (y/n): ").strip().lower()
    
    if download_all == 'y':
        success_count = 0
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Downloading: {url[:50]}...")
            if validate_url(url):
                if download_video(url, output_dir):
                    success_count += 1
            else:
                print_warning(f"⚠️  Skipping invalid URL")
        
        print_header(f"📊 Summary")
        print(f"✅ Successfully downloaded: {success_count}/{len(urls)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='🎬 YouTube Video Downloader - Download videos, playlists, and audio',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://youtube.com/watch?v=VIDEO_ID
  %(prog)s --playlist https://youtube.com/playlist?list=PLAYLIST_ID
  %(prog)s --audio-format mp3,m4a https://youtube.com/watch?v=VIDEO_ID
  %(prog)s -f urls.txt
        """
    )
    
    parser.add_argument('url', nargs='?', help='YouTube URL to download')
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT_DIR,
                       help=f'Output directory (default: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('-p', '--playlist', action='store_true',
                       help='Download entire playlist')
    parser.add_argument('-f', '--audio-format', type=str, default=None,
                       help='Audio format(s) to extract (comma-separated)')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--file', '-F', type=str,
                       help='File containing URLs (one per line)')
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive or not args.url and not args.file:
        interactive_menu()
        return
    
    # File-based download
    if args.file:
        if not os.path.exists(args.file):
            print_error(f"❌ File not found: {args.file}")
            sys.exit(1)
        
        with open(args.file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        print_info(f"📋 Found {len(urls)} URLs in file")
        
        success_count = 0
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Downloading...")
            if validate_url(url):
                if download_video(url, args.output, args.playlist,
                                 args.audio_format.split(',') if args.audio_format else None):
                    success_count += 1
            else:
                print_warning(f"⚠️  Skipping invalid URL")
        
        print_header(f"📊 Summary")
        print(f"✅ Successfully downloaded: {success_count}/{len(urls)}")
    
    # Single URL or playlist download
    elif args.url:
        if not validate_url(args.url):
            print_warning("⚠️  Warning: This doesn't look like a valid YouTube URL.")
            continue_download = input("Continue anyway? (y/n): ").strip().lower()
            if continue_download != 'y':
                sys.exit(1)
        
        audio_formats = args.audio_format.split(',') if args.audio_format else None
        audio_only = bool(audio_formats)
        
        download_video(
            args.url,
            args.output,
            args.playlist,
            audio_formats,
            audio_only
        )
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
