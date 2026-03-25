#!/usr/bin/env python3
"""
ASCII Fireworks
===============
A colorful animated fireworks display in your terminal. Watch rockets launch
and explode into dazzling bursts of ASCII art with realistic physics-based
particle trails.

Usage:
    python3 ascii_fireworks.py

Controls:
    - Press Ctrl+C to exit the show
"""

import math
import random
import time
import os
import sys

# ANSI colors and cursor control
COLORS = [
    "\033[91m",  # red
    "\033[92m",  # green
    "\033[93m",  # yellow
    "\033[94m",  # blue
    "\033[95m",  # magenta
    "\033[96m",  # cyan
    "\033[97m",  # white
]
RESET  = "\033[0m"
BOLD   = "\033[1m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

PARTICLE_CHARS = ["*", ".", "+", "o", "x", "·", "★", "✦"]
TRAIL_CHARS    = ["|", ":", ".", " "]  # rocket trail, top to bottom


def move_to(row, col):
    sys.stdout.write(f"\033[{row};{col}H")


def term_size():
    size = os.get_terminal_size()
    return size.lines, size.columns


class Particle:
    def __init__(self, x, y, vx, vy, color, char, lifetime):
        self.x  = x
        self.y  = y
        self.vx = vx
        self.vy = vy
        self.color    = color
        self.char     = char
        self.lifetime = lifetime
        self.age      = 0
        self.gravity  = 0.12

    def step(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += self.gravity     # gravity pulls downward
        self.vx *= 0.97             # air resistance
        self.age += 1

    @property
    def alive(self):
        return self.age < self.lifetime

    @property
    def dim_char(self):
        """Fade to dim dot as particle ages."""
        frac = self.age / self.lifetime
        if frac < 0.4:
            return self.char
        elif frac < 0.7:
            return "·"
        else:
            return "."


class Rocket:
    def __init__(self, cols):
        self.x      = random.randint(cols // 6, 5 * cols // 6)
        self.y      = 0          # tracks from bottom; rendered as rows - y
        self.speed  = random.uniform(1.0, 1.8)
        self.target = random.randint(10, 25)   # rows from top to explode
        self.color  = random.choice(COLORS)
        self.trail  = []         # list of (x, y) positions
        self.done   = False
        self.exploded = False

    def step(self):
        self.trail.insert(0, (self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop()
        self.y += self.speed

    def should_explode(self, rows):
        return (rows - int(self.y)) <= self.target


def explode(rocket, rows):
    """Return a list of Particle objects from a firework explosion."""
    particles = []
    cx = rocket.x
    cy = rows - int(rocket.y)
    color = rocket.color
    num_particles = random.randint(40, 70)

    for _ in range(num_particles):
        angle    = random.uniform(0, 2 * math.pi)
        speed    = random.uniform(0.4, 1.6)
        vx       = math.cos(angle) * speed
        vy       = math.sin(angle) * speed * 0.5   # squash vertically (chars are tall)
        char     = random.choice(PARTICLE_CHARS)
        lifetime = random.randint(14, 28)
        particles.append(Particle(cx, cy, vx, vy, color, char, lifetime))

    return particles


def draw_frame(screen, rows, cols):
    """Write the screen buffer to the terminal in one shot."""
    sys.stdout.write("\033[H")  # move home
    lines = []
    for r in range(rows - 1):
        line = []
        for c in range(cols):
            cell = screen.get((r, c))
            if cell:
                color, ch = cell
                line.append(f"{color}{ch}{RESET}")
            else:
                line.append(" ")
        lines.append("".join(line))
    sys.stdout.write("\n".join(lines))
    sys.stdout.flush()


def run():
    rows, cols = term_size()

    sys.stdout.write(HIDE_CURSOR)
    os.system("clear" if os.name == "posix" else "cls")

    # Title
    title = "  ★  ASCII FIREWORKS  ★  (Ctrl+C to exit)"
    move_to(rows, 1)
    sys.stdout.write(f"{BOLD}\033[93m{title}{RESET}")
    sys.stdout.flush()

    rockets   = []
    particles = []
    tick      = 0

    try:
        while True:
            rows, cols = term_size()
            screen = {}

            # Launch a new rocket occasionally
            if tick % random.randint(12, 22) == 0:
                rockets.append(Rocket(cols))

            # Update rockets
            still_flying = []
            for r in rockets:
                r.step()
                if r.should_explode(rows) and not r.exploded:
                    particles.extend(explode(r, rows))
                    r.exploded = True
                    r.done = True
                if not r.done:
                    still_flying.append(r)
            rockets = still_flying

            # Draw rocket trails
            for r in rockets:
                for i, (tx, ty) in enumerate(r.trail):
                    row = rows - int(ty)
                    col = int(tx)
                    if 1 <= row < rows and 1 <= col <= cols:
                        ch = TRAIL_CHARS[min(i, len(TRAIL_CHARS) - 1)]
                        screen[(row, col)] = (r.color, ch)

            # Update and draw particles
            live = []
            for p in particles:
                p.step()
                if p.alive:
                    row = int(p.y)
                    col = int(p.x)
                    if 1 <= row < rows and 1 <= col <= cols:
                        screen[(row, col)] = (p.color, p.dim_char)
                    live.append(p)
            particles = live

            draw_frame(screen, rows, cols)

            # Redraw static footer
            move_to(rows, 1)
            title_text = "  ★  ASCII FIREWORKS  ★  (Ctrl+C to exit)"
            sys.stdout.write(f"{BOLD}\033[93m{title_text}{RESET}")
            sys.stdout.flush()

            tick += 1
            time.sleep(0.05)   # ~20 fps

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(SHOW_CURSOR)
        os.system("clear" if os.name == "posix" else "cls")
        print("\033[93mHappy New Year! 🎆\033[0m\n")


if __name__ == "__main__":
    run()
