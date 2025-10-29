import sys
import os

sys.path.insert(0, "/system/apps/xebia")
os.chdir("/system/apps/xebia")

from badgeware import screen, shapes, brushes, io, run, Image
import random
import math
import json

# Screen dimensions
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 120

# Xebia purple color
XEBIA_PURPLE = (156, 39, 176)
# GitHub-style green colors (from dark to bright)
GREEN_COLORS = [
    (14, 68, 41),      # darkest
    (0, 109, 50),
    (38, 166, 65),
    (57, 211, 83),     # brightest
]
# Confetti colors - multicolored
CONFETTI_COLORS = [
    (255, 0, 0),       # red
    (255, 165, 0),     # orange
    (255, 255, 0),     # yellow
    (0, 255, 0),       # green
    (0, 127, 255),     # blue
    (148, 0, 211),     # purple
    (255, 20, 147),    # pink
]
BLACK = (0, 0, 0)
BLOCK_SIZE = 10

# Load the Xebia logo image
logo_image = Image.load("xebia-logo.png")

# Load block positions (precomputed on PC)
with open("block_positions.json", "r") as f:
    block_data = json.load(f)
    BLOCK_POSITIONS = block_data["positions"]

# Animation states
STATE_LOGO = 0
STATE_TRANSFORM = 1
STATE_RAIN = 2
STATE_AWARD = 3
STATE_CONFETTI = 4
STATE_HOLD = 5
STATE_FADEOUT = 6

# Timing
LOGO_FADEIN_DURATION = 30  # frames (~1 second for fade-in)
LOGO_DISPLAY_DURATION = 90  # frames (~3 seconds to display logo after fade-in)
TRANSFORM_DURATION = 40  # frames
RAIN_DURATION = 45  # frames
AWARD_DURATION = 30  # frames (~1 second)
CONFETTI_DURATION = 60  # frames per burst (~2 seconds)
CONFETTI_BURSTS = 3  # Number of confetti explosions
HOLD_DURATION = 60  # frames (~2 seconds)
FADEOUT_DURATION = 30  # frames

class Block:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.start_y = y
        self.color = color
        self.velocity = random.uniform(1.5, 3.5)
        self.fall_delay = random.randint(0, 20)
        self.falling = False
        
    def update(self):
        if self.fall_delay > 0:
            self.fall_delay -= 1
        else:
            self.falling = True
            self.y += self.velocity
            self.velocity += 0.1  # gravity
            
    def draw(self, alpha=255):
        if self.y < SCREEN_HEIGHT + BLOCK_SIZE:
            # Apply alpha to the color
            r, g, b = self.color
            screen.brush = brushes.color(r, g, b, alpha)
            screen.draw(shapes.rectangle(int(self.x), int(self.y), BLOCK_SIZE - 1, BLOCK_SIZE - 1))
            
    def is_offscreen(self):
        return self.y > SCREEN_HEIGHT + BLOCK_SIZE


class Confetti:
    def __init__(self, origin_x=None, origin_y=None):
        # Start from specified origin or default to center bottom
        if origin_x is None:
            origin_x = SCREEN_WIDTH / 2
        if origin_y is None:
            origin_y = SCREEN_HEIGHT - 10
            
        self.x = origin_x + random.uniform(-20, 20)
        self.y = origin_y
        
        # Shoot upward in radiating directions
        angle = random.uniform(-180, 0)  # Upward directions (degrees)
        speed = random.uniform(2, 5)
        self.velocity_x = math.cos(math.radians(angle)) * speed
        self.velocity_y = math.sin(math.radians(angle)) * speed
        
        self.color = random.choice(CONFETTI_COLORS)  # Multicolored
        self.size = random.randint(2, 4)
        self.lifetime = 0
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.15  # gravity pulls down
        self.lifetime += 1
        
    def draw(self, alpha=255):
        if 0 <= self.x < SCREEN_WIDTH and 0 <= self.y < SCREEN_HEIGHT:
            r, g, b = self.color
            screen.brush = brushes.color(r, g, b, alpha)
            screen.draw(shapes.rectangle(int(self.x), int(self.y), self.size, self.size))
            
    def is_offscreen(self):
        return self.y > SCREEN_HEIGHT or self.x < -10 or self.x > SCREEN_WIDTH + 10


class XebiaAnimation:
    def __init__(self):
        self.state = STATE_LOGO
        self.frame = 0
        self.blocks = []
        self.confetti = []
        self.confetti_burst_count = 0
        
    def create_blocks_from_logo(self):
        """Convert logo pixels to grid blocks using precomputed positions"""
        self.blocks = []
        
        # Use precomputed block positions
        for grid_x, grid_y in BLOCK_POSITIONS:
            # Randomly assign a green shade
            color = random.choice(GREEN_COLORS)
            self.blocks.append(Block(grid_x, grid_y, color))
    
    def create_confetti(self, origin_x=None, origin_y=None):
        """Create confetti particles from specified origin"""
        self.confetti = []
        for _ in range(50):
            self.confetti.append(Confetti(origin_x, origin_y))
    
    def draw_award_text(self, alpha=255):
        """Draw the award text in Xebia purple"""
        # Load a font (using the same as other apps)
        from badgeware import PixelFont
        small_font = PixelFont.load("/system/assets/fonts/nope.ppf")
        screen.font = small_font
        
        r, g, b = XEBIA_PURPLE
        screen.brush = brushes.color(r, g, b, alpha)
        
        # Text lines - bold years without checkmarks
        lines = [
            "GitHub overall",
            "partner of the year",
            "",
            "**2024**",
            "**2025**"
        ]
        
        y_start = 25
        line_height = 15
        
        for i, line in enumerate(lines):
            w, _ = screen.measure_text(line)
            x = (SCREEN_WIDTH - w) // 2
            y = y_start + i * line_height
            screen.text(line, x, y)
    
    def draw_logo(self, alpha=255):
        """Draw the Xebia logo from image with optional alpha"""
        # Center the logo
        img_width = logo_image.width
        img_height = logo_image.height
        offset_x = (SCREEN_WIDTH - img_width) // 2
        offset_y = (SCREEN_HEIGHT - img_height) // 2
        
        # Draw the image
        screen.blit(logo_image, offset_x, offset_y)
        
        # Apply fade by drawing black rectangle with inverse alpha
        if alpha < 255:
            screen.brush = brushes.color(0, 0, 0, 255 - alpha)
            screen.draw(shapes.rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def update(self):
        # Clear screen
        screen.brush = brushes.color(*BLACK)
        screen.draw(shapes.rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        if self.state == STATE_LOGO:
            # Fade in logo, then hold it
            if self.frame < LOGO_FADEIN_DURATION:
                # Fade in
                progress = self.frame / LOGO_FADEIN_DURATION
                logo_alpha = int(progress * 255)
                self.draw_logo(logo_alpha)
            else:
                # Display at full opacity
                self.draw_logo(255)
            
            self.frame += 1
            
            if self.frame >= LOGO_FADEIN_DURATION + LOGO_DISPLAY_DURATION:
                self.state = STATE_TRANSFORM
                self.frame = 0
                self.create_blocks_from_logo()
                
        elif self.state == STATE_TRANSFORM:
            # Cross-fade from logo to blocks
            progress = self.frame / TRANSFORM_DURATION
            
            # Logo fades out (255 -> 0)
            logo_alpha = int((1 - progress) * 255)
            # Blocks fade in (0 -> 255)
            blocks_alpha = int(progress * 255)
            
            # Draw logo fading out
            self.draw_logo(logo_alpha)
            
            # Draw blocks fading in
            for block in self.blocks:
                block.draw(blocks_alpha)
            
            self.frame += 1
            
            if self.frame >= TRANSFORM_DURATION:
                self.state = STATE_RAIN
                self.frame = 0
                
        elif self.state == STATE_RAIN:
            # Make blocks fall (full opacity)
            for block in self.blocks:
                block.update()
                block.draw(255)
            
            self.frame += 1
            
            # Check if all blocks are offscreen
            if all(block.is_offscreen() for block in self.blocks):
                # Move to award text
                self.state = STATE_AWARD
                self.frame = 0
                self.blocks = []
        
        elif self.state == STATE_AWARD:
            # Fade in award text
            progress = self.frame / AWARD_DURATION
            text_alpha = int(progress * 255)
            self.draw_award_text(text_alpha)
            self.frame += 1
            
            if self.frame >= AWARD_DURATION:
                self.state = STATE_CONFETTI
                self.frame = 0
                # First burst: lower left corner
                self.create_confetti(origin_x=10, origin_y=SCREEN_HEIGHT - 10)
        
        elif self.state == STATE_CONFETTI:
            # Show award text with confetti
            self.draw_award_text(255)
            
            # Update and draw confetti
            for confetto in self.confetti:
                confetto.update()
                confetto.draw(255)
            
            self.frame += 1
            
            if self.frame >= CONFETTI_DURATION:
                self.confetti_burst_count += 1
                
                # Check if we've done all bursts
                if self.confetti_burst_count >= CONFETTI_BURSTS:
                    # Move to hold state
                    self.state = STATE_HOLD
                    self.frame = 0
                    self.confetti = []
                else:
                    # Create another burst of confetti with different origin
                    self.frame = 0
                    if self.confetti_burst_count == 1:
                        # Second burst: lower right corner
                        self.create_confetti(origin_x=SCREEN_WIDTH - 10, origin_y=SCREEN_HEIGHT - 10)
                    elif self.confetti_burst_count == 2:
                        # Third burst: lower center
                        self.create_confetti(origin_x=SCREEN_WIDTH / 2, origin_y=SCREEN_HEIGHT - 10)
        
        elif self.state == STATE_HOLD:
            # Hold the text on screen for 2 more seconds
            self.draw_award_text(255)
            self.frame += 1
            
            if self.frame >= HOLD_DURATION:
                self.state = STATE_FADEOUT
                self.frame = 0
        
        elif self.state == STATE_FADEOUT:
            # Fade out award text
            progress = self.frame / FADEOUT_DURATION
            alpha = int((1 - progress) * 255)
            
            self.draw_award_text(alpha)
            
            self.frame += 1
            
            if self.frame >= FADEOUT_DURATION:
                # Reset animation
                self.state = STATE_LOGO
                self.frame = 0
                self.confetti_burst_count = 0


animation = XebiaAnimation()


def update():
    # Check if any button is pressed to return to menu
    if io.pressed:
        return False
    
    animation.update()
    return None


if __name__ == "__main__":
    run(update)
