from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional, Union, Dict, Any
import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin, urlparse

class BeautifulSoupScraperInput(BaseModel):
    """Inputs for the BeautifulSoup web scraper tool"""
    url: str = Field(description="URL to scrape or download files from")
    action: str = Field(
        default="scrape",  # Added default value to fix the validation error
        description="Action to perform: 'scrape' for HTML content, 'find_links' to locate file links, or 'download' for file download"
    )
    file_type: str = Field(
        default="", 
        description="File type to search for when using 'find_links' action (e.g., 'zip', 'csv', 'xlsx')"
    )
    css_selector: str = Field(
        default="", 
        description="CSS selector to target specific content when scraping"
    )
    filename: str = Field(
        default="", 
        description="Filename to save downloaded content (optional for 'download' action)"
    )

class BeautifulSoupScraperTool(BaseTool):
    name: str = "bs4_scraper"
    description: str = "Web scraper tool using BeautifulSoup4 that can extract content, find download links, and download files (ZIP, CSV, PDF) from websites. Use action='scrape' (default) for HTML content, action='find_links' with file_type to locate file links, or action='download' for file download."
    args_schema: Type[BaseModel] = BeautifulSoupScraperInput
    return_direct: bool = False
    
    def _get_headers(self):
        """Return headers that mimic a browser visit"""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    
    def _download_file(self, url, filename=None):
        """Download a file from URL and save it"""
        try:
            response = requests.get(url, headers=self._get_headers(), stream=True, timeout=30)
            response.raise_for_status()
            
            # If no filename provided, use the filename from URL
            if not filename:
                # Extract filename from URL or content-disposition header
                if "Content-Disposition" in response.headers:
                    content_disposition = response.headers["Content-Disposition"]
                    filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
                    if filename_match:
                        filename = filename_match.group(1)
                
                # If still no filename, use the last part of the URL
                if not filename:
                    filename = url.split("/")[-1]
                    # Remove query parameters if any
                    filename = filename.split("?")[0]
            
            # Create downloads directory if it doesn't exist
            os.makedirs("downloads", exist_ok=True)
            file_path = os.path.join("downloads", filename)
            
            # Save file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return f"Successfully downloaded file to {file_path}"
        
        except Exception as e:
            return f"Error downloading file: {str(e)}"
    
    def _normalize_url(self, base_url, link):
        """Convert relative URLs to absolute URLs"""
        parsed_base = urlparse(base_url)
        
        # Already absolute URL
        if link.startswith(('http://', 'https://')):
            return link
        
        # Protocol-relative URL
        if link.startswith('//'):
            return f"{parsed_base.scheme}:{link}"
        
        return urljoin(base_url, link)
    
    # Fix: Add tool_call_id parameter with default value of None
    def _parse_input(self, tool_input: Union[str, Dict[str, Any]], tool_call_id: Optional[str] = None) -> Dict[str, Any]:
        """Parse the tool input to handle both string and dict inputs"""
        if isinstance(tool_input, str):
            # If tool_input is just a string, assume it's a URL
            return {"url": tool_input, "action": "scrape"}
        return tool_input
    
    def _run(self, url: str, action: str = "scrape", file_type: str = "", css_selector: str = "", filename: str = "") -> str:
        """Run the tool synchronously."""
        try:
            # For direct downloads
            if action == "download":
                return self._download_file(url, filename)
            
            # Get the page content for scraping or finding links
            response = requests.get(url, headers=self._get_headers(), timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if action == "scrape":
                if css_selector:
                    # Extract content based on selector
                    elements = soup.select(css_selector)
                    if not elements:
                        return f"No elements found matching selector: '{css_selector}'"
                    
                    result = "\n\n".join([elem.get_text(strip=True) for elem in elements])
                    return result
                else:
                    # Extract readable text content from the page
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.extract()
                    
                    # Get text
                    text = soup.get_text(separator='\n', strip=True)
                    
                    # Break into lines and remove leading/trailing space
                    lines = (line.strip() for line in text.splitlines())
                    # Break multi-headlines into a line each
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    # Drop blank lines
                    text = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    return text[:4000] + "..." if len(text) > 4000 else text
            
            elif action == "find_links":
                # Find links with the specified file type
                file_links = []
                
                # Look for anchor tags with href attributes
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    link_text = a_tag.get_text(strip=True) or href.split('/')[-1]
                    
                    # Convert relative URLs to absolute
                    absolute_url = self._normalize_url(url, href)
                    
                    # Check if the link contains the specified file type
                    if file_type.lower() in href.lower() or file_type.lower() in link_text.lower():
                        file_links.append({
                            'text': link_text,
                            'url': absolute_url
                        })
                
                # Look for other elements that might contain download links
                download_buttons = soup.find_all(['button', 'div', 'span'], 
                                               string=re.compile(r'download|.zip|.csv|.xlsx', re.I))
                for button in download_buttons:
                    # Check if parent or nearby elements have href
                    parent = button.parent
                    if parent.name == 'a' and parent.has_attr('href'):
                        href = parent['href']
                        absolute_url = self._normalize_url(url, href)
                        file_links.append({
                            'text': button.get_text(strip=True),
                            'url': absolute_url
                        })
                
                # Remove duplicates while preserving order
                unique_links = []
                seen_urls = set()
                for link in file_links:
                    if link['url'] not in seen_urls:
                        unique_links.append(link)
                        seen_urls.add(link['url'])
                
                if not unique_links:
                    return f"No links containing '{file_type}' found on the page."
                
                result = f"Found {len(unique_links)} links related to '{file_type}':\n\n"
                for i, link in enumerate(unique_links, 1):
                    result += f"{i}. {link['text']}: {link['url']}\n"
                
                return result
            
            return f"Invalid action specified: {action}. Use 'scrape', 'find_links', or 'download'."
            
        except Exception as e:
            return f"Error during web scraping: {str(e)}"

# Create the tool
bs4_scraper = BeautifulSoupScraperTool()