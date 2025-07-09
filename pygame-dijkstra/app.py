import pygame
from algorithms import dijkstra_stepwise, astar_stepwise, dfs_stepwise, bfs_stepwise
from maze_generators import generate_maze_type_3
import time
"""
Path-finding Visualization with Pygame

This application visualizes several path-finding algorithms (Dijkstra, A*, BFS, DFS) on a grid using Pygame.
Users can interactively set walls, start, and end points, generate mazes, and observe the algorithm's progress step by step.

Features:
    - Interactive grid for drawing/removing walls.
    - Move start/end points with mouse.
    - Visualize Dijkstra, A*, BFS, and DFS algorithms.
    - Maze generation and clearing.
    - Displays elapsed time and recent run history.

Controls:
    - Left-click & drag: Draw/remove walls.
    - Right-click: Move start point.
    - Middle-click: Move end point.
    - 1/2/3/4: Switch algorithm (Dijkstra/A*/DFS/BFS).
    - SPACE: Start visualization.
    - TAB: Generate maze.
    - ` (backquote): Clear grid.

Modules:
    - pygame: Rendering and user interaction.
    - algorithms: Stepwise implementations of path-finding algorithms.
    - maze_generators: Maze generation utilities.

Main Components:
    - Grid state and rendering.
    - Event handling for mouse and keyboard.
    - Stepwise algorithm execution and visualization.
    - History tracking for recent runs.
"""

# --- Constants ---
ROWS, COLS = 30, 45
CELL_SIZE = 15
WIDTH, HEIGHT = 1440, 720
# Center the grid in the window
GRID_OFFSET = (
    (WIDTH - (COLS * CELL_SIZE)) // 2,
    (HEIGHT - (ROWS * CELL_SIZE)) // 2
)

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Path-finding Visualization - Where's Jerry?")
clock = pygame.time.Clock()

# --- Grid and State ---
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
start = (0, 0)
end = (ROWS - 1, COLS - 1)
path = []
mouse_down = False
drawing_wall = None

# Algorithm mode: "dijkstra" or "astar"
algorithm_mode = "dijkstra"

# Dijkstra visualization state
dijkstra_running = False
dijkstra_gen = None
visited = set()
frontier = set()

# --- Helper Functions ---

def get_cell_from_pos(pos):
    x, y = pos
    col = (x - GRID_OFFSET[0]) // CELL_SIZE
    row = (y - GRID_OFFSET[1]) // CELL_SIZE
    if 0 <= row < ROWS and 0 <= col < COLS:
        return (row, col)
    return None

# Load mouse and cheese icons (ensure these files exist in your project directory)
mouse_icon = pygame.image.load("tom.jpg")
cheese_icon = pygame.image.load("jerry.png")
mouse_icon = pygame.transform.smoothscale(mouse_icon, (CELL_SIZE - 4, CELL_SIZE - 4))
cheese_icon = pygame.transform.smoothscale(cheese_icon, (CELL_SIZE - 4, CELL_SIZE - 4))

