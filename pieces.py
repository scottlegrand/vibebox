import pygame
import math
import random
from config import *

class ArtilleryPiece:
    def __init__(self, game, x, y, piece_type):
        self.game = game
        self.x = x
        self.y = y
        self.piece_type = piece_type
        
        # Define firing directions based on piece type
        if piece_type == HORIZONTAL:
            # Cardinal directions (up, right, down, left)
            self.directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        elif piece_type == DIAGONAL:
            # Diagonal directions (up-right, down-right, down-left, up-left)
            self.directions = [(1, -1), (1, 1), (-1, 1), (-1, -1)]
        else:
            # Default to horizontal if unknown type
            self.directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        self.base_color = GREEN if piece_type == HORIZONTAL else RED
        self.highlight_color = tuple(min(c + 50, 255) for c in self.base_color)
        self.shadow_color = tuple(max(c - 50, 0) for c in self.base_color)
        self.radius = CELL_SIZE // 3  # Main piece radius
        self.turret_radius = CELL_SIZE // 6  # Central turret radius
        self.barrel_radius = CELL_SIZE // 12  # Smaller barrel radius
        self.barrel_offset = CELL_SIZE // 5  # Distance from center to barrel centers
        
    def draw(self, surface):
        center_x = self.x + CELL_SIZE // 2
        center_y = self.y + CELL_SIZE // 2
        
        # Draw main base shadow
        pygame.draw.circle(surface, self.shadow_color, 
                         (center_x + 2, center_y + 2), self.radius)
        
        # Draw main base
        pygame.draw.circle(surface, self.base_color, 
                         (center_x, center_y), self.radius)
        
        # Draw main base highlight
        highlight_radius = self.radius * 3 // 4
        pygame.draw.circle(surface, self.highlight_color, 
                         (center_x - 2, center_y - 2), highlight_radius)
        
        # Draw central turret shadow
        pygame.draw.circle(surface, self.shadow_color,
                         (center_x + 1, center_y + 1), self.turret_radius)
        
        # Draw central turret
        pygame.draw.circle(surface, self.base_color,
                         (center_x, center_y), self.turret_radius)
        
        # Draw turret highlight
        pygame.draw.circle(surface, self.highlight_color,
                         (center_x - 1, center_y - 1), self.turret_radius // 2)
        
        # Draw barrels
        barrel_color = (200, 200, 200)  # Silver color
        barrel_interior = (50, 50, 50)  # Dark interior
        
        for dx, dy in self.directions:
            # Calculate barrel position
            barrel_x = center_x + dx * self.barrel_offset
            barrel_y = center_y + dy * self.barrel_offset
            
            # Draw barrel shadow
            pygame.draw.circle(surface, (100, 100, 100),
                             (barrel_x + 1, barrel_y + 1), self.barrel_radius)
            
            # Draw barrel
            pygame.draw.circle(surface, barrel_color,
                             (barrel_x, barrel_y), self.barrel_radius)
            
            # Draw barrel interior
            pygame.draw.circle(surface, barrel_interior,
                             (barrel_x, barrel_y), self.barrel_radius // 2)

class Target:
    def __init__(self, scene, x, y):
        self.scene = scene
        self.x = x
        self.y = y
        self.radius = CELL_SIZE // 3
        
    def draw(self, surface):
        center_x = self.x + CELL_SIZE // 2
        center_y = self.y + CELL_SIZE // 2
        
        # Draw outer ring shadow
        pygame.draw.circle(surface, (180, 0, 0), 
                         (center_x + 2, center_y + 2), self.radius)
        
        # Draw outer ring
        pygame.draw.circle(surface, RED, 
                         (center_x, center_y), self.radius)
        
        # Draw middle ring shadow
        pygame.draw.circle(surface, (220, 220, 220), 
                         (center_x + 2, center_y + 2), self.radius * 2 // 3)
        
        # Draw middle ring
        pygame.draw.circle(surface, WHITE, 
                         (center_x, center_y), self.radius * 2 // 3)
        
        # Draw inner ring shadow
        pygame.draw.circle(surface, (180, 0, 0), 
                         (center_x + 1, center_y + 1), self.radius // 3)
        
        # Draw inner ring
        pygame.draw.circle(surface, RED, 
                         (center_x, center_y), self.radius // 3)
        
        # Draw highlight
        highlight_radius = self.radius // 4
        pygame.draw.circle(surface, (255, 100, 100), 
                         (center_x - 2, center_y - 2), highlight_radius)

class Monolith:
    def __init__(self, scene, x, y):
        self.scene = scene
        self.x = x
        self.y = y
        self.width = CELL_SIZE * 2 // 3
        self.height = CELL_SIZE * 2 // 3  # Make it more square
        self.wall_thickness = CELL_SIZE // 8
        
    def draw(self, surface):
        # Calculate base position (centered in the cell)
        base_x = self.x + (CELL_SIZE - self.width) // 2
        base_y = self.y + (CELL_SIZE - self.height) // 2
        
        # Draw shadow
        shadow_rect = pygame.Rect(
            base_x + 3,
            base_y + 3,
            self.width,
            self.height
        )
        pygame.draw.rect(surface, (70, 70, 70), shadow_rect)
        
        # Draw main structure
        main_rect = pygame.Rect(
            base_x,
            base_y,
            self.width,
            self.height
        )
        pygame.draw.rect(surface, (100, 100, 100), main_rect)
        
        # Draw highlight
        highlight_rect = pygame.Rect(
            base_x + 2,
            base_y + 2,
            self.width - 4,
            10
        )
        pygame.draw.rect(surface, (130, 130, 130), highlight_rect)
        
        # Draw walls
        wall_color = (80, 80, 80)
        wall_highlight = (110, 110, 110)
        wall_shadow = (50, 50, 50)
        
        # Draw front wall
        front_wall = pygame.Rect(
            base_x + self.wall_thickness,
            base_y + self.wall_thickness,
            self.width - 2 * self.wall_thickness,
            self.height - self.wall_thickness
        )
        pygame.draw.rect(surface, wall_color, front_wall)
        
        # Draw side walls
        left_wall = pygame.Rect(
            base_x,
            base_y + self.wall_thickness,
            self.wall_thickness,
            self.height - self.wall_thickness
        )
        pygame.draw.rect(surface, wall_shadow, left_wall)
        
        right_wall = pygame.Rect(
            base_x + self.width - self.wall_thickness,
            base_y + self.wall_thickness,
            self.wall_thickness,
            self.height - self.wall_thickness
        )
        pygame.draw.rect(surface, wall_shadow, right_wall)
        
        # Draw broken top
        top_points = [
            (base_x, base_y),
            (base_x + self.width // 4, base_y - 5),
            (base_x + self.width // 2, base_y - 10),
            (base_x + 3 * self.width // 4, base_y - 5),
            (base_x + self.width, base_y)
        ]
        pygame.draw.polygon(surface, wall_color, top_points)
        
        # Draw cracks and damage
        crack_color = (60, 60, 60)
        # Vertical cracks
        for i in range(2):
            crack_x = base_x + (i + 1) * self.width // 3
            pygame.draw.line(
                surface,
                crack_color,
                (crack_x, base_y + self.wall_thickness),
                (crack_x, base_y + self.height - 10),
                2
            )
        
        # Horizontal cracks
        for i in range(2):
            crack_y = base_y + (i + 1) * self.height // 3
            pygame.draw.line(
                surface,
                crack_color,
                (base_x + self.wall_thickness, crack_y),
                (base_x + self.width - self.wall_thickness, crack_y),
                2
            )

class Projectile:
    def __init__(self, game, start_x, start_y, direction):
        self.game = game
        self.x = start_x
        self.y = start_y
        self.direction = direction
        self.speed = CELL_SIZE // 4  # Speed in pixels per frame
        self.radius = CELL_SIZE // 8
        self.color = (255, 200, 0)  # Bright yellow
        self.trail_length = 3  # Number of trail segments
        self.trail = []  # Store previous positions for trail effect
        
        # Arc trajectory parameters
        self.arc_height = CELL_SIZE // 2  # Maximum height of arc
        self.progress = 0  # Progress along trajectory (0 to 1)
        self.start_pos = (start_x, start_y)
        # Calculate target position (center of the target cell)
        self.target_pos = (
            start_x + direction[0] * CELL_SIZE,
            start_y + direction[1] * CELL_SIZE
        )
        
    def update(self):
        # Add current position to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)
            
        # Update progress along arc
        self.progress += 0.1  # Faster progress
        if self.progress >= 1:
            self.progress = 1
            self.x = self.target_pos[0]  # Ensure we end exactly at target
            self.y = self.target_pos[1]
            return
            
        # Calculate position along arc
        t = self.progress
        # Quadratic bezier curve for arc
        control_point = (
            (self.start_pos[0] + self.target_pos[0]) / 2,
            min(self.start_pos[1], self.target_pos[1]) - self.arc_height
        )
        
        # Calculate new position
        new_x = (1-t)**2 * self.start_pos[0] + 2*(1-t)*t * control_point[0] + t**2 * self.target_pos[0]
        new_y = (1-t)**2 * self.start_pos[1] + 2*(1-t)*t * control_point[1] + t**2 * self.target_pos[1]
        
        # Update position
        self.x = new_x
        self.y = new_y
        
    def draw(self, surface):
        # Draw trail
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i + 1) / (len(self.trail) + 1))
            trail_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (*self.color, alpha), 
                             (self.radius, self.radius), self.radius)
            surface.blit(trail_surface, (trail_x - self.radius, trail_y - self.radius))
            
        # Draw projectile
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        
    def is_off_screen(self):
        return self.progress >= 1

class Particle:
    def __init__(self, game, x, y, color):
        self.game = game
        self.x = x
        self.y = y
        self.color = color
        self.radius = CELL_SIZE // 8
        self.max_radius = self.radius * 3  # Increased max size
        self.growth_rate = 0.3  # Slower growth
        self.fade_rate = 8  # Slower fade
        self.alpha = 255
        self.lifetime = 40  # Longer lifetime
        
        # Add some randomness to the explosion
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(1, 3)  # Slower movement
        self.distance = 0
        self.max_distance = random.uniform(CELL_SIZE // 3, CELL_SIZE // 2)
        print(f"New particle created at ({x}, {y}) with lifetime {self.lifetime}")
        
    def update(self):
        # Always update particle properties
        self.radius += self.growth_rate
        self.alpha = max(0, self.alpha - self.fade_rate)
        self.lifetime -= 1
        
        # Move particle outward from center if not at max distance
        if self.distance < self.max_distance:
            move_x = math.cos(self.angle) * self.speed
            move_y = math.sin(self.angle) * self.speed
            self.x += move_x
            self.y += move_y
            self.distance += self.speed
            
        print(f"Particle at ({self.x}, {self.y}) - alpha: {self.alpha}, lifetime: {self.lifetime}")
        
    def draw(self, surface):
        if self.alpha <= 0:
            return
            
        # Create surface for particle with alpha
        particle_surface = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        
        # Draw outer glow
        pygame.draw.circle(particle_surface, (*self.color, self.alpha // 2),
                         (self.max_radius, self.max_radius), self.radius)
        
        # Draw inner core
        pygame.draw.circle(particle_surface, (*self.color, self.alpha),
                         (self.max_radius, self.max_radius), self.radius // 2)
        
        # Blit to main surface
        surface.blit(particle_surface, 
                    (self.x - self.max_radius, self.y - self.max_radius))
        print(f"Drawing particle at ({self.x}, {self.y}) with alpha {self.alpha}")
        
    def is_dead(self):
        # Particle is dead when either its lifetime is up or it's fully faded out
        is_dead = self.lifetime <= 0 or self.alpha <= 0
        if is_dead:
            print(f"Particle at ({self.x}, {self.y}) is dead - lifetime: {self.lifetime}, alpha: {self.alpha}")
        return is_dead 