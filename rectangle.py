import matplotlib.pyplot as plt
import numpy as np
import math
import base64
import io

def draw_rectangle(width: float, height: float, title: str = None) -> str:
    """Generate a rectangle (or square) visualization on a properly scaled graph."""
    fig, ax = plt.subplots(figsize=(7, 7))  # Square figure for correct aspect ratio

    # Set the lower-left corner of the rectangle at (0,0) for intuitive placement
    rect = plt.Rectangle((0, 0), width, height, fill=False, color='blue', linewidth=2)
    ax.add_patch(rect)

    # Dynamic axis limits
    max_dim = max(width, height)
    padding = max_dim * 0.2  # Add 20% padding for better visualization
    ax.set_xlim(-padding, width + padding)
    ax.set_ylim(-padding, height + padding)

    # Ensure equal aspect ratio
    ax.set_aspect('equal', adjustable='datalim')

    # Grid and axis settings
    ax.grid(True, linestyle="--", linewidth=0.5)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(0, color='black', linewidth=0.8)

    # Add width and height labels
    ax.text(width / 2, -padding / 2, f'Width: {width} cm', ha='center', color='green')
    ax.text(-padding / 2, height / 2, f'Height: {height} cm', va='center', rotation=90, color='green')

    # Area label in the center of the rectangle
    ax.text(width / 2, height / 2, f'Area = {width} × {height}\n= {width * height} cm²',
            ha='center', va='center', bbox=dict(boxstyle="round", fc="#f0f8ff", ec="#4682b4"))

    # Set title based on whether it's a square
    if title:
        ax.set_title(title, pad=15)
    else:
        if width == height:
            ax.set_title(f"Square (Side {width} cm)", pad=15)
        else:
            ax.set_title(f"Rectangle ({width} cm × {height} cm)", pad=15)

    # Save image to base64 format
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return f"data:image/png;base64,{img_base64}"

def generate_image(fig) -> str:
    """Convert matplotlib figure to base64 encoded PNG"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode('utf-8')  # Add data URI prefix

def normalize_square_parameters(params: dict) -> dict:
    """
    Normalize square-related parameters to determine side length from 
    perimeter, diagonal, or area if they are given.
    """
    normalized = {k: v for k, v in params.items() if v is not None}  # Ignore None values

    if "side" in normalized:  # Square case
        normalized["width"] = normalized["side"]
        normalized["height"] = normalized["side"]

    elif "perimeter" in normalized and "width" not in normalized:  
        # Convert perimeter to side length
        normalized["width"] = normalized["height"] = normalized["perimeter"] / 4

    elif "diagonal" in normalized and "width" not in normalized:  
        # Convert diagonal to side length using √2 rule
        normalized["width"] = normalized["height"] = normalized["diagonal"] / math.sqrt(2)

    elif "area" in normalized and "width" not in normalized:  
        # Convert area to side length using √area rule
        normalized["width"] = normalized["height"] = math.sqrt(normalized["area"])

    return normalized

# Rules for normalization and formula calculations
RECTANGLE_NORMALIZATION_RULES = {
    "rectangle": {
        "required": ["width", "height"],
        "derived": {
            "width": [
                {"source": ["area", "height"], "formula": lambda a, h: a / h},
                {"source": ["side"], "formula": lambda s: s},
                {"source": ["diagonal"], "formula": lambda d: d / math.sqrt(2)},
                {"source": ["perimeter"], "formula": lambda p: p / 4},  # For squares
                {"source": ["diagonal", "height"], "formula": lambda d, h: math.sqrt(d**2 - h**2)},
                {"source": ["perimeter", "height"], "formula": lambda p, h: (p - 2 * h) / 2}
            ],
            "height": [
                {"source": ["area", "width"], "formula": lambda a, w: a / w},
                {"source": ["side"], "formula": lambda s: s},
                {"source": ["diagonal"], "formula": lambda d: d / math.sqrt(2)},
                {"source": ["perimeter"], "formula": lambda p: p / 4},  # For squares
                {"source": ["diagonal", "width"], "formula": lambda d, w: math.sqrt(d**2 - w**2)},
                {"source": ["perimeter", "width"], "formula": lambda p, w: (p - 2 * w) / 2}
            ]
        }
    }
}