from phi.model.groq import Groq  # Assuming this is how you import Groq Llama
from phi.agent import Agent
from phi.tools.serpapi_tools import SerpApiTools

travel_agent = Agent(
    name="Travel Planner",
    model=Groq(id="llama-3.3-70b-versatile"),  # Adjust if necessary based on actual import
    instructions = [
        "You are a travel planning assistant using Groq Llama.",
        "You are required to answer the traveller's questions and adjust the existing travel plan based on his/her preferences",
        "Help users customize and refine their travel plans by adjusting schedules, preferences, and budgets.",
        "if it is required, summarize key details of destinations, accommodations, and attractions for easy decision-making.",
        "Ensure all information is current and verified before making recommendations.",
        "If a user is unsure, offer personalized suggestions based on their travel style (luxury, budget, adventure, etc.)."
    ],
    show_tool_calls=True,
    markdown=True,
    tools=[SerpApiTools()]
)