def draw_grid():
    # Color palette: black walls, off-white background
    COLOR_BG = (245, 245, 245)         # Off-white background
    COLOR_GRID = (0, 0, 0)             # Black grid lines (outer border)
    COLOR_INNER_GRID = (200, 200, 200) # Light gray for inner grid lines
    COLOR_WALL = (0, 0, 0)             # Black for walls
    COLOR_PATH = (128, 0, 255)         # Purple for final path
    COLOR_VISITED = (255, 128, 192)    # Pink for visited (initial path)
    COLOR_FRONTIER = (0, 168, 0)       # Green for frontier

    # Fill background
    screen.fill(COLOR_BG)

    # Draw outer border
    outer_rect = pygame.Rect(
        GRID_OFFSET[0],
        GRID_OFFSET[1],
        COLS * CELL_SIZE,
        ROWS * CELL_SIZE
    )
    pygame.draw.rect(screen, COLOR_GRID, outer_rect, width=2)

    # Draw inner grid lines (vertical and horizontal)
    for row in range(1, ROWS):
        y = GRID_OFFSET[1] + row * CELL_SIZE
        pygame.draw.line(
            screen, COLOR_INNER_GRID,
            (GRID_OFFSET[0], y),
            (GRID_OFFSET[0] + COLS * CELL_SIZE, y),
            width=1
        )
    for col in range(1, COLS):
        x = GRID_OFFSET[0] + col * CELL_SIZE
        pygame.draw.line(
            screen, COLOR_INNER_GRID,
            (x, GRID_OFFSET[1]),
            (x, GRID_OFFSET[1] + ROWS * CELL_SIZE),
            width=1
        )

    # Draw cells (no inner grid lines)
    for row in range(ROWS):
        for col in range(COLS):
            cell = (row, col)
            border_radius = 6
            rect_x = GRID_OFFSET[0] + col * CELL_SIZE + 2
            rect_y = GRID_OFFSET[1] + row * CELL_SIZE + 2
            rect_w = CELL_SIZE - 4
            rect_h = CELL_SIZE - 4

            if cell == start:
                # Draw mouse icon
                screen.blit(mouse_icon, (rect_x, rect_y))
            elif cell == end:
                # Draw cheese icon
                screen.blit(cheese_icon, (rect_x, rect_y))
            elif grid[row][col] == 1:
                color = COLOR_WALL
                wall_margin = 0
                rect_x = GRID_OFFSET[0] + col * CELL_SIZE + wall_margin
                rect_y = GRID_OFFSET[1] + row * CELL_SIZE + wall_margin
                rect_w = CELL_SIZE - 2 * wall_margin
                rect_h = CELL_SIZE - 2 * wall_margin
                border_radius = 0
                pygame.draw.rect(
                    screen,
                    color,
                    (
                        rect_x,
                        rect_y,
                        rect_w,
                        rect_h,
                    ),
                    border_radius=border_radius
                )
            elif cell in path:
                color = COLOR_PATH
                pygame.draw.rect(
                    screen,
                    color,
                    (
                        rect_x,
                        rect_y,
                        rect_w,
                        rect_h,
                    ),
                    border_radius=border_radius
                )
            elif cell in visited:
                color = COLOR_VISITED
                pygame.draw.rect(
                    screen,
                    color,
                    (
                        rect_x,
                        rect_y,
                        rect_w,
                        rect_h,
                    ),
                    border_radius=border_radius
                )
            elif cell in frontier:
                color = COLOR_FRONTIER
                pygame.draw.rect(
                    screen,
                    color,
                    (
                        rect_x,
                        rect_y,
                        rect_w,
                        rect_h,
                    ),
                    border_radius=border_radius
                )

    # Draw outer border LAST so it appears above wall cells
    pygame.draw.rect(screen, COLOR_GRID, outer_rect, width=2)

def reset_path_states():
    global path, visited, frontier, dijkstra_running, dijkstra_gen
    path.clear()
    visited.clear()
    frontier.clear()
    dijkstra_running = False
    dijkstra_gen = None

# --- Main Loop ---
running = True
algo_start_time = None
algo_elapsed_time = 0.0

