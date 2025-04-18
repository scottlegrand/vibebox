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
        
        if self.type == HORIZONTAL:
            # Cardinal directions (plus sign)
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        else:
            # Diagonal directions (square) - normalized to same distance as cardinal
            diagonal_factor = 0.7071  # 1/sqrt(2) to maintain same distance
            directions = [
                (diagonal_factor, diagonal_factor),
                (-diagonal_factor, diagonal_factor),
                (diagonal_factor, -diagonal_factor),
                (-diagonal_factor, -diagonal_factor)
            ]
            
        for dx, dy in directions:
            # Calculate barrel center position
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