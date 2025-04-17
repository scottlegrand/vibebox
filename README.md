# Artillery Chain Reaction

A Python implementation of the Artillery Chain Reaction game using Pygame.

## Setup

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

To start the game, run:
```bash
python src/game/game.py
```

## Game Controls

- Left-click and drag pieces from the tray to the board
- Click the "Detonate" button to start the chain reaction
- Click the "Undo" button to undo your last move
- Close the window to exit the game

## Game Rules

- Place artillery pieces on the board to create chain reactions
- Horizontal pieces fire in four cardinal directions
- Diagonal pieces fire in four diagonal directions
- Hit all targets to complete the level
- Avoid hitting monoliths 