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
    """Enhanced normalization with angle validation and parameter handling"""
    normalized = params.copy()
    
    if shape_type == "right_triangle":
        # Convert legacy parameter names
        normalized = {k.replace('leg', 'side'): v for k, v in normalized.items()}
        
        # Validate and process angles
        angles = normalized.get("angles", [])
        if 90 in angles:
            try:
                # Calculate third angle if needed
                if len(angles) == 2:
                    angles.append(90)
                    angles = list(set(angles))  # Remove duplicate 90 if present
                    angles.append(180 - sum(angles))
                
                # Get non-right angles
                non_right_angles = [a for a in angles if a != 90]
                if sum(non_right_angles) != 90:
                    raise ValueError("Invalid right triangle angles")
                
                angle = non_right_angles[0]  # Use first non-right angle for calculations
                normalized["angle"] = angle

                # Calculate missing sides
                if "side1" in normalized:
                    s1 = normalized["side1"]
                    normalized["side2"] = s1 / math.tan(math.radians(angle))
                    normalized["hypotenuse"] = s1 / math.sin(math.radians(angle))
                elif "side2" in normalized:
                    s2 = normalized["side2"]
                    normalized["side1"] = s2 * math.tan(math.radians(angle))
                    normalized["hypotenuse"] = s2 / math.cos(math.radians(angle))
                elif "hypotenuse" in normalized:
                    h = normalized["hypotenuse"]
                    normalized["side1"] = h * math.sin(math.radians(angle))
                    normalized["side2"] = h * math.cos(math.radians(angle))
                    
            except (IndexError, ValueError) as e:
                logging.error(f"Angle validation failed: {e}")

    # Existing normalization logic
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
                        if result is not None:
                            normalized[param] = result
                            break
                    except Exception as e:
                        logging.warning(f"Formula failed for {param}: {e}")
        attempts -= 1
        
    return normalized