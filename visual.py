import openai
import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import FileResponse, PlainTextResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import logging

# Initialize the FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add CORS Middleware (optional, useful if interacting with other domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with specific origins in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure this is set in Railway's environment variables

# Pydantic model for user input
class Message(BaseModel):
    user_message: str

# Function to interact with OpenAI's GPT
def get_gpt_response(user_message: str) -> str:
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
        # Log detailed error information
        logging.error(f"Error communicating with OpenAI: {str(e)}")
        return f"Sorry, I encountered an error: {str(e)}"


# Middleware to log all incoming requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    return response

# Root route for health check or welcome message
@app.get("/")
async def root():
    logging.info("Root endpoint accessed")
    return {"message": "Welcome to the GeoChat API - Geometry Helper!"}

# Chatbot interaction endpoint
@app.post("/chat")
async def chat_with_bot(message: Message):
    """
    Endpoint to interact with the chatbot.
    Accepts a POST request with the user's message.
    """
    try:
        user_message = message.user_message
        logging.info(f"Received message: {user_message}")
        response = get_gpt_response(user_message)
        logging.info(f"Response: {response}")
        return {"response": response}
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

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
async def custom_404_handler(request: Request, exc: HTTPException):
    """
    Custom handler for 404 errors to improve debugging.
    """
    if exc.status_code == 404:
        logging.warning(f"404 Error: {request.url}")
    return {"error": "The requested resource was not found."}
