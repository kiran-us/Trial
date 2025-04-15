from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional, Union, Dict, Any, List, ClassVar
import asyncio
import os
import re
from urllib.parse import urljoin, urlparse
import time
from playwright.async_api import async_playwright
import json


class PlaywrightScraperInput(BaseModel):
    """Inputs for the Playwright web interaction tool"""
    url: str = Field(description="URL to navigate to")
    action: str = Field(
        default="scrape_page",
        description="Action to perform: 'scrape_page', 'find_links', 'download_file', 'click', 'fill_form', 'search', 'extract_table', 'navigate'"
    )
    selector: str = Field(
        default="", 
        description="CSS selector for targeting specific elements (for click, fill_form, etc.)"
    )
    text_to_enter: str = Field(
        default="", 
        description="Text to enter in form fields when using 'fill_form' action"
    )
    file_type: str = Field(
        default="", 
        description="File type to search for when using 'find_links' action (e.g., 'zip', 'csv', 'xlsx')"
    )
    wait_for: str = Field(
        default="", 
        description="Selector to wait for before proceeding with the action"
    )
    download_path: str = Field(
        default="downloads", 
        description="Directory to save downloaded files"
    )
    form_data: Dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary of form field selectors and values to fill"
    )
    search_term: str = Field(
        default="",
        description="Term to search for on the page"
    )
    table_selector: str = Field(
        default="table",
        description="CSS selector for targeting tables for extraction"
    )


