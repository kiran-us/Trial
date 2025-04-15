from langchain_tavily import TavilySearch


tavily_tool = TavilySearch(
    max_results=5,
    topic="general",
    include_domains=["https://www.fda.gov"]
    # include_answer=False,
    # include_raw_content=False,
    # include_images=False,
    # include_image_descriptions=False,
    # search_depth="basic",
    # time_range="day",
    # include_domains=None,
    # exclude_domains=None
)
