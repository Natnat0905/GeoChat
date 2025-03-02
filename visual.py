import openai
import os
import re
import json
import logging
import base64
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from illustration import (
    draw_circle,
    draw_right_triangle,
    draw_rectangle,
    plot_trigonometric_function
)

# Initialize FastAPI app
app = FastAPI()
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

# Enhanced tutoring prompt
TUTOR_PROMPT = """You are an expert mathematics educator for secondary students. For every response:
1. Break solutions into numbered, atomic steps
2. Explain underlying principles/formulas with **bold terms**
3. Include real-world applications (e.g., "This helps architects calculate...")
4. Highlight common errors using ❌ symbol
5. Provide memory aids/mnemonics where applicable
6. Use analogies suitable for teenagers
7. For visual questions, follow this template:
{
  "shape": "shape_type",
  "parameters": {...},
  "explanation": "### Geometric Analysis\\n**Step 1:**...\\n**Formula:**...\\n📐 Visualization shows..."
}"""

def enhance_explanation(response: str) -> str:
    """Convert LaTeX math to plain text symbols and add tutoring enhancements"""
    replacements = {
        r"\\\(": "", r"\\\)": "",
        r"\^2": "²", r"\^3": "³",
        r"\sqrt": "√", r"\\times": "×",
        r"\\div": "÷", r"\\frac{(\d+)}{(\d+)}": r"\1/\2",
        r"\\rightarrow": "→", r"\\approx": "≈", r"\\pi": "π",
        r"\*": "•"  # Convert asterisks to bullet points
    }
    for pattern, repl in replacements.items():
        response = re.sub(pattern, repl, response)
    # Add step numbering validation
    response = re.sub(r"(\d+\.)\s+", r"\n**Step \1** ", response)
    return response

def get_tutor_response(user_message: str) -> dict:
    """Get structured response from GPT-3.5 with tutoring enhancements"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": TUTOR_PROMPT},
                {"role": "user", "content": user_message}
            ],
            max_tokens=650,
            temperature=0.4
        )
        
        raw = response.choices[0].message.content.strip()
        
        try:
            json_response = json.loads(raw)
            if isinstance(json_response, dict) and "shape" in json_response:
                json_response["explanation"] = enhance_explanation(json_response["explanation"])
                return json_response
        except json.JSONDecodeError:
            pass
        
        return {"response": enhance_explanation(raw)}
    
    except Exception as e:
        logging.error(f"GPT Error: {e}")
        return {"response": "Let's try to work through this problem together. First..."}

@app.post("/chat")
async def tutor_endpoint(message: Message):
    """Main endpoint for math problem solving with tutoring enhancements"""
    try:
        user_input = message.user_message
        logging.info(f"Tutoring: {user_input}")
        
        response = get_tutor_response(user_input)
        
        if "shape" in response:
            return add_learning_components(handle_visualization(response))
        
        return JSONResponse(content={
            "type": "text",
            "content": response.get("response", "Let's break this down step by step..."),
            "pedagogy": generate_pedagogical_links(user_input)
        })
    
    except Exception as e:
        logging.error(f"Tutor Error: {e}")
        return JSONResponse(
            content={"type": "error", "content": "Let's try another approach..."},
            status_code=500
        )

def handle_visualization(data: dict) -> JSONResponse:
    """Generate and return visualization response with tutoring enhancements"""
    try:
        shape = data["shape"].lower()
        params = data.get("parameters", {})
        explanation = data.get("explanation", "")
        
        img_func = {
            "circle": lambda: draw_circle(params.get("radius", 5)),
            "rectangle": lambda: draw_rectangle(
                params.get("width", 5),
                params.get("height", params.get("width", 5))
            ),
            "right-angled triangle": lambda: draw_right_triangle(
                params.get("leg1", 0),
                params.get("leg2", 0)
            ),
            "trigonometric": lambda: plot_trigonometric_function(
                params.get("function", "sin")
            )
        }.get(shape, lambda: None)
        
        if not img_func:
            return JSONResponse(
                content={"type": "error", "content": "Unsupported visual concept"},
                status_code=400
            )
            
        img_base64 = img_func()
        
        return JSONResponse(content={
            "type": "visual",
            "explanation": explanation,
            "image": img_base64,
            "shape": shape
        })
        
    except Exception as e:
        logging.error(f"Visual Tutor Error: {e}")
        return JSONResponse(
            content={"type": "error", "content": explanation + "\n(Visual aid unavailable)"},
            status_code=500
        )

def add_learning_components(response: JSONResponse) -> JSONResponse:
    """Enrich visual responses with learning materials"""
    content = response.body.decode()
    data = json.loads(content)
    
    # Add related learning resources based on shape
    learning_components = {
        "circle": ["Circumference Formula", "Area Applications"],
        "rectangle": ["Surface Area", "Tiling Problems"],
        "triangle": ["Pythagorean Theorem", "Trigonometric Ratios"]
    }
    
    data["learning_resources"] = learning_components.get(
        data.get("shape", ""), 
        ["Basic Geometry Concepts"]
    )
    
    return JSONResponse(content=data)

def generate_pedagogical_links(query: str) -> dict:
    """Generate contextual learning aids"""
    return {
        "related_concepts": ["Geometric Properties", "Measurement Units"],
        "practice_problems": [
            f"Calculate the area of a {query.split()[1]} with given dimensions",
            f"Find the perimeter of a {query.split()[1]}"
        ],
        "video_resources": [
            f"https://example.com/videos/{query.split()[1]}",
            "https://example.com/geometry-basics"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "active", "service": "Math Tutor API v2.0"}