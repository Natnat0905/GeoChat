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
from circle import (draw_circle, CIRCLE_NORMALIZATION_RULES, normalize_circle_parameters, draw_circle_angle)
from rectangle import (draw_rectangle, RECTANGLE_NORMALIZATION_RULES, normalize_square_parameters)
from illustration import (draw_right_triangle, plot_trigonometric_function)
from triangle import TRIANGLE_NORMALIZATION_RULES, draw_similar_triangles, normalize_triangle_parameters, draw_right_triangle, draw_equilateral_triangle, draw_general_triangle, is_valid_triangle

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

TUTOR_PROMPT = """You are a high school math tutor. Follow these STRICT RULES:

1. Analyze if the user's question meets ALL criteria:
   - Is a mathematics problem
   - Falls under high school level (Grades 9-12)
   - Covers: Algebra, Geometry, Trigonometry, or Basic Calculus
   
2. If NOT a valid math question, respond EXACTLY:
{
  "error": "I specialize in high school math questions only"
}

3. Response Requirements:
- Break down problems into 3-5 clear steps
- Explain concepts using real-world examples
- Highlight common mistakes
- Use simple language with analogies

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

- For similar triangles:
  - Use "ratio" of similarity
  - Include pairs of corresponding sides
  - Example: {"shape":"similar_triangles", "parameters":{"corresponding_side1":20, "corresponding_side2":5}}

- For right triangles with 30-60-90 angles:
  - Specify hypotenuse or one leg
  - Include angles parameter: "angles": [30, 60, 90]
  - Example: {"shape":"right_triangle", "parameters": {"hypotenuse": 21, "angles": [30,60,90]}

- For right triangles with any angles:
  - Specify at least one side and the non-right angles
  - Include angles parameter: "angles": [90, x, y]
  - Example: {"shape":"right_triangle", "parameters": {"side1": 4, "angles": [90, 40, 50]}

- For right triangles with any angles:
  - Use parameters: side1, side2, hypotenuse
  - Specify at least one side and angles
  - Example: {"shape":"right_triangle", "parameters": {"side1": 4, "angles": [90, 40, 50]}

- For circle intersection angles:
  - Specify both intercepted arcs
  - Example: {"shape":"circle_angle", "parameters": {"arc1": 120, "arc2": 50}}

- For equilateral triangles:
  - Specify side length
  - Example: {"shape":"equilateral_triangle", "parameters": {"side": 5}}

- For any triangle with three sides:
  - Use "shape": "general_triangle"
  - Include parameters: "side_a", "side_b", "side_c"
  - Example: {"shape":"general_triangle", "parameters":{"side_a":7, "side_b":5, "side_c":9}}

- For isosceles triangles:
  - Specify "base" and "equal_sides" parameters
  - Example: {"shape":"isosceles_triangle", "parameters":{"base":10, "equal_sides":6}}

- For right triangles with 30-60-90 angles:
  - Specify hypotenuse or one leg
  - Include angles parameter: "angles": [30,60,90]
  - Example: {"shape":"right_triangle", "parameters": {"hypotenuse": 10, "angles": [30,60,90]}
"""

SHAPE_NORMALIZATION_RULES = {
    "trigonometric": {
        "required": ["function"],
        "derived": {}
    }
}
SHAPE_NORMALIZATION_RULES.update(TRIANGLE_NORMALIZATION_RULES)
SHAPE_NORMALIZATION_RULES["circle"] = CIRCLE_NORMALIZATION_RULES
SHAPE_NORMALIZATION_RULES["circle_angle"] = CIRCLE_NORMALIZATION_RULES["circle_angle"]


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
    if isinstance(value, list):
        try:
            return [float(v) for v in value]
        except:
            return None
    try:
        if isinstance(value, (int, float)):
            return float(value)
        if not isinstance(value, str) or value.strip() == "":
            return None
        expr = value.lower().replace('π', 'math.pi').replace('^', '**')
        return eval(expr, {"__builtins__": None}, {"math": math})
    except Exception as e:
        logging.error(f"Parameter evaluation failed: {value} -> {e}")
        return None

