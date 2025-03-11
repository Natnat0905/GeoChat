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
                 "formula": lambda h, s2: math.sqrt(h**2 - s2**2)},
                {"source": ["base"], "formula": lambda b: b}  # Direct mapping
            ],
            "side2": [
                {"source": ["hypotenuse", "angle"], 
                 "formula": lambda h, a: h * math.cos(math.radians(a))},
                {"source": ["side1", "angle"], 
                 "formula": lambda s1, a: s1 / math.tan(math.radians(a))},
                {"source": ["hypotenuse", "side1"], 
                 "formula": lambda h, s1: math.sqrt(h**2 - s1**2)},
                {"source": ["height"], "formula": lambda h: h}  # Direct mapping
            ],
            "hypotenuse": [
                {"source": ["side1", "angle"], 
                 "formula": lambda s, a: s / math.sin(math.radians(a))},
                {"source": ["side2", "angle"], 
                 "formula": lambda s, a: s / math.cos(math.radians(a))},
                {"source": ["side1", "side2"], 
                 "formula": lambda s1, s2: math.sqrt(s1**2 + s2**2)},
                {"source": ["base", "height"],  # New direct calculation
                 "formula": lambda b, h: math.sqrt(b**2 + h**2)}
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
    },
    "general_triangle": {
        "required": ["side_a", "side_b", "side_c"],
        "derived": {
            "angle_a": [{"source": ["side_a", "side_b", "side_c"], 
                       "formula": lambda a, b, c: math.degrees(math.acos((b**2 + c**2 - a**2)/(2*b*c)))}],
            "angle_b": [{"source": ["side_a", "side_b", "side_c"], 
                       "formula": lambda a, b, c: math.degrees(math.acos((a**2 + c**2 - b**2)/(2*a*c)))}],
            "area": [{"source": ["side_a", "side_b", "side_c"],
                     "formula": lambda a, b, c: herons_formula(a, b, c)}],
            "height": [{"source": ["area", "side_a"],
                      "formula": lambda area, a: (2*area)/a}
            ]
        }
    },
    "isosceles_triangle": {
        "required": ["base", "equal_sides"],
        "derived": {
            "side_a": [{"source": ["base"], "formula": lambda b: b}],
            "side_b": [{"source": ["equal_sides"], "formula": lambda s: s}],
            "side_c": [{"source": ["equal_sides"], "formula": lambda s: s}],
            "base": [{"source": ["side_a"], "formula": lambda a: a}],
            "equal_sides": [{"source": ["side_b"], "formula": lambda b: b}]
        }
    }
}

def is_valid_triangle(sides: list) -> bool:
    """Enhanced validation with parameter order preservation"""
    a, b, c = sides  # Keep original order
    return (a + b > c) and (a + c > b) and (b + c > a) and all(s > 0 for s in sides)

def draw_general_triangle(side_a: float, side_b: float, side_c: float) -> str:
    """Draw any triangle with given side lengths and full annotations"""
    # Validate triangle inequality
    sides = [side_a, side_b, side_c]    # Validate triangle inequality
    if not is_valid_triangle([side_a, side_b, side_c]):
        raise ValueError("Invalid triangle dimensions")
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_aspect('equal')
    
    # Preserve original order but ensure base is horizontal
    base = side_a
    left = side_b
    right = side_c
    
    # Calculate angles using Law of Cosines
    try:
        angle = math.acos((left**2 + base**2 - right**2)/(2*left*base))
    except ValueError:
        # Handle floating point precision issues
        angle = math.acos(round((left**2 + base**2 - right**2)/(2*left*base), 10))
    
    # Calculate vertex coordinates
    vertices = [
        [0, 0],                   # Vertex A (base start)
        [base, 0],                # Vertex B (base end)
        [left*math.cos(angle),    # Vertex C (apex)
         left*math.sin(angle)]
    ]
    # Draw triangle
    triangle = Polygon(vertices, closed=True, fill=None, 
                      edgecolor='blue', linewidth=2)
    ax.add_patch(triangle)
    
    # Set axis limits with padding
    padding = max(sides) * 0.2
    ax.set_xlim(-padding, base + padding)
    ax.set_ylim(-padding, vertices[2][1] + padding)  # Fixed line
    
    # Label sides and angles
    label_sides(ax, vertices, sides)  # Use sorted sides for labeling
    label_angles(ax, vertices)
    
    # Calculate and display properties
    area = herons_formula(side_a, side_b, side_c)
    perimeter = sum(sides)
    ax.text(0.5*base, vertices[2][1] + padding/3,  # Also fixed here
            f"Area: {area:.2f} cm² | Perimeter: {perimeter:.1f} cm",
            ha='center', va='bottom', 
            bbox=dict(boxstyle="round", fc="#f0f8ff", ec="#4682b4"))
    
    # Add title
    ax.set_title(f"General Triangle (Sides: {side_a} cm, {side_b} cm, {side_c} cm)", pad=15)
    
    # Save to base64
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

