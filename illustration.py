import matplotlib.pyplot as plt
import numpy as np
import logging

def draw_circle(radius: float) -> str:
    """
    Draw a circle based on the provided radius.
    """
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

def draw_right_triangle(leg_a: float, leg_b: float) -> str:
    """
    Draw a right triangle with two legs: leg_a (x-axis) and leg_b (y-axis).
    """
    fig, ax = plt.subplots()
    points = np.array([[0, 0], [leg_a, 0], [0, leg_b]])
    triangle = plt.Polygon(points, fill=None, edgecolor="purple", linewidth=2)
    ax.add_patch(triangle)

    ax.set_xlim(-1, leg_a + 1)
    ax.set_ylim(-1, leg_b + 1)
    ax.set_aspect("equal", "box")
    ax.set_title(f"Right Triangle (Leg A={leg_a}, Leg B={leg_b})")
    plt.grid(True)

    filepath = "right_triangle_plot.png"
    plt.savefig(filepath)
    plt.close(fig)
    return filepath


def draw_generic_triangle(side_a: float, side_b: float, side_c: float) -> str:
    """
    Draw a generic triangle based on three side lengths (side_a, side_b, side_c).
    Validates the Triangle Inequality Theorem before plotting.
    """
    # Validate Triangle Inequality Theorem
    if (
        side_a + side_b <= side_c
        or side_a + side_c <= side_b
        or side_b + side_c <= side_a
    ):
        raise ValueError(
            "Invalid side lengths: Triangle Inequality Theorem violated. Cannot plot the triangle."
        )

    # Calculate approximate triangle vertices
    x1, y1 = 0, 0
    x2, y2 = side_a, 0
    x3 = (side_a**2 + side_b**2 - side_c**2) / (2 * side_a)
    y3 = np.sqrt(side_b**2 - x3**2)

    fig, ax = plt.subplots()
    points = np.array([[x1, y1], [x2, y2], [x3, y3]])
    triangle = plt.Polygon(points, fill=None, edgecolor="purple", linewidth=2)
    ax.add_patch(triangle)

    ax.set_xlim(-1, max(x2, x3) + 1)
    ax.set_ylim(-1, y3 + 1)
    ax.set_aspect("equal", "box")
    ax.set_title("Triangle")
    plt.grid(True)

    filepath = "generic_triangle_plot.png"
    plt.savefig(filepath)
    plt.close(fig)
    return filepath

def draw_rectangle(width: float, height: float) -> str:
    """
    Draw a rectangle based on the provided width and height.
    """
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

def plot_trigonometric_function(function: str) -> str:
    """
    Plot a trigonometric function such as sine, cosine, or tangent.
    """
    x = np.linspace(0, 2 * np.pi, 500)
    if function == "sin":
        y = np.sin(x)
        title, label = "Sine Function", "sin(x)"
    elif function == "cos":
        y = np.cos(x)
        title, label = "Cosine Function", "cos(x)"
    elif function == "tan":
        y = np.tan(x)
        y[np.abs(y) > 10] = np.nan  # Avoid asymptotes
        title, label = "Tangent Function", "tan(x)"
    else:
        raise ValueError("Unsupported function for plotting")

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
