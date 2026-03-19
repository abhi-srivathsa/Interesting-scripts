#!/usr/bin/env python3
"""
Conway's Game of Life - Terminal Animation
==========================================
A classic cellular automaton devised by mathematician John Conway in 1970.

Rules:
  1. Any live cell with fewer than 2 live neighbors dies (underpopulation)
  2. Any live cell with 2 or 3 live neighbors survives
  3. Any live cell with more than 3 live neighbors dies (overpopulation)
  4. Any dead cell with exactly 3 live neighbors becomes alive (reproduction)

Usage:
  python3 conways_life.py              # Random starting pattern
  python3 conways_life.py --pattern glider
  python3 conways_life.py --pattern pulsar
  python3 conways_life.py --pattern gosper  # Gosper's Glider Gun
  python3 conways_life.py --rows 30 --cols 80 --speed 0.1

Controls:
  Ctrl+C to quit
"""

import argparse
import os
import random
import sys
import time

# ANSI color codes
ALIVE = "\033[92m█\033[0m"   # Green filled block
DEAD  = "\033[90m·\033[0m"   # Dark grey dot
CLEAR = "\033[2J\033[H"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

PATTERNS = {
    "glider": [
        (0, 1),
        (1, 2),
        (2, 0), (2, 1), (2, 2),
    ],
    "blinker": [
        (1, 0), (1, 1), (1, 2),
    ],
    "pulsar": [
        (2,4),(2,5),(2,6),(2,10),(2,11),(2,12),
        (4,2),(4,7),(4,9),(4,14),
        (5,2),(5,7),(5,9),(5,14),
        (6,2),(6,7),(6,9),(6,14),
        (7,4),(7,5),(7,6),(7,10),(7,11),(7,12),
        (9,4),(9,5),(9,6),(9,10),(9,11),(9,12),
        (10,2),(10,7),(10,9),(10,14),
        (11,2),(11,7),(11,9),(11,14),
        (12,2),(12,7),(12,9),(12,14),
        (14,4),(14,5),(14,6),(14,10),(14,11),(14,12),
    ],
    "gosper": [
        (5,1),(5,2),(6,1),(6,2),
        (5,11),(6,11),(7,11),(4,12),(8,12),(3,13),(9,13),
        (3,14),(9,14),(6,15),(4,16),(8,16),(5,17),(6,17),(7,17),(6,18),
        (3,21),(4,21),(5,21),(3,22),(4,22),(5,22),(2,23),(6,23),
        (1,25),(2,25),(6,25),(7,25),
        (3,35),(4,35),(3,36),(4,36),
    ],
}


def make_empty_grid(rows, cols):
    return [[False] * cols for _ in range(rows)]


def random_grid(rows, cols, density=0.3):
    grid = make_empty_grid(rows, cols)
    for r in range(rows):
        for c in range(cols):
            grid[r][c] = random.random() < density
    return grid


def place_pattern(grid, pattern, offset_r=0, offset_c=0):
    rows = len(grid)
    cols = len(grid[0])
    for (r, c) in pattern:
        nr, nc = r + offset_r, c + offset_c
        if 0 <= nr < rows and 0 <= nc < cols:
            grid[nr][nc] = True
    return grid


def count_neighbors(grid, r, c):
    rows = len(grid)
    cols = len(grid[0])
    count = 0
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr = (r + dr) % rows  # wrap around
            nc = (c + dc) % cols
            if grid[nr][nc]:
                count += 1
    return count


def next_generation(grid):
    rows = len(grid)
    cols = len(grid[0])
    new_grid = make_empty_grid(rows, cols)
    for r in range(rows):
        for c in range(cols):
            neighbors = count_neighbors(grid, r, c)
            if grid[r][c]:
                new_grid[r][c] = neighbors in (2, 3)
            else:
                new_grid[r][c] = neighbors == 3
    return new_grid


def render(grid, generation, population):
    rows = len(grid)
    cols = len(grid[0])
    lines = []
    lines.append(f"\033[1mConway's Game of Life\033[0m  "
                 f"Gen: \033[93m{generation:>5}\033[0m  "
                 f"Pop: \033[96m{population:>5}\033[0m  "
                 f"(\033[90mCtrl+C to quit\033[0m)")
    lines.append("─" * (cols * 1 + 2))
    for row in grid:
        lines.append("".join(ALIVE if cell else DEAD for cell in row))
    lines.append("─" * (cols * 1 + 2))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Conway's Game of Life in the terminal")
    parser.add_argument("--rows", type=int, default=28, help="Grid height (default: 28)")
    parser.add_argument("--cols", type=int, default=60, help="Grid width (default: 60)")
    parser.add_argument("--speed", type=float, default=0.08, help="Seconds per generation (default: 0.08)")
    parser.add_argument("--pattern", choices=list(PATTERNS.keys()) + ["random"],
                        default="random", help="Starting pattern")
    args = parser.parse_args()

    rows, cols = args.rows, args.cols

    if args.pattern == "random":
        grid = random_grid(rows, cols, density=0.3)
    else:
        grid = make_empty_grid(rows, cols)
        pattern = PATTERNS[args.pattern]
        offset_r = rows // 2 - 8
        offset_c = cols // 2 - 10
        grid = place_pattern(grid, pattern, max(0, offset_r), max(0, offset_c))

    print(HIDE_CURSOR, end="")
    generation = 0
    try:
        while True:
            population = sum(cell for row in grid for cell in row)
            frame = render(grid, generation, population)
            sys.stdout.write(CLEAR + frame + "\n")
            sys.stdout.flush()
            grid = next_generation(grid)
            generation += 1
            time.sleep(args.speed)
    except KeyboardInterrupt:
        pass
    finally:
        print(SHOW_CURSOR, end="")
        print(f"\nSimulation ended after {generation} generations.")


if __name__ == "__main__":
    main()
