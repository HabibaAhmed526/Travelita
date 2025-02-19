## https://serper.dev/

from dotenv import load_dotenv
load_dotenv()
import os

os.environ['SERPER_API_KEY'] = os.getenv('SERPER_API_KEY')


from crewai_tools import SerperDevTool
serper_search_tool = SerperDevTool()


# tool=[serper_search_tool, scrap_tool, website_search_tool]

tool = SerperDevTool()

