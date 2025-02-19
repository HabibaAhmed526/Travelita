import google.generativeai as genai
import os
from dotenv import load_dotenv
import faiss
import requests
import numpy as np
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()
token = os.getenv("GOOGLE_API_KEY")
hf_token = os.getenv("HF_TOKEN")

# Configure Gemini model
genai.configure(api_key=token)
model = genai.GenerativeModel("gemini-pro")

# Hugging Face embedding API
embedding_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

def generate_embedding(text: str) -> np.ndarray:
    """
    Generate an embedding for a given text using Hugging Face API.
    """
    response = requests.post(
        embedding_url,
        headers={"Authorization": f"Bearer {hf_token}"},
        json={"inputs": text}
    )

    if response.status_code != 200:
        raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")

    return np.array(response.json())

def encode_md_files(folder_path, chunk_size=1000, chunk_overlap=200):
    """
    Load Markdown files, split them into chunks, and create a FAISS vector store.
    """
    texts = []
        
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder '{folder_path}' does not exist.")
    
    md_files = [f for f in os.listdir(folder_path) if f.endswith(".md")]
    
    if not md_files:
        raise ValueError("No Markdown (.md) files found in the folder.")

    for file_name in md_files:
        file_path = os.path.join(folder_path, file_name)
        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        
        texts.extend(chunk.page_content for chunk in chunks)

    
    if not texts:
        raise ValueError("No valid text chunks generated.")

    # Generate embeddings
    embeddings = np.array([generate_embedding(text) for text in texts])

    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    
    return index, texts

def similarity_search(query, folder_path, chunk_size=1000, chunk_overlap=200, top_k=5):
    """
    Perform similarity search on encoded text chunks.
    """
    query_embedding = generate_embedding(query).reshape(1, -1)

    # Load vector index & texts
    index, texts = encode_md_files(folder_path, chunk_size, chunk_overlap)

    if index.ntotal == 0:
        raise ValueError("FAISS index is empty. No data to search.")

    # Perform search
    distances, indices = index.search(query_embedding, min(top_k, len(texts)))

    # Convert L2 distances to cosine similarities
    similarities = 1 - distances / 2
    results = []
    threshold = 0.5  # Minimum similarity threshold
    # print('similarities: {}'.format(similarities[0]))
    print(f"\nSemantic Results for '{query}':")
    for sim, idx in zip(similarities[0], indices[0]):
        if sim >= threshold:
            print(f"Similarity: {sim:.2f} - {texts[idx]}")
            results.append(texts[idx])

    return results if results else [query.upper()]

# Define a prompt template
def prompt_template(query, context):
    """
    Generates a structured prompt for a travel assistant chatbot.
    """
    prompt = f"""
    You are a travel assistant. Use the following context to answer the travel-related question concisely.
    If unsure, state that you don't know the answer.
    Limit your response to three sentences.
    Always end with "Thanks for asking!".

    Context:
    {context}

    Question: {query}
    Helpful Answer:
    """
    return prompt

def get_rag_answer(query, folder_path):
    try:
        results = similarity_search(query, folder_path)
        print("\nTop results:", results, flush=True)
        response = model.generate_content(prompt_template(query, results))
        print(response)
        return response
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I'm unable to provide an accurate answer at the moment."
    
