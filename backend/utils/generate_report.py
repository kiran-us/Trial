import json

def generate_report(data):
    # Initialize Markdown string with main heading
    markdown = "# 2020 Hyundai Car Listings\n\n"
    
    # Iterate through each platform's data
    for platform_data in data:
        platform = platform_data['platform']
        listings = platform_data['listings']
        filters = platform_data['filters_applied']
        observations = platform_data['observations']
        
        # Add platform heading and sections
        markdown += f"## {platform}\n\n"
        markdown += "**Listings:**\n\n"
        
        # Process each car listing
        for listing in listings:
            # Use model as the main bullet point
            markdown += f"- **{listing['model']}**\n"
            # Iterate through listing details, excluding 'model'
            for key, value in listing.items():
                if key != 'model':
                    if key == 'link':
                        # Format link as clickable Markdown link
                        markdown += f"  - **Link:** [View Listing]({value})\n"
                    else:
                        # Format other keys with title case and proper spacing
                        markdown += f"  - **{key.replace('_', ' ').title()}:** {value}\n"
            # Add a blank line after each listing
            markdown += "\n"
        
        # Add filters and observations as paragraphs
        markdown += f"**Filters Applied:** {filters}\n\n"
        markdown += f"**Observations:** {observations}\n\n"
    
    return markdown