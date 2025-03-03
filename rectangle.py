import matplotlib.pyplot as plt
import numpy as np
import math
import base64
import io

def draw_rectangle(width: float, height: float, title: str = None) -> str:
    """Generate rectangle (or square) visualization with optional title."""
    fig, ax = plt.subplots(figsize=(7, 6))
    
    rect = plt.Rectangle((0, 0), width, height, fill=False, color='#17becf', linewidth=2.5)
    ax.add_patch(rect)
    
    ax.text(width/2, -0.1*height, f'Width: {width} cm', ha='center', va='top', color='#2ca02c')
    ax.text(-0.1*width, height/2, f'Height: {height} cm', ha='right', va='center', rotation=90, color='#2ca02c')

    ax.text(width/2, height/2, f'Area = {width} × {height}\n= {width*height} cm²', 
           ha='center', va='center', bbox=dict(boxstyle="round", fc="#f0f8ff", ec="#4682b4"))

    # Set title based on whether it's a square
    if title:
        ax.set_title(title, pad=15)
    else:
        if width == height:
            ax.set_title(f"Square (Side {width} cm)", pad=15)
        else:
            ax.set_title(f"Rectangle ({width} cm × {height} cm)", pad=15)
    
    ax.set_xlim([-1, width + 1])
    ax.set_ylim([-1, height + 1])
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')

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