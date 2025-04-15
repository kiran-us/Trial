import requests
import os
from tqdm import tqdm

def download_fda_labeler_codes():
    url = "https://download.open.fda.gov/ndc_nhric_labeler_codes.zip"
    filename = "ndc_nhric_labeler_codes.zip"
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*'
    }
    
    try:
        print(f"Downloading FDA Labeler Codes from {url}")
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Get total file size
        total_size = int(response.headers.get('content-length', 0))
        
        # Create a progress bar
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
        
        # Open file and write the content in chunks
        with open(filename, 'wb') as file:
            for data in response.iter_content(chunk_size=8192):
                size = file.write(data)
                progress_bar.update(size)
        
        progress_bar.close()
        print(f"\nDownload completed successfully. File saved as {filename}")
        
    except requests.RequestException as e:
        print(f"Error downloading the file: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response headers: {e.response.headers}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    download_fda_labeler_codes()
Test
