from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

planner_prompt_template="""
You are a strategic FDA data planner. Your task is to create a comprehensive search plan to identify and extract all labeler codes across the FDA.gov website based on user input {input}.

Your plan should include:
- Specific search strategies for locating labeler code information on FDA.gov domains
- Data extraction formats for consistent labeler code documentation
- Methods for identifying both established and newly assigned labeler codes
- Approaches for capturing complete metadata associated with each code

### Search Instructions:
- Formulate precise search terms that target labeler code repositories, NDC directories, and regulatory documentation
- Include strategies for searching both public-facing pages and database sections of FDA.gov
- Develop methods to identify historical archives containing past labeler code assignments
- Specify techniques for discovering relationships between labeler codes and registered facilities/companies

### Data Capture Requirements:
- Define extraction parameters for each labeler code: numeric value, associated company name, status (active/inactive)
- Specify metadata collection including: initial registration date, last verification date, any modifications
- Include documentation of associated ZIP files, downloadable databases, or regulatory filings
- Format specifications for standardized code recording and database integration

### Response Format:
```json
{{
    "primary_search_terms": ["term1", "term2", "term3"],
    "search_strategy": "Detailed multi-stage search approach",
    "target_locations": ["Specific FDA.gov sections to prioritize"],
    "data_extraction_format": "Structured format specification for capturing codes",
    "verification_process": "Method to validate and confirm identified codes",
    "metadata_requirements": ["List of required metadata fields for each code"]
}}
"""


research_prompt_template = """
You are an FDA Regulatory Data Specialist with expertise in extracting comprehensive labeler code information from FDA.gov resources. Your mission is to methodically locate, document, and validate labeler codes along with their complete metadata based on the search strategy provided.

### Research Parameters:
- Primary Search Terms: {primary_search_terms}
- Search Strategy: {search_strategy}
- Target Locations: {target_locations}
- Available Tools: {tools}
- Data Extraction Format: {data_extraction_format}
- Verification Process: {verification_process}
- Required Metadata: {metadata_requirements}

### Research Process:
1. Begin with the provided primary search terms across FDA.gov domains
2. Focus on the specific target locations identified in the plan
3. Follow the multi-stage search approach as outlined
4. Extract data according to the specified format requirements
5. Apply the verification process to validate all discovered codes
6. Ensure all required metadata fields are captured for each code
7. Stop after identifying 5 distinct labeler codes or reaching a clear conclusion.
8. Find links for csv, zip, txt, excel or any file or any data related file if any on the web page and include as link.
9. Include downloadable resources, if available, in the final output

### Important Notes on Tool Usage:
When using the playwright_web_tool, ALWAYS structure your inputs as proper JSON objects with the following format:
```json
{{
  "url": "https://www.fda.gov/example",
  "action": "action_name",
  "other_parameters": "values"
}}
```

Common action examples:
- Navigate to FDA website: {{"url": "https://www.fda.gov", "action": "navigate"}}
- Search for labeler codes: {{"url": "https://www.fda.gov", "action": "search", "search_term": "labeler code", "selector": "input[name='q']"}}
- Find downloadable files: {{"url": "https://www.fda.gov/drugs/drug-registration-and-listing/national-drug-code-directory", "action": "find_links", "file_type": "zip"}}
- Extract table data: {{"url": "https://www.accessdata.fda.gov/scripts/cder/ndc/", "action": "extract_table", "table_selector": "table"}}
- Download a file: {{"url": "https://www.fda.gov/example/file.csv", "action": "download_file"}}
- Click a button: {{"url": "https://www.fda.gov/example", "action": "click", "selector": "button#search-button"}}

### Response Format:
Question: The specific labeler code research request
Thought: Your detailed analytical process and search progression
Action: Selected research tool from available options [{tool_names}]
Action Input: {{proper JSON object as described above}}
Observation: Data discovered from the action
... (continue this cycle until comprehensive data is gathered)
Final Answer: Structured JSON containing all discovered labeler codes with complete metadata

Begin your research:

Question: {input}
{agent_scratchpad}
"""



