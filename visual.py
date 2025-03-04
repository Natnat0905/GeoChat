# Updated visual.py
import openai
import os
import re
import tempfile
import shutil
import json
import logging
import math
import base64
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import pytesseract
from io import BytesIO
import numpy as np
import cv2
from sympy import sympify, SympifyError
from circle import (draw_circle, CIRCLE_NORMALIZATION_RULES, normalize_circle_parameters)
from rectangle import (draw_rectangle, RECTANGLE_NORMALIZATION_RULES, normalize_square_parameters)
from illustration import (draw_right_triangle, plot_trigonometric_function)
from image import (extract_text_from_image, parse_math_expression)

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

SHAPE_NORMALIZATION_RULES = {
    "right_triangle": {
        "required": ["leg1", "leg2"],
        "derived": {
            "leg1": [
                {"source": ["hypotenuse", "leg2"], 
                 "formula": lambda h, l2: math.sqrt(h**2 - l2**2)}
            ],
            "leg2": [
                {"source": ["hypotenuse", "leg1"], 
                 "formula": lambda h, l1: math.sqrt(h**2 - l1**2)}
            ]
        }
    },
    "trigonometric": {
        "required": ["function"],
        "derived": {}
    }
}

# Merge circle rules into SHAPE_NORMALIZATION_RULES dynamically
SHAPE_NORMALIZATION_RULES["circle"] = CIRCLE_NORMALIZATION_RULES

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
        logging.info(f"Tutoring request: {user_input}")

        response = get_tutor_response(user_input)

        should_draw = any(keyword in user_input.lower() for keyword in ["draw", "illustrate", "sketch", "visualize"])

        if "shape" in response:
            # Normalize the parameters and handle visualization if required
            normalized_params = normalize_parameters(response["shape"], response.get("parameters", {}))
            if should_draw:
                # Call the function to generate visualization for the shape
                return handle_visualization({"shape": response["shape"], "parameters": normalized_params, "explanation": response.get("explanation", "")})
            else:
                return JSONResponse(content={"type": "text", "content": response.get("explanation", "Let's work through this step by step...")})

        return JSONResponse(content={"type": "text", "content": response.get("response", "Let's work through this step by step...")})

    except Exception as e:
        logging.error(f"Endpoint error: {str(e)}")
        return JSONResponse(content={"type": "error", "content": "Please try rephrasing your question"}, status_code=500)
    
