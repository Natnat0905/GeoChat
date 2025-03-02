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
    plot_trigonometric_function,
    draw_equilateral_triangle,
    draw_isosceles_triangle,
    draw_scalene_triangle
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
                {"source": ["area", "height"], "formula": lambda a, h: a / h},
                {"source": ["side"], "formula": lambda s: s},  # Square support
                {"source": ["diagonal"], "formula": lambda d: d / math.sqrt(2)},  # ✅ FIXED
                {"source": ["diagonal", "height"], "formula": lambda d, h: math.sqrt(d**2 - h**2)},
                {"source": ["perimeter", "height"], "formula": lambda p, h: (p - 2 * h) / 2}
            ],
            "height": [
                {"source": ["area", "width"], "formula": lambda a, w: a / w},
                {"source": ["side"], "formula": lambda s: s},  # Square support
                {"source": ["diagonal"], "formula": lambda d: d / math.sqrt(2)},  # ✅ FIXED
                {"source": ["diagonal", "width"], "formula": lambda d, w: math.sqrt(d**2 - w**2)},
                {"source": ["perimeter", "width"], "formula": lambda p, w: (p - 2 * w) / 2}
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
    "triangle": {
        "required": ["side1", "side2", "side3"],
        "derived": {
            # Right-angled triangle: Compute missing leg using Pythagoras
            "side1": [
                {"source": ["hypotenuse", "side2"], "formula": lambda h, s2: math.sqrt(h**2 - s2**2)}
            ],
            "side2": [
                {"source": ["hypotenuse", "side1"], "formula": lambda h, s1: math.sqrt(h**2 - s1**2)}
            ],
            # Equilateral triangle: If only one side is given, assume all sides are equal
            "side1": [{"source": ["side"], "formula": lambda s: s}],
            "side2": [{"source": ["side"], "formula": lambda s: s}],
            "side3": [{"source": ["side"], "formula": lambda s: s}],
            # Isosceles triangle: Compute height using Pythagorean theorem
            "height": [
                {"source": ["base", "equal_side"], "formula": lambda b, e: math.sqrt(e**2 - (b/2)**2)}
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

def safe_eval_parameter(value: Any) -> Optional[float]:
    """Safely evaluate mathematical expressions with π support, handling both strings and numbers."""
    try:
        # If the value is already a number (int or float), return it directly
        if isinstance(value, (int, float)):
            return float(value)

        # Ensure value is a string before calling .strip()
        if not isinstance(value, str) or value.strip() == "":
            return None  # Return None for invalid values

        # Replace π with math.pi and handle exponents
        expr = value.lower().replace('π', 'math.pi').replace('^', '**')
        return eval(expr, {"__builtins__": None}, {"math": math})

    except Exception as e:
        logging.error(f"Parameter evaluation failed: {value} -> {e}")
        return None  # Return None for invalid cases

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
        logging.info(f"Tutoring request: {user_input}")  # Log the input

        response = get_tutor_response(user_input)

        # Add debug print to check parsed shape parameters
        logging.info(f"GPT Response: {response}")

        # Check if the user explicitly asked for an illustration
        should_draw = any(keyword in user_input.lower() for keyword in ["draw", "illustrate", "sketch", "visualize"])

        if "shape" in response:
            if should_draw:
                return handle_visualization(response)  # Provide a drawing
            else:
                return JSONResponse(content={
                    "type": "text",
                    "content": response.get("explanation", "Let's work through this step by step...")
                })

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

    normalized = {k: v for k, v in params.items() if v is not None}  # Ignore None values

    # Special case for squares
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
                        result = formula["formula"](*[normalized[s] for s in formula["source"]])
                        if result is not None:
                            normalized[param] = result
                            break
                    except Exception as e:
                        logging.warning(f"Formula failed for {param} from {formula['source']}: {e}")
        attempts -= 1

    # Validate triangle existence
    if shape == "triangle":
        s1, s2, s3 = normalized.get("side1"), normalized.get("side2"), normalized.get("side3")
        if s1 and s2 and s3:
            if not (s1 + s2 > s3 and s1 + s3 > s2 and s2 + s3 > s1):
                raise ValueError("Invalid triangle dimensions. The sum of any two sides must be greater than the third.")

    # Ensure all required parameters exist
    for p in required:
        if p not in normalized or not isinstance(normalized[p], (int, float)):
            raise ValueError(f"Missing or invalid parameter: {p}")

    return normalized

def handle_visualization(data: dict) -> JSONResponse:
    try:
        shape = data["shape"].lower()
        explanation = data.get("explanation", "")
        raw_params = data.get("parameters", {})

        evaluated_params = {key: float(value) for key, value in raw_params.items()}
        clean_params = normalize_parameters(shape, evaluated_params)

        if not clean_params:
            return JSONResponse(
                content={"type": "error", "content": "Invalid or missing parameters for visualization."},
                status_code=400
            )

        if shape == "triangle":
            side1, side2, side3 = clean_params["side1"], clean_params["side2"], clean_params["side3"]
            
            if side1 == side2 == side3:
                explanation += f"\nThis is an equilateral triangle with sides {side1} cm."
                img = draw_equilateral_triangle(side1)
            elif side1 == side2 or side1 == side3 or side2 == side3:
                explanation += f"\nThis is an isosceles triangle with base {side1} cm and equal sides {side2} cm."
                img = draw_isosceles_triangle(side1, side2)
            else:
                explanation += f"\nThis is a scalene triangle with sides {side1} cm, {side2} cm, and {side3} cm."
                img = draw_scalene_triangle(side1, side2, side3)

        return JSONResponse(content={"type": "visual", "explanation": explanation, "image": img})

        # Generate visualization
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