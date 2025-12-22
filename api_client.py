#!/usr/bin/env python3
"""
Simple CLI client to interact with RunPod API
Upload videos from local machine, process on cloud, download results
"""

import requests
import sys
import time
from pathlib import Path

def upload_and_process(api_url: str, video_path: str, model_name: str = "default_model"):
    """Upload video to RunPod API and start processing"""
    
    if not Path(video_path).exists():
        print(f"❌ Error: Video file not found: {video_path}")
        return None
    
    print(f"📤 Uploading {video_path} to {api_url}...")
    
    with open(video_path, 'rb') as f:
        files = {'video': f}
        data = {'model_name': model_name}
        
        try:
            response = requests.post(
                f"{api_url}/process",
                files=files,
                data=data,
                timeout=300  # 5 min timeout for upload
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Upload successful!")
            print(f"📋 Job ID: {result['job_id']}")
            return result['job_id']
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Upload failed: {e}")
            return None

def check_status(api_url: str, job_id: str):
    """Check processing status"""
    try:
        response = requests.get(f"{api_url}/status/{job_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Status check failed: {e}")
        return None

def download_result(api_url: str, job_id: str, output_path: str):
    """Download processed video"""
    print(f"⬇️  Downloading result to {output_path}...")
    
    try:
        response = requests.get(f"{api_url}/download/{job_id}", stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Downloaded to {output_path}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Download failed: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python api_client.py <runpod_url> <video_file> [model_name]")
        print("\nExample:")
        print("  python api_client.py https://abc123-8000.proxy.runpod.net input.mp4")
        print("  python api_client.py https://abc123-8000.proxy.runpod.net input.mp4 default_model")
        sys.exit(1)
    
    api_url = sys.argv[1].rstrip('/')
    video_path = sys.argv[2]
    model_name = sys.argv[3] if len(sys.argv) > 3 else "default_model"
    
    # Upload and start processing
    job_id = upload_and_process(api_url, video_path, model_name)
    if not job_id:
        sys.exit(1)
    
    # Poll for completion
    print("\n⏳ Processing video on RunPod A100...")
    print("(This will take ~15-20 minutes for a 10-second clip)\n")
    
    while True:
        status = check_status(api_url, job_id)
        if not status:
            break
        
        current_status = status['status']
        
        if current_status == "completed":
            print("✅ Processing complete!")
            
            # Download result
            output_path = f"processed_{Path(video_path).stem}.mp4"
            download_result(api_url, job_id, output_path)
            
            # Cleanup
            print("🧹 Cleaning up remote files...")
            requests.delete(f"{api_url}/cleanup/{job_id}")
            
            print(f"\n🎉 Done! Output saved to: {output_path}")
            break
            
        elif current_status == "failed":
            print(f"❌ Processing failed: {status.get('error', 'Unknown error')}")
            break
            
        else:
            print(f"⏳ Status: {current_status} (checking again in 10s...)")
            time.sleep(10)

if __name__ == "__main__":
    main()
