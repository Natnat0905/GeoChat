# triangle.py

import matplotlib.pyplot as plt
import numpy as np
import math
import base64
import io

def generate_image(fig) -> str:
    """Convert matplotlib figure to base64 encoded PNG"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode('utf-8')

def draw_equilateral_triangle(side: float) -> str:
    """Generate equilateral triangle visualization"""
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Equilateral triangle vertices
    height = (math.sqrt(3) / 2) * side
    vertices = np.array([[0, 0], [side, 0], [side / 2, height], [0, 0]])

    # Plot triangle
    ax.plot(vertices[:, 0], vertices[:, 1], label=f'Side = {side} cm', color='b', lw=2)
    ax.fill(vertices[:, 0], vertices[:, 1], 'b', alpha=0.1)

    # Annotate the sides
    ax.text(side / 2, height / 2, f'{side} cm', ha='center', fontsize=10, color='r')

    ax.set_aspect('equal')
    ax.set_title("Equilateral Triangle Visualization", pad=20)
    ax.set_xlabel("Centimeters (cm)", labelpad=10)
    ax.set_ylabel("Centimeters (cm)", labelpad=10)
    ax.grid(True, linestyle='--', alpha=0.7)

    return generate_image(fig)

def draw_isosceles_triangle(base: float, equal_side: float) -> str:
    """Generate isosceles triangle visualization"""
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Isosceles triangle vertices
    height = math.sqrt(equal_side**2 - (base / 2)**2)
    vertices = np.array([[0, 0], [base, 0], [base / 2, height], [0, 0]])

    # Plot triangle
    ax.plot(vertices[:, 0], vertices[:, 1], label=f'Base = {base} cm, Side = {equal_side} cm', color='g', lw=2)
    ax.fill(vertices[:, 0], vertices[:, 1], 'g', alpha=0.1)

    # Annotate the sides
    ax.text(base / 2, height / 2, f'{equal_side} cm', ha='center', fontsize=10, color='r')

    ax.set_aspect('equal')
    ax.set_title("Isosceles Triangle Visualization", pad=20)
    ax.set_xlabel("Centimeters (cm)", labelpad=10)
    ax.set_ylabel("Centimeters (cm)", labelpad=10)
    ax.grid(True, linestyle='--', alpha=0.7)

    return generate_image(fig)

def draw_scalene_triangle(side1: float, side2: float, side3: float) -> str:
    """Generate scalene triangle visualization"""
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Using Heron's formula to calculate the height
    s = (side1 + side2 + side3) / 2  # semi-perimeter
    height = 2 * math.sqrt(s * (s - side1) * (s - side2) * (s - side3)) / side1

    # Scalene triangle vertices (simplified, can be adjusted for more accuracy)
    vertices = np.array([[0, 0], [side1, 0], [side2 / 2, height], [0, 0]])

    # Plot triangle
    ax.plot(vertices[:, 0], vertices[:, 1], label=f'Sides = {side1}, {side2}, {side3}', color='r', lw=2)
    ax.fill(vertices[:, 0], vertices[:, 1], 'r', alpha=0.1)

    # Annotate the sides
    ax.text(side2 / 4, height / 2, f'{side2} cm', ha='center', fontsize=10, color='b')

    ax.set_aspect('equal')
    ax.set_title("Scalene Triangle Visualization", pad=20)
    ax.set_xlabel("Centimeters (cm)", labelpad=10)
    ax.set_ylabel("Centimeters (cm)", labelpad=10)
    ax.grid(True, linestyle='--', alpha=0.7)

    return generate_image(fig)
