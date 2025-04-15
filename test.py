import os
import requests
from typing import Optional

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
    
    
download_file(
    url="https://www.accessdata.fda.gov/cder/ndcxls.zip",
    filename="FDA_SPL_Guide.pdf"
)