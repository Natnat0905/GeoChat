import matplotlib.pyplot as plt
import numpy as np
import io
import math
from typing import Dict, Any, Optional, Tuple
import base64  # Added missing import

def generate_image(fig) -> str:
    """Convert matplotlib figure to base64 encoded PNG"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode('utf-8')  # Add data URI prefix


def draw_right_triangle(leg1: float, leg2: float) -> str:
    """Generate right-angled triangle with educational annotations"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Triangle vertices
    vertices = np.array([[0, 0], [leg1, 0], [0, leg2], [0, 0]])
    
    # Plot triangle
    ax.plot(vertices[:, 0], vertices[:, 1], 'o-', color='#9467bd', linewidth=2.5)
    
    # Add measurements
    ax.text(leg1/2, -0.1*leg2, f'{leg1} cm', ha='center', va='top', color='#2ca02c')
    ax.text(-0.1*leg1, leg2/2, f'{leg2} cm', ha='right', va='center', rotation=90, color='#2ca02c')
    
    # Calculate and annotate hypotenuse
    hypotenuse = np.hypot(leg1, leg2)
    ax.text(leg1/2, leg2/2, f'√({leg1}² + {leg2}²)\n≈ {hypotenuse:.1f} cm', 
           ha='center', va='center', color='#d62728')
    
    # Add proof visualization
    ax.text(0.5, -1.2, 
           f"Pythagorean Proof:\n{leg1}² + {leg2}² = {leg1**2 + leg2**2}\n"
           f"∴ c = √{leg1**2 + leg2**2} ≈ {hypotenuse:.2f}",
           bbox=dict(boxstyle="round", fc="#f0f8ff", ec="#4682b4"))
    
    # Configure plot
    ax.set_xlim(-0.5, max(leg1, 3) + 1)
    ax.set_ylim(-0.5, max(leg2, 3) + 1)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_title(f"Right-Angled Triangle Visualization\n(Legs: {leg1} cm & {leg2} cm)", pad=15)
    ax.set_xlabel("Centimeters (cm)", labelpad=10)
    ax.set_ylabel("Centimeters (cm)", labelpad=10)
    
    # Add right angle indicator
    ax.add_patch(plt.Rectangle((0, 0), 0.4, 0.4, 
                             fill=True, color='#ff7f0e', alpha=0.3))
    
    return generate_image(fig)

def plot_trigonometric_function(function: str) -> str:
    """Generate trigonometric function plot with educational annotations"""
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.linspace(0, 2*np.pi, 1000)
    
    functions = {
        'sin': {'color': '#1f77b4', 'label': 'Sine'},
        'cos': {'color': '#ff7f0e', 'label': 'Cosine'},
        'tan': {'color': '#2ca02c', 'label': 'Tangent'}
    }
    
    if function not in functions:
        raise ValueError("Unsupported trigonometric function")
    
    cfg = functions[function]
    y = getattr(np, function)(x)
    
    if function == 'tan':
        y[np.abs(y) > 5] = np.nan  # Handle asymptotes
    
    ax.plot(x, y, color=cfg['color'], lw=2, label=cfg['label'])
    
    # Configure plot
    ax.set_title(f"{cfg['label']} Function Analysis", pad=20, fontsize=14)
    ax.set_xlabel("Angle (radians)", fontsize=12)
    ax.set_ylabel("Function Value", fontsize=12)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xticks(np.arange(0, 2.1*np.pi, np.pi/2))
    ax.set_xticklabels(['0', 'π/2', 'π', '3π/2', '2π'])
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    
    return generate_image(fig)

def draw_equilateral_triangle(side: float) -> str:
    """Draw an equilateral triangle with a given side length."""
    height = (math.sqrt(3) / 2) * side
    fig, ax = plt.subplots()
    
    # Triangle vertices
    vertices = np.array([
        [0, 0], [side, 0], [side/2, height], [0, 0]
    ])
    
    ax.plot(vertices[:, 0], vertices[:, 1], 'o-', color='blue', linewidth=2.5)
    ax.set_title(f"Equilateral Triangle (Side: {side} cm)")
    
    return generate_image(fig)

def draw_isosceles_triangle(base: float, equal_side: float) -> str:
    """Draw an isosceles triangle with a base and two equal sides."""
    height = math.sqrt(equal_side**2 - (base/2)**2)
    fig, ax = plt.subplots()
    
    vertices = np.array([
        [0, 0], [base, 0], [base/2, height], [0, 0]
    ])
    
    ax.plot(vertices[:, 0], vertices[:, 1], 'o-', color='green', linewidth=2.5)
    ax.set_title(f"Isosceles Triangle (Base: {base} cm, Side: {equal_side} cm)")
    
    return generate_image(fig)

def draw_scalene_triangle(side1: float, side2: float, side3: float) -> str:
    """Draw a scalene triangle given three side lengths."""
    fig, ax = plt.subplots()
    
    vertices = np.array([
        [0, 0], [side1, 0], [side1 / 2, side2], [0, 0]
    ])
    
    ax.plot(vertices[:, 0], vertices[:, 1], 'o-', color='red', linewidth=2.5)
    ax.set_title(f"Scalene Triangle (Sides: {side1}, {side2}, {side3} cm)")
    
    return generate_image(fig)