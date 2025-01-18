import matplotlib.pyplot as plt
import numpy as np
import re
import logging

def create_visualization(user_message: str) -> str:
    """
    Dynamically create illustrations for 2D geometry shapes or mathematical functions.
    """
    try:
        if "circle" in user_message:
            radius = extract_numeric_parameter(user_message, "radius", default=5)
            return draw_circle(radius)

        if "triangle" in user_message:
            base = extract_numeric_parameter(user_message, "base", default=4)
            height = extract_numeric_parameter(user_message, "height", default=3)
            return draw_triangle(base, height)

        if "rectangle" in user_message:
            width = extract_numeric_parameter(user_message, "width", default=6)
            height = extract_numeric_parameter(user_message, "height", default=3)
            return draw_rectangle(width, height)

        if "sin" in user_message or "cos" in user_message or "tan" in user_message:
            return plot_trigonometric_function(user_message)

        return ""
    except Exception as e:
        logging.error(f"Error creating visualization: {e}")
        return ""

def extract_numeric_parameter(user_message: str, param: str, default: float = 0) -> float:
    match = re.search(rf"{param}\s*is\s*(\d+)", user_message.lower())
    if match:
        return float(match.group(1))
    return default

def draw_circle(radius: float) -> str:
    fig, ax = plt.subplots()
    circle = plt.Circle((0, 0), radius, fill=False, color="blue", linewidth=2)
    ax.add_artist(circle)
    ax.set_xlim(-radius - 1, radius + 1)
    ax.set_ylim(-radius - 1, radius + 1)
    ax.set_aspect('equal', 'box')
    ax.set_title(f"Circle with Radius {radius}")
    plt.grid(True)
    filepath = "circle_plot.png"
    plt.savefig(filepath)
    plt.close(fig)
    return filepath

def draw_triangle(base: float, height: float) -> str:
    fig, ax = plt.subplots()
    points = np.array([[0, 0], [base, 0], [base / 2, height]])
    triangle = plt.Polygon(points, fill=None, edgecolor="purple", linewidth=2)
    ax.add_patch(triangle)
    ax.set_xlim(-1, base + 1)
    ax.set_ylim(-1, height + 1)
    ax.set_aspect('equal', 'box')
    ax.set_title(f"Triangle (Base={base}, Height={height})")
    plt.grid(True)
    filepath = "triangle_plot.png"
    plt.savefig(filepath)
    plt.close(fig)
    return filepath

def draw_rectangle(width: float, height: float) -> str:
    fig, ax = plt.subplots()
    rectangle = plt.Rectangle((0, 0), width, height, fill=None, edgecolor="green", linewidth=2)
    ax.add_patch(rectangle)
    ax.set_xlim(-1, width + 1)
    ax.set_ylim(-1, height + 1)
    ax.set_aspect('equal', 'box')
    ax.set_title(f"Rectangle ({width}x{height})")
    plt.grid(True)
    filepath = "rectangle_plot.png"
    plt.savefig(filepath)
    plt.close(fig)
    return filepath

def plot_trigonometric_function(user_message: str) -> str:
    x = np.linspace(0, 2 * np.pi, 500)
    if "sin" in user_message:
        y = np.sin(x)
        return plot_function(x, y, "Sine Function", "sin(x)")
    if "cos" in user_message:
        y = np.cos(x)
        return plot_function(x, y, "Cosine Function", "cos(x)")
    if "tan" in user_message:
        y = np.tan(x)
        y[np.abs(y) > 10] = np.nan  # Avoid asymptotes
        return plot_function(x, y, "Tangent Function", "tan(x)")
    return ""

def plot_function(x, y, title: str, label: str) -> str:
    fig, ax = plt.subplots()
    ax.plot(x, y, label=label)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.legend()
    ax.set_title(title)
    ax.grid(True)
    filepath = f"{title.replace(' ', '_').lower()}.png"
    plt.savefig(filepath)
    plt.close(fig)
    return filepath
