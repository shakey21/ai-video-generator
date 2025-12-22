#!/usr/bin/env python3
"""
Download Instagram Reels using yt-dlp
Usage: python download_reel.py <instagram_reel_url> [output_filename]
"""
import subprocess
import sys
import os
from pathlib import Path

def download_reel(url: str, output_dir: str = "outputs", output_filename: str = None):
    """
    Download an Instagram reel using yt-dlp
    
    Args:
        url: Instagram reel URL
        output_dir: Directory to save the video (default: outputs)
        output_filename: Optional custom filename (without extension)
    
    Returns:
        Path to the downloaded video file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Build output template
    if output_filename:
        output_template = os.path.join(output_dir, f"{output_filename}.%(ext)s")
    else:
        output_template = os.path.join(output_dir, "%(id)s.%(ext)s")
    
    cmd = [
        "yt-dlp",
        "--merge-output-format", "mp4",
        "-f", "bv*+ba/best",
        "-o", output_template,
        url
    ]
    
    print(f"Downloading reel from: {url}")
    print(f"Output directory: {output_dir}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Download complete!")
        print(result.stdout)
        
        # Try to find the downloaded file
        if output_filename:
            expected_file = os.path.join(output_dir, f"{output_filename}.mp4")
            if os.path.exists(expected_file):
                return expected_file
        
        # Look for most recent .mp4 file in output directory
        mp4_files = list(Path(output_dir).glob("*.mp4"))
        if mp4_files:
            latest_file = max(mp4_files, key=os.path.getctime)
            return str(latest_file)
        
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"Error downloading reel: {e}")
        print(f"stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        print("ERROR: yt-dlp is not installed!")
        print("Install it with: pip install yt-dlp")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_reel.py <instagram_reel_url> [output_filename]")
        print("\nExample:")
        print("  python download_reel.py https://www.instagram.com/reel/DSiZWm8jugB/")
        print("  python download_reel.py https://www.instagram.com/reel/DSiZWm8jugB/ my_video")
        sys.exit(1)
    
    url = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) > 2 else None
    
    downloaded_file = download_reel(url, output_filename=output_filename)
    
    if downloaded_file:
        print(f"\n✅ Video saved to: {downloaded_file}")
    else:
        print("\n❌ Download failed")
        sys.exit(1)
