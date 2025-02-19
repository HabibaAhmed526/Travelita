import streamlit as st
import PIL
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import time
import google.generativeai as genai  # Import Gemini API
import os
from pathlib import Path


# Set up Gemini API Key
genai.configure(api_key=os.getenv('GOOGLE_API_KEY')) 

# Define Model URLs & Label Files
models_urls = [
    'https://tfhub.dev/google/on_device_vision/classifier/landmarks_classifier_asia_V1/1',
    'https://www.kaggle.com/models/google/landmarks/TensorFlow1/classifier-africa-v1/1',
    'https://www.kaggle.com/models/google/landmarks/TensorFlow1/classifier-europe-v1/1',
    'https://www.kaggle.com/models/google/landmarks/TensorFlow1/classifier-north-america-v1/1',
    'https://www.kaggle.com/models/google/landmarks/TensorFlow1/classifier-south-america-v1/1',
    'https://www.kaggle.com/models/google/landmarks/TensorFlow1/classifier-oceania-antarctica-v1/1'
]
current_directory = Path.cwd()
print("current dir : ", current_directory)
labels_files = [
    os.path.join(current_directory, 'landmark_detection', 'landmarks_classifier_africa_V1_label_map.csv'),
    os.path.join(current_directory, 'landmark_detection', 'landmarks_classifier_africa_V1_label_map.csv'),
    os.path.join(current_directory, 'landmark_detection', 'landmarks_classifier_europe_V1_label_map.csv'),
    os.path.join(current_directory, 'landmark_detection', 'landmarks_classifier_north_america_V1_label_map.csv'),
    os.path.join(current_directory, 'landmark_detection', 'landmarks_classifier_south_america_V1_label_map.csv'),
    os.path.join(current_directory, 'landmark_detection', 'landmarks_classifier_oceania_antarctica_V1_label_map.csv')
]

# Load Labels
labels_dict = []
for file in labels_files:
    df = pd.read_csv(file)
    labels_dict.append(dict(zip(df.id, df.name)))

# Function to get responses from Gemini
def get_gemini_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text if response else "No relevant information found."
    except Exception as e:
        return f"Error: {str(e)}"


# Image Processing Function
def image_processing(image):
    img_shape = (321, 321)
    img = PIL.Image.open(image)
    img = img.resize(img_shape)
    img1 = img
    img = np.array(img) / 255.0
    img = img[np.newaxis]

    best_prediction = None
    highest_confidence = -np.inf

    # Process the image through each model
    for i, model_url in enumerate(models_urls):
        classifier = hub.KerasLayer(model_url, input_shape=(321, 321, 3), output_key="predictions:logits")
        result = classifier(img)[0]
        highest_index = np.argmax(result)
        confidence = result[highest_index]

        if confidence > highest_confidence:
            highest_confidence = confidence
            best_prediction = labels_dict[i].get(highest_index, "Unknown Landmark")

    return best_prediction, img1

# Get Location Info
def get_map(loc):
    geolocator = Nominatim(user_agent="landmark_finder")
    location = geolocator.geocode(loc)
    return location.address, location.latitude, location.longitude

# Initialize Session State
if "landmark" not in st.session_state:
    st.session_state.landmark = None
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

# Streamlit App
def run():
    st.title("\U0001F3DB️ Landmark Recognition")

    # Display Logo
    img = PIL.Image.open("logo.png").resize((256, 256))
    st.image(img)

    # Upload Image
    img_file = st.file_uploader("\U0001F4F7 Upload an Image", type=["png", "jpg", "jpeg"])

    if img_file is not None:
        images_dir = "./Uploaded_Images/"
        save_image_path = os.path.join(images_dir, img_file.name)
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
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

# run()