@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    temp_path = None
    try:
        # Validate content type
        if not file.content_type.startswith('image/'):
            return JSONResponse(
                content={"type": "error", "content": "Invalid file type"},
                status_code=400
            )

        # Limit file size
        MAX_SIZE = 5 * 1024 * 1024  # 5MB
        if file.size > MAX_SIZE:
            return JSONResponse(
                content={"type": "error", "content": "File too large (max 5MB)"},
                status_code=400
            )

        # Save uploaded image
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            content = await file.read()
            if len(content) > MAX_SIZE:
                raise ValueError("File size exceeds limit")
            temp.write(content)
            temp_path = temp.name

        # OCR processing
        extracted_text = extract_text_from_image(temp_path)
        logging.info(f"Extracted text: {extracted_text}")

        # Math parsing
        math_problem = parse_math_expression(extracted_text)
        if not math_problem:
            return JSONResponse(
                content={"type": "error", "content": "No math problem detected"},
                status_code=400
            )

        # Get tutor response
        tutor_response = get_tutor_response(math_problem)
        return handle_tutor_response(math_problem, tutor_response)

    except Exception as e:
        logging.error(f"Image processing error: {str(e)}")
        return JSONResponse(
            content={"type": "error", "content": "Error processing image"},
            status_code=500
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

def handle_tutor_response(math_problem: str, tutor_response: dict) -> JSONResponse:
    try:
        # Handle the tutor's response, which might include a visualization
        explanation = tutor_response.get("explanation", "")
        shape = tutor_response.get("shape", "").lower()
        parameters = tutor_response.get("parameters", {})

        should_draw = any(keyword in math_problem.lower() for keyword in ["draw", "illustrate", "sketch", "visualize"])
        
        # Handle the visualization part if needed
        if should_draw and shape:
            return handle_visualization({"shape": shape, "parameters": parameters, "explanation": explanation})
        else:
            return JSONResponse(content={"type": "text", "content": explanation})

    except Exception as e:
        logging.error(f"Error in handle_tutor_response: {str(e)}")
        return JSONResponse(content={"type": "error", "content": "Error processing the tutor's response"}, status_code=500)
    
def normalize_parameters(shape: str, params: Dict[str, float]) -> Dict[str, float]:
    """Normalize parameters to required values using defined rules"""
    
    if shape == "rectangle":  # Check for squares
        params = normalize_square_parameters(params)  # This modifies params correctly

    elif shape == "circle":  
        params = normalize_circle_parameters(params)  # Convert circles

    rules = SHAPE_NORMALIZATION_RULES.get(shape, {})
    required = rules.get("required", [])
    derived = rules.get("derived", {})

    normalized = {k: v for k, v in params.items() if v is not None}  # Ignore None values

    attempts = 3  # Prevent infinite loops
    while attempts > 0:
        missing = [p for p in required if p not in normalized]
        if not missing:
            break

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

    # Ensure all required parameters exist
    for p in required:
        if p not in normalized or not isinstance(normalized[p], (int, float)):
            raise ValueError(f"Missing or invalid parameter: {p}")

    return normalized

def handle_visualization(data: dict) -> JSONResponse:
    try:
        shape = data["shape"].lower().replace(" ", "_")
        explanation = data.get("explanation", "")
        raw_params = data.get("parameters", {})

        # Ensure parameters are evaluated and properly normalized
        evaluated_params = {key: safe_eval_parameter(value) for key, value in raw_params.items()}
        clean_params = normalize_parameters(shape, evaluated_params)

        if not clean_params:
            return JSONResponse(content={"type": "error", "content": "Invalid parameters for drawing."}, status_code=400)

        visualization_mapping = {
            "circle": (draw_circle, ["radius"]),  # Ensure only 'radius' is passed for circles
            "rectangle": (draw_rectangle, ["width", "height"]),
            "right_triangle": (draw_right_triangle, ["leg1", "leg2"]),
            "trigonometric": (plot_trigonometric_function, ["function"])
        }

        if shape not in visualization_mapping:
            return JSONResponse(
                content={"type": "error", "content": f"Unsupported shape '{shape}'."},
                status_code=400
            )

        # Extract the corresponding function and expected parameters
        viz_func, expected_params = visualization_mapping[shape]
        args = [clean_params.get(p) for p in expected_params]

        # Check if all expected parameters are available
        if None in args:
            return JSONResponse(
                content={"type": "error", "content": f"Missing required parameters for {shape} drawing."},
                status_code=400
            )

        # Handle square case separately
        if shape == "rectangle" and abs(clean_params["width"] - clean_params["height"]) < 0.001:
            explanation = explanation.replace("rectangle", "square")
            explanation += f"\nNote: Square with side length {clean_params['width']:.2f} cm."
        
        # Generate the image
        if shape == "circle":
            # Only pass the radius for circle drawing
            img_base64 = draw_circle(clean_params["radius"])
        else:
            img_base64 = viz_func(*args)

        # Clean the base64 string to remove prefix
        clean_base64 = img_base64.split(",")[-1] if img_base64 else ""

        return JSONResponse(content={
            "type": "visual",
            "explanation": explanation,
            "image": clean_base64,
            "parameters": clean_params
        })

    except Exception as e:
        logging.error(f"Visualization Error: {e}")
        return JSONResponse(content={"type": "error", "content": "Error generating image."}, status_code=500)

@app.get("/health")
async def health_check():
    return {"status": "active", "service": "Math Tutor API v2.0"}