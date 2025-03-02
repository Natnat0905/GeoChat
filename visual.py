import openai
import os
import re
import json
import logging
import math
import base64
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from illustration import (
    draw_circle,
    draw_right_triangle,
    draw_rectangle,
    plot_trigonometric_function
)

app = FastAPI()
logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

class Message(BaseModel):
    user_message: str

TUTOR_PROMPT = """You are a math tutor specializing in geometry. For shape-related questions:

1. **Always provide both explanation AND visualization**
2. Use this exact JSON format:
{
  "shape": "shape_type",
  "parameters": {
    "param1": numerical_value,
    "param2": numerical_value
  },
  "explanation": "### Solution Steps\\n**Step 1:** Calculate parameters...\\n**Visual Concept:** Explanation..."
}

**Critical Requirements:**
- Parameters must be calculated NUMERICAL VALUES (NOT expressions)
- Supported shapes: circle, rectangle, right_triangle, trigonometric
- Example: For "radius = 5/(2π)", calculate 5/(2*3.1416) = 0.7958
- Include units in explanation but NOT in parameters
- Always explain both calculations AND visual representation
"""

def enhance_explanation(response: str) -> str:
    replacements = {
        r"\\\(": "", r"\\\)": "",
        r"\^2": "²", r"\^3": "³",
        r"\sqrt": "√", r"\\times": "×",
        r"\\div": "÷", r"\\frac{(\d+)}{(\d+)}": r"\1/\2"
    }
    for pattern, repl in replacements.items():
        response = re.sub(pattern, repl, response)
    return response

def safe_eval_parameter(value: str) -> float:
    """Safely evaluate mathematical expressions with π support"""
    try:
        # Replace π with math.pi and handle exponents
        expr = value.lower().replace('π', 'math.pi').replace('^', '**')
        return eval(expr, {"__builtins__": None}, {"math": math})
    except:
        logging.error(f"Parameter evaluation failed: {value}")
        return 5.0  # Return default safe value

def get_tutor_response(user_message: str) -> dict:
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
    try:
        user_input = message.user_message
        logging.info(f"Tutoring: {user_input}")
        
        response = get_tutor_response(user_input)
        
        if "shape" in response:
            return handle_visualization(response)
        else:
            return JSONResponse(content={
                "type": "text",
                "content": response.get("response", "Let's work through this step by step...")
            })
            
    except Exception as e:
        logging.error(f"Endpoint error: {str(e)}")
        return JSONResponse(
            content={"type": "error", "content": "Please try rephrasing your question"},
            status_code=500
        )

# visual.py - Fix parameter handling
def handle_visualization(data: dict) -> JSONResponse:
    try:
        shape = data["shape"].lower().replace(" ", "_")
        explanation = data.get("explanation", "")
        params = data.get("parameters", {})
        
        # Process parameters with safe evaluation
        evaluated_params = {}
        for key, value in params.items():
            if isinstance(value, str):
                evaluated_params[key] = safe_eval_parameter(value)
            else:
                try:
                    evaluated_params[key] = float(value)
                except:
                    evaluated_params[key] = 5.0

        # Map to visualization functions with correct parameter names
        visualization_functions = {
            "circle": lambda: draw_circle(evaluated_params.get("radius", 5)),
            "rectangle": lambda: draw_rectangle(
                evaluated_params.get("width", 5),
                evaluated_params.get("height", 5)
            ),
            "right_triangle": lambda: draw_right_triangle(
                evaluated_params.get("leg1", 5),  # Changed from 'base'
                evaluated_params.get("leg2", 5)   # Changed from 'height'
            ),
            "trigonometric": lambda: plot_trigonometric_function(
                evaluated_params.get("function", "sin")
            )
        }

        if shape not in visualization_functions:
            return JSONResponse(
                content={"type": "error", "content": "Unsupported shape type"},
                status_code=400
            )

        img_base64 = visualization_functions[shape]()
        clean_base64 = img_base64.split(",")[-1] if img_base64 else ""

        return JSONResponse(content={
            "type": "visual",
            "explanation": explanation,
            "image": clean_base64,
            "parameters": evaluated_params
        })
        
    except Exception as e:
        logging.error(f"Visualization failed: {str(e)}")
        return JSONResponse(
            content={"type": "error", "content": "Failed to generate visualization"},
            status_code=500
        )

@app.get("/health")
async def health_check():
    return {"status": "active", "service": "Math Tutor API v2.0"}