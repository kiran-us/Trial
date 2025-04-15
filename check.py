# import requests
# from bs4 import BeautifulSoup

# def get_html_body(url):
#     response = requests.get(url)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, "html.parser")

#         # Remove unnecessary tags
#         for tag in soup(["script", "style", "meta", "noscript"]):
#             tag.extract()

#         return soup.body  # Returns cleaned HTML body
#     else:
#         return f"Failed to retrieve page, status code: {response.status_code}"


# url = "https://www.cartrade.com/second-hand/hyderabad/hyundai-verna/mh1vioa2/"
# html_body = get_html_body(url)
# print(html_body)


from tavily import TavilyClient
tavily_client = TavilyClient(api_key="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")


urls=[""]

query = "Information about Car https://www.cartrade.com/second-hand/hyderabad/hyundai-verna/mh1vioa2/"
context = tavily_client.search(query=query, search_depth="advanced", max_results=7)


print("context",context)