def label_sides(ax, vertices, original_sides):
    """Label all three sides with proper orientation"""
    # Base label (side_a)
    ax.text((vertices[0][0] + vertices[1][0])/2, 
           (vertices[0][1] + vertices[1][1])/2 - 0.5,
           f'{original_sides[0]:.1f} cm', 
           ha='center', va='top', color='darkgreen')
    
    # Left side label (side_b)
    dx = vertices[2][0] - vertices[0][0]
    dy = vertices[2][1] - vertices[0][1]
    rotation = math.degrees(math.atan2(dy, dx))
    ax.text((vertices[0][0] + vertices[2][0])/2 - 0.2,
           (vertices[0][1] + vertices[2][1])/2,
           f'{original_sides[1]:.1f} cm',
           rotation=rotation, 
           ha='right' if dx < 0 else 'left',
           va='center',
           color='navy')
    
    # Right side label (side_c)
    dx = vertices[2][0] - vertices[1][0]
    dy = vertices[2][1] - vertices[1][1]
    rotation = math.degrees(math.atan2(dy, dx))
    ax.text((vertices[1][0] + vertices[2][0])/2 + 0.2,
           (vertices[1][1] + vertices[2][1])/2,
           f'{original_sides[2]:.1f} cm',
           rotation=rotation,
           ha='left' if dx > 0 else 'right',
           va='center',
           color='maroon')
    
def label_angles(ax, vertices):
    """Label all three angles"""
    for i in range(3):
        prev = vertices[i]
        curr = vertices[(i+1)%3]
        next_v = vertices[(i+2)%3]
        
        angle = math.degrees(math.atan2(next_v[1]-curr[1], next_v[0]-curr[0]) - 
                            math.atan2(prev[1]-curr[1], prev[0]-curr[0]))
        angle = (angle + 360) % 360
        label = f"{angle:.1f}°"
        
        ax.text(curr[0], curr[1], label, ha='center', va='center',
               bbox=dict(facecolor='white', edgecolor='none', pad=1))

def herons_formula(a: float, b: float, c: float) -> float:
    """Calculate area using Heron's formula"""
    s = (a + b + c) / 2
    return math.sqrt(s * (s - a) * (s - b) * (s - c))

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
    
    # Convert legacy parameter names for general triangles
    if shape_type == "general_triangle":
        param_map = {
            'side1': 'side_a',
            'side2': 'side_b', 
            'side3': 'side_c',
            'a': 'side_a',
            'b': 'side_b',
            'c': 'side_c'
        }
        for old_name, new_name in param_map.items():
            if old_name in normalized:
                normalized[new_name] = normalized.pop(old_name)

    # Convert legacy parameter names
    if 'leg1' in normalized:
        normalized['side1'] = normalized.pop('leg1')
    if 'leg2' in normalized:
        normalized['side2'] = normalized.pop('leg2')
    
    if shape_type == "isosceles_triangle":
        if "base" in normalized and "equal_sides" in normalized:
            # Preserve parameter order for drawing
            normalized["side_a"] = normalized["base"]
            normalized["side_b"] = normalized["equal_sides"]
            normalized["side_c"] = normalized["equal_sides"]
            del normalized["base"]
            del normalized["equal_sides"]
            
            # Verify isosceles property
            if normalized["side_b"] != normalized["side_c"]:
                raise ValueError("Invalid isosceles triangle parameters")

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