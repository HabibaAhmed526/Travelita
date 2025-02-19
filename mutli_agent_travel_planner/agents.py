from .tools import tool 
from crewai import Agent, Crew, Task, LLM 
from dotenv import load_dotenv
load_dotenv()
import os

llm = LLM(
    model="gemini/gemini-2.0-flash",
    api_key=os.environ["GOOGLE_API_KEY"]
)

# Best Time to Visit Agent
best_time_agent = Agent(
    role='Best Time to Visit Specialist',
    goal='Provide seasonal highlights and weather considerations for {destination} based on {travel_style} and {budget}, ensuring the best experience during {duration} days.',
    verbose=False,
    memory=True,
    backstory=(
        "You specialize in understanding the best times to visit a destination based on weather conditions, seasonal events, and budget-friendly travel periods."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=False,
    max_iter=2
)

# Accommodation Agent
accommodation_agent = Agent(
    role='Accommodation Specialist',
    goal='Find hotels or stays in the {budget} range in {destination} for {duration} days, considering {travel_style}. Gather essential details including hotel name, description, price, rating, address, and website link.',
    verbose=False,
    memory=True,
    backstory=(
        "You are an expert in finding budget-friendly accommodation options tailored to different travel styles."
        "Extract key details such as hotel name, description, price, rating, and link from reputable sources."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=False,
    max_iter=3
)

# Itinerary Agent
itinerary_agent = Agent(
    role='Itinerary Planner',
    goal='Generate a day-by-day itinerary for {destination} for {duration} days, including key activities and must-visit places for {travel_style} within the {budget} range. Provide image links for each recommended place.',
    verbose=False,
    memory=True,
    backstory=(
        "You are skilled at planning personalized travel itineraries, ensuring activities align with different budgets and travel styles while incorporating engaging images."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=False,
    max_iter=2
)

# Culinary Experience Agent
culinary_experience_agent = Agent(
    role='Culinary Experience Guide',
    goal='Suggest local dishes, restaurant recommendations, and food experiences in {destination}, considering {budget}, {travel_style}, and {duration}. Provide image links for recommended dishes.',
    verbose=False,
    memory=True,
    backstory=(
        "You have extensive knowledge of local cuisines and can suggest the best food experiences tailored to different travel styles and budgets."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=False,
    max_iter=2
)

# Practical Tips Agent
practical_tips_agent = Agent(
    role='Practical Tips Specialist',
    goal='Provide essential travel tips for {destination}, including transportation, cultural etiquette, safety, and daily budget estimates for {duration} days, aligned with {travel_style} and {budget}.',
    verbose=False,
    memory=True,
    backstory=(
        "You are a travel expert providing practical advice to ensure a smooth and safe trip, focusing on budgeting, cultural practices, and local transportation."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=False,
    max_iter=2
)

# Cost Estimation Agent
cost_estimation_agent = Agent(
    role='Cost Estimator',
    goal='Estimate the total cost for {destination} for {duration} days, considering {travel_style} and staying within the {budget} range. Include accommodation, food, and activities while providing money-saving tips.',
    verbose=False,
    memory=True,
    backstory=(
        "You are proficient at estimating travel costs based on provided details from other agents, considering all aspects like accommodation, meals, and activities. You also offer cost-saving suggestions."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=False,
    max_iter=3
)

# Finalizer Agent
finalizer_agent = Agent(
    role="Final Report Compiler",
    goal="Merge and format outputs from multiple agents into a structured Markdown travel plan for {destination}, ensuring alignment with {duration}, {travel_style}, and {budget}. Ensure that each section is properly formatted in an appealing way and includes relevant images.",
    verbose=False,
    memory=True,
    backstory=(
        "You are proficient at structuring and formatting travel plans. Your role is to compile all outputs from other agents into a visually appealing markdown format for easy display in a Streamlit app."
    ),
    llm=llm,
    allow_delegation=False
)

# Initialize travel agent with Groq Llama model and SerpAPI
travel_agent = Agent(
    role="Travel Planner",
    goal="Provide a focused, concise answer that relates to the existing travel plan if possible. Now, please answer this specific question: {question}. Here's the existing plan: {travel_plan} th finding attractions, suggesting accommodations, and providing transportation options.",
    backstory=("You are a helpful agent that help people answer questions based on the existing travel plan, or provides tailored travel plans based on their preferences."),
    llm=llm,
    verbose=False,
    memory=True,
    allow_delegation=False
)
