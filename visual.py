import openai
import os
import re
import matplotlib.pyplot as plt
import io
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
    math_symbols = [
        "+", "-", "*", "/", "=", "^", "%", "π", "∑", "√", "∫", "≠", "<", ">", "≤", "≥", "≈", "∼", "∝", "∞",
        "!", "∂", "Δ", "∇", "∩", "∪", "⊂", "⊃", "⊆", "⊇", "⊕", "⊗", "∴", "∵", "±", "∓", "|", "∣", "∥", "⊥",
        "→", "↔", "↦", "⇒", "⇔", "∈", "∉", "∋", "∀", "∃", "∅", "∓", "∖", "ℝ", "ℤ", "ℚ", "ℕ", "ℂ", "ℙ", "÷","×"
                ]
    
    geometry_keywords = [
        "triangle", "geometry", "area", "perimeter", "angle", "isosceles",
        "equilateral", "scalene", "acute", "obtuse", "right triangle",
        "circle", "radius", "diameter", "chord", "arc", "sector",
        "circumference", "square", "rectangle", "parallelogram",
        "rhombus", "trapezoid", "quadrilateral", "polygon", "pentagon",
        "hexagon", "octagon", "surface area", "volume", "prism", "pyramid",
        "sphere", "cone", "cylinder", "base", "height", "altitude",
        "Pythagorean theorem", "midpoint", "distance formula",
        "slope", "coordinate plane", "axes", "x-axis", "y-axis", "origin",
        "geometry problem", "geometry tutor", "7th grade", "8th grade",
        "9th grade", "10th grade", "line segment", "congruent",
        "similar", "scale factor", "ratio", "proportions", "adjacent",
        "opposite", "hypotenuse", "angles", "degrees", "radians",
        "tan", "sin", "cos", "sec", "cosec", "cot", "logarithm", "log",
        "factorial"
    ]

    # Combine math symbols and geometry-related keywords
    math_related_keywords = math_symbols + geometry_keywords

    # Convert the message to lowercase for case-insensitive matching
    user_message = user_message.lower()

    # Check if any math-related keyword or symbol exists in the message
    return any(keyword in user_message for keyword in math_related_keywords)

# Function to draw geometry figures
def draw_geometry_figure(user_message: str) -> io.BytesIO:
    """
    Draw geometry figures based on the user's message.
    Supports visualization for circle, triangle, rectangle, square, and polygon.
    """
    fig, ax = plt.subplots()

    if "circle" in user_message:
        circle = plt.Circle((0.5, 0.5), 0.4, color="blue", fill=False)
        ax.add_artist(circle)
        ax.set_title("Circle Visualization")
    elif "triangle" in user_message:
        triangle = plt.Polygon([[0.1, 0.1], [0.9, 0.1], [0.5, 0.8]], closed=True, color="green", fill=False)
        ax.add_artist(triangle)
        ax.set_title("Triangle Visualization")
    elif "rectangle" in user_message:
        rectangle = plt.Rectangle((0.1, 0.1), 0.8, 0.4, color="red", fill=False)
        ax.add_artist(rectangle)
        ax.set_title("Rectangle Visualization")
    elif "square" in user_message:
        square = plt.Rectangle((0.3, 0.3), 0.4, 0.4, color="purple", fill=False)
        ax.add_artist(square)
        ax.set_title("Square Visualization")
    elif "polygon" in user_message:
        polygon = plt.Polygon([[0.2, 0.1], [0.8, 0.2], [0.6, 0.8], [0.4, 0.8], [0.1, 0.3]], closed=True, color="orange", fill=False)
        ax.add_artist(polygon)
        ax.set_title("Polygon Visualization")
    else:
        ax.text(0.5, 0.5, "No specific shape to visualize!", ha="center", va="center", fontsize=12)
        ax.set_title("No Shape Found")
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    plt.axis('off')

    # Save figure to a BytesIO object
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format="png")
    plt.close(fig)
    img_bytes.seek(0)
    return img_bytes

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
                    "You are a geometry tutor for grades 7 to 10. Focus on explaining geometry concepts "
                    "such as angles, shapes, theorems, coordinate geometry, and measurements. Use clear explanations "
                    "and plain math symbols (e.g., ² for squared, √ for square root, × for multiplication, π for pi). "
                    "Avoid answering questions unrelated to geometry."
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
    return {"message": "Welcome to the Geometry Tutor API for Grades 7–10!"}

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
            non_math_response = "I can only assist with geometry-related questions for grades 7 to 10. Please ask a geometry question."
            logging.info(f"Non-geometry question detected. Response: {non_math_response}")
            return {"response": non_math_response}

        # Process geometry-related questions using GPT
        response = get_gpt_response(user_message)
        logging.info(f"Response: {response}")
        return {"response": response}
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
