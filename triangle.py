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
                 "formula": lambda s2, a: s2 * math.tan(math.radians(a))}
            ],
            "side2": [
                {"source": ["hypotenuse", "angle"], 
                 "formula": lambda h, a: h * math.cos(math.radians(a))},
                {"source": ["side1", "angle"], 
                 "formula": lambda s1, a: s1 / math.tan(math.radians(a))}
            ],
            "hypotenuse": [
                {"source": ["side1", "angle"], 
                 "formula": lambda s, a: s / math.sin(math.radians(a))},
                {"source": ["side2", "angle"], 
                 "formula": lambda s, a: s / math.cos(math.radians(a))}
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

# triangle.py
def draw_equilateral_triangle(side: float) -> str:
    """Draw an equilateral triangle with proper scaling and labels"""
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_aspect('equal')
    
    # Calculate triangle properties
    height = (math.sqrt(3)/2) * side
    area = (math.sqrt(3)/4) * side**2
    
    # Create triangle coordinates
    vertices = [
        [0, 0],
        [side, 0],
        [side/2, height]
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
    
    # Add labels with proper positioning
    ax.text(side/2, -padding/2, f'Side: {side} cm', 
           ha='center', va='top', color='green')
    
    # Height label
    ax.annotate(f'Height: {height:.2f} cm', 
                xy=(side/2, height/2), xytext=(-padding, height/2),
                arrowprops=dict(arrowstyle="->", color='red'),
                ha='right', va='center', color='red')
    
    # Area label
    ax.text(side/2, height + padding/2, 
           f'Area = (√3/4) × {side}² = {area:.2f} cm²',
           ha='center', va='bottom', 
           bbox=dict(boxstyle="round", fc="#f0f8ff", ec="#4682b4"))
    
    # Add title
    ax.set_title(f"Equilateral Triangle (Side {side} cm)", pad=15)
    
    # Save to base64
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

def draw_right_triangle(side1: float, side2: float, hypotenuse: float) -> str:
    """Draw right triangle with automatic orientation"""
    base = max(side1, side2)
    height = min(side1, side2)
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')
    
    triangle = Polygon(
        [[0, 0], [base, 0], [0, height]],
        closed=True, fill=None, edgecolor='blue', linewidth=2
    )
    ax.add_patch(triangle)
    
    plt.text(base/2, -0.8, f'{base:.2f} cm', ha='center')
    plt.text(-0.8, height/2, f'{height:.2f} cm', va='center')
    plt.text(base/2, height/2, f'{hypotenuse:.2f} cm', 
             ha='center', color='red')
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

def draw_similar_triangles(ratio: float, side1: float, side2: float) -> str:
    """Draw two similar triangles with labeled sides and similarity ratio"""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_aspect('equal')
    plt.axis('off')
    
    # Draw first triangle (ΔABC)
    triangle1 = Polygon(
        [[0, 0], [side1, 0], [0, side1*0.6]],
        closed=True, fill=None, edgecolor='blue', linewidth=2
    )
    ax.add_patch(triangle1)
    
    # Draw second similar triangle (ΔDEF)
    triangle2 = Polygon(
        [[side1 + 2, 0], 
         [side1 + 2 + side2, 0], 
         [side1 + 2, side2 * 0.6 * ratio]],
        closed=True, fill=None, edgecolor='red', linewidth=2
    )
    ax.add_patch(triangle2)
    
    # Add labels and annotations
    plt.text(side1/2, -0.8, f'AB = {side1}', ha='center', fontsize=10)
    plt.text(side1 + 2 + side2/2, -0.8, f'DE = {side2}', ha='center', fontsize=10)
    plt.text((side1 + side1 + 2)/2, max(side1*0.6, side2*0.6*ratio)/2,
             f'Similarity Ratio: {ratio:.2f}:1', ha='center', va='center',
             fontsize=12, color='purple')
    
    # Save to base64
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

 # illustration.py
def draw_right_triangle(side1: float, side2: float, hypotenuse: float) -> str:
    """Draw right triangle with automatic orientation"""
    # Determine triangle orientation
    base = max(side1, side2)
    height = min(side1, side2)
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')
    
    triangle = plt.Polygon(
        [[0, 0], [base, 0], [0, height]],
        closed=True, fill=None, edgecolor='blue', linewidth=2
    )
    ax.add_patch(triangle)
    
    # Label sides
    plt.text(base/2, -0.8, f'{base:.2f}', ha='center')
    plt.text(-0.8, height/2, f'{height:.2f}', va='center')
    plt.text(base/2, height/2, f'{hypotenuse:.2f}', ha='center', color='red')
    
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