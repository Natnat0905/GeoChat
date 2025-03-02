import matplotlib.pyplot as plt
import numpy as np
import io
import math
from typing import Tuple
import base64  # Added missing import

def generate_image(fig) -> str:
    """Convert matplotlib figure to base64 encoded PNG"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode('utf-8')  # Add data URI prefix

def draw_circle(radius: float) -> str:
    """Generate circle visualization with educational annotations"""
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Create circle
    circle = plt.Circle((0, 0), radius, fill=False, color='#1f77b4', linewidth=2.5)
    ax.add_artist(circle)
    
    # Add radius annotation
    ax.annotate(f'r = {radius} cm', xy=(0, 0), xytext=(0, radius/2),
               arrowprops=dict(arrowstyle="->", color='#2ca02c'),
               ha='center', fontsize=10)
    
    # Add practical applications
    ax.text(radius*1.1, 0, 
           "Practical Measurements:\n"
           f"- Wheel rotation: {radius*2*math.pi:.1f}cm/rev\n"
           f"- Pizza area: {math.pi*radius**2:.1f}cm²",
           fontsize=9)
    
    # Configure plot
    ax.set_xlim(-radius*1.2, radius*1.2)
    ax.set_ylim(-radius*1.2, radius*1.2)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_title(f"Circle Visualization (Radius: {radius} cm)", pad=20)
    ax.set_xlabel("Centimeters (cm)", labelpad=10)
    ax.set_ylabel("Centimeters (cm)", labelpad=10)
    
    return generate_image(fig)

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

def draw_rectangle(width: float, height: float) -> str:
    """Generate rectangle/square visualization with educational annotations"""
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Create rectangle
    rect = plt.Rectangle((0, 0), width, height, fill=False, color='#17becf', linewidth=2.5)
    ax.add_patch(rect)
    
    # Add measurements
    ax.text(width/2, -0.1*height, f'Width: {width} cm', ha='center', va='top', color='#2ca02c')
    ax.text(-0.1*width, height/2, f'Height: {height} cm', ha='right', va='center', rotation=90, color='#2ca02c')
    
    # Add area calculation
    ax.text(width/2, height/2, f'Area = {width} × {height}\n= {width*height} cm²', 
           ha='center', va='center', bbox=dict(boxstyle="round", fc="#f0f8ff", ec="#4682b4"))
    
    # Configure plot
    ax.set_xlim(-1, width + 1)
    ax.set_ylim(-1, height + 1)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_title(f"Rectangle Visualization ({width} cm × {height} cm)", pad=15)
    ax.set_xlabel("Centimeters (cm)", labelpad=10)
    ax.set_ylabel("Centimeters (cm)", labelpad=10)
    
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