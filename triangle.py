# triangle.py
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from io import BytesIO
import base64
import logging

TRIANGLE_NORMALIZATION_RULES = {
   "right_triangle": {
        "required": [],
        "derived": {
            "side1": [
                {"source": ["hypotenuse", "side2"], 
                 "formula": lambda h, s2: math.sqrt(h**2 - s2**2)},
                {"source": ["hypotenuse", "angle"], 
                 "formula": lambda h, a: h * math.sin(math.radians(a))},
                {"source": ["side2", "angle"], 
                 "formula": lambda s2, a: s2 * math.tan(math.radians(a))},
            ],
            "side2": [
                {"source": ["hypotenuse", "side1"], 
                 "formula": lambda h, s1: math.sqrt(h**2 - s1**2)},
                {"source": ["hypotenuse", "angle"], 
                 "formula": lambda h, a: h * math.cos(math.radians(a))},
                {"source": ["side1", "angle"], 
                 "formula": lambda s1, a: s1 / math.tan(math.radians(a))},
            ],
            "hypotenuse": [
                {"source": ["side1", "side2"], 
                 "formula": lambda s1, s2: math.sqrt(s1**2 + s2**2)},
                {"source": ["side1", "angle"], 
                 "formula": lambda s, a: s / math.sin(math.radians(a))},
                {"source": ["side2", "angle"], 
                 "formula": lambda s, a: s / math.cos(math.radians(a))},
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
    
    fig, ax = plt.subplots(figsize=(10, 10))  # Bigger image
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
    fig, ax = plt.subplots(figsize=(10, 10))  # Bigger image
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

def draw_right_triangle(side1: float, side2: float, hypotenuse: float, angles: list = None) -> str:
    """Draw a right-angled triangle with validated parameters and clear labeling."""
    # Validate input parameters
    if None in (side1, side2, hypotenuse) or any(x <= 0 for x in (side1, side2, hypotenuse)):
        raise ValueError("All sides must be positive numbers.")
    if angles is None: 
        try:
            if (math.isclose(side1*2, hypotenuse, rel_tol=0.01) and 
                math.isclose(side2, side1*math.sqrt(3), rel_tol=0.01)):
                angles = [30.0, 60.0, 90.0]
        except TypeError:
            pass
        
    fig, ax = plt.subplots(figsize=(10, 10))  # Bigger image
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
    
    # Label all sides
    ax.text(base/2, -padding/3, f'{base} cm', ha='center', va='top', color='green')  # Base
    ax.text(-padding/3, height/2, f'{height} cm', ha='right', va='center', color='green')  # Height
    ax.text(base/2, height/2, f'{hypotenuse} cm', ha='center', va='center', 
            color='red', rotation=45)  # Hypotenuse
    
    # Label angles if provided (specifically for 30-60-90 triangle)
    if angles and sorted(angles) == [30, 60, 90]:
        ax.text(0, 0, '90°', ha='center', va='center', color='red')  # Right angle
        shorter = min(side1, side2)
        if shorter == side1:
            # Shorter leg is horizontal (30° opposite)
            ax.text(base - 0.5, 0.5, '60°', ha='center', va='center', color='red')
            ax.text(0.5, height - 0.5, '30°', ha='center', va='center', color='red')
        else:
            # Shorter leg is vertical
            ax.text(base - 0.5, 0.5, '30°', ha='center', va='center', color='red')
            ax.text(0.5, height - 0.5, '60°', ha='center', va='center', color='red')
    
    # Calculate and display area
    area = 0.5 * base * height
    ax.text(base/2, height + padding/4, 
            f'Area = ½ × {base} × {height} = {area:.2f} cm²',
            ha='center', va='bottom', 
            bbox=dict(boxstyle="round", fc="#f0f8ff", ec="#4682b4"))
    
    # Add title
    title = f"Right-Angled Triangle (Legs: {base} cm, {height} cm; Hypotenuse: {hypotenuse} cm)"
    if angles:
        title += f" - {angles[0]}°-{angles[1]}°-{angles[2]}° Triangle"
    ax.set_title(title, pad=15)
    
    # Save to base64
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

def draw_similar_triangles(ratio: float, side1: float, side2: float) -> str:
    """Improved drawing function with additional validation"""
    try:
        side1 = float(side1)
        side2 = float(side2)
        hypotenuse = float(hypotenuse)
    except (TypeError, ValueError):
        raise ValueError("All parameters must be numeric values")

    # Enhanced validation
    if not all(isinstance(x, (int, float)) for x in [side1, side2, hypotenuse]):
        raise ValueError("Invalid parameter types")
    
    fig, ax = plt.subplots(figsize=(10, 10))  # Bigger image
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
    """Enhanced normalization with parameter conversion and validation"""
    normalized = params.copy()

    # Preserve angles through conversion process
    angles = normalized.get('angles')
    if isinstance(angles, list):
        try:
            normalized['angles'] = [float(a) for a in angles]
            if not math.isclose(sum(normalized['angles']), 180, rel_tol=0.01):
                del normalized['angles']
        except (TypeError, ValueError):
            del normalized['angles']

    # Convert numeric parameters while preserving angles
    for k, v in list(normalized.items()):
        if k == 'angles':  # Skip angle list from numeric check
            continue
            
        if isinstance(v, str):
            try:
                normalized[k] = float(v)
            except ValueError:
                del normalized[k]
                logging.warning(f"Removed invalid parameter: {k}={v}")
        elif not isinstance(v, (int, float)):
            del normalized[k]
            logging.warning(f"Removed non-numeric parameter: {k}={v}")

    # Handle 30-60-90 triangle logic first
    if shape_type == "right_triangle" and normalized.get('angles') == [30.0, 60.0, 90.0]:
        # Set default hypotenuse if no parameters provided
        if not any(k in normalized for k in ['side1', 'side2', 'hypotenuse']):
            normalized['hypotenuse'] = 2.0  # Default to hypotenuse=2 for ratio 1:√3:2
            
        # Calculate missing sides based on 30-60-90 ratios
        if 'hypotenuse' in normalized:
            normalized.setdefault('side1', normalized['hypotenuse'] / 2)
            normalized.setdefault('side2', (normalized['hypotenuse'] * math.sqrt(3)) / 2)
        elif 'side1' in normalized:
            normalized.setdefault('hypotenuse', normalized['side1'] * 2)
            normalized.setdefault('side2', normalized['side1'] * math.sqrt(3))
        elif 'side2' in normalized:
            normalized.setdefault('hypotenuse', (normalized['side2'] * 2) / math.sqrt(3))
            normalized.setdefault('side1', normalized['side2'] / math.sqrt(3))
    
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
    
    if shape_type == "right_triangle" and normalized.get('angles') == [30.0, 60.0, 90.0]:
            # Handle 30-60-90 triangle ratios
            hypotenuse = normalized.get('hypotenuse')
            side1 = normalized.get('side1')
            side2 = normalized.get('side2')
            
            if hypotenuse:
                normalized['side1'] = hypotenuse / 2
                normalized['side2'] = (hypotenuse * math.sqrt(3)) / 2
            elif side1:
                normalized['hypotenuse'] = 2 * side1
                normalized['side2'] = side1 * math.sqrt(3)
            elif side2:
                normalized['hypotenuse'] = (2 * side2) / math.sqrt(3)
                normalized['side1'] = side2 / math.sqrt(3)
            else:
                raise ValueError("For 30-60-90 triangle, provide one side.")
            
            # Validate provided sides match ratios
            if 'hypotenuse' in params and not math.isclose(params['hypotenuse'], normalized['hypotenuse'], rel_tol=0.01):
                raise ValueError("Provided hypotenuse doesn't match 30-60-90 ratio.")
            if 'side1' in params and not math.isclose(params['side1'], normalized['side1'], rel_tol=0.01):
                raise ValueError("Provided side1 doesn't match 30-60-90 ratio.")
            if 'side2' in params and not math.isclose(params['side2'], normalized['side2'], rel_tol=0.01):
                raise ValueError("Provided side2 doesn't match 30-60-90 ratio.")
    
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
    
    if shape_type == "right_triangle":
        # Ensure numeric types for calculations
        try:
            hypotenuse = float(normalized.get("hypotenuse", 0))
            side1 = float(normalized.get("side1", 0))
            side2 = float(normalized.get("side2", 0))
        except (TypeError, ValueError):
            raise ValueError("Invalid numeric parameters for right triangle")

        # Pythagorean calculation with validation
        if hypotenuse and side1 and not side2:
            normalized["side2"] = math.sqrt(hypotenuse**2 - side1**2)
        elif hypotenuse and side2 and not side1:
            normalized["side1"] = math.sqrt(hypotenuse**2 - side2**2)
        elif side1 and side2 and not hypotenuse:
            normalized["hypotenuse"] = math.sqrt(side1**2 + side2**2)

        # Apply Pythagorean theorem if two sides are provided
        provided = [k for k in ['side1', 'side2', 'hypotenuse'] if k in normalized]
        if len(provided) == 2:
            if 'hypotenuse' in provided:
                h = normalized['hypotenuse']
                if 'side1' in provided:
                    s1 = normalized['side1']
                    normalized['side2'] = math.sqrt(h**2 - s1**2)
                elif 'side2' in provided:
                    s2 = normalized['side2']
                    normalized['side1'] = math.sqrt(h**2 - s2**2)
            else:
                s1 = normalized.get('side1', 0)
                s2 = normalized.get('side2', 0)
                normalized['hypotenuse'] = math.sqrt(s1**2 + s2**2)

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