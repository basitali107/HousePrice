# floor_map/services/generator.py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, FancyBboxPatch
from io import BytesIO
import base64
import math

def generate_floor_plan(data):
    """
    Generate a realistic floor plan based on input data
    """
    try:
        # Extract and validate data
        total_area = int(data.get('total_area', 1000))
        bedrooms = int(data.get('bedrooms', 2))
        bathrooms = int(data.get('bathrooms', 1))
        
        # Create figure with better size
        fig, ax = plt.subplots(figsize=(14, 12))
        ax.set_facecolor('#f5f5f5')
        
        # Calculate dimensions (roughly square layout)
        side_length = math.sqrt(total_area)
        width = side_length * 1.3  # Make it slightly rectangular
        height = total_area / width
        
        # Room allocation (percentage of total area)
        room_data = calculate_room_sizes(total_area, bedrooms, bathrooms)
        
        # Create layout
        rooms = create_room_layout(room_data, width, height, bedrooms, bathrooms)
        
        # Draw outer walls
        outer_wall = FancyBboxPatch(
            (0, 0), width, height,
            boxstyle="round,pad=0.1",
            linewidth=4,
            edgecolor='#2c3e50',
            facecolor='white',
            zorder=1
        )
        ax.add_patch(outer_wall)
        
        # Draw each room
        for room in rooms:
            draw_room(ax, room)
        
        # Add doors
        add_doors(ax, rooms, width, height)
        
        # Add dimensions
        add_dimensions(ax, width, height, total_area)
        
        # Set plot properties
        margin = max(width, height) * 0.1
        ax.set_xlim(-margin, width + margin)
        ax.set_ylim(-margin, height + margin)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Add title and legend
        title = f'Floor Plan Design\n{total_area} sq ft | {bedrooms} Bedroom(s) | {bathrooms} Bathroom(s)'
        plt.title(title, fontsize=18, fontweight='bold', pad=20, color='#2c3e50')
        
        # Add compass rose
        add_compass_rose(ax, width, height, margin)
        
        # Save to base64
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
    
    except Exception as e:
        plt.close('all')
        raise Exception(f"Error generating floor plan: {str(e)}")


def calculate_room_sizes(total_area, bedrooms, bathrooms):
    """Calculate size allocation for each room type"""
    # Typical percentages
    living_percent = 0.25
    kitchen_percent = 0.15
    bedroom_percent = 0.40 / bedrooms  # Share 40% among bedrooms
    bathroom_percent = 0.10 / bathrooms  # Share 10% among bathrooms
    hallway_percent = 0.10
    
    return {
        'living': total_area * living_percent,
        'kitchen': total_area * kitchen_percent,
        'bedroom': total_area * bedroom_percent,
        'bathroom': total_area * bathroom_percent,
        'hallway': total_area * hallway_percent
    }


def create_room_layout(room_data, width, height, bedrooms, bathrooms):
    """Create a realistic room layout"""
    rooms = []
    
    # Calculate column widths (3 columns)
    col1_width = width * 0.35
    col2_width = width * 0.30
    col3_width = width * 0.35
    
    # Row heights
    row_height = height / 3
    
    # Living Room (bottom left, large)
    rooms.append({
        'type': 'Living Room',
        'x': 0,
        'y': 0,
        'width': col1_width + col2_width,
        'height': row_height * 1.5,
        'color': '#e8f5e9',
        'furniture': ['sofa', 'tv']
    })
    
    # Kitchen (top left)
    rooms.append({
        'type': 'Kitchen',
        'x': 0,
        'y': row_height * 1.5,
        'width': col1_width,
        'height': row_height * 1.5,
        'color': '#fff3e0',
        'furniture': ['counter', 'stove']
    })
    
    # Dining Area (top middle)
    rooms.append({
        'type': 'Dining',
        'x': col1_width,
        'y': row_height * 1.5,
        'width': col2_width,
        'height': row_height * 1.5,
        'color': '#fce4ec',
        'furniture': ['table']
    })
    
    # Bedrooms (right side)
    bedroom_height = (height * 0.9) / bedrooms
    for i in range(bedrooms):
        rooms.append({
            'type': f'Bedroom {i+1}',
            'x': col1_width + col2_width,
            'y': i * bedroom_height,
            'width': col3_width,
            'height': bedroom_height,
            'color': '#e3f2fd',
            'furniture': ['bed', 'closet']
        })
    
    # Bathrooms (bottom right corners)
    bathroom_width = col3_width * 0.45
    bathroom_height = row_height * 0.6
    for i in range(bathrooms):
        if i == 0:
            # First bathroom bottom right
            rooms.append({
                'type': f'Bath {i+1}',
                'x': width - bathroom_width,
                'y': 0,
                'width': bathroom_width,
                'height': bathroom_height,
                'color': '#f3e5f5',
                'furniture': ['toilet', 'sink']
            })
        else:
            # Additional bathrooms
            rooms.append({
                'type': f'Bath {i+1}',
                'x': col1_width + col2_width,
                'y': height - bathroom_height,
                'width': bathroom_width,
                'height': bathroom_height,
                'color': '#f3e5f5',
                'furniture': ['toilet', 'sink']
            })
    
    return rooms


