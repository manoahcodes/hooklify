import requests
from pathlib import Path

def download_to_local(url: str, path: Path, parent_mkdir: bool = True):
    if not isinstance(path, Path):
        raise ValueError("path must be a Path object")
    if parent_mkdir:
        path.parent.mkdir(parents=True, exist_ok=True)
    try:
        response = requests.get(url)
        response.raise_for_status()
        path.write_bytes(response.content)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url} to {path}: {e}")
        return False