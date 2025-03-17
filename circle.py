import matplotlib.pyplot as plt
import math
import io
import base64
from io import BytesIO

def draw_circle(radius: float) -> str:
    """Generate a circle visualization on a properly scaled graph."""
    fig, ax = plt.subplots(figsize=(10, 10))  # Bigger image

    # Draw the circle centered at (0,0)
    circle = plt.Circle((0, 0), radius, color='blue', fill=False, linewidth=2)
    ax.add_patch(circle)

    # Dynamic axis limits
    max_dim = radius * 1.2  # Add 20% padding
    ax.set_xlim(-max_dim, max_dim)
    ax.set_ylim(-max_dim, max_dim)

    # Ensure equal aspect ratio
    ax.set_aspect('equal', adjustable='datalim')

    # Grid and axis settings
    ax.grid(True, linestyle="--", linewidth=0.5)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(0, color='black', linewidth=0.8)

    # Label the radius
    ax.text(radius / 2, -radius * 0.1, f'Radius: {radius} cm', ha='center', color='green')

    # Label the area inside the circle
    ax.text(0, 0, f'Area = π × {radius}²\n= {math.pi * radius ** 2:.2f} cm²',
            ha='center', va='center', bbox=dict(boxstyle="round", fc="#f0f8ff", ec="#4682b4"))

    # Title
    ax.set_title(f"Circle (Radius {radius} cm)", pad=15)

    # Save image to base64 format
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"  # Keep prefix for proper image handling

def normalize_circle_parameters(params: dict) -> dict:
    """
    Normalize circle-related parameters by converting diameter or 
    circumference to radius if needed.
    """
    normalized = params.copy()
    normalized = {k: v for k, v in params.items() if v is not None}  # Ignore None values

    if "radius" in normalized:  
        return normalized  # Already has radius, nothing to compute

    elif "diameter" in normalized:  
        # Convert diameter to radius
        normalized["radius"] = normalized["diameter"] / 2

    elif "circumference" in normalized:  
        # Convert circumference to radius using C = 2πr
        normalized["radius"] = normalized["circumference"] / (2 * math.pi)

    elif "arc1" in normalized and "arc2" in normalized:
        # Use default radius if not specified
        normalized.setdefault("radius", 5)
        # Calculate angle using intersecting chords theorem
        normalized["angle"] = (normalized["arc1"] + normalized["arc2"]) / 2

    return normalized

def draw_circle_angle(arc1: float, arc2: float, radius: float = 5) -> str:
    """Visualize intersecting chords with angle calculation"""
    fig, ax = plt.subplots(figsize=(10, 10))  # Bigger image
    ax.set_aspect('equal')
    
    # Draw circle with default radius if not provided
    circle = plt.Circle((0, 0), radius, fill=False, edgecolor='blue')
    ax.add_patch(circle)
    
    # Calculate angle position
    angle = (arc1 + arc2) / 2
    start_angle = 90 - arc1/2  # Position arcs vertically for clarity
    
    # Draw arcs and chords
    ax.annotate("", xytext=(0, 0), 
                xy=(radius*math.cos(math.radians(start_angle)), 
                    radius*math.sin(math.radians(start_angle))),
                arrowprops=dict(arrowstyle="-", color="red"))
    
    ax.annotate("", xytext=(0, 0),
                xy=(radius*math.cos(math.radians(start_angle + arc1)), 
                    radius*math.sin(math.radians(start_angle + arc1))),
                arrowprops=dict(arrowstyle="-", color="green"))
    
    # Draw angle marker
    ax.text(0, 0, f"{angle:.1f}°", ha='center', va='center', 
            fontsize=12, color='purple', bbox=dict(facecolor='white', alpha=0.8))
    
    # Add arc labels
    ax.text(radius*0.7, radius*0.7, f"{arc1}°", ha='center', color='red')
    ax.text(-radius*0.7, radius*0.7, f"{arc2}°", ha='center', color='green')
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"    

# Circle Normalization Rules (Kept for reference in visual.py)
CIRCLE_NORMALIZATION_RULES = {
    "circle": {
        "required": ["radius"],
        "derived": {
            "radius": [
                {"source": ["diameter"], "formula": lambda d: d/2},
                {"source": ["circumference"], "formula": lambda c: c/(2*math.pi)}
            ]
        }
    },
    "circle_angle": {
        "required": ["arc1", "arc2"],
        "derived": {
            "angle": [{"source": ["arc1", "arc2"], "formula": lambda a1, a2: (a1 + a2)/2}]
        }
    }
}

