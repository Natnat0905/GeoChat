import matplotlib.pyplot as plt
import math
import io
import base64

def draw_circle(radius: float) -> str:
    """Generate a circle visualization on a properly scaled graph."""
    fig, ax = plt.subplots(figsize=(7, 7))  # Keep graph size consistent with rectangles/squares

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

    return f"data:image/png;base64,{img_base64}"

def normalize_circle_parameters(params: dict) -> dict:
    """
    Normalize circle-related parameters by converting diameter or 
    circumference to radius if needed.
    """
    normalized = {k: v for k, v in params.items() if v is not None}  # Ignore None values

    if "radius" in normalized:  
        return normalized  # Already has radius, nothing to compute

    elif "diameter" in normalized:  
        # Convert diameter to radius
        normalized["radius"] = normalized["diameter"] / 2

    elif "circumference" in normalized:  
        # Convert circumference to radius using C = 2πr
        normalized["radius"] = normalized["circumference"] / (2 * math.pi)

    return normalized

# Circle Normalization Rules (Kept for reference in visual.py)
CIRCLE_NORMALIZATION_RULES = {
    "required": ["radius"],
    "derived": {
        "radius": [
            {"source": ["diameter"], "formula": lambda d: d / 2},
            {"source": ["circumference"], "formula": lambda c: c / (2 * math.pi)}
        ]
    }
}