def draw_room(ax, room):
    """Draw a single room with details"""
    # Room rectangle
    rect = FancyBboxPatch(
        (room['x'], room['y']),
        room['width'],
        room['height'],
        boxstyle="round,pad=0.02",
        linewidth=2,
        edgecolor='#34495e',
        facecolor=room['color'],
        alpha=0.7,
        zorder=2
    )
    ax.add_patch(rect)
    
    # Room label
    center_x = room['x'] + room['width'] / 2
    center_y = room['y'] + room['height'] / 2
    
    ax.text(center_x, center_y, room['type'],
           ha='center', va='center',
           fontsize=11, fontweight='bold',
           color='#2c3e50',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                    edgecolor='none', alpha=0.8),
           zorder=3)
    
    # Add furniture symbols
    draw_furniture(ax, room)
    
    # Add room dimensions
    dim_text = f"{room['width']:.1f}' × {room['height']:.1f}'"
    ax.text(center_x, room['y'] + room['height'] * 0.15, dim_text,
           ha='center', va='center',
           fontsize=8, color='#7f8c8d', style='italic',
           zorder=3)


def draw_furniture(ax, room):
    """Add simple furniture symbols to rooms"""
    furniture = room.get('furniture', [])
    x, y, w, h = room['x'], room['y'], room['width'], room['height']
    
    for item in furniture:
        if item == 'bed':
            # Draw bed
            bed_w, bed_h = w * 0.4, h * 0.5
            bed = Rectangle((x + w * 0.3, y + h * 0.25), bed_w, bed_h,
                          facecolor='#b39ddb', edgecolor='#7e57c2',
                          linewidth=2, zorder=3)
            ax.add_patch(bed)
            
        elif item == 'sofa':
            # Draw sofa
            sofa_w, sofa_h = w * 0.35, h * 0.15
            sofa = Rectangle((x + w * 0.1, y + h * 0.2), sofa_w, sofa_h,
                           facecolor='#90a4ae', edgecolor='#546e7a',
                           linewidth=2, zorder=3)
            ax.add_patch(sofa)
            
        elif item == 'table':
            # Draw dining table
            table_w, table_h = w * 0.4, h * 0.3
            table = Rectangle((x + w * 0.3, y + h * 0.35), table_w, table_h,
                            facecolor='#a1887f', edgecolor='#6d4c41',
                            linewidth=2, zorder=3)
            ax.add_patch(table)
            
        elif item == 'counter':
            # Draw kitchen counter
            counter_w, counter_h = w * 0.7, h * 0.15
            counter = Rectangle((x + w * 0.15, y + h * 0.1), counter_w, counter_h,
                              facecolor='#ffab91', edgecolor='#e64a19',
                              linewidth=2, zorder=3)
            ax.add_patch(counter)
            
        elif item == 'toilet':
            # Draw toilet symbol
            toilet = plt.Circle((x + w * 0.3, y + h * 0.6), w * 0.12,
                              facecolor='white', edgecolor='#9e9e9e',
                              linewidth=2, zorder=3)
            ax.add_patch(toilet)
            
        elif item == 'sink':
            # Draw sink
            sink = Rectangle((x + w * 0.6, y + h * 0.7), w * 0.25, h * 0.15,
                           facecolor='#e0f7fa', edgecolor='#00acc1',
                           linewidth=2, zorder=3)
            ax.add_patch(sink)


def add_doors(ax, rooms, width, height):
    """Add door symbols between rooms"""
    door_length = min(width, height) * 0.08
    
    # Main entrance (bottom center)
    door_x = width / 2
    door = Rectangle((door_x - door_length/2, -0.1), door_length, 0.3,
                    facecolor='#8d6e63', edgecolor='#5d4037',
                    linewidth=2, zorder=4)
    ax.add_patch(door)
    ax.text(door_x, -0.5, 'ENTRY', ha='center', fontsize=9,
           fontweight='bold', color='#5d4037')


def add_dimensions(ax, width, height, total_area):
    """Add dimension lines and measurements"""
    # Width dimension (bottom)
    y_offset = -1.5
    ax.plot([0, width], [y_offset, y_offset], 'k-', linewidth=1)
    ax.plot([0, 0], [y_offset-0.2, y_offset+0.2], 'k-', linewidth=1)
    ax.plot([width, width], [y_offset-0.2, y_offset+0.2], 'k-', linewidth=1)
    ax.text(width/2, y_offset-0.5, f"{width:.1f} ft",
           ha='center', fontsize=9, color='#2c3e50')
    
    # Height dimension (left)
    x_offset = -1.5
    ax.plot([x_offset, x_offset], [0, height], 'k-', linewidth=1)
    ax.plot([x_offset-0.2, x_offset+0.2], [0, 0], 'k-', linewidth=1)
    ax.plot([x_offset-0.2, x_offset+0.2], [height, height], 'k-', linewidth=1)
    ax.text(x_offset-0.5, height/2, f"{height:.1f} ft",
           ha='center', va='center', rotation=90, fontsize=9, color='#2c3e50')


def add_compass_rose(ax, width, height, margin):
    """Add a compass rose to the floor plan"""
    compass_x = width + margin * 0.5
    compass_y = height + margin * 0.5
    compass_size = margin * 0.3
    
    # North arrow
    ax.annotate('', xy=(compass_x, compass_y + compass_size),
               xytext=(compass_x, compass_y),
               arrowprops=dict(arrowstyle='->', lw=2, color='#e74c3c'))
    ax.text(compass_x, compass_y + compass_size + 0.5, 'N',
           ha='center', fontsize=12, fontweight='bold', color='#e74c3c')
    
    # Draw circle
    circle = plt.Circle((compass_x, compass_y), compass_size * 0.3,
                       fill=False, edgecolor='#95a5a6', linewidth=1.5)
    ax.add_patch(circle)