import streamlit as st
import os
import time
from crewai import Crew, Process
from mutli_agent_travel_planner.agents import best_time_agent, accommodation_agent, itinerary_agent, culinary_experience_agent, practical_tips_agent, cost_estimation_agent, finalizer_agent, travel_agent
from mutli_agent_travel_planner.tasks import best_time_task, accommodation_task, itinerary_task, culinary_task, practical_tips_task, cost_estimation_task, travel_plan_task, travel_query_task
# from mutli_agent_travel_planner.qa_rag import model, encode_md_files, prompt_template
import re
from google.generativeai import configure, GenerativeModel
from mutli_agent_travel_planner.qa_travel_agent import travel_agent
from landmark_detection.main import image_processing, get_map, get_gemini_response
import pandas as pd
import PIL
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from geopy.geocoders import Nominatim
import google.generativeai as genai
from email_sender.email_sender import send_email_gmail
from mutli_agent_travel_planner.qa_rag import *


# Initialize page config with custom layout and styling
st.set_page_config(
    page_title="Travelita: Your AI Travel Planner Empowered by Multi-Agent System",
    page_icon="🌎",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Main UI section for displaying and generating the travel plan
st.title("🌎 Travelita")

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/airplane-take-off.png")
st.sidebar.title("Choose Your Service")

option = st.sidebar.radio("Select an option:", ("AI Travel Planner", "Landmark Recognition"))
st.markdown('\n')

# Initialize session state variables
if "landmark" not in st.session_state:
    st.session_state.landmark = None
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []
if 'travel_plan' not in st.session_state:
    st.session_state.travel_plan = None
if 'qa_expanded' not in st.session_state:
    st.session_state.qa_expanded = False
if 'qa_history' not in st.session_state:
    st.session_state.qa_history = []  

# Stream response function
def stream_response(response, delay=0.1):
    """Simulates streaming the output by yielding one word at a time."""
    print("Streaming response:", response)
    for word in response.split(' '):
        yield word + ' '
        time.sleep(delay)

if option == "Landmark Recognition":
    st.title("\U0001F3DB️ Landmark Recognition")
    img_file = st.file_uploader("\U0001F4F7 Upload an Image", type=["png", "jpg", "jpeg"])

    if img_file is not None:
        images_dir = "./Uploaded_Images/"
        save_image_path = os.path.join(images_dir, img_file.name)
        os.makedirs(images_dir, exist_ok=True)

        with open(save_image_path, "wb") as f:
            f.write(img_file.getbuffer())

        # Process Image
        prediction, image = image_processing(save_image_path)
        st.session_state.landmark = prediction

        # Display Image & Prediction
        st.image(image)
        st.header(f"\U0001F4CD **Predicted Landmark:** {prediction}")

        # Get Map Details
        try:
            address, latitude, longitude = get_map(prediction)
            st.success(f"\U0001F4CC **Address:** {address}")
            st.json({"Latitude": latitude, "Longitude": longitude})

            # Show on Map
            df = pd.DataFrame([[latitude, longitude]], columns=["lat", "lon"])
            st.subheader(f"\U0001F5FA **{prediction} on the Map**")
            st.map(df)

        except Exception:
            st.warning("⚠️ No address found!")
    # 📌 **Q&A Section**
    st.divider()
    qa_expander = st.expander("\U0001F914 Ask about the Landmark", expanded=True)

    with qa_expander:
        question = st.chat_input("What would you like to know about this landmark?")

        if question and st.session_state.landmark:
            with st.spinner("🔍 Searching for an answer..."):
                try:
                    with st.chat_message("user"):
                        st.markdown(question)

                    # Get answer from Gemini LLM
                    query = f"Provide information about {st.session_state.landmark}. {question}"
                    ai_answer = get_gemini_response(query)

                    with st.chat_message("assistant"):
                        st.write_stream(stream_response(ai_answer))

                    # Save chat history
                    st.session_state.qa_history.append(("You", question))
                    st.session_state.qa_history.append(("AI Assistant", ai_answer))

                except Exception as e:
                    st.error(f"Error getting answer: {str(e)}")

        elif not st.session_state.landmark:
            st.warning("Please upload an image and get a prediction first.")

        elif st.session_state.qa_history:
            for sender, message in st.session_state.qa_history:
                if sender == "You":
                    st.chat_message("user").markdown(message)
                elif sender == "AI Assistant":
                    st.chat_message("assistant").markdown(message)



elif option == "AI Travel Planner":
    st.title("🌎 AI Travel Planner - Multi-Agent System")

    # Custom CSS for UI enhancements
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
        }
        </style>
    """, unsafe_allow_html=True)

    # Directory to save outputs
    output_dir = "agents_output"
    os.makedirs(output_dir, exist_ok=True)

    # Sidebar configuration
    with st.sidebar:
        st.title("Trip Settings")
        
        destination = st.text_input("🌍 Where would you like to go?", "")
        duration = st.number_input("📅 How many days?", min_value=1, max_value=30, value=5)
        budget = st.select_slider("💰 What's your budget level?", options=["Budget", "Moderate", "Luxury"], value="Moderate")
        travel_style = st.multiselect("🎯 Travel Style", ["Culture", "Nature", "Adventure", "Relaxation", "Food", "Shopping"], ["Culture"])

        
        receiver_email = st.text_input("Enter the recipient's email address: ")
        send_email_button = st.button("Send Email")
        # Send the email
        sender_email = os.getenv("GMAIL_USER")
        sender_password = os.getenv("GMAIL_PASSWORD")

        if send_email_button:
            send_email_gmail(sender_email, sender_password, receiver_email, st.session_state.travel_plan)

        st.markdown("What do you need to generate? ✨")

        # Select Tasks
        selected_tasks = [
            st.checkbox("Find the best travel time"),
            st.checkbox("Find accommodations"),
            st.checkbox("Plan a daily itinerary"),
            st.checkbox("Suggest food places"),
            st.checkbox("Provide travel tips"),
            st.checkbox("Estimate trip cost"),
        ]

   

    # Travel summary section with user inputs
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

    # Process selected tasks
    selected_tasks_list = []
    selected_agents_list = []

    
    agents = [best_time_agent, accommodation_agent, itinerary_agent, culinary_experience_agent, practical_tips_agent, cost_estimation_agent]
    tasks = [best_time_task, accommodation_task, itinerary_task, culinary_task, practical_tips_task, cost_estimation_task]


    # Select only the checked tasks
    selected_tasks_list = []
    selected_agents_list = []

    for i, task in enumerate(selected_tasks):
        if selected_tasks[i]:
            selected_tasks_list.append(tasks[i])
            selected_agents_list.append(agents[i])

    # Function to handle task processing
    def process_travel_plan():
        if destination:
            with st.spinner("🔍 Researching and planning your trip..."):
                crew = Crew(
                    agents=selected_agents_list,
                    tasks=selected_tasks_list,
                    process=Process.sequential,
                    verbose=True
                )

                inputs={
                        'destination': destination,
                        'duration': duration,
                        'budget': budget,
                        'travel_style': travel_style,  # Convert list to string
                }

                print('inputs', inputs)

                crew.kickoff(
                    inputs={
                        'destination': destination,
                        'duration': duration,
                        'budget': budget,
                        'travel_style': " ".join(travel_style),  # Convert list to string
                    }
                )
            
            st.success("🎉 Travel plan generated successfully!")
            output_files = [
                "best_time_to_visit.md",
                "accommodation_recommendations.md",
                "itinerary_plan.md",
                "culinary_experiences.md",
                "practical_tips.md",
                "cost_estimation.md",
            ]
            # Display final output
            all_outputs = []
            for output_file in output_files:
                output_path = os.path.join(output_dir, output_file)
                if os.path.exists(output_path):
                    with open(output_path, "r") as file:
                        content = file.read().strip()  # Strip leading/trailing whitespace
                        # Remove surrounding triple backticks with or without "markdown"
                        content = re.sub(r"^(```(?:markdown)?)\n?|```$", "", content, flags=re.MULTILINE).strip()
                        all_outputs.append(content)
            st.session_state.travel_plan = "\n".join(all_outputs)
            st.write_stream(stream_response(st.session_state.travel_plan))

    if st.button("✨ Generate My Perfect Travel Plan", type="primary"):
        process_travel_plan()
    elif st.session_state.travel_plan:
        st.markdown((st.session_state.travel_plan))

    st.markdown('\n')
    st.title("Adjust Plan | QnA with Plan")
    travel_plan_option = st.radio("Select an option:", ("Adjust your Plan", "QnA with your Plan"))
    st.markdown('\n')
    st.divider()
    expander = st.expander("🤔 Ask a specific question about your destination or travel plan", expanded=st.session_state.qa_expanded)

    with expander:
        if travel_plan_option == "Adjust your Plan":
            question = st.text_input("Your question:", placeholder="What would you like to adjust to your trip?")
        elif travel_plan_option == "QnA with your Plan":
            question = st.text_input("Your question:", placeholder="What would you like to know about your trip?")

        st.session_state.qa_expanded = True
        

        if question and st.session_state.travel_plan and destination:
            try:
                ai_answer = ""
                if travel_plan_option == "Adjust your Plan":
                    context_question = f"""
                        I have a travel plan for {destination}. Here's the existing plan:
                        {st.session_state.travel_plan}

                        Now, I need to make adjustments based on this question: {question}
                        
                        Provide a focused, concise answer that relates to the existing travel plan if possible.
                        You can search for unkown information that is not provided in the existing plan.
                    """
                    ai_answer = travel_agent.run(context_question).content
                
                elif travel_plan_option == "QnA with your Plan":
                    response = get_rag_answer(question, output_dir)
                    ai_answer = response.text

                with st.chat_message("user"):
                    st.markdown(question)
                with st.chat_message("assistant"):
                    st.write_stream(stream_response(ai_answer))

            except Exception as e:
                st.error(f"Error getting answer: {str(e)}")
        
        elif not st.session_state.travel_plan:
            st.warning("Please generate a travel plan first before asking questions.")
        elif not question:
            st.warning("Please enter a question")
        