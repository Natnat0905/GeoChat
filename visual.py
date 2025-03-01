# visual.py
import openai
import os
import re
import json
import logging
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from illustration import (
    draw_circle,
    draw_right_triangle,
    draw_rectangle,
    plot_trigonometric_function
)

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Pydantic model for user input
class Message(BaseModel):
    user_message: str

def clean_math_text(response: str) -> str:
    """Convert LaTeX math to plain text symbols"""
    replacements = {
        r"\\\(": "", r"\\\)": "",
        r"\^2": "²", r"\^3": "³",
        r"\sqrt": "√", r"\\times": "×",
        r"\\div": "÷", r"\\frac{(\d+)}{(\d+)}": r"\1/\2"
    }
    for pattern, repl in replacements.items():
        response = re.sub(pattern, repl, response)
    return response.replace("\\", "").strip()

# Update the system prompt to handle squares
def get_gpt_response(user_message: str) -> dict:
    """Get structured response from GPT-3.5"""
    system_prompt = """You are a math assistant. Follow these rules:
1. Solve problems from arithmetic to calculus
2. Use standard math symbols (², √, ×, π)
3. For visual shapes:
   - Squares should use {"shape": "rectangle", "parameters": {"width": X, "height": X}}
   - Other shapes use their specific format
4. Return JSON for visualizations, plain text otherwise"""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        raw_output = response.choices[0].message.content.strip()
        
        # Try to parse JSON first
        try:
            json_response = json.loads(raw_output)
            if isinstance(json_response, dict) and "shape" in json_response:
                return json_response
        except json.JSONDecodeError:
            pass
        
        # Fallback to cleaned text response
        return {"response": clean_math_text(raw_output)}
    
    except Exception as e:
        logging.error(f"GPT Error: {e}")
        return {"response": "Error processing your request"}

@app.post("/chat")
async def chat_handler(message: Message):
    """Main endpoint for math problem solving"""
    try:
        user_input = message.user_message
        logging.info(f"Processing: {user_input}")
        
        gpt_response = get_gpt_response(user_input)
        
        if "shape" in gpt_response:
            return handle_visualization(gpt_response)
        
        return JSONResponse(content={
            "response": gpt_response.get("response", "No solution generated")
        })
    
    except Exception as e:
        logging.error(f"System Error: {e}")
        return JSONResponse(
            content={"response": "System error. Please try again."},
            status_code=500
        )

# Update the visualization handler
def handle_visualization(data: dict) -> Response:
    """Generate and return visualization response"""
    shape_type = data["shape"].lower()
    params = data.get("parameters", {})
    explanation = data.get("explanation", "Visual representation")
    
    try:
        match shape_type:
            case "circle":
                image = draw_circle(params.get("radius", 5))
            case "rectangle" | "square":  # Handle squares as special rectangles
                width = params.get("width", params.get("side", 5))
                height = params.get("height", width)  # Use width if height missing
                image = draw_rectangle(width, height)
            case "right-angled triangle" | "right triangle":
                image = draw_right_triangle(
                    params.get("leg1", 0),
                    params.get("leg2", 0)
                )
            case "trigonometric":
                image = plot_trigonometric_function(
                    params.get("function", "sin")
                )
            case _:
                return JSONResponse(
                    content={"response": "Unsupported shape type"},
                    status_code=400
                )
        
        return Response(
            content=image,
            media_type="image/png",
            headers={"X-Explanation": explanation}
        )
    
    except Exception as e:
        logging.error(f"Visualization Error: {e}")
        return JSONResponse(
            content={"response": f"{explanation} (Visualization failed)"},
            status_code=500
        )

@app.get("/health")
async def health_check():
    """Service health endpoint"""
    return {"status": "healthy", "version": "1.1.0"}

# Error handler for validation errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        content={"response": exc.detail},
        status_code=exc.status_code
    )