import heapq
from collections import deque

DIRECTIONS = [(-1,0), (1,0), (0,-1), (0,1)]

def reconstruct_path(prev, start, end):
    path = []
    cur = end
    while cur and prev[cur[0]][cur[1]] is not None:
        path.append(cur)
        cur = prev[cur[0]][cur[1]]
    if cur == start:
        path.append(start)
        path.reverse()
        return path
    return []

def dijkstra_stepwise(start, end, rows, cols, grid):
    dist = [[float('inf')] * cols for _ in range(rows)]
    prev = [[None] * cols for _ in range(rows)]
    dist[start[0]][start[1]] = 0
    heap = [(0, start)]
    visited = set()
    frontier = {start}
    while heap:
        d, (r, c) = heapq.heappop(heap)
        if (r, c) in visited:
            continue
        visited.add((r, c))
        frontier.discard((r, c))
        yield {
            "visited": visited.copy(),
            "frontier": frontier.copy(),
            "current": (r, c),
        }
        if (r, c) == end:
            break
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                if dist[nr][nc] > d + 1:
                    dist[nr][nc] = d + 1
                    prev[nr][nc] = (r, c)
                    heapq.heappush(heap, (dist[nr][nc], (nr, nc)))
                    frontier.add((nr, nc))
    path = reconstruct_path(prev, start, end)
    yield {
        "visited": visited,
        "frontier": set(),
        "current": None,
        "path": path,
    }

def bfs_stepwise(start, end, rows, cols, grid):
    queue = deque([start])
    prev = [[None] * cols for _ in range(rows)]
    visited = set()
    frontier = {start}
    while queue:
        r, c = queue.popleft()
        if (r, c) in visited:
            continue
        visited.add((r, c))
        frontier.discard((r, c))
        yield {
            "visited": visited.copy(),
            "frontier": frontier.copy(),
            "current": (r, c),
        }
        if (r, c) == end:
            break
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and (nr, nc) not in visited:
                queue.append((nr, nc))
                if prev[nr][nc] is None:
                    prev[nr][nc] = (r, c)
                frontier.add((nr, nc))
    path = reconstruct_path(prev, start, end)
    yield {
        "visited": visited,
        "frontier": set(),
        "current": None,
        "path": path,
    }

def dfs_stepwise(start, end, rows, cols, grid):
    stack = [start]
    prev = [[None] * cols for _ in range(rows)]
    visited = set()
    frontier = {start}
    while stack:
        r, c = stack.pop()
        if (r, c) in visited:
            continue
        visited.add((r, c))
        frontier.discard((r, c))
        yield {
            "visited": visited.copy(),
            "frontier": frontier.copy(),
            "current": (r, c),
        }
        if (r, c) == end:
            break
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and (nr, nc) not in visited:
                stack.append((nr, nc))
                if prev[nr][nc] is None:
                    prev[nr][nc] = (r, c)
                frontier.add((nr, nc))
    path = reconstruct_path(prev, start, end)
    yield {
        "visited": visited,
        "frontier": set(),
        "current": None,
        "path": path,
    }

def astar_stepwise(start, end, rows, cols, grid):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    g_score = [[float('inf')] * cols for _ in range(rows)]
    f_score = [[float('inf')] * cols for _ in range(rows)]
    prev = [[None] * cols for _ in range(rows)]
    g_score[start[0]][start[1]] = 0
    f_score[start[0]][start[1]] = heuristic(start, end)
    heap = [(f_score[start[0]][start[1]], start)]
    visited = set()
    frontier = {start}
    while heap:
        _, (r, c) = heapq.heappop(heap)
        if (r, c) in visited:
            continue
        visited.add((r, c))
        frontier.discard((r, c))
        yield {
            "visited": visited.copy(),
            "frontier": frontier.copy(),
            "current": (r, c),
        }
        if (r, c) == end:
            break
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                tentative_g = g_score[r][c] + 1
                if tentative_g < g_score[nr][nc]:
                    g_score[nr][nc] = tentative_g
                    f_score[nr][nc] = tentative_g + heuristic((nr, nc), end)
                    prev[nr][nc] = (r, c)
                    heapq.heappush(heap, (f_score[nr][nc], (nr, nc)))
                    frontier.add((nr, nc))
    path = reconstruct_path(prev, start, end)
    yield {
        "visited": visited,
        "frontier": set(),
        "current": None,
        "path": path,
    }
