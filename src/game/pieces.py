import pygame
import math
from config import *

class ArtilleryPiece:
    def __init__(self, scene, x, y, piece_type):
        self.scene = scene
        self.x = x
        self.y = y
        self.type = piece_type
        self.base_color = GREEN if piece_type == HORIZONTAL else RED
        self.highlight_color = tuple(min(c + 50, 255) for c in self.base_color)
        self.shadow_color = tuple(max(c - 50, 0) for c in self.base_color)
        self.radius = CELL_SIZE // 3
        self.barrel_length = CELL_SIZE // 3
        self.barrel_width = CELL_SIZE // 8
        self.turret_radius = self.radius * 2 // 3
        self.turret_height = self.radius // 4
        
    def draw(self, surface):
        center_x = self.x + CELL_SIZE // 2
        center_y = self.y + CELL_SIZE // 2
        
        # Draw base shadow
        pygame.draw.circle(surface, self.shadow_color, 
                         (center_x + 2, center_y + 2), self.radius)
        
        # Draw base
        pygame.draw.circle(surface, self.base_color, 
                         (center_x, center_y), self.radius)
        
        # Draw base highlight
        highlight_radius = self.radius * 3 // 4
        pygame.draw.circle(surface, self.highlight_color, 
                         (center_x - 2, center_y - 2), highlight_radius)
        
        # Draw turret shadow (elliptical due to perspective)
        turret_center_y = center_y - self.radius // 3
        pygame.draw.ellipse(surface, self.shadow_color,
                          (center_x - self.turret_radius + 2,
                           turret_center_y - self.turret_height // 2 + 2,
                           self.turret_radius * 2,
                           self.turret_height))
        
        # Draw turret (elliptical due to perspective)
        pygame.draw.ellipse(surface, self.base_color,
                          (center_x - self.turret_radius,
                           turret_center_y - self.turret_height // 2,
                           self.turret_radius * 2,
                           self.turret_height))
        
        # Draw turret highlight
        highlight_rect = pygame.Rect(
            center_x - self.turret_radius + 2,
            turret_center_y - self.turret_height // 2 + 2,
            self.turret_radius * 2 - 4,
            self.turret_height // 2
        )
        pygame.draw.ellipse(surface, self.highlight_color, highlight_rect)
        
        # Draw barrels
        barrel_color = (150, 150, 150)  # Base metallic gray
        barrel_highlight = (180, 180, 180)  # Lighter metallic gray
        barrel_shadow = (120, 120, 120)  # Darker metallic gray
        
        if self.type == HORIZONTAL:
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        else:
            directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
            
        for dx, dy in directions:
            # Calculate barrel positions with more overhead view
            horizontal_length = self.barrel_length * 0.7  # For left/right barrels
            vertical_length = self.barrel_length * 0.7  # For up/down barrels
            
            start_x = center_x + dx * self.turret_radius
            start_y = turret_center_y + dy * self.turret_height // 2
            
            # Calculate end points with proper perspective
            if dy != 0:  # For up/down barrels
                # Make up/down barrels point in different directions with longer length
                end_x = center_x + dx * (self.turret_radius + horizontal_length * 0.5)  # Reduced horizontal component
                if dy > 0:  # Down barrel
                    end_y = start_y + vertical_length
                else:  # Up barrel
                    end_y = start_y - vertical_length
            else:  # For left/right barrels
                end_x = center_x + dx * (self.turret_radius + horizontal_length)
                end_y = start_y
            
            # For diagonal pieces, adjust the end points
            if self.type != HORIZONTAL:
                if dx != 0 and dy != 0:  # Diagonal barrels
                    end_x = center_x + dx * (self.turret_radius + horizontal_length)
                    end_y = turret_center_y + dy * vertical_length
            
            # Draw barrel shadow
            pygame.draw.line(
                surface,
                barrel_shadow,
                (start_x + 2, start_y + 2),
                (end_x + 2, end_y + 2),
                self.barrel_width
            )
            
            # Draw barrel
            pygame.draw.line(
                surface,
                barrel_color,
                (start_x, start_y),
                (end_x, end_y),
                self.barrel_width
            )
            
            # Draw barrel highlight
            highlight_width = self.barrel_width // 2
            pygame.draw.line(
                surface,
                barrel_highlight,
                (start_x - 1, start_y - 1),
                (end_x - 1, end_y - 1),
                highlight_width
            )

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
        
        # Draw rubble at base
        rubble_height = 5
        rubble_rect = pygame.Rect(
            base_x,
            base_y + self.height - rubble_height,
            self.width,
            rubble_height
        )
        pygame.draw.rect(surface, (90, 90, 90), rubble_rect) 