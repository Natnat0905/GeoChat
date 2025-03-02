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
from typing import Dict, Any, Optional, Tuple
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

**Key Requirements:**
1. Provide BOTH explanation AND visualization
2. Use EXACT JSON format:
{
  "shape": "shape_type",
  "parameters": {"param1": value, ...}, 
  "explanation": "Steps..."
}

**Critical Rules:**
- Parameters must be NUMERICAL VALUES (no expressions)
- Supported shapes: circle, rectangle, right_triangle, trigonometric
- For rectangles/squares:
  - Use width/height pair OR area with one dimension
  - For squares, use "side" parameter
- Example square: {"shape":"rectangle", "parameters":{"side":5}}
- Example rectangle: {"shape":"rectangle", "parameters":{"area":20, "height":4}}
- Always include units in explanation but NOT in parameters
"""

# Add after TUTOR_PROMPT
SHAPE_NORMALIZATION_RULES = {
    "circle": {
        "required": ["radius"],
        "derived": {
            "radius": [
                {"source": ["diameter"], "formula": lambda d: d/2},
                {"source": ["circumference"], "formula": lambda c: c/(2*math.pi)}
            ]
        }
    },
    "rectangle": {
        "required": ["width", "height"],
        "derived": {
            "width": [
                {"source": ["area", "height"], "formula": lambda a,h: a/h},
                {"source": ["side"], "formula": lambda s: s}  # For squares
            ],
            "height": [
                {"source": ["area", "width"], "formula": lambda a,w: a/w},
                {"source": ["side"], "formula": lambda s: s}  # For squares
            ]
        }
    },
    "right_triangle": {
        "required": ["leg1", "leg2"],
        "derived": {
            "leg1": [
                {"source": ["hypotenuse", "leg2"], 
                 "formula": lambda h,l2: math.sqrt(h**2 - l2**2)}
            ],
            "leg2": [
                {"source": ["hypotenuse", "leg1"], 
                 "formula": lambda h,l1: math.sqrt(h**2 - l1**2)}
            ]
        }
    },
    "trigonometric": {
        "required": ["function"],
        "derived": {}
    }
}

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
         # Add support for 'side' parameter
        if 'side' in value.lower():
            return safe_eval_parameter(value.lower().replace('side', ''))
        
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
    
def normalize_parameters(shape: str, params: Dict[str, float]) -> Dict[str, float]:
    """Normalize parameters to required values using defined rules"""
    rules = SHAPE_NORMALIZATION_RULES.get(shape, {})
    required = rules.get("required", [])
    derived = rules.get("derived", {})
    
    normalized = params.copy()
    
    # Handle square special case first
    if shape == "rectangle" and "side" in normalized:
        normalized["width"] = normalized["side"]
        normalized["height"] = normalized["side"]
    
    attempts = 3  # Prevent infinite loops
    while attempts > 0:
        missing = [p for p in required if p not in normalized]
        if not missing: break
        
        for param in missing:
            for formula in derived.get(param, []):
                if all(s in normalized for s in formula["source"]):
                    try:
                        normalized[param] = formula["formula"](
                            *[normalized[s] for s in formula["source"]]
                        )
                        break
                    except Exception as e:
                        logging.warning(f"Formula failed: {param} from {formula['source']}")
        attempts -= 1
    
    # Final validation
    for p in required:
        if p not in normalized or not isinstance(normalized[p], (int, float)):
            raise ValueError(f"Missing/invalid parameter: {p}")
    return normalized

def handle_visualization(data: dict) -> JSONResponse:
    try:
        shape = data["shape"].lower().replace(" ", "_")
        explanation = data.get("explanation", "")
        raw_params = data.get("parameters", {})
        
        # Evaluate all parameters first
        evaluated_params = {}
        for key, value in raw_params.items():
            try:
                evaluated_params[key] = (
                    safe_eval_parameter(value) 
                    if isinstance(value, str) 
                    else float(value)
                )  # Fixed missing closing parenthesis
            except Exception as e:
                logging.error(f"Invalid parameter {key}={value}: {str(e)}")
                evaluated_params[key] = None

        # Normalize to required parameters
        try:
            clean_params = normalize_parameters(shape, evaluated_params)
        except ValueError as e:
            return JSONResponse(
                content={"type": "error", "content": str(e)},
                status_code=400
            )
        
        # Square detection and explanation update
        if shape == "rectangle":
            width = clean_params.get("width", 0)
            height = clean_params.get("height", 0)
            if abs(width - height) < 0.001:
                explanation = explanation.replace("rectangle", "square")
                explanation += f"\nNote: This is a square with side length {width:.2f} cm"

        # Unified visualization mapping
        visualization_mapping = {
            "circle": (draw_circle, ["radius"]),
            "rectangle": (draw_rectangle, ["width", "height"]),
            "right_triangle": (draw_right_triangle, ["leg1", "leg2"]),
            "trigonometric": (plot_trigonometric_function, ["function"])
        }
        
        if shape not in visualization_mapping:
            return JSONResponse(
                content={"type": "error", "content": "Unsupported shape"},
                status_code=400
            )
        
        viz_func, expected_params = visualization_mapping[shape]
        args = [clean_params[p] for p in expected_params]
        
        img_base64 = viz_func(*args)
        clean_base64 = img_base64.split(",")[-1] if img_base64 else ""

        return JSONResponse(content={
            "type": "visual",
            "explanation": explanation,
            "image": clean_base64,
            "parameters": clean_params
        })
        
    except Exception as e:
        logging.error(f"Visualization failed: {str(e)}")
        return JSONResponse(
            content={"type": "error", "content": "Visualization generation failed"},
            status_code=500
        )

@app.get("/health")
async def health_check():
    return {"status": "active", "service": "Math Tutor API v2.0"}