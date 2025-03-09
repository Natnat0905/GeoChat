# triangle.py
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from io import BytesIO
import base64
import logging

TRIANGLE_NORMALIZATION_RULES = {
   "right_triangle": {
        "required": ["side1", "side2", "hypotenuse"],
        "derived": {
            "side1": [
                {"source": ["hypotenuse", "angle"], 
                 "formula": lambda h, a: h * math.sin(math.radians(a))},
                {"source": ["side2", "angle"], 
                 "formula": lambda s2, a: s2 * math.tan(math.radians(a))},
                {"source": ["hypotenuse", "side2"], 
                 "formula": lambda h, s2: math.sqrt(h**2 - s2**2)}
            ],
            "side2": [
                {"source": ["hypotenuse", "angle"], 
                 "formula": lambda h, a: h * math.cos(math.radians(a))},
                {"source": ["side1", "angle"], 
                 "formula": lambda s1, a: s1 / math.tan(math.radians(a))},
                {"source": ["hypotenuse", "side1"], 
                 "formula": lambda h, s1: math.sqrt(h**2 - s1**2)}
            ],
            "hypotenuse": [
                {"source": ["side1", "angle"], 
                 "formula": lambda s, a: s / math.sin(math.radians(a))},
                {"source": ["side2", "angle"], 
                 "formula": lambda s, a: s / math.cos(math.radians(a))},
                {"source": ["side1", "side2"], 
                 "formula": lambda s1, s2: math.sqrt(s1**2 + s2**2)}
            ]
        }
    },
    "equilateral_triangle": {
        "required": ["side"],
        "derived": {
            "height": [{"source": ["side"], "formula": lambda s: (math.sqrt(3)/2)*s}],
            "area": [{"source": ["side"], "formula": lambda s: (math.sqrt(3)/4)*s**2}],
            "side": [
                {"source": ["height"], "formula": lambda h: (2*h)/math.sqrt(3)},
                {"source": ["area"], "formula": lambda a: math.sqrt((4*a)/math.sqrt(3))}
            ]
        }
    },
    "similar_triangles": {
        "required": ["ratio", "corresponding_side1", "corresponding_side2"],
        "derived": {
            "ratio": [
                {"source": ["corresponding_side1", "corresponding_side2"],
                 "formula": lambda s1, s2: s1/s2}
            ]
        }
    }
}

def draw_equilateral_triangle(side: float) -> str:
    """Draw an equilateral triangle with clear labeling of all equal sides"""
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_aspect('equal')
    
    # Calculate triangle properties
    height = (math.sqrt(3)/2) * side
    x_center = side/2
    y_center = height/2
    
    # Create triangle coordinates
    vertices = [
        [0, 0],          # Left vertex
        [side, 0],        # Right vertex
        [side/2, height]  # Top vertex
    ]
    
    # Draw triangle
    triangle = Polygon(vertices, closed=True, fill=None, 
                      edgecolor='blue', linewidth=2)
    ax.add_patch(triangle)
    
    # Set axis limits with padding
    padding = side * 0.2
    ax.set_xlim(-padding, side + padding)
    ax.set_ylim(-padding, height + padding)
    
    # Add grid and axes
    ax.grid(True, linestyle='--', linewidth=0.5)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(0, color='black', linewidth=0.8)
    
    # Label all three equal sides
    ax.text(side/2, -padding/2, f'All sides: {side} cm',  # Base
           ha='center', va='top', color='green')
    ax.text(side/4, height/2, f'{side} cm',               # Left side
           rotation=60, ha='right', va='center', color='green')
    ax.text(3*side/4, height/2, f'{side} cm',             # Right side
           rotation=-60, ha='left', va='center', color='green')
    
    # Area label above triangle
    ax.text(x_center, height + padding/3, 
           f'Area = (√3/4) × {side}² = {(math.sqrt(3)/4)*side**2:.2f} cm²',
           ha='center', va='bottom', 
           bbox=dict(boxstyle="round", fc="#f0f8ff", ec="#4682b4"))
    
    # Add title
    ax.set_title(f"Equilateral Triangle (All sides = {side} cm)", pad=15)
    
    # Save to base64
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

def draw_right_triangle(side1: float, side2: float, hypotenuse: float) -> str:
    """Draw a right-angled triangle with clear labeling of all sides and area."""
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_aspect('equal')
    
    # Determine base and height (longer side as base)
    base = max(side1, side2)
    height = min(side1, side2)
    
    # Vertices for the right-angled triangle
    vertices = [
        [0, 0],          # Right angle vertex
        [base, 0],       # Base vertex
        [0, height]      # Height vertex
    ]
    
    # Draw the triangle
    triangle = Polygon(vertices, closed=True, fill=None, 
                      edgecolor='blue', linewidth=2)
    ax.add_patch(triangle)
    
    # Set axis limits with padding
    padding = max(base, height) * 0.2
    ax.set_xlim(-padding, base + padding)
    ax.set_ylim(-padding, height + padding)
    
    # Add grid and axes
    ax.grid(True, linestyle='--', linewidth=0.5)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(0, color='black', linewidth=0.8)
    
    # Label all sides
    ax.text(base/2, -padding/3, f'{base} cm', ha='center', va='top', color='green')  # Base
    ax.text(-padding/3, height/2, f'{height} cm', ha='right', va='center', color='green')  # Height
    ax.text(base/2, height/2, f'{hypotenuse} cm', ha='center', va='center', 
            color='red', rotation=45)  # Hypotenuse
    
    # Calculate and display area
    area = 0.5 * base * height
    ax.text(base/2, height + padding/4, 
            f'Area = ½ × {base} × {height} = {area:.2f} cm²',
            ha='center', va='bottom', 
            bbox=dict(boxstyle="round", fc="#f0f8ff", ec="#4682b4"))
    
    # Add title
    ax.set_title(f"Right-Angled Triangle (Legs: {base} cm, {height} cm; Hypotenuse: {hypotenuse} cm)", pad=15)
    
    # Save to base64
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

def normalize_triangle_parameters(shape_type: str, params: dict) -> dict:
    """Enhanced normalization with parameter conversion and validation"""
    normalized = params.copy()
    
    # Convert legacy parameter names
    if 'leg1' in normalized:
        normalized['side1'] = normalized.pop('leg1')
    if 'leg2' in normalized:
        normalized['side2'] = normalized.pop('leg2')
        
    # Handle equilateral triangle conversions
    if shape_type == "equilateral_triangle":
        if "height" in normalized:
            normalized["side"] = (2 * normalized["height"]) / math.sqrt(3)
        elif "area" in normalized:
            normalized["side"] = math.sqrt((4 * normalized["area"]) / math.sqrt(3))
    
    # Handle right triangle angles
    if shape_type == "right_triangle":
        angles = normalized.get("angles", [])
        if 90 in angles:
            non_right_angles = [a for a in angles if a != 90]
            if non_right_angles:
                angle = non_right_angles[0]
                if "side1" in normalized:
                    s = normalized["side1"]
                    normalized.setdefault("side2", s / math.tan(math.radians(angle)))
                    normalized.setdefault("hypotenuse", s / math.sin(math.radians(angle)))
                elif "side2" in normalized:
                    s = normalized["side2"]
                    normalized.setdefault("side1", s * math.tan(math.radians(angle)))
                    normalized.setdefault("hypotenuse", s / math.cos(math.radians(angle)))
                elif "hypotenuse" in normalized:
                    h = normalized["hypotenuse"]
                    normalized.setdefault("side1", h * math.sin(math.radians(angle)))
                    normalized.setdefault("side2", h * math.cos(math.radians(angle)))

    # Apply normalization rules
    rules = TRIANGLE_NORMALIZATION_RULES.get(shape_type, {})
    required = rules.get("required", [])
    derived = rules.get("derived", {})
    
    attempts = 3
    while attempts > 0:
        missing = [p for p in required if p not in normalized]
        if not missing:
            break
            
        for param in missing:
            for formula in derived.get(param, []):
                if all(s in normalized for s in formula["source"]):
                    try:
                        result = formula["formula"](*[normalized[s] for s in formula["source"]])
                        normalized[param] = result
                        break
                    except Exception as e:
                        logging.warning(f"Formula failed: {e}")
        attempts -= 1
        
    return normalized