import requests
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
import re

def download_fda_labeler_codes():
    base_url = "https://www.fda.gov"
    page_url = f"{base_url}/industry/structured-product-labeling-resources/ndcnhric-labeler-codes"
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    try:
        # First get the page content to find the zip file link
        print("Fetching webpage...")
        session = requests.Session()
        response = session.get(page_url, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug: Print all links found on the page
        print("\nDebug: Scanning for zip file links...")
        for link in soup.find_all('a', href=True):
            print(f"Found link: {link['href']}")
        
        # Look for links that might contain the zip file
        zip_links = []
        for link in soup.find_all('a', href=True):
            if '.zip' in link['href'].lower():
                zip_links.append(link['href'])
                print(f"Found zip link: {link['href']}")
        
        if not zip_links:
            raise Exception("No zip file link found on the page")
            
        # Get the first zip link found
        zip_url = zip_links[0]
        if not zip_url.startswith('http'):
            zip_url = base_url + zip_url if zip_url.startswith('/') else base_url + '/' + zip_url
            
        print(f"\nAttempting to download from: {zip_url}")
        
        # Make a GET request to download the file
        print("Downloading FDA Labeler Codes file...")
        response = session.get(zip_url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Get the filename from the URL or use default name
        filename = os.path.basename(zip_url) or "labeler_codes.zip"
        content_length = int(response.headers.get('content-length', 0))
        
        # Create a progress bar
        progress_bar = tqdm(total=content_length, unit='iB', unit_scale=True)
        
        # Open file and write the content in chunks
        with open(filename, 'wb') as file:
            for data in response.iter_content(chunk_size=8192):
                size = file.write(data)
                progress_bar.update(size)
        
        progress_bar.close()
        print(f"Download completed successfully. File saved as {filename}")
        
    except requests.RequestException as e:
        print(f"Error downloading the file: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response content: {e.response.text[:500]}")  # Print first 500 chars of response
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    download_fda_labeler_codes()
