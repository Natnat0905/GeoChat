import matplotlib.pyplot as plt
import numpy as np
import re
import logging

def create_visualization(user_message: str) -> str:
    """
    Dynamically create illustrations for 2D geometry shapes or mathematical functions.
    """
    try:
        parameters = extract_numeric_parameters(user_message)

        # Check for specific shapes or functions in the message
        if "circle" in user_message:
            radius = parameters.get("radius") or (parameters.get("diameter", 0) / 2) or 5
            return draw_circle(radius)

        if "triangle" in user_message:
            base = parameters.get("base", 4)
            height = parameters.get("height", 3)
            return draw_triangle(base, height)

        if "rectangle" in user_message:
            width = parameters.get("width", 6)
            height = parameters.get("height", 3)
            return draw_rectangle(width, height)

        if "ellipse" in user_message:
            major_axis = parameters.get("major_axis", 6)
            minor_axis = parameters.get("minor_axis", 4)
            return draw_ellipse(major_axis, minor_axis)

        if "polygon" in user_message:
            sides = parameters.get("sides", 5)
            radius = parameters.get("radius", 3)
            return draw_polygon(sides, radius)

        if "sin" in user_message or "cos" in user_message or "tan" in user_message:
            return plot_trigonometric_function(user_message)

        return ""  # Return an empty string if no matching shape or function is found
    except Exception as e:
        logging.error(f"Error creating visualization: {e}")
        return ""

def extract_numeric_parameters(user_message: str) -> dict:
    """
    Extract all numeric parameters from the user message.
    Supports phrases like 'radius is 10', 'base is 5, height is 8', or 'diameter of 15'.
    """
    parameter_regex = r"(?P<key>\w+)\s*(is|of)\s*(?P<value>\d+(\.\d+)?)"
    matches = re.findall(parameter_regex, user_message.lower())
    return {match[0]: float(match[2]) for match in matches}

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

def draw_ellipse(major_axis: float, minor_axis: float) -> str:
    fig, ax = plt.subplots()
    ellipse = plt.Ellipse((0, 0), 2 * major_axis, 2 * minor_axis, fill=False, color="red", linewidth=2)
    ax.add_artist(ellipse)
    ax.set_xlim(-major_axis - 1, major_axis + 1)
    ax.set_ylim(-minor_axis - 1, minor_axis + 1)
    ax.set_aspect('equal', 'box')
    ax.set_title(f"Ellipse (Major Axis={major_axis}, Minor Axis={minor_axis})")
    plt.grid(True)
    filepath = "ellipse_plot.png"
    plt.savefig(filepath)
    plt.close(fig)
    return filepath

def draw_polygon(sides: int, radius: float) -> str:
    if sides < 3:
        raise ValueError("A polygon must have at least 3 sides.")
    angles = np.linspace(0, 2 * np.pi, sides, endpoint=False)
    x = radius * np.cos(angles)
    y = radius * np.sin(angles)
    fig, ax = plt.subplots()
    ax.plot(np.append(x, x[0]), np.append(y, y[0]), color="orange", linewidth=2)
    ax.set_xlim(-radius - 1, radius + 1)
    ax.set_ylim(-radius - 1, radius + 1)
    ax.set_aspect('equal', 'box')
    ax.set_title(f"Polygon (Sides={sides}, Radius={radius})")
    plt.grid(True)
    filepath = "polygon_plot.png"
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
