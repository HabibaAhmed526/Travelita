from crewai.tools import tool
import os
# from scrapegraph_py import Client
from tavily import TavilyClient


search_client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
# scrape_client = Client(api_key=os.getenv('scrapegraph'))



@tool
def search_engine_tool(query: str):
    """Useful for search-based queries. Use this to find current information about any query related pages using a search engine"""
    return search_client.search(query)

# @tool
# def web_scraping_tool(page_url: str):
#     """
#     An AI Tool to help an agent to scrape a web page

#     Example:
#     web_scraping_tool(
#         page_url="https://unsplash.com/s/photos/british-museum"
#     )
#     """
#     details = scrape_client.smartscraper(
#         website_url=page_url,
#         user_prompt="Extract 1 relevant image url From the web page"
#     )

#     return {
#         "page_url": page_url,
#         "details": details
#     }