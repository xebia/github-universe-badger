"""
Generate block positions from the Xebia logo image.
This script runs on the PC to analyze the logo and create a data file
with the positions of blocks that should appear in the animation.
"""

from PIL import Image
import json

# Configuration
LOGO_FILE = "xebia-logo.png"
OUTPUT_FILE = "block_positions.json"
BLOCK_SIZE = 10
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 120

# Purple color threshold - stricter filtering
MIN_PURPLE_VALUE = 100  # Minimum red or blue value for purple
MIN_ALPHA = 200  # Minimum alpha (opacity)

def analyze_logo():
    """Analyze the logo image and determine block positions"""
    
    # Load the image
    img = Image.open(LOGO_FILE)
    img = img.convert("RGBA")  # Ensure we have alpha channel
    
    img_width, img_height = img.size
    print(f"Logo image size: {img_width}x{img_height}")
    
    # Center the logo on screen
    offset_x = (SCREEN_WIDTH - img_width) // 2
    offset_y = (SCREEN_HEIGHT - img_height) // 2
    print(f"Logo offset: ({offset_x}, {offset_y})")
    
    # Count purple pixels per grid cell
    grid_purple_counts = {}
    pixels = img.load()
    
    for y in range(img_height):
        for x in range(img_width):
            r, g, b, a = pixels[x, y]
            
            # Check if pixel is purple - stricter criteria
            is_purple = (a > MIN_ALPHA and  
                        (r > MIN_PURPLE_VALUE or b > MIN_PURPLE_VALUE) and
                        r + b > g * 2)
            
            if is_purple:
                # Calculate screen position
                screen_x = offset_x + x
                screen_y = offset_y + y
                
                # Calculate which grid cell this pixel belongs to
                grid_x = (screen_x // BLOCK_SIZE) * BLOCK_SIZE
                grid_y = (screen_y // BLOCK_SIZE) * BLOCK_SIZE
                
                # Count purple pixels in this grid cell
                key = (grid_x, grid_y)
                grid_purple_counts[key] = grid_purple_counts.get(key, 0) + 1
    
    # Only include grid cells that have at least 70% purple pixels
    min_purple_pixels = int(BLOCK_SIZE * BLOCK_SIZE * 0.7)
    block_positions = []
    
    for (grid_x, grid_y), count in grid_purple_counts.items():
        if count >= min_purple_pixels and 0 <= grid_x < SCREEN_WIDTH and 0 <= grid_y < SCREEN_HEIGHT:
            block_positions.append((grid_x, grid_y))
    
    block_positions.sort()
    
    print(f"Total purple pixels: {sum(grid_purple_counts.values())}")
    print(f"Grid cells with purple: {len(grid_purple_counts)}")
    print(f"Grid cells with >={min_purple_pixels} purple pixels: {len(block_positions)}")
    
    # Save to JSON file
    data = {
        "block_size": BLOCK_SIZE,
        "positions": block_positions,
        "image_size": [img_width, img_height],
        "offset": [offset_x, offset_y]
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f)
    
    print(f"Saved block positions to {OUTPUT_FILE}")
    print(f"Sample positions: {block_positions[:5]}")
    
    return block_positions

if __name__ == "__main__":
    analyze_logo()