class PlaywrightScraperTool(BaseTool):
    name: str = "playwright_web_tool"
    description: str = """
    Advanced web interaction tool using Playwright that can navigate websites, extract content, 
    fill forms, click buttons, find and download files, and extract tables. Capable of performing 
    complex web interactions similar to a human user.
    
    Actions:
    - 'scrape_page': Extract readable text content from the current page
    - 'find_links': Locate links matching specified file types (zip, csv, pdf, etc.)
    - 'download_file': Download a file from a given URL
    - 'click': Click on elements matching the provided selector
    - 'fill_form': Fill form fields with provided data
    - 'search': Search for text on a website
    - 'extract_table': Extract data from HTML tables
    - 'navigate': Navigate to a URL or click through multiple pages
    
    Usage examples:
    {"url": "https://www.fda.gov", "action": "navigate"}
    {"url": "https://www.fda.gov", "action": "scrape_page"}
    {"url": "https://www.fda.gov", "action": "search", "search_term": "labeler code", "selector": "input[name='q']"}
    {"url": "https://www.fda.gov/drugs/drug-registration-and-listing/national-drug-code-directory", "action": "find_links", "file_type": "zip"}
    """
    args_schema: Type[BaseModel] = PlaywrightScraperInput
    return_direct: bool = False
    
    # Define class variables to store browser state
    # Note: These will be reset on each new instance
    _browser_state: ClassVar[Dict[str, Any]] = {
        "browser": None,
        "context": None,
        "page": None
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create downloads directory
        os.makedirs("downloads", exist_ok=True)
    
    def _parse_input(self, tool_input: Union[str, Dict[str, Any]], tool_call_id: Optional[str] = None) -> Dict[str, Any]:
        """Parse the tool input to handle both string and dict inputs"""
        if isinstance(tool_input, str):
            try:
                # Try to parse as JSON if it's a string
                return json.loads(tool_input)
            except json.JSONDecodeError:
                # If not valid JSON, assume it's a URL
                return {"url": tool_input, "action": "scrape_page"}
        return tool_input
    
    async def _setup_browser(self):
        """Set up the Playwright browser instance"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            viewport={'width': 1280, 'height': 800},
            accept_downloads=True
        )
        
        # Add storage state if needed for maintaining sessions
        # await context.add_cookies([...])
        
        return playwright, browser, context
    
    async def _close_browser(self, playwright, browser):
        """Close the Playwright browser instance"""
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()
    
    async def _scrape_page_content(self, page, selector="body"):
        """Extract readable text content from the page"""
        if selector and selector != "body":
            try:
                elements = await page.query_selector_all(selector)
                texts = []
                for element in elements:
                    text = await element.evaluate('el => el.textContent')
                    if text:
                        texts.append(text.strip())
                return "\n\n".join(texts)
            except Exception as e:
                return f"Error extracting content with selector '{selector}': {str(e)}"
        
        # Default extraction of all page content
        try:
            # Extract text content
            content = await page.evaluate('''
                () => {
                    // Remove script and style elements
                    const scripts = document.querySelectorAll('script, style');
                    scripts.forEach(script => script.remove());
                    
                    // Get text content
                    return document.body.innerText;
                }
            ''')
            
            # Clean up the content
            lines = content.splitlines()
            clean_lines = [line.strip() for line in lines if line.strip()]
            return "\n".join(clean_lines)
        except Exception as e:
            return f"Error extracting page content: {str(e)}"
    
    async def _find_links(self, page, file_type=""):
        """Find links on the page that match the specified file type"""
        try:
            links = await page.evaluate(f'''
                (fileType) => {{
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    return links
                        .filter(link => link.href.toLowerCase().includes(fileType.toLowerCase()) || 
                                        (link.textContent && link.textContent.toLowerCase().includes(fileType.toLowerCase())))
                        .map(link => ({{
                            text: link.textContent ? link.textContent.trim() : link.href.split('/').pop(),
                            url: link.href,
                            type: 'link'
                        }}));
                }}
            ''', file_type)
            
            # Also find download buttons or other elements
            buttons = await page.evaluate(f'''
                (fileType) => {{
                    // Look for buttons, divs, spans with download-related text
                    const downloadPattern = new RegExp('download|' + fileType, 'i');
                    const elements = Array.from(document.querySelectorAll('button, div, span, a'));
                    return elements
                        .filter(el => el.textContent && downloadPattern.test(el.textContent))
                        .map(el => {{
                            // Check if it's a button within a link or has a parent link
                            const parentLink = el.closest('a[href]');
                            return {{
                                text: el.textContent.trim(),
                                url: parentLink ? parentLink.href : null,
                                type: el.tagName.toLowerCase(),
                                hasLink: !!parentLink
                            }};
                        }})
                        .filter(item => item.hasLink); // Only keep items that have an associated link
                }}
            ''', file_type)
            
            # Combine and remove duplicates
            all_items = links + [b for b in buttons if b["url"]]
            unique_links = []
            seen_urls = set()
            
            for item in all_items:
                if item["url"] and item["url"] not in seen_urls:
                    unique_links.append(item)
                    seen_urls.add(item["url"])
            
            if not unique_links:
                return f"No links containing '{file_type}' found on the page."
            
            result = f"Found {len(unique_links)} links related to '{file_type}':\n\n"
            for i, link in enumerate(unique_links, 1):
                result += f"{i}. {link['text']}: {link['url']}\n"
            
            return result
        
        except Exception as e:
            return f"Error finding links: {str(e)}"
    
    async def _download_file(self, page, url, download_path="downloads"):
        """Download a file from the given URL"""
        try:
            # Create download directory if it doesn't exist
            os.makedirs(download_path, exist_ok=True)
            
            # Navigate to the URL if not already there
            current_url = page.url
            if current_url != url:
                await page.goto(url, wait_until="domcontentloaded")
            
            # Set up download listener
            download_promise = page.wait_for_download()
            
            # Try clicking if there's a download button (common for download pages)
            try:
                # Look for download buttons
                download_button = await page.query_selector("a[download], button:has-text('Download'), a:has-text('Download')")
                if download_button:
                    await download_button.click()
                else:
                    # If no button found, the URL itself might be the download link
                    await page.goto(url, wait_until="domcontentloaded")
            except Exception:
                # If clicking fails, the URL itself is probably the download link
                await page.goto(url, wait_until="domcontentloaded")
            
            # Wait for download to start
            try:
                download = await download_promise
                # Save the download to the specified path
                path = os.path.join(download_path, download.suggested_filename())
                await download.save_as(path)
                return f"Successfully downloaded file to {path}"
            except Exception as e:
                return f"Error initiating download: {str(e)}"
                
        except Exception as e:
            return f"Error during download: {str(e)}"
    
    async def _click_element(self, page, selector):
        """Click an element matching the selector"""
        try:
            # Wait for the element to be visible
            await page.wait_for_selector(selector, state="visible", timeout=5000)
            # Click the element
            await page.click(selector)
            # Wait for any navigation or network requests to complete
            await page.wait_for_load_state("networkidle")
            
            return f"Successfully clicked element matching selector: '{selector}'"
        except Exception as e:
            return f"Error clicking element: {str(e)}"
    
    async def _fill_form(self, page, form_data):
        """Fill form fields with the provided data"""
        try:
            results = []
            
            for selector, value in form_data.items():
                try:
                    # Wait for the form field to be visible
                    await page.wait_for_selector(selector, state="visible", timeout=5000)
                    # Fill the form field
                    await page.fill(selector, value)
                    results.append(f"Filled '{selector}' with value: '{value}'")
                except Exception as e:
                    results.append(f"Error filling '{selector}': {str(e)}")
            
            return "\n".join(results)
        except Exception as e:
            return f"Error filling form: {str(e)}"
    
    async def _search(self, page, url, search_term, selector=""):
        """Search for a term on a website"""
        try:
            # Navigate to the URL
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle")
            
            # Look for a search box if selector is not provided
            if not selector:
                search_selectors = [
                    "input[type='search']",
                    "input[name='search']", 
                    "input[name='q']",
                    "input[placeholder*='search' i]",
                    "input[aria-label*='search' i]",
                    ".search-input",
                    "#search"
                ]
                
                for search_selector in search_selectors:
                    if await page.query_selector(search_selector):
                        selector = search_selector
                        break
            
            if not selector:
                return "Could not find a search input on the page."
            
            # Fill the search box
            await page.fill(selector, search_term)
            
            # Press Enter to submit the search
            await page.press(selector, "Enter")
            
            # Wait for results to load
            await page.wait_for_load_state("networkidle")
            
            # Return confirmation and also get the search results text
            search_results = await self._scrape_page_content(page)
            return f"Searched for '{search_term}' using selector '{selector}'. Current URL: {page.url}\n\nSearch Results Preview:\n{search_results[:1500]}..."
        
        except Exception as e:
            return f"Error during search: {str(e)}"
    
    async def _extract_table(self, page, table_selector="table"):
        """Extract data from HTML tables on the page"""
        try:
            # Check if tables exist
            tables = await page.query_selector_all(table_selector)
            
            if not tables:
                return "No tables found matching the selector."
            
            all_tables_data = []
            
            for i, table in enumerate(tables):
                # Extract table data
                table_data = await page.evaluate('''
                    (table) => {
                        const rows = Array.from(table.querySelectorAll('tr'));
                        
                        // Extract headers
                        const headers = Array.from(rows[0]?.querySelectorAll('th, td') || [])
                            .map(cell => cell.textContent.trim());
                        
                        // Extract data rows
                        const dataRows = rows.slice(headers.length > 0 ? 1 : 0)
                            .map(row => {
                                const cells = Array.from(row.querySelectorAll('td, th'))
                                    .map(cell => cell.textContent.trim());
                                return cells;
                            });
                        
                        return {
                            headers: headers,
                            rows: dataRows
                        };
                    }
                ''', table)
                
                all_tables_data.append({
                    "table_index": i,
                    "data": table_data
                })
            
            # Format the result
            result = f"Extracted {len(all_tables_data)} table(s):\n\n"
            
            for table_info in all_tables_data:
                table_idx = table_info["table_index"]
                table_data = table_info["data"]
                
                result += f"Table {table_idx + 1}:\n"
                
                if table_data["headers"]:
                    result += "Headers: " + json.dumps(table_data["headers"]) + "\n"
                
                result += f"Rows: {len(table_data['rows'])}\n"
                
                # Show first 5 rows as preview
                preview_rows = table_data["rows"][:5]
                result += "Preview:\n"
                
                for row in preview_rows:
                    result += json.dumps(row) + "\n"
                
                result += "\n"
            
            return result
        
        except Exception as e:
            return f"Error extracting tables: {str(e)}"
    
    async def _navigate(self, page, url, wait_for=""):
        """Navigate to a URL and wait for specified selector if provided"""
        try:
            # Navigate to the URL
            response = await page.goto(url, wait_until="domcontentloaded")
            
            # Wait for load state
            await page.wait_for_load_state("networkidle")
            
            # Wait for specific selector if provided
            if wait_for:
                try:
                    await page.wait_for_selector(wait_for, timeout=10000)
                    return f"Successfully navigated to {url} and found element matching '{wait_for}'"
                except Exception as e:
                    return f"Navigated to {url} but could not find element matching '{wait_for}': {str(e)}"
            
            return f"Successfully navigated to {url}"
        
        except Exception as e:
            return f"Error navigating to {url}: {str(e)}"
    
    def _run(self, 
             url: str, 
             action: str = "scrape_page", 
             selector: str = "", 
             text_to_enter: str = "",
             file_type: str = "", 
             wait_for: str = "", 
             download_path: str = "downloads",
             form_data: Dict[str, str] = None,
             search_term: str = "",
             table_selector: str = "table") -> str:
        """Run the tool synchronously by running the async method in an event loop."""
        return asyncio.run(self._arun(
            url=url,
            action=action,
            selector=selector,
            text_to_enter=text_to_enter,
            file_type=file_type,
            wait_for=wait_for,
            download_path=download_path,
            form_data=form_data or {},
            search_term=search_term,
            table_selector=table_selector
        ))
    
    async def _arun(self, 
                    url: str, 
                    action: str = "scrape_page", 
                    selector: str = "", 
                    text_to_enter: str = "",
                    file_type: str = "", 
                    wait_for: str = "", 
                    download_path: str = "downloads",
                    form_data: Dict[str, str] = None,
                    search_term: str = "",
                    table_selector: str = "table") -> str:
        """Run the tool asynchronously."""
        playwright = None
        browser = None
        context = None
        page = None
        
        try:
            # Set up the browser
            playwright, browser, context = await self._setup_browser()
            
            # Create a new page
            page = await context.new_page()
            
            # Set timeout for navigation
            page.set_default_timeout(30000)  # 30 seconds
            
            # Handle the different actions
            if action == "navigate":
                return await self._navigate(page, url, wait_for)
            
            # Navigate to the URL first for all other actions
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle")
            
            # Wait for specific element if requested
            if wait_for:
                try:
                    await page.wait_for_selector(wait_for, timeout=10000)
                except Exception as e:
                    return f"Navigated to {url} but failed to find element matching '{wait_for}': {str(e)}"
            
            # Perform the requested action
            if action == "scrape_page":
                return await self._scrape_page_content(page, selector)
            elif action == "find_links":
                return await self._find_links(page, file_type)
            elif action == "download_file":
                return await self._download_file(page, url, download_path)
            elif action == "click":
                return await self._click_element(page, selector)
            elif action == "fill_form":
                return await self._fill_form(page, form_data if form_data else {selector: text_to_enter})
            elif action == "search":
                return await self._search(page, url, search_term, selector)
            elif action == "extract_table":
                return await self._extract_table(page, table_selector)
            else:
                return f"Unknown action: {action}"
        
        except Exception as e:
            return f"Error during {action}: {str(e)}"
        
        finally:
            # Clean up
            if page:
                await page.close()
            
            # Close the browser
            await self._close_browser(playwright, browser)

# Create the tool
playwright_web_tool = PlaywrightScraperTool()