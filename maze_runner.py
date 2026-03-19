#!/usr/bin/env python3
"""
Maze Runner - Generator & Animated Solver
==========================================
Generates a random perfect maze using Recursive Backtracking (DFS),
then animates solving it using Breadth-First Search (BFS) to find
the shortest path.

Features:
  - Procedurally generated unique maze every run
  - Animated BFS solver that shows the search frontier
  - Highlights the final shortest path in a different color
  - Adjustable size and animation speed

Usage:
  python3 maze_runner.py
  python3 maze_runner.py --width 20 --height 10
  python3 maze_runner.py --width 30 --height 15 --speed 0.02

Controls:
  Ctrl+C to quit at any time
"""

import argparse
import collections
import random
import sys
import time

# ANSI codes
RESET   = "\033[0m"
WALL    = "\033[37m█\033[0m"          # White wall
PATH    = "  "                          # Empty passage (2 chars wide)
START   = "\033[92m S\033[0m"          # Green S
END     = "\033[91m E\033[0m"          # Red E
VISITED = "\033[34m ·\033[0m"          # Blue dot (BFS frontier)
FINAL   = "\033[93m *\033[0m"          # Yellow star (shortest path)
CLEAR   = "\033[2J\033[H"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"


def generate_maze(width, height):
    """Generate a perfect maze using recursive backtracking (iterative DFS)."""
    # Each cell tracks which walls are removed: N, S, E, W
    # True = wall exists
    walls = {(r, c): {"N": True, "S": True, "E": True, "W": True}
             for r in range(height) for c in range(width)}
    visited = set()
    directions = [("N", -1, 0), ("S", 1, 0), ("E", 0, 1), ("W", 0, -1)]
    opposite = {"N": "S", "S": "N", "E": "W", "W": "E"}

    stack = [(0, 0)]
    visited.add((0, 0))

    while stack:
        r, c = stack[-1]
        neighbors = []
        for d, dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < height and 0 <= nc < width and (nr, nc) not in visited:
                neighbors.append((d, nr, nc))
        if neighbors:
            d, nr, nc = random.choice(neighbors)
            walls[(r, c)][d] = False
            walls[(nr, nc)][opposite[d]] = False
            visited.add((nr, nc))
            stack.append((nr, nc))
        else:
            stack.pop()

    return walls


def render_maze(walls, width, height, visited_cells=None, path=None):
    """Render maze as a list of strings (each row is two display rows)."""
    if visited_cells is None:
        visited_cells = set()
    if path is None:
        path = set()

    lines = []
    # Top border
    lines.append(WALL * (width * 2 + 1))

    for r in range(height):
        # Middle row: left wall + cells + right wall
        row_cells = WALL  # left border
        for c in range(width):
            cell = (r, c)
            if cell == (0, 0):
                row_cells += START
            elif cell == (height - 1, width - 1):
                row_cells += END
            elif cell in path:
                row_cells += FINAL
            elif cell in visited_cells:
                row_cells += VISITED
            else:
                row_cells += PATH
            # East wall
            if walls[cell]["E"]:
                row_cells += WALL
            else:
                row_cells += PATH

        lines.append(row_cells)

        # Bottom wall row
        bottom = WALL
        for c in range(width):
            # South wall
            if walls[(r, c)]["S"]:
                bottom += WALL + WALL
            else:
                bottom += PATH + WALL
        lines.append(bottom)

    return lines


def bfs_solve(walls, width, height):
    """BFS from (0,0) to (height-1, width-1). Yields visited sets and path steps."""
    directions = [("N", -1, 0), ("S", 1, 0), ("E", 0, 1), ("W", 0, -1)]
    start = (0, 0)
    end = (height - 1, width - 1)

    queue = collections.deque([[start]])
    seen = {start}

    while queue:
        current_path = queue.popleft()
        cell = current_path[-1]
        yield seen, None  # yield frontier state

        if cell == end:
            yield seen, current_path
            return

        r, c = cell
        for d, dr, dc in directions:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)
            if (0 <= nr < height and 0 <= nc < width
                    and neighbor not in seen
                    and not walls[cell][d]):
                seen.add(neighbor)
                queue.append(current_path + [neighbor])

    yield seen, None  # no path found


def print_frame(lines, title):
    sys.stdout.write(CLEAR)
    sys.stdout.write(f"\033[1m{title}\033[0m\n")
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(description="Maze generator and animated BFS solver")
    parser.add_argument("--width",  type=int, default=20, help="Maze width in cells (default: 20)")
    parser.add_argument("--height", type=int, default=10, help="Maze height in cells (default: 10)")
    parser.add_argument("--speed",  type=float, default=0.03, help="Animation delay in seconds (default: 0.03)")
    args = parser.parse_args()

    W, H = args.width, args.height
    speed = args.speed

    print(HIDE_CURSOR, end="")
    try:
        # --- Generate ---
        walls = generate_maze(W, H)
        lines = render_maze(walls, W, H)
        print_frame(lines, f"Maze {W}×{H}  |  \033[92mS\033[0m=Start  \033[91mE\033[0m=End  Generating...")
        time.sleep(0.5)

        # --- Solve (animated BFS) ---
        solver = bfs_solve(walls, W, H)
        final_path = None
        step = 0

        for visited, path in solver:
            if path is not None:
                final_path = set(path)
                break
            # Throttle rendering for speed
            step += 1
            if step % max(1, (W * H) // 300) == 0:
                lines = render_maze(walls, W, H, visited_cells=visited)
                print_frame(lines,
                    f"Maze {W}×{H}  |  \033[34m·\033[0m=Searching  "
                    f"Explored: \033[96m{len(visited)}\033[0m cells")
                time.sleep(speed)

        # --- Show solution ---
        if final_path:
            lines = render_maze(walls, W, H, path=final_path)
            print_frame(lines,
                f"Maze {W}×{H}  |  \033[93m*\033[0m=Shortest path  "
                f"Length: \033[93m{len(final_path)}\033[0m steps  Solved!")
        else:
            print("No path found (this shouldn't happen with a perfect maze).")

        time.sleep(3)

    except KeyboardInterrupt:
        pass
    finally:
        print(SHOW_CURSOR, end="")
        print("\nThanks for running Maze Runner!")


if __name__ == "__main__":
    main()
