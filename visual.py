import openai
import os
import re
import time
import logging
import asyncio
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.responses import JSONResponse  # Import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from illustration import draw_circle, draw_right_triangle, draw_rectangle, plot_trigonometric_function, draw_generic_triangle  # Import required functions
from responses import log_memory_usage

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

# Add the memory usage logging middleware
app.middleware("http")(log_memory_usage)

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure this is set in Railway's environment variables

# Pydantic model for user input
class Message(BaseModel):
    user_message: str

def extract_numeric_parameters(user_message: str) -> dict:
    """
    Extract all numeric parameters from the user message.
    Supports phrases like 'base is 5, height is 4', or 'x1 is 0, y1 is 0, x2 is 5, y2 is 0, x3 is 3, y3 is 4'.
    """
    param_regex = r"(?P<key>\b(?:leg|leg_a|leg_b|radius|side_a|side_b|side_c|width|height)\b)\s*(is|of)?\s*(?P<value>\d+(\.\d+)?)"
    matches = re.findall(param_regex, user_message.lower())
    return {match[0]: float(match[2]) for match in matches}

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

# Function to interact with OpenAI's GPT with retry and timeout handling
def get_gpt_response_with_retry(user_message: str, retries: int = 3, delay: int = 5) -> dict:
    """
    Retry logic for handling slow responses or timeouts from OpenAI.
    """
    for attempt in range(retries):
        try:
            # Updated system prompt to handle all math questions
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a math assistant. Your tasks are:\n"
                        "1. Answer all math-related questions, from basic arithmetic to advanced topics like algebra, calculus, trigonometry, etc.\n"
                        "2. Provide clear, concise explanations using standard math symbols (e.g., ² for squared, √ for square root, × for multiplication, π for pi).\n"
                        "3. If a question requires visualizing a mathematical shape or graph, provide the corresponding illustration in Python format.\n"
                        "4. If the question doesn't require a visualization, respond with a plain-text explanation."
                    ),
                },
                {"role": "user", "content": user_message},
            ]
            
            # Call OpenAI's ChatCompletion endpoint with timeout
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  #gpt-3.5-turbo
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                timeout=120,  # Increase timeout for long responses
            )

            gpt_output = response["choices"][0]["message"]["content"].strip()
            logging.info(f"GPT Output: {gpt_output}")

            if gpt_output == "I can only assist with geometry-related questions for grades 7 to 10. Please ask a geometry question.":
                return {"response": gpt_output}

            # Clean LaTeX-style math expressions
            clean_output = convert_to_plain_math(gpt_output)

            # Check for JSON-style responses (for visualizations)
            try:
                parsed_response = eval(gpt_output)  # Ensure GPT outputs a valid Python dictionary
                if isinstance(parsed_response, dict) and "shape" in parsed_response and "parameters" in parsed_response:
                    return parsed_response  # Return structured data for visualizations
            except Exception:
                pass  # If parsing fails, treat the output as plain text

            # Return plain-text response after cleaning up LaTeX math
            return {"response": clean_output}

        except openai.error.Timeout as timeout_error:
            logging.error(f"Timeout error occurred: {timeout_error}")
            if attempt < retries - 1:
                logging.info(f"Retrying ({attempt + 1}/{retries})...")
                time.sleep(delay)
            else:
                return {"response": "Request timed out. Please try again later."}
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            return {"response": "An error occurred. Please try again later."}

    return {"response": "Unable to get a valid response after multiple attempts. Please try again later."}

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
    return {"message": "Welcome to the Geometry Tutor API for Grades 7–10!"}

