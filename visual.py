import openai
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.responses import Response
import logging

# Initialize the FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure this is set in Railway's environment variables

# Pydantic model for user input
class Message(BaseModel):
    user_message: str

# Function to interact with OpenAI's GPT
def get_gpt_response(user_message: str) -> str:
    """
    Send the user's message to GPT and return its response.
    Includes structured prompting to ensure accurate geometry explanations.
    """
    try:
        # Structured messages for the GPT chat model
        messages = [
            {"role": "system", "content": "You are a geometry tutor for grades 7-10."},
            {"role": "user", "content": user_message}
        ]

        # Call OpenAI's ChatCompletion endpoint
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logging.error(f"Error communicating with OpenAI: {e}")
        return "Sorry, I encountered an error. Please try again."
    
# Root route for health check or welcome message
@app.get("/")
async def root():
    logging.info("Root endpoint accessed")
    return {"message": "Welcome to the GeoChat API - Geometry Helper!"}

# Chatbot interaction endpoint
@app.post("/chat")
async def chat_with_bot(message: Message):
    user_message = message.user_message
    logging.info(f"Received message: {user_message}")
    response = get_gpt_response(user_message)
    logging.info(f"Response: {response}")
    return {"response": response}

# Favicon route (optional)
@app.get("/favicon.ico", response_class=Response)
async def favicon():
    logging.info("Favicon endpoint accessed")
    # Return an empty response for favicon.ico
    return Response(status_code=204)
# Robots.txt handler
@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    """
    Handle requests for robots.txt to prevent crawler errors.
    """
    logging.info("robots.txt endpoint accessed")
    return "User-agent: *\nDisallow: /"

# Custom 404 handler for unmatched routes
@app.exception_handler(HTTPException)
async def custom_404_handler(request, exc):
    """
    Custom handler for 404 errors to improve debugging.
    """
    if exc.status_code == 404:
        logging.warning(f"404 Error: {request.url}")
    return {"error": "The requested resource was not found."}
