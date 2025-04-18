import pygame
import sys
from config import *
from pieces import ArtilleryPiece, Target, Monolith

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Artillery Chain Reaction")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Game state
        self.score = 0
        self.pieces = []
        self.targets = []
        self.monoliths = []
        self.dragged_piece = None
        self.selected_piece = None  # Track selected piece for detonation
        self.drag_offset = (0, 0)
        self.move_history = []  # Track all moves for undo functionality
        self.detonation_brightness = {}  # Track brightness of each tile
        self.was_dragged = False  # Track if piece was actually moved
        
        # Add test pieces
        self.add_test_pieces()
        self.update_detonation_zones()  # Initialize detonation zones
        
        # UI elements
        self.detonate_button = pygame.Rect(
            DETONATE_BUTTON_X,
            DETONATE_BUTTON_Y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )
        self.undo_button = pygame.Rect(
            UNDO_BUTTON_X,
            UNDO_BUTTON_Y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )
        
        # Hover states
        self.detonate_hover = False
        self.undo_hover = False
        
    def add_test_pieces(self):
        # Add a horizontal artillery piece to the tray
        self.pieces.append(ArtilleryPiece(
            self,
            BOARD_X + CELL_SIZE,  # First position in tray
            TRAY_Y + (TRAY_HEIGHT - CELL_SIZE) // 2,
            HORIZONTAL
        ))
        
        # Add a diagonal artillery piece to the tray
        self.pieces.append(ArtilleryPiece(
            self,
            BOARD_X + 2 * CELL_SIZE,  # Second position in tray
            TRAY_Y + (TRAY_HEIGHT - CELL_SIZE) // 2,
            DIAGONAL
        ))
        
        # Add a target
        self.targets.append(Target(
            self,
            BOARD_X + 3 * CELL_SIZE,
            BOARD_Y + 3 * CELL_SIZE
        ))
        
        # Add a monolith
        self.monoliths.append(Monolith(
            self,
            BOARD_X + 5 * CELL_SIZE,
            BOARD_Y + 5 * CELL_SIZE
        ))
        
    def is_valid_placement(self, x, y):
        # Convert from top-left to center coordinates
        center_x = x + CELL_SIZE // 2
        center_y = y + CELL_SIZE // 2
        
        # Check if position is in tray
        if TRAY_Y <= center_y < TRAY_Y + TRAY_HEIGHT:
            # For tray placement, only check for piece overlap
            for piece in self.pieces:
                if piece != self.dragged_piece:
                    piece_center_x = piece.x + CELL_SIZE // 2
                    piece_center_y = piece.y + CELL_SIZE // 2
                    if abs(center_x - piece_center_x) < CELL_SIZE and abs(center_y - piece_center_y) < CELL_SIZE:
                        return False
            return True
        
        # For board placement, check bounds and all objects
        if not (BOARD_X <= center_x < BOARD_X + BOARD_SIZE * CELL_SIZE and
                BOARD_Y <= center_y < BOARD_Y + BOARD_SIZE * CELL_SIZE):
            return False
            
        # Check if position overlaps with targets or monoliths
        for target in self.targets:
            target_center_x = target.x + CELL_SIZE // 2
            target_center_y = target.y + CELL_SIZE // 2
            if abs(center_x - target_center_x) < CELL_SIZE and abs(center_y - target_center_y) < CELL_SIZE:
                return False
                
        for monolith in self.monoliths:
            monolith_center_x = monolith.x + CELL_SIZE // 2
            monolith_center_y = monolith.y + CELL_SIZE // 2
            if abs(center_x - monolith_center_x) < CELL_SIZE and abs(center_y - monolith_center_y) < CELL_SIZE:
                return False
                
        # Check if position overlaps with other pieces
        for piece in self.pieces:
            if piece != self.dragged_piece:
                piece_center_x = piece.x + CELL_SIZE // 2
                piece_center_y = piece.y + CELL_SIZE // 2
                if abs(center_x - piece_center_x) < CELL_SIZE and abs(center_y - piece_center_y) < CELL_SIZE:
                    return False
                
        return True
        
    def snap_to_grid(self, x, y):
        # Convert from top-left to center coordinates
        center_x = x + CELL_SIZE // 2
        center_y = y + CELL_SIZE // 2
        
        # Snap center to nearest grid cell center
        grid_center_x = ((center_x - BOARD_X) // CELL_SIZE) * CELL_SIZE + BOARD_X + CELL_SIZE // 2
        grid_center_y = ((center_y - BOARD_Y) // CELL_SIZE) * CELL_SIZE + BOARD_Y + CELL_SIZE // 2
        
        # Convert back to top-left coordinates
        grid_x = grid_center_x - CELL_SIZE // 2
        grid_y = grid_center_y - CELL_SIZE // 2
        
        return grid_x, grid_y
        
    def draw_header(self):
        # Draw header background
        header_rect = pygame.Rect(
            UI_MARGIN,
            HEADER_Y,
            WINDOW_WIDTH - 2 * UI_MARGIN,
            UI_HEADER_HEIGHT
        )
        pygame.draw.rect(self.screen, GRAY, header_rect)
        pygame.draw.rect(self.screen, BLACK, header_rect, 2)
        
        # Draw buttons and score
        self.draw_buttons()
        self.draw_score()
        
    def draw_board(self):
        # Draw board background
        board_rect = pygame.Rect(
            BOARD_X,
            BOARD_Y,
            BOARD_SIZE * CELL_SIZE,
            BOARD_SIZE * CELL_SIZE
        )
        pygame.draw.rect(self.screen, BLACK, board_rect)
        
        # Draw detonation zones with cumulative brightness
        for (grid_x, grid_y), brightness in self.detonation_brightness.items():
            # Calculate tile position
            x = BOARD_X + grid_x * CELL_SIZE
            y = BOARD_Y + grid_y * CELL_SIZE
            
            # Create a surface for the brightening effect
            bright_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            
            # Calculate brightness based on number of overlapping zones
            # Max brightness is 255 (white) when 3 or more zones overlap
            alpha = min(255, brightness * 85)  # 85 = 255/3
            
            # Fill with white at calculated alpha
            bright_surface.fill((255, 255, 255, alpha))
            self.screen.blit(bright_surface, (x, y))
        
        # Draw grid lines
        for i in range(BOARD_SIZE + 1):
            # Vertical lines
            pygame.draw.line(
                self.screen,
                WHITE,
                (BOARD_X + i * CELL_SIZE, BOARD_Y),
                (BOARD_X + i * CELL_SIZE, BOARD_Y + BOARD_SIZE * CELL_SIZE)
            )
            # Horizontal lines
            pygame.draw.line(
                self.screen,
                WHITE,
                (BOARD_X, BOARD_Y + i * CELL_SIZE),
                (BOARD_X + BOARD_SIZE * CELL_SIZE, BOARD_Y + i * CELL_SIZE)
            )
        
        # Draw glowing border for selected piece
        if self.selected_piece and self.selected_piece.y < TRAY_Y:
            # Calculate cell position
            cell_x = ((self.selected_piece.x + CELL_SIZE // 2) - BOARD_X) // CELL_SIZE
            cell_y = ((self.selected_piece.y + CELL_SIZE // 2) - BOARD_Y) // CELL_SIZE
            
            # Draw outer glow
            glow_rect = pygame.Rect(
                BOARD_X + cell_x * CELL_SIZE - 2,
                BOARD_Y + cell_y * CELL_SIZE - 2,
                CELL_SIZE + 4,
                CELL_SIZE + 4
            )
            pygame.draw.rect(self.screen, (255, 255, 255, 200), glow_rect, 4)
            
            # Draw inner glow
            glow_rect = pygame.Rect(
                BOARD_X + cell_x * CELL_SIZE - 1,
                BOARD_Y + cell_y * CELL_SIZE - 1,
                CELL_SIZE + 2,
                CELL_SIZE + 2
            )
            pygame.draw.rect(self.screen, (255, 255, 255, 100), glow_rect, 2)
        
        # Draw pieces
        for piece in self.pieces:
            piece.draw(self.screen)
            
        # Draw targets
        for target in self.targets:
            target.draw(self.screen)
            
        # Draw monoliths
        for monolith in self.monoliths:
            monolith.draw(self.screen)
    
    def draw_tray(self):
        # Draw tray background
        tray_rect = pygame.Rect(
            BOARD_X,
            TRAY_Y,
            BOARD_SIZE * CELL_SIZE,
            TRAY_HEIGHT
        )
        pygame.draw.rect(self.screen, GRAY, tray_rect)
        pygame.draw.rect(self.screen, BLACK, tray_rect, 2)
    
    def draw_buttons(self):
        # Draw detonate button shadow
        shadow_rect = pygame.Rect(
            self.detonate_button.x + BUTTON_SHADOW_OFFSET,
            self.detonate_button.y + BUTTON_SHADOW_OFFSET,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )
        pygame.draw.rect(self.screen, BUTTON_SHADOW, shadow_rect)
        
        # Draw detonate button
        button_color = DETONATE_HOVER if self.detonate_hover else DETONATE_COLOR
        pygame.draw.rect(self.screen, button_color, self.detonate_button)
        detonate_text = self.font.render("Detonate", True, WHITE)
        self.screen.blit(
            detonate_text,
            (
                self.detonate_button.x + (BUTTON_WIDTH - detonate_text.get_width()) // 2,
                self.detonate_button.y + (BUTTON_HEIGHT - detonate_text.get_height()) // 2
            )
        )
        
        # Draw undo button shadow
        shadow_rect = pygame.Rect(
            self.undo_button.x + BUTTON_SHADOW_OFFSET,
            self.undo_button.y + BUTTON_SHADOW_OFFSET,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )
        pygame.draw.rect(self.screen, BUTTON_SHADOW, shadow_rect)
        
        # Draw undo button
        button_color = UNDO_HOVER if self.undo_hover else UNDO_COLOR
        pygame.draw.rect(self.screen, button_color, self.undo_button)
        undo_text = self.font.render("Undo", True, WHITE)
        self.screen.blit(
            undo_text,
            (
                self.undo_button.x + (BUTTON_WIDTH - undo_text.get_width()) // 2,
                self.undo_button.y + (BUTTON_HEIGHT - undo_text.get_height()) // 2
            )
        )
    
    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (SCORE_X, SCORE_Y))
    
    def save_move(self, piece, old_x, old_y, new_x, new_y):
        """Save a move to the history for undo functionality"""
        self.move_history.append({
            'piece': piece,
            'old_x': old_x,
            'old_y': old_y,
            'new_x': new_x,
            'new_y': new_y
        })
        
    def undo_last_move(self):
        """Undo the last move in the history"""
        if self.move_history:
            move = self.move_history.pop()
            move['piece'].x = move['old_x']
            move['piece'].y = move['old_y']
            return True
        return False
        
    def update_detonation_zones(self):
        """Update the brightness of tiles based on all pieces' detonation zones"""
        # Reset brightness
        self.detonation_brightness = {}
        
        # Calculate brightness for each piece
        for piece in self.pieces:
            # Only process pieces on the board (not in tray)
            if piece.y < TRAY_Y:
                # Convert piece position to grid coordinates using center
                piece_center_x = piece.x + CELL_SIZE // 2
                piece_center_y = piece.y + CELL_SIZE // 2
                piece_grid_x = (piece_center_x - BOARD_X) // CELL_SIZE
                piece_grid_y = (piece_center_y - BOARD_Y) // CELL_SIZE
                    
                # Get detonation zone for this piece
                for dx, dy in piece.directions:
                    # Calculate adjacent grid position
                    grid_x = piece_grid_x + dx
                    grid_y = piece_grid_y + dy
                    
                    # Check if within board bounds
                    if 0 <= grid_x < BOARD_SIZE and 0 <= grid_y < BOARD_SIZE:
                        key = (grid_x, grid_y)
                        # Increment brightness for this tile
                        self.detonation_brightness[key] = self.detonation_brightness.get(key, 0) + 1

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        # Update hover states
        self.detonate_hover = self.detonate_button.collidepoint(mouse_pos)
        self.undo_hover = self.undo_button.collidepoint(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if self.detonate_button.collidepoint(event.pos):
                        if self.selected_piece:
                            print("Detonating from selected piece")
                            # TODO: Implement detonation from selected piece
                        else:
                            print("No piece selected for detonation")
                    elif self.undo_button.collidepoint(event.pos):
                        if self.undo_last_move():
                            print("Undo successful")
                            self.update_detonation_zones()  # Update zones after undo
                        else:
                            print("No moves to undo")
                    else:
                        # Check if clicking on a piece
                        for piece in self.pieces:
                            piece_center_x = piece.x + CELL_SIZE // 2
                            piece_center_y = piece.y + CELL_SIZE // 2
                            # Check if click is within piece's radius
                            if ((event.pos[0] - piece_center_x) ** 2 + 
                                (event.pos[1] - piece_center_y) ** 2 <= 
                                (CELL_SIZE // 2) ** 2):
                                print(f"Mouse down on piece at ({piece.x}, {piece.y})")  # Debug print
                                self.dragged_piece = piece
                                self.drag_offset = (
                                    event.pos[0] - piece_center_x,
                                    event.pos[1] - piece_center_y
                                )
                                # Store initial position for potential move
                                self.initial_drag_x = piece.x
                                self.initial_drag_y = piece.y
                                self.was_dragged = False  # Reset drag state
                                break
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragged_piece:
                    print(f"Mouse up on piece at ({self.dragged_piece.x}, {self.dragged_piece.y})")  # Debug print
                    if self.was_dragged:
                        print("Piece was dragged")  # Debug print
                        # Handle drag operation
                        if (self.dragged_piece.x != self.initial_drag_x or 
                            self.dragged_piece.y != self.initial_drag_y):
                            
                            # Check if dropped in tray area
                            if TRAY_Y <= event.pos[1] < TRAY_Y + TRAY_HEIGHT:
                                # Find first available position in tray
                                new_x = BOARD_X
                                new_y = TRAY_Y + (TRAY_HEIGHT - CELL_SIZE) // 2
                                while True:
                                    # Check if this position is valid
                                    if self.is_valid_placement(new_x, new_y):
                                        break
                                    new_x += CELL_SIZE
                                    # If we've checked all positions, return to original position
                                    if new_x >= BOARD_X + BOARD_SIZE * CELL_SIZE:
                                        new_x = self.initial_drag_x
                                        new_y = self.initial_drag_y
                                        break
                                
                                self.dragged_piece.x = new_x
                                self.dragged_piece.y = new_y
                                if self.selected_piece == self.dragged_piece:
                                    self.selected_piece = None
                                self.save_move(self.dragged_piece, self.initial_drag_x, self.initial_drag_y, new_x, new_y)
                            else:
                                # Calculate piece center based on mouse position and offset
                                piece_center_x = event.pos[0] - self.drag_offset[0]
                                piece_center_y = event.pos[1] - self.drag_offset[1]
                                
                                # Convert center to top-left for snapping
                                piece_x = piece_center_x - CELL_SIZE // 2
                                piece_y = piece_center_y - CELL_SIZE // 2
                                
                                # Snap to grid
                                grid_x, grid_y = self.snap_to_grid(piece_x, piece_y)
                                
                                if self.is_valid_placement(grid_x, grid_y):
                                    self.dragged_piece.x = grid_x
                                    self.dragged_piece.y = grid_y
                                    self.save_move(self.dragged_piece, self.initial_drag_x, self.initial_drag_y, grid_x, grid_y)
                                else:
                                    # Return to original position if invalid
                                    self.dragged_piece.x = self.initial_drag_x
                                    self.dragged_piece.y = self.initial_drag_y
                    else:
                        print("Piece was clicked (not dragged)")  # Debug print
                        # Handle selection
                        self.selected_piece = self.dragged_piece
                    
                    self.dragged_piece = None
                    self.update_detonation_zones()  # Update zones after piece placement
            elif event.type == pygame.MOUSEMOTION:
                if self.dragged_piece:
                    # Update piece center position while dragging
                    piece_center_x = event.pos[0] - self.drag_offset[0]
                    piece_center_y = event.pos[1] - self.drag_offset[1]
                    
                    # Convert center to top-left for drawing
                    self.dragged_piece.x = piece_center_x - CELL_SIZE // 2
                    self.dragged_piece.y = piece_center_y - CELL_SIZE // 2
                    self.was_dragged = True  # Mark that the piece was actually moved
                    self.update_detonation_zones()  # Update zones while dragging
        
    def update(self):
        self.handle_events()
    
    def draw(self):
        self.screen.fill(WHITE)
        self.draw_header()
        self.draw_board()
        self.draw_tray()
        
        # Draw all pieces
        for piece in self.pieces:
            piece.draw(self.screen)
        
        # Draw targets
        for target in self.targets:
            target.draw(self.screen)
        
        # Draw monoliths
        for monolith in self.monoliths:
            monolith.draw(self.screen)
        
        # Update and draw detonation zones for moving piece
        if self.dragged_piece:
            # Use exact same logic as snap_to_grid
            center_x = self.dragged_piece.x + CELL_SIZE // 2
            center_y = self.dragged_piece.y + CELL_SIZE // 2
            
            # Get current cell
            current_cell_x = (center_x - BOARD_X) // CELL_SIZE
            current_cell_y = (center_y - BOARD_Y) // CELL_SIZE
            
            # Snap center to nearest grid cell center
            grid_center_x = current_cell_x * CELL_SIZE + BOARD_X + CELL_SIZE // 2
            grid_center_y = current_cell_y * CELL_SIZE + BOARD_Y + CELL_SIZE // 2
            
            # Convert back to top-left coordinates
            snapped_x = grid_center_x - CELL_SIZE // 2
            snapped_y = grid_center_y - CELL_SIZE // 2
            
            # Temporarily move piece to snapped position for zone drawing
            original_x, original_y = self.dragged_piece.x, self.dragged_piece.y
            self.dragged_piece.x, self.dragged_piece.y = snapped_x, snapped_y
            self.update_detonation_zones()
            self.dragged_piece.x, self.dragged_piece.y = original_x, original_y
        
        pygame.display.flip()
    
    def run(self):
        while True:
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run() 