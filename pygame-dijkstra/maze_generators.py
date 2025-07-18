import random

def generate_maze_type_1(rows, cols, grid_ref, start_pos, end_pos):
    """
    Maze type 1: Random winding path with minimal heuristic advantage for A*
    Params:
        rows (int): Number of rows in the grid.
        cols (int): Number of columns in the grid.
        grid_ref (list of list): The grid to modify.
        start_pos (tuple): Start cell (row, col).
        end_pos (tuple): End cell (row, col).
    """
    # Set all cells as walls
    for row in range(rows):
        for col in range(cols):
            grid_ref[row][col] = 1

    # Start at the start cell, carve a random winding path to the end
    r, c = start_pos
    path_cells = [(r, c)]
    visited_cells = set(path_cells)
    while (r, c) != end_pos:
        neighbors = []
        # Only allow moves that stay in bounds and are not visited
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited_cells:
                # Prefer moves that get closer to the end, but allow some randomness
                dist_now = abs(r - end_pos[0]) + abs(c - end_pos[1])
                dist_next = abs(nr - end_pos[0]) + abs(nc - end_pos[1])
                weight = 2 if dist_next < dist_now else 1
                neighbors.extend([(nr, nc)] * weight)
        if not neighbors:
            # If stuck, backtrack to previous cell
            if len(path_cells) > 1:
                path_cells.pop()
                r, c = path_cells[-1]
                continue
            else:
                break  # No path possible
        next_cell = random.choice(neighbors)
        path_cells.append(next_cell)
        visited_cells.add(next_cell)
        r, c = next_cell

    # Carve the path in the grid
    for cell in path_cells:
        grid_ref[cell[0]][cell[1]] = 0

    # Randomly open enough extra cells so that walls are 50-60% of the grid
    total_cells = rows * cols
    open_cells = sum(1 for row in range(rows) for col in range(cols) if grid_ref[row][col] == 0)
    min_walls = int(total_cells * 0.5)
    max_walls = int(total_cells * 0.6)
    target_walls = random.randint(min_walls, max_walls)
    target_open = total_cells - target_walls
    extra_to_open = max(0, target_open - open_cells)
    opened = 0
    attempts = 0
    while opened < extra_to_open and attempts < total_cells * 5:
        rr = random.randint(0, rows - 1)
        cc = random.randint(0, cols - 1)
        if grid_ref[rr][cc] == 1 and (rr, cc) != start_pos and (rr, cc) != end_pos:
            grid_ref[rr][cc] = 0
            opened += 1
        attempts += 1

    # Ensure start and end are open
    grid_ref[start_pos[0]][start_pos[1]] = 0
    grid_ref[end_pos[0]][end_pos[1]] = 0

def generate_maze_type_2(rows, cols, grid_ref, start_pos, end_pos):
    """
    Maze type 2: Random maze with vertical bias using wall probability.
    Ensures at least 2 distinct paths from start to end.
    Params:
        rows (int): Number of rows in the grid.
        cols (int): Number of columns in the grid.
        grid_ref (list of list): The grid to modify.
        start_pos (tuple): Start cell (row, col).
        end_pos (tuple): End cell (row, col).
    """
    wall_prob = 0.3  # You can adjust this for more/less walls

    # Step 1: Fill grid with walls according to vertical bias
    for row in range(rows):
        for col in range(cols):
            prob = wall_prob + 0.3 if col % 2 == 1 else wall_prob
            grid_ref[row][col] = 1 if random.random() < prob else 0

    # Step 2: Carve two random paths from start to end
    def carve_random_path():
        r, c = start_pos
        path_cells = [(r, c)]
        visited_cells = set(path_cells)
        while (r, c) != end_pos:
            neighbors = []
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited_cells:
                    dist_now = abs(r - end_pos[0]) + abs(c - end_pos[1])
                    dist_next = abs(nr - end_pos[0]) + abs(nc - end_pos[1])
                    weight = 2 if dist_next < dist_now else 1
                    neighbors.extend([(nr, nc)] * weight)
            if not neighbors:
                if len(path_cells) > 1:
                    path_cells.pop()
                    r, c = path_cells[-1]
                    continue
                else:
                    break
            next_cell = random.choice(neighbors)
            path_cells.append(next_cell)
            visited_cells.add(next_cell)
            r, c = next_cell
        return path_cells

    path1 = carve_random_path()
    path2 = carve_random_path()

    # Step 3: Open the cells along both paths
    for cell in path1:
        grid_ref[cell[0]][cell[1]] = 0
    for cell in path2:
        grid_ref[cell[0]][cell[1]] = 0

    # Step 4: Ensure start and end are open
    grid_ref[start_pos[0]][start_pos[1]] = 0
    grid_ref[end_pos[0]][end_pos[1]] = 0

def generate_maze_type_3(rows, cols, grid_ref, start_pos, end_pos):
    """
    Maze type 3: Recursive Backtracking Maze (Perfect Maze)
    Ensures the start cell always has at least one open neighbor (a way out).
    Params:
        rows (int): Number of rows in the grid.
        cols (int): Number of columns in the grid.
        grid_ref (list of list): The grid to modify (if None, uses global grid).
        start_pos (tuple): Start cell (row, col). If None, uses global start.
        end_pos (tuple): End cell (row, col). If None, uses global end.
    """
    g = grid_ref
    s = start_pos
    e = end_pos

    # Initialize all cells as walls
    for row in range(rows):
        for col in range(cols):
            g[row][col] = -2  # wall

    def in_bounds(r, c):
        return 0 <= r < rows and 0 <= c < cols

    def neighbors(r, c):
        # 2-step neighbors (for maze carving)
        dirs = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        result = []
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc) and g[nr][nc] == -2:
                result.append((nr, nc))
        random.shuffle(result)
        return result

    # Start at a cell with odd coordinates for best results
    sr, sc = s
    sr = sr if sr % 2 == 1 else 1
    sc = sc if sc % 2 == 1 else 1
    stack = [(sr, sc)]
    g[sr][sc] = -1  # path

    while stack:
        r, c = stack[-1]
        nbs = neighbors(r, c)
        if nbs:
            nr, nc = nbs[0]
            # Remove wall between (r, c) and (nr, nc)
            wall_r, wall_c = (r + nr) // 2, (c + nc) // 2
            g[wall_r][wall_c] = -1  # path
            g[nr][nc] = -1  # path
            stack.append((nr, nc))
        else:
            stack.pop()

    # Convert -1 to 0 (path), -2 to 1 (wall)
    for row in range(rows):
        for col in range(cols):
            if g[row][col] == -1:
                g[row][col] = 0
            else:
                g[row][col] = 1

    # Ensure start and end are open
    g[s[0]][s[1]] = 0
    g[e[0]][e[1]] = 0

    # Ensure start cell has at least one open neighbor (a way out)
    sr, sc = s
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    has_exit = False
    for dr, dc in directions:
        nr, nc = sr + dr, sc + dc
        if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == 0:
            has_exit = True
            break
    if not has_exit:
        # Open a random neighbor cell
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = sr + dr, sc + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                g[nr][nc] = 0
                break