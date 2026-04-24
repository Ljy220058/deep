import os
import sys
import argparse
import shutil
import time
from pathlib import Path
from huggingface_hub import snapshot_download, hf_hub_download

# Ensure UTF-8 output for Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_downloads_folder():
    if os.name == 'nt':
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    return os.path.expanduser('~/Downloads')

def move_from_downloads(filename, target_dir):
    downloads = get_downloads_folder()
    source = os.path.join(downloads, filename)
    if os.path.exists(source):
        print(f"Found {filename} in Downloads. Moving to {target_dir}...")
        os.makedirs(target_dir, exist_ok=True)
        shutil.move(source, os.path.join(target_dir, filename))
        return True
    return False

def download_model(repo_id, cache_dir, filename=None, mirror=True):
    if mirror:
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        print(f"Using mirror: {os.environ['HF_ENDPOINT']}")

    os.environ["HF_HOME"] = cache_dir
    os.environ["MODEL_CACHE_DIR"] = cache_dir
    
    try:
        if filename:
            print(f"Downloading file '{filename}' from repo '{repo_id}'...")
            path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                cache_dir=cache_dir,
                resume_download=True,
                local_dir_use_symlinks=False
            )
        else:
            print(f"Downloading entire repo '{repo_id}'...")
            path = snapshot_download(
                repo_id=repo_id,
                cache_dir=cache_dir,
                resume_download=True,
                local_dir_use_symlinks=False,
                max_workers=8
            )
        print(f"✅ Successfully downloaded to: {path}")
        return path
    except Exception as e:
        print(f"❌ Error during download: {str(e)}")
        return None

def validate_dir(path):
    if not os.path.exists(path):
        print(f"❌ Path does not exist: {path}")
        return False
    
    files = list(Path(path).rglob('*'))
    total_size = sum(f.stat().st_size for f in files if f.is_file()) / (1024 * 1024)
    print(f"✅ Directory validated. Total size: {total_size:.2f} MB")
    print(f"Files found: {len(files)}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hugging Face Model Manager")
    parser.add_argument("--repo", required=True, help="Hugging Face repo ID")
    parser.add_argument("--cache", required=True, help="Cache directory")
    parser.add_argument("--file", help="Specific file to download")
    parser.add_argument("--move", help="Filename to move from Downloads first")
    parser.add_argument("--no-mirror", action="store_true", help="Disable HF mirror")
    
    args = parser.parse_args()
    
    if args.move:
        # If move is specified, we try to move it to a subfolder in cache first
        # For simplicity, we move it to a 'manual_downloads' folder or repo-specific folder
        target = os.path.join(args.cache, args.repo.replace('/', '--'))
        move_from_downloads(args.move, target)
        
    path = download_model(args.repo, args.cache, args.file, not args.no_mirror)
    if path:
        validate_dir(path)
