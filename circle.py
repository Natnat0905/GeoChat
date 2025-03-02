import matplotlib.pyplot as plt
import math
import io
import base64

def calculate_circumference(radius: float) -> float:
    """Calculate the circumference of a circle given the radius."""
    return 2 * math.pi * radius

def calculate_diameter(radius: float) -> float:
    """Calculate the diameter of a circle given the radius."""
    return 2 * radius

def calculate_area(radius: float) -> float:
    """Calculate the area of a circle given the radius."""
    return math.pi * radius**2

def draw_circle(radius: float) -> str:
    """Draw a circle given a radius and return the image as a base64 string."""
    fig, ax = plt.subplots()

    # Draw the circle
    circle = plt.Circle((0, 0), radius, color='blue', fill=False, linewidth=2)
    ax.add_artist(circle)

    # Set limits
    ax.set_xlim(-radius-1, radius+1)
    ax.set_ylim(-radius-1, radius+1)
    ax.set_aspect('equal', 'box')
    
    ax.set_title(f"Circle with Radius {radius}")
    ax.grid(True)

    return generate_image(fig)

def generate_image(fig) -> str:
    """Convert matplotlib figure to base64 encoded PNG."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode('utf-8')
