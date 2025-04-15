import os 
import requests
from typing import List, Dict, Any, Optional


def download_file(url: str, filename: str, download_directory: str = "downloaded_files") -> Optional[str]:
    """
    Downloads a file from a URL and saves it to the specified directory.

    Args:
        url (str): The URL of the file to download.
        filename (str): The name to save the file as.
        download_directory (str, optional): The directory to save the file in.
                                            Defaults to "downloaded_files".

    Returns:
        Optional[str]: The full path to the downloaded file, or None if the download failed.
    """
    os.makedirs(download_directory, exist_ok=True)
    filepath = os.path.join(download_directory, filename)

    try:
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()  # Raises HTTPError for bad responses
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        print(f"[✓] Successfully downloaded '{filename}' to '{filepath}'")
        return filepath
    except requests.exceptions.RequestException as e:
        print(f"[✗] Failed to download from '{url}': {e}")
        return None

def download_and_list_files(data: List[Dict[str, Any]]) -> List[str]:
    """Downloads files from a list of dictionaries containing file URLs and names.

    Args:
        data (List[Dict[str, Any]]): A list of dictionaries, where each dictionary
                                     is expected to have 'file_url' and 'file_name' keys.

    Returns:
        List[str]: A list of full paths to the successfully downloaded files.
    """
    downloaded_files = []
    for item in data:
        if "source_file" in item or "file_url" in item or "file_name" in item:
            filepath = download_file(item["file_url"], item["file_name"])
            if filepath:
                downloaded_files.append(filepath)
        else:
            print("Warning: 'file_url' or 'file_name' not found in an item.")
    return downloaded_files