# --- History State ---
# Now each history entry is (algorithm_mode, elapsed_time, path_length)
history = []  # List of (algorithm_mode, elapsed_time, path_length) tuples, max length 4

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            cell = get_cell_from_pos(event.pos)
            if cell:
                if event.button == 1 and cell != start and cell != end:
                    mouse_down = True
                    drawing_wall = grid[cell[0]][cell[1]] == 0
                    grid[cell[0]][cell[1]] = 1 if drawing_wall else 0
                    reset_path_states()
                elif event.button == 2:
                    if cell != end:
                        start = cell
                    reset_path_states()
                elif event.button == 3:  # Middle mouse button for end point
                    if cell != start:
                        end = cell
                    reset_path_states()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_down = False
                drawing_wall = None

        elif event.type == pygame.MOUSEMOTION:
            if mouse_down and drawing_wall is not None:
                cell = get_cell_from_pos(event.pos)
                if cell and cell != start and cell != end:
                    grid[cell[0]][cell[1]] = 1 if drawing_wall else 0
                    reset_path_states()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                algorithm_mode = "dijkstra"
                reset_path_states()
            elif event.key == pygame.K_2:
                algorithm_mode = "astar"
                reset_path_states()
            elif event.key == pygame.K_3:
                algorithm_mode = "dfs"
                reset_path_states()
            elif event.key == pygame.K_4:
                algorithm_mode = "bfs"
                reset_path_states()
            elif event.key == pygame.K_SPACE:
                dijkstra_running = True
                if algorithm_mode == "dijkstra":
                    dijkstra_gen = dijkstra_stepwise(start, end, rows=ROWS, cols=COLS, grid=grid)
                elif algorithm_mode == "astar":
                    dijkstra_gen = astar_stepwise(start, end, rows=ROWS, cols=COLS, grid=grid)
                elif algorithm_mode == "bfs":
                    dijkstra_gen = bfs_stepwise(start, end, rows=ROWS, cols=COLS, grid=grid)
                elif algorithm_mode == "dfs":
                    dijkstra_gen = dfs_stepwise(start, end, rows=ROWS, cols=COLS, grid=grid)
                path.clear()
                visited.clear()
                frontier.clear()
                algo_start_time = time.time()
                algo_elapsed_time = 0.0
            elif event.key == pygame.K_TAB:
                generate_maze_type_3(rows=ROWS, cols=COLS, grid_ref=grid, start_pos=start, end_pos=end)
                reset_path_states()
            elif event.key == pygame.K_BACKQUOTE:  # Nút "`" để xóa hết maze
                for row in range(ROWS):
                    for col in range(COLS):
                        grid[row][col] = 0
                reset_path_states()

    if dijkstra_running and dijkstra_gen:
        try:
            step = next(dijkstra_gen)
            visited.clear()
            visited.update(step.get("visited", set()))
            frontier.clear()
            frontier.update(step.get("frontier", set()))
            if "path" in step:
                path.clear()
                path.extend(step["path"])
                dijkstra_running = False
                if algo_start_time is not None:
                    algo_elapsed_time = time.time() - algo_start_time
                    # --- Update history ---
                    path_length = len(path) if path else 0
                    history.append((algorithm_mode, algo_elapsed_time, path_length))
                    if len(history) > 4:
                        history.pop(0)
        except StopIteration:
            dijkstra_running = False
            if algo_start_time is not None and algo_elapsed_time == 0.0:
                algo_elapsed_time = time.time() - algo_start_time
                # --- Update history ---
                path_length = len(path) if path else 0
                history.append((algorithm_mode, algo_elapsed_time, path_length))
                if len(history) > 4:
                    history.pop(0)

    # Draw current algorithm mode on the screen
    font = pygame.font.SysFont(None, 28)
    mode_text = f"Algorithm: {algorithm_mode.upper()} (1:Dijkstra | 2:A* | 3:DFS | 4:BFS | TAB: Maze | `: Clear)"
    text_surface = font.render(mode_text, True, (0, 0, 0))

    screen.fill("black")
    draw_grid()
    screen.blit(text_surface, (20, 20))

    # Draw stopwatch (elapsed time) and history at bottom left, stacked vertically (Elapsed above, history below, but history is horizontal)
    font_time = pygame.font.SysFont(None, 28)
    font_hist = pygame.font.SysFont(None, 24)
    padding = 20
    spacing = 8

    # Calculate y position for bottom
    time_surface = font_time.render("Elapsed: 0.000 s", True, (0, 0, 0))
    hist_height = font_hist.get_height()
    bottom_y = HEIGHT - padding - time_surface.get_height() - (hist_height if history else 0) - (spacing if history else 0)

    # Draw stopwatch
    if dijkstra_running and algo_start_time is not None:
        elapsed = time.time() - algo_start_time
    else:
        elapsed = algo_elapsed_time
    time_text = f"Elapsed: {elapsed:.3f} s"
    time_surface = font_time.render(time_text, True, (0, 0, 0))
    screen.blit(time_surface, (padding, bottom_y))

    # Draw history horizontally below stopwatch if exists
    if history:
        y = bottom_y + time_surface.get_height() + spacing
        x = padding
        for idx, (algo, t, plen) in enumerate(reversed(history)):
            hist_text = f"{idx+1}. {algo.upper()} - {t:.3f} s - Len: {plen}"
            hist_surface = font_hist.render(hist_text, True, (0, 0, 0))
            screen.blit(hist_surface, (x, y))
            x += hist_surface.get_width() + 16  # horizontal spacing between history items

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
