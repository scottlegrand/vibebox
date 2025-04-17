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
        self.drag_offset = (0, 0)
        self.undo_stack = []  # Track piece positions for undo
        
        # Add test pieces
        self.add_test_pieces()
        
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
        # Add a horizontal artillery piece
        self.pieces.append(ArtilleryPiece(
            self,
            BOARD_X + CELL_SIZE,
            BOARD_Y + CELL_SIZE,
            HORIZONTAL
        ))
        
        # Add a diagonal artillery piece to the board
        self.pieces.append(ArtilleryPiece(
            self,
            BOARD_X + 4 * CELL_SIZE,
            BOARD_Y + 4 * CELL_SIZE,
            DIAGONAL
        ))
        
        # Add a diagonal artillery piece to the tray
        self.pieces.append(ArtilleryPiece(
            self,
            BOARD_X + 2 * CELL_SIZE,
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
        # Check if position is within board bounds
        if not (BOARD_X <= x < BOARD_X + BOARD_SIZE * CELL_SIZE and
                BOARD_Y <= y < BOARD_Y + BOARD_SIZE * CELL_SIZE):
            return False
            
        # Check if position overlaps with targets or monoliths
        for target in self.targets:
            if (target.x <= x < target.x + CELL_SIZE and
                target.y <= y < target.y + CELL_SIZE):
                return False
                
        for monolith in self.monoliths:
            if (monolith.x <= x < monolith.x + CELL_SIZE and
                monolith.y <= y < monolith.y + CELL_SIZE):
                return False
                
        # Check if position overlaps with other pieces
        for piece in self.pieces:
            if piece != self.dragged_piece and (
                piece.x <= x < piece.x + CELL_SIZE and
                piece.y <= y < piece.y + CELL_SIZE
            ):
                return False
                
        return True
        
    def snap_to_grid(self, x, y):
        # Snap to nearest grid cell
        grid_x = (x - BOARD_X) // CELL_SIZE * CELL_SIZE + BOARD_X
        grid_y = (y - BOARD_Y) // CELL_SIZE * CELL_SIZE + BOARD_Y
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
        pygame.draw.rect(self.screen, WHITE, board_rect)
        pygame.draw.rect(self.screen, BLACK, board_rect, 2)
        
        # Draw grid lines
        for i in range(BOARD_SIZE + 1):
            # Vertical lines
            pygame.draw.line(
                self.screen,
                BLACK,
                (BOARD_X + i * CELL_SIZE, BOARD_Y),
                (BOARD_X + i * CELL_SIZE, BOARD_Y + BOARD_SIZE * CELL_SIZE)
            )
            # Horizontal lines
            pygame.draw.line(
                self.screen,
                BLACK,
                (BOARD_X, BOARD_Y + i * CELL_SIZE),
                (BOARD_X + BOARD_SIZE * CELL_SIZE, BOARD_Y + i * CELL_SIZE)
            )
        
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
                        print("Detonate button clicked")
                    elif self.undo_button.collidepoint(event.pos):
                        print("Undo button clicked")
                    else:
                        # Check if clicking on a piece
                        for piece in self.pieces:
                            # Calculate the center of the piece's dome
                            dome_center_x = piece.x + CELL_SIZE // 2
                            dome_center_y = piece.y + CELL_SIZE // 2
                            
                            # Check if click is within the piece's bounds
                            if (piece.x <= event.pos[0] < piece.x + CELL_SIZE and
                                piece.y <= event.pos[1] < piece.y + CELL_SIZE):
                                # Calculate offset from dome center to mouse
                                self.drag_offset = (
                                    event.pos[0] - dome_center_x,
                                    event.pos[1] - dome_center_y
                                )
                                self.dragged_piece = piece
                                # Save current position for undo
                                self.undo_stack.append((piece, piece.x, piece.y))
                                break
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragged_piece:
                    # Calculate the dome's center position
                    dome_center_x = event.pos[0] - self.drag_offset[0]
                    dome_center_y = event.pos[1] - self.drag_offset[1]
                    
                    # Convert dome center to piece's top-left position
                    piece_x = dome_center_x - CELL_SIZE // 2
                    piece_y = dome_center_y - CELL_SIZE // 2
                    
                    # Snap to grid if on board
                    if (BOARD_X <= piece_x < BOARD_X + BOARD_SIZE * CELL_SIZE and
                        BOARD_Y <= piece_y < BOARD_Y + BOARD_SIZE * CELL_SIZE):
                        # Calculate the grid cell center
                        grid_cell_x = ((dome_center_x - BOARD_X) // CELL_SIZE) * CELL_SIZE + BOARD_X + CELL_SIZE // 2
                        grid_cell_y = ((dome_center_y - BOARD_Y) // CELL_SIZE) * CELL_SIZE + BOARD_Y + CELL_SIZE // 2
                        
                        # Convert grid cell center to piece position
                        piece_x = grid_cell_x - CELL_SIZE // 2
                        piece_y = grid_cell_y - CELL_SIZE // 2
                        
                        if self.is_valid_placement(piece_x, piece_y):
                            self.dragged_piece.x = piece_x
                            self.dragged_piece.y = piece_y
                        else:
                            # Return to original position if invalid
                            self.dragged_piece.x = self.undo_stack[-1][1]
                            self.dragged_piece.y = self.undo_stack[-1][2]
                            self.undo_stack.pop()
                    else:
                        # Return to original position if not on board
                        self.dragged_piece.x = self.undo_stack[-1][1]
                        self.dragged_piece.y = self.undo_stack[-1][2]
                        self.undo_stack.pop()
                    self.dragged_piece = None
            elif event.type == pygame.MOUSEMOTION:
                if self.dragged_piece:
                    # Calculate the dome's center position
                    dome_center_x = event.pos[0] - self.drag_offset[0]
                    dome_center_y = event.pos[1] - self.drag_offset[1]
                    
                    # Convert dome center to piece's top-left position
                    self.dragged_piece.x = dome_center_x - CELL_SIZE // 2
                    self.dragged_piece.y = dome_center_y - CELL_SIZE // 2
    
    def update(self):
        self.handle_events()
    
    def draw(self):
        self.screen.fill(WHITE)
        self.draw_header()  # Draw header first
        self.draw_board()
        self.draw_tray()
        pygame.display.flip()
    
    def run(self):
        while True:
            self.update()
            self.draw()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run() 