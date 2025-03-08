# triangle.py
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from io import BytesIO
import base64
import logging

TRIANGLE_NORMALIZATION_RULES = {
    "right_triangle": {
        "required": ["leg1", "leg2", "hypotenuse"],
        "derived": {
            "leg1": [
                {"source": ["hypotenuse"], 
                 "formula": lambda h: h/2},  # 30° leg
                {"source": ["hypotenuse", "leg2"], 
                 "formula": lambda h, l2: math.sqrt(h**2 - l2**2)}
            ],
            "leg2": [
                {"source": ["hypotenuse"], 
                 "formula": lambda h: (h*math.sqrt(3))/2},  # 60° leg
                {"source": ["hypotenuse", "leg1"], 
                 "formula": lambda h, l1: math.sqrt(h**2 - l1**2)}
            ],
            "hypotenuse": [
                {"source": ["leg1"], 
                 "formula": lambda l1: l1*2},
                {"source": ["leg2"], 
                 "formula": lambda l2: l2*2/math.sqrt(3)}
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

def normalize_triangle_parameters(shape_type: str, params: dict) -> dict:
    """Enhanced normalization with angle handling"""
    normalized = params.copy()
    
    if shape_type == "right_triangle":
        # Handle special 30-60-90 case
        angles = normalized.get("angles")
        if angles and set(angles) == {30, 60, 90}:
            try:
                if "hypotenuse" in normalized:
                    h = normalized["hypotenuse"]
                    normalized.setdefault("leg1", h/2)
                    normalized.setdefault("leg2", (h*math.sqrt(3))/2)
                elif "leg1" in normalized:  # 30° leg
                    l1 = normalized["leg1"]
                    normalized.setdefault("hypotenuse", l1*2)
                    normalized.setdefault("leg2", l1*math.sqrt(3))
                elif "leg2" in normalized:  # 60° leg
                    l2 = normalized["leg2"]
                    normalized.setdefault("hypotenuse", l2*2/math.sqrt(3))
                    normalized.setdefault("leg1", l2/math.sqrt(3))
            except KeyError as e:
                logging.warning(f"Missing parameter for 30-60-90 triangle: {e}")

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