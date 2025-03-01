# illustration.py
import matplotlib.pyplot as plt
import numpy as np
import io
from typing import Tuple

# Base image generation function
def generate_image(fig) -> bytes:
    """Convert matplotlib figure to PNG bytes"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()

def draw_circle(radius: float) -> bytes:
    """Generate circle visualization with measurement annotations"""
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Create circle
    circle = plt.Circle((0, 0), radius, fill=False, 
                       color='#1f77b4', linewidth=2.5)
    ax.add_artist(circle)
    
    # Add radius annotation
    ax.annotate(f'r = {radius} cm', xy=(0, 0), xytext=(0, radius/2),
               arrowprops=dict(arrowstyle="->", color='#2ca02c'),
               ha='center', fontsize=10)
    
    # Configure plot
    ax.set_xlim(-radius*1.2, radius*1.2)
    ax.set_ylim(-radius*1.2, radius*1.2)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_title(f"Circle Visualization (Radius: {radius} cm)", pad=20)
    ax.set_xlabel("Centimeters (cm)", labelpad=10)
    ax.set_ylabel("Centimeters (cm)", labelpad=10)
    
    return generate_image(fig)

def draw_right_triangle(leg1: float, leg2: float) -> bytes:
    """Generate right-angled triangle with proper annotation"""
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Create triangle vertices
    vertices = np.array([
        [0, 0],         # Right angle
        [leg1, 0],      # Horizontal leg
        [0, leg2],      # Vertical leg
        [0, 0]          # Close shape
    ])
    
    # Plot triangle
    ax.plot(vertices[:, 0], vertices[:, 1], 
           color='#9467bd', linewidth=2.5, marker='o')
    
    # Add measurements
    ax.text(leg1/2, -0.1*leg2, f'{leg1} cm', 
           ha='center', va='top', color='#2ca02c')
    ax.text(-0.1*leg1, leg2/2, f'{leg2} cm', 
           ha='right', va='center', rotation=90, color='#2ca02c')
    
    # Calculate and annotate hypotenuse
    hypotenuse = np.hypot(leg1, leg2)
    ax.text(leg1/2, leg2/2, f'√({leg1}² + {leg2}²)\n≈ {hypotenuse:.1f} cm', 
           ha='center', va='center', color='#d62728')
    
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

def draw_rectangle(width: float, height: float) -> bytes:
    """Generate rectangle visualization with area calculation"""
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Create rectangle
    rect = plt.Rectangle((0, 0), width, height, 
                        fill=False, color='#17becf', linewidth=2.5)
    ax.add_patch(rect)
    
    # Add measurements
    ax.text(width/2, -0.1*height, f'Width: {width} cm', 
           ha='center', va='top', color='#2ca02c')
    ax.text(-0.1*width, height/2, f'Height: {height} cm', 
           ha='right', va='center', rotation=90, color='#2ca02c')
    ax.text(width/2, height/2, f'Area: {width*height} cm²', 
           ha='center', va='center', color='#d62728')
    
    # Configure plot
    ax.set_xlim(-1, width + 1)
    ax.set_ylim(-1, height + 1)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_title(f"Rectangle Visualization ({width} cm × {height} cm)", pad=15)
    ax.set_xlabel("Centimeters (cm)", labelpad=10)
    ax.set_ylabel("Centimeters (cm)", labelpad=10)
    
    return generate_image(fig)

def plot_trigonometric_function(function: str) -> bytes:
    """Generate trigonometric function plot with key features"""
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.linspace(0, 2*np.pi, 1000)
    
    # Configure function parameters
    config = {
        'sin': {'color': '#1f77b4', 'label': 'Sine', 'text_pos': (3*np.pi/2, -0.9)},
        'cos': {'color': '#ff7f0e', 'label': 'Cosine', 'text_pos': (np.pi, -0.9)},
        'tan': {'color': '#2ca02c', 'label': 'Tangent', 'text_pos': (3*np.pi/4, 0)}
    }
    
    # Handle different functions
    if function.lower() in config:
        cfg = config[function.lower()]
        y = getattr(np, function.lower())(x)
        
        if function.lower() == 'tan':
            y[np.abs(y) > 5] = np.nan  # Remove asymptotes
            
        ax.plot(x, y, color=cfg['color'], label=cfg['label'], linewidth=2)
        ax.text(*cfg['text_pos'], f"{cfg['label']} Function", 
               color=cfg['color'], fontsize=12, ha='center')
    else:
        raise ValueError(f"Unsupported function: {function}")
    
    # Configure plot
    ax.set_title(f"{config[function.lower()]['label']} Function (0 to 2π)", pad=15)
    ax.set_xlabel("Angle (radians)", labelpad=10)
    ax.set_ylabel("Value", labelpad=10)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xticks(np.arange(0, 2.1*np.pi, np.pi/2))
    ax.set_xticklabels(['0', 'π/2', 'π', '3π/2', '2π'])
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_ylim(-1.2, 1.2) if function in ['sin', 'cos'] else None
    
    return generate_image(fig)

def draw_generic_triangle(sides: Tuple[float, float, float]) -> bytes:
    """Generate any valid triangle visualization with angle information"""
    a, b, c = sorted(sides)
    if not (a + b > c):
        raise ValueError("Invalid triangle dimensions")
    
    # Calculate coordinates using Law of Cosines
    x = (a**2 - b**2 + c**2) / (2*c)
    y = np.sqrt(a**2 - x**2)
    
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Plot triangle
    points = np.array([[0, 0], [c, 0], [x, y], [0, 0]])
    ax.plot(points[:, 0], points[:, 1], 
           color='#e377c2', linewidth=2.5, marker='o')
    
    # Add side labels
    ax.text(c/2, -0.1*y, f'{c} cm', ha='center', va='top', color='#2ca02c')
    ax.text(x/2, y/2, f'{a} cm', ha='right', va='center', color='#2ca02c')
    ax.text((c+x)/2, y/2, f'{b} cm', ha='left', va='center', color='#2ca02c')
    
    # Configure plot
    ax.set_xlim(-1, c + 1)
    ax.set_ylim(-1, y + 1)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_title(f"Triangle with Sides: {a} cm, {b} cm, {c} cm", pad=15)
    ax.set_xlabel("Centimeters (cm)", labelpad=10)
    ax.set_ylabel("Centimeters (cm)", labelpad=10)
    
    return generate_image(fig)