import openai
import os
import re
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

# Function to check if a message is math-related
def is_math_related(user_message: str) -> bool:
    """
    Check if the user's message is math-related using keywords and patterns.
    """
    math_keywords = [
        "triangle", "geometry", "area", "perimeter", "angle", "algebra",
        "equation", "square", "circle", "radius", "pi", "hypotenuse", "theorem",
        "sum", "difference", "product", "quotient", "divide", "multiply",
        "add", "subtract", "math", "mathematics", "Pythagorean"
    ]

    # Convert the message to lowercase for case-insensitive matching
    user_message = user_message.lower()

    # Check if any math-related keyword exists in the message
    return any(keyword in user_message for keyword in math_keywords)

# Post-processing function to clean LaTeX-style output
def convert_to_plain_math(response: str) -> str:
    """
    Convert LaTeX-style math expressions in the GPT response to plain text math symbols.
    """
    replacements = {
        r"\\\(": "",  # Remove \( (opening LaTeX math delimiter)
        r"\\\)": "",  # Remove \) (closing LaTeX math delimiter)
        r"\^2": "²",  # Replace ^2 with superscript ²
        r"\^3": "³",  # Replace ^3 with superscript ³
        r"\sqrt": "√",  # Replace \sqrt with √
        r"\\times": "×",  # Replace \times with ×
        r"\\div": "÷",  # Replace \div with ÷
        r"\\frac{(\d+)}{(\d+)}": r"(\1/\2)",  # Replace fractions \frac{a}{b} with (a/b)
        r"\\[a-zA-Z]+": "",  # Remove any other unhandled LaTeX commands
    }
    for pattern, replacement in replacements.items():
        response = re.sub(pattern, replacement, response)

    # Additional cleanup: remove double backslashes
    response = response.replace("\\", "")
    return response.strip()

# Function to interact with OpenAI's GPT
def get_gpt_response(user_message: str) -> str:
    try:
        # Structured messages for the GPT chat model
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful geometry tutor. Respond to mathematical questions using plain text "
                    "mathematical symbols (e.g., use ² for squared, √ for square root, × for multiplication, etc.). "
                    "Avoid using LaTeX-style expressions."
                ),
            },
            {"role": "user", "content": user_message},
        ]

        # Call OpenAI's ChatCompletion endpoint
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )

        # Extract GPT response and process it
        raw_response = response["choices"][0]["message"]["content"].strip()
        processed_response = convert_to_plain_math(raw_response)  # Post-process the response
        return processed_response
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
    Only processes math-related questions.
    """
    try:
        user_message = message.user_message
        logging.info(f"Received message: {user_message}")

        # Check if the question is math-related
        if not is_math_related(user_message):
            non_math_response = "I can only assist with math-related questions, especially GEOMETRY. Please ask me something about mathematics."
            logging.info(f"Non-math question detected. Response: {non_math_response}")
            return {"response": non_math_response}

        # Process math-related questions using GPT
        response = get_gpt_response(user_message)
        logging.info(f"Response: {response}")
        return {"response": response}
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