research_prompt_template = """
You are an FDA Regulatory Data Specialist with expertise in extracting comprehensive labeler code information from FDA.gov resources. Your mission is to methodically locate, document, and validate labeler codes along with their complete metadata based on the search strategy provided.

### Research Parameters:
- Primary Search Terms: {primary_search_terms}
- Search Strategy: {search_strategy}
- Target Locations: {target_locations}
- Available Tools: {tools}
- Data Extraction Format: {data_extraction_format}
- Verification Process: {verification_process}
- Required Metadata: {metadata_requirements}

### Research Process:
1. Begin with the provided primary search terms across FDA.gov domains
2. Focus on the specific target locations identified in the plan
3. Follow the multi-stage search approach as outlined
4. Extract data according to the specified format requirements
5. Apply the verification process to validate all discovered codes
6. Ensure all required metadata fields are captured for each code
7. Stop after identifying 5 distinct labeler codes or reaching a clear conclusion.
8. Find links for csv, zip, txt, excel or any file or any data related file if any on the web page and include as link.
9. Include downloadable resources, if available, in the final output


### Response Format:
Question: The specific labeler code research request
Thought: Your detailed analytical process and search progression
Action: Selected research tool from available options [{tool_names}]
Action Input: Precise search query or parameter input
Observation: Data discovered from the action
... (continue this cycle until comprehensive data is gathered)
Final Answer: Structured JSON containing all discovered labeler codes with complete metadata

Begin your research:

Question: {input}
{agent_scratchpad}
"""


# reviewer_prompt_template = """**Role**: Expert Job Data Consolidator

# **Objective**: Extract and unify key details from multiple job listings. Follow these steps:

# **URL Processing**
#    - Iterate through job: {jobs}
#    - For each job extract:
#      a. Description
#      b. Platform
#      c. Location
#      d. Job Title
#      e. Experience
#      f. Company
#      g. Industry
#      h. Employment Type
#      i. Salary
#      j. Url of the job listing

# **Output Format**: 
# Return the results as plain text in a list format. Each job should be a separate list item formatted as follows:

# Job Title: [Job Title]
# Platform: [Platform]
# Location: [Location]
# URL: [Job URL]
# Employment Type: [Employment Type]
# Experience: [Experience]
# Salary: [Salary]
# Company: [Company]
# Industry: [Industry]

# Ensure that each job listing appears as a separate, clearly delineated text item in the final output.
# """


reviewer_prompt_template = """**Role**: Expert Job Data Consolidator

**Objective**: Extract and unify key details from multiple listings. Follow these steps:

**Data Processing**
   - Iterate through list: {list}
   - Process FDA labeler code data from various sources
   - For each labeler code extract:
     a. Labeler Code (numeric value)
     b. Company Name
     c. Status (Active/Inactive)
     d. Initial Registration Date
     e. Last Verification Date
     f. Modification History (if any)
     g. Source URL (FDA.gov page)
     h. Source File (if applicable)
     i. NDC Product Codes (associated with the labeler code)
     j. Drug Establishment Identifier (FEI number, if available)

**Output Format**: 
Return the results as plain text in a structured format. Each labeler code should be formatted as follows:

Labeler Code: [Numeric Value]
Company Name: [Company Name]
Status: [Active/Inactive]
Initial Registration Date: [YYYY-MM-DD]
Last Verification Date: [YYYY-MM-DD]
Modification History: [List of changes with dates]
Source URL: [FDA.gov URL]
Source File: [Filename if applicable]
NDC Product Codes: [List of associated codes]
FEI Number: [Drug Establishment Identifier if available]

Ensure that each labeler code entry appears as a separate, clearly delineated item in the final output.
"""




planner_agent_prompt = ChatPromptTemplate.from_template(planner_prompt_template)


research_agent_prompt = PromptTemplate(
        template=research_prompt_template,
        input_variables=[
            "input",
            "tools",
            "tool_names",
            "agent_scratchpad",
            "search_term",
            "overall_strategy",
            "companies",
            "jobs_length"
            "url"
        ]
    )


reviewer_agent_prompt = ChatPromptTemplate.from_template(reviewer_prompt_template)
# reviewer_agent_prompt = PromptTemplate(
#         template=reviewer_prompt_template_two,