# Chatbot interaction endpoint
@app.post("/chat")
async def chat_with_bot(message: Message):
    """
    Chat endpoint to process user requests and create visualizations.
    Handles both structured GPT responses for visualization and plain-text explanations.
    """
    try:
        user_message = message.user_message
        logging.info(f"Received message: {user_message}")

        # Step 1: Use GPT to process the message (GPT decides if it's math-related)
        gpt_response = get_gpt_response_with_retry(user_message)
        logging.info(f"GPT Response: {gpt_response}")

        # Step 2: If GPT responds with the non-math response, return it
        if isinstance(gpt_response, dict) and "response" in gpt_response and gpt_response["response"] == "I can only assist with geometry-related questions for grades 7 to 10. Please ask a geometry question.":
            return PlainTextResponse(content=gpt_response["response"], status_code=200)

        # Step 3: Check if "illustrate" is explicitly mentioned in the message
        if "illustrate" in user_message.lower():
            # Extract numeric parameters manually
            parameters = extract_numeric_parameters(user_message)

            # Handle manual visualization requests
            if "circle" in user_message:
                radius = parameters.get("radius", parameters.get("diameter", 10) / 2)
                filepath = draw_circle(radius)
                return FileResponse(filepath, media_type="image/png")
            
            # Handle right triangle visualization
            if "right triangle" in user_message:
                leg_a = parameters.get("leg_a", 3)  # Default leg_a = 3
                leg_b = parameters.get("leg_b", 4)  # Default leg_b = 4
                filepath = draw_right_triangle(leg_a, leg_b)
                return FileResponse(filepath, media_type="image/png")
    
            # Handle generic triangle visualization
            if "triangle" in user_message:
                side_a = parameters.get("side_a", 5)
                side_b = parameters.get("side_b", 10)
                side_c = parameters.get("side_c", 7)
                try:
                    filepath = draw_generic_triangle(side_a, side_b, side_c)
                    return FileResponse(filepath, media_type="image/png")
                except ValueError as e:
                    logging.error(str(e))
                    return JSONResponse(content={"response": str(e)}, status_code=400)
                
            if "rectangle" in user_message:
                width = parameters.get("width", 5)
                height = parameters.get("height", 3)
                filepath = draw_rectangle(width, height)
                return FileResponse(filepath, media_type="image/png")

            if "sin" in user_message or "cos" in user_message or "tan" in user_message:
                if "sin" in user_message:
                    filepath = plot_trigonometric_function("sin")
                elif "cos" in user_message:
                    filepath = plot_trigonometric_function("cos")
                elif "tan" in user_message:
                    filepath = plot_trigonometric_function("tan")
                return FileResponse(filepath, media_type="image/png")

            return PlainTextResponse(content="Sorry, I couldn't create an illustration for that request.", status_code=400)

        # Step 4: Handle structured GPT response if "illustrate" is not mentioned
        if isinstance(gpt_response, dict) and "shape" in gpt_response:
            shape = gpt_response["shape"]
            params = gpt_response["parameters"]

            # Handle GPT-generated visualizations
            if shape == "circle":
                radius = params.get("radius", 5)  # Default radius is 5
                filepath = draw_circle(radius)
                return FileResponse(filepath, media_type="image/png")

            if shape == "triangle" and params.get("type") == "right":
                leg_a = params.get("leg_a")
                leg_b = params.get("leg_b")

                if leg_a is None or leg_b is None:
                    return PlainTextResponse(content="Missing parameters for right triangle visualization.", status_code=400)

                filepath = draw_right_triangle(leg_a, leg_b)
                return FileResponse(filepath, media_type="image/png")

            elif shape == "rectangle":
                width = params.get("width", 5)
                height = params.get("height", 3)
                filepath = draw_rectangle(width, height)
                return FileResponse(filepath, media_type="image/png")

            elif shape == "trigonometric":
                function = params.get("function", "sin")  # Default to sin
                filepath = plot_trigonometric_function(function)
                return FileResponse(filepath, media_type="image/png")

            return PlainTextResponse(content="Sorry, I couldn't create an illustration for that request.", status_code=400)

        # Step 5: Handle plain-text GPT
        return PlainTextResponse(content=gpt_response["response"], status_code=200)

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return PlainTextResponse(content="An error occurred. Please try again later.", status_code=500)
