import streamlit as st
import os
from phi.agent import Agent
from phi.model.groq import Groq  
from phi.tools.serpapi_tools import SerpApiTools
import time
from dotenv import load_dotenv

load_dotenv()


st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    :root {
        --primary-color: #2E86C1;
        --accent-color: #FF6B6B;
        --background-light: #F8F9FA;
        --text-color: #2C3E50;
        --hover-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .main {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: var(--accent-color) !important;
        color: white !important;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--hover-shadow);
        background-color: #FF4A4A !important;
    }

    .sidebar .element-container {
        background-color: var(--background-light);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .stExpander {
        background-color: #262730;
        border-radius: 10px;
        padding: 1rem;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .travel-summary {
        background-color: #262730;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    .travel-summary h4 {
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }

    .spinner-text {
        font-size: 1.2rem;
        font-weight: bold;
        color: var(--primary-color);
    }

    .streamed-text span {
        color:rgb(255, 255, 255);  /* Red color for words */
        font-weight: bold;
        font-size: 1.1rem;
        padding: 0 0.1rem;
        display: inline-block;
        animation: fadeIn 0.3s ease-in-out;
    }

    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }

    </style>
""", unsafe_allow_html=True)

def stream_response(response, delay=0.1):
    """Simulates streaming the output by yielding one word at a time."""
    print("Streaming response:", response)
    for word in response.split(' '):
        yield word + ' '
        time.sleep(delay)


with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/airplane-take-off.png")
    st.title("Trip Settings")
    
    # groq_api_key = st.text_input("🔑 Enter your Groq API Key", type="password")
    # serpapi_key = st.text_input("🔑 Enter your SerpAPI Key", type="password")
    
    destination = st.text_input("🌍 Where would you like to go?", "")
    duration = st.number_input("📅 How many days?", min_value=1, max_value=30, value=5)
    
    budget = st.select_slider(
        "💰 What's your budget level?",
        options=["Budget", "Moderate", "Luxury"],
        value="Moderate"
    )
    
    travel_style = st.multiselect(
        "🎯 Travel Style",
        ["Culture", "Nature", "Adventure", "Relaxation", "Food", "Shopping"],
        ["Culture", "Nature"]
    )

if 'travel_plan' not in st.session_state:
    st.session_state.travel_plan = None
if 'qa_expanded' not in st.session_state:
    st.session_state.qa_expanded = False
if 'qa_history' not in st.session_state:
    st.session_state.qa_history = []

loading_container = st.empty()

try:
    os.environ["GROQ_API_KEY"] = os.getenv('GROQ_API_KEY')
    os.environ["SERP_API_KEY"] = os.getenv('SERP_API_KEY')

    travel_agent = Agent(
        name="Travel Planner",
        model=Groq(id="llama-3.3-70b-versatile"),  
        tools=[SerpApiTools()],
        instructions=[
            "You are a travel planning assistant using Groq Llama.",
            "Help users plan their trips by researching destinations, finding attractions, suggesting accommodations, and providing transportation options.",
            "Give me relevant live Links of each places and hotels you provide by searching on internet (It's important)",
            "Always verify information is current before making recommendations."
        ],
        show_tool_calls=True,
        markdown=True
    )

    st.title("🌎 AI Travel Planner")
    
    st.markdown(f"""
        <div class="travel-summary">
            <h4>Welcome to your personal AI Travel Assistant! 🌟</h4>
            <p>Let me help you create your perfect travel itinerary based on your preferences.</p>
            <p><strong>Destination:</strong> {destination}</p>
            <p><strong>Duration:</strong> {duration} days</p>
            <p><strong>Budget:</strong> {budget}</p>
            <p><strong>Travel Styles:</strong> {', '.join(travel_style)}</p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("✨ Generate My Perfect Travel Plan", type="primary"):
        if destination:
            try:
                with st.spinner("🔍 Researching and planning your trip..."):
                    prompt = f"""
                    Create a travel plan for {destination} for {duration} days, considering:
1. 🌞 Best Time to Visit
Seasonal highlights and weather considerations
2. 🏨 Accommodation
Hotels/stays in the {budget} range, near main attractions
3. 🗺️ Day-by-Day Itinerary
Key activities, must-visit places, and experiences for {', '.join(travel_style)}
4. 🍽️ Culinary Experiences
Local dishes, restaurant recommendations, and food experiences
5. 💡 Practical Tips
Transportation, cultural etiquette, safety, and daily budget estimates
6. 💰 Estimated Total Cost
Expense breakdown and money-saving tips
Please include sources and links, formatted clearly in markdown.
                    """

                    travel_plan_container = st.empty()
                    
                    response = travel_agent.run(prompt)
                    if hasattr(response, 'content'):
                        clean_response = response.content.replace('∣', '|').replace('\n\n\n', '\n\n')
                        st.write_stream(stream_response(clean_response))
                        st.session_state.travel_plan = clean_response  
                    else:
                        st.write_stream(stream_response(response))  
                        st.session_state.travel_plan = str(response)

            except Exception as e:
                st.error(f"Error generating travel plan: {str(e)}")
                st.info("Please try again in a few moments.")
        else:
            st.warning("Please enter a destination")


    else:
        if st.session_state.travel_plan:
                st.markdown(st.session_state.travel_plan)

    
    st.divider()

    qa_expander = st.expander("🤔 Ask a specific question about your destination or travel plan", expanded=st.session_state.qa_expanded)
    
    with qa_expander:
        st.session_state.qa_expanded = True
        
        question = st.chat_input("Your question, What would you like to know about your trip?")
        
        if question is not None and question != "" and st.session_state.travel_plan:

            with st.spinner("🔍 Finding answer..."):
                try:
                    with st.chat_message("user"):
                        st.markdown(question)
                    
                    context_question = f"""
                    I have a travel plan for {destination}. Here's the existing plan:
                    {st.session_state.travel_plan}

                    Now, please answer this specific question: {question}
                    
                    Provide a focused, concise answer that relates to the existing travel plan if possible.
                    """
                    
                    response = travel_agent.run(context_question)
                    if hasattr(response, 'content'):
                        ai_answer = response.content
                    else:
                        ai_answer = str(response)
                    
                    with st.chat_message("assistant"):
                        st.write_stream(stream_response(ai_answer))
                    
                    st.session_state.qa_history.append(("You", question))
                    st.session_state.qa_history.append(("AI Assistant", ai_answer))

                except Exception as e:
                    st.error(f"Error getting answer: {str(e)}")
        elif not st.session_state.travel_plan:
            st.warning("Please generate a travel plan first before asking questions.")

        elif st.session_state.qa_history:
            for sender, message in st.session_state.qa_history:
                if sender == "You":
                    st.chat_message("user").markdown(message)
                elif sender == "AI Assistant":
                    st.chat_message("assistant").markdown(message)
        else:
            st.warning("Please enter a question")
        
except Exception as e:
    st.error(f"Application Error: {str(e)}")