def get_tutor_response(user_message: str) -> dict:
    try:
        # Hybrid prompt for speed and quality
        system_msg = """You are a MATH specialist. Follow these rules:
        1. Only answer math questions
        2. Supported shapes: circle, rectangle, triangle variants
        3. For non-math queries: {"response": "I specialize in math questions"}"""

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=700,
            request_timeout=15  # Add timeout
        )
        
        raw = response.choices[0].message.content
        
        # Improved JSON extraction
        json_match = re.search(r'\{.*?\}', raw, re.DOTALL)
        json_str = json_match.group() if json_match else raw
        
        try:
            json_response = json.loads(json_str)
            if "shape" in json_response:
                return {
                    "explanation": enhance_explanation(json_response.get("explanation", "")),
                    "shape": json_response["shape"],
                    "parameters": json_response.get("parameters", {})
                }
        except json.JSONDecodeError:
            pass
        
        return {"response": enhance_explanation(raw)}
    
    except Exception as e:
        logging.error(f"GPT Error: {e}")
        return {"response": "Let's try to work through this problem together. First..."}

def get_fallback_response(user_message: str) -> dict:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Provide math explanations with JSON formatting"},
                {"role": "user", "content": user_message}
            ],
            temperature=0.4,
            max_tokens=600,
            request_timeout=10
        )
        raw = response.choices[0].message.content
        
        # Improved JSON extraction
        json_match = re.search(r'\{.*?\}', raw, re.DOTALL)
        json_str = json_match.group() if json_match else raw
        
        try:
            json_response = json.loads(json_str)
            if "shape" in json_response:
                return {
                    "explanation": enhance_explanation(json_response.get("explanation", "")),
                    "shape": json_response["shape"],
                    "parameters": json_response.get("parameters", {})
                }
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
    
    if shape in TRIANGLE_NORMALIZATION_RULES:
        params = normalize_triangle_parameters(shape, params)
    elif shape == "rectangle":
        params = normalize_square_parameters(params)
    elif shape == "circle":
        params = normalize_circle_parameters(params)

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
        
            # Handle right triangle angle labeling
        if shape == "right_triangle" and 'angles' in clean_params:
            # Ensure angles are passed to the drawing function
            clean_params['angles'] = [float(a) for a in clean_params['angles']]

        visualization_mapping = {
            "circle": (draw_circle, ["radius"]),
            "rectangle": (draw_rectangle, ["width", "height"]),
            "right_triangle": (draw_right_triangle, ["side1", "side2", "hypotenuse"]),  # Updated parameter names
            "trigonometric": (plot_trigonometric_function, ["function"]),
            "similar_triangles": (draw_similar_triangles, ["ratio", "corresponding_side1", "corresponding_side2"]),
            "equilateral_triangle": (draw_equilateral_triangle, ["side"]),
            "general_triangle": (draw_general_triangle, ["side_a", "side_b", "side_c"]),
            "triangle": (draw_general_triangle, ["side_a", "side_b", "side_c"]), # Alias
            "isosceles_triangle": (lambda a, b, c: draw_general_triangle(a, b, c).replace("General Triangle", f"Isosceles Triangle (Base: {a}cm, Equal Sides: {b}cm)"),["side_a", "side_b", "side_c"])
            }  

        if shape not in visualization_mapping:
            return JSONResponse(
                content={"type": "error", "content": f"Unsupported shape '{shape}'."},
                status_code=400
            )

        # Extract the corresponding function and expected parameters
        viz_func, expected_params = visualization_mapping[shape]
        args = [clean_params.get(p) for p in expected_params]
        if shape == "right_triangle" and 'angles' in clean_params:
            args.append(clean_params['angles'])

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
        
        if shape == "isosceles_triangle":
            sides = [clean_params["side_a"], clean_params["side_b"], clean_params["side_c"]]
            if len(set(sides)) != 2:
                return JSONResponse(content={"type": "error", "content": "Invalid isosceles triangle."}, status_code=400)

        # Generate the image
        try:
            if shape == "circle":
                img_base64 = draw_circle(clean_params["radius"])
            elif shape == "general_triangle":
                # Special handling for triangle validation
                sides = [clean_params["side_a"], clean_params["side_b"], clean_params["side_c"]]
                if not is_valid_triangle(sides):
                    return JSONResponse(
                        content={"type": "error", "content": "Invalid triangle dimensions - violates triangle inequality"},
                        status_code=400
                    )
                img_base64 = viz_func(*args)
            else:
                img_base64 = viz_func(*args)
        except ValueError as ve:
            return JSONResponse(
                content={"type": "error", "content": str(ve)},
                status_code=400
            )

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