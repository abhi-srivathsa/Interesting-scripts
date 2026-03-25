#!/usr/bin/env python3
"""
ASCII Fireworks
===============
A colorful fireworks show right in your terminal!

Rockets launch from the bottom, explode into colorful bursts
of particles that fade out over time. Runs continuously until
you press Ctrl+C.

Usage:
  python3 fireworks.py

No external dependencies required.
"""

import random
import time
import math
import os
import sys
import signal

# ANSI colors
COLORS = [
    "\033[91m",  # bright red
    "\033[92m",  # bright green
    "\033[93m",  # bright yellow
    "\033[94m",  # bright blue
    "\033[95m",  # bright magenta
    "\033[96m",  # bright cyan
    "\033[97m",  # bright white
    "\033[33m",  # orange-ish
]
RESET = "\033[0m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

# Particle chars by age (bright -> dim -> fade)
PARTICLE_CHARS = ["*", "+", ".", "·", " "]
TRAIL_CHARS = ["|", ":", ".", " "]


def get_terminal_size():
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except Exception:
        return 80, 24


def move_cursor(x, y):
    # Clamp to terminal
    return f"\033[{int(y)};{int(x)}H"


def clear_screen():
    print("\033[2J\033[H", end="")


class Particle:
    def __init__(self, x, y, vx, vy, color, char_set=None):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.color = color
        self.age = 0
        self.max_age = random.randint(8, 16)
        self.chars = char_set or PARTICLE_CHARS

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.12  # gravity
        self.vx *= 0.96  # air resistance
        self.age += 1

    def is_alive(self):
        return self.age < self.max_age

    def draw_char(self):
        idx = min(int(self.age / self.max_age * len(self.chars)), len(self.chars) - 1)
        return self.chars[idx]


class Rocket:
    def __init__(self, x, height, color):
        self.x = float(x)
        self.y = float(height)
        self.target_y = float(random.randint(5, height // 2))
        self.vy = -random.uniform(1.5, 2.5)
        self.color = color
        self.exploded = False
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 4:
            self.trail.pop(0)
        self.y += self.vy
        if self.y <= self.target_y:
            self.exploded = True

    def is_done(self):
        return self.exploded


def explode(x, y, color, width, height):
    """Create a burst of particles in a circular pattern."""
    particles = []
    # Main burst
    num_particles = random.randint(20, 35)
    burst_type = random.choice(["circle", "star", "heart"])

    for i in range(num_particles):
        if burst_type == "circle":
            angle = (2 * math.pi * i) / num_particles + random.uniform(-0.2, 0.2)
            speed = random.uniform(0.4, 1.2)
        elif burst_type == "star":
            angle = (2 * math.pi * i) / num_particles
            # Alternating long and short spokes
            speed = 1.1 if i % 2 == 0 else 0.4
            speed += random.uniform(-0.1, 0.1)
        else:  # heart shape approximation
            t = (2 * math.pi * i) / num_particles
            hx = 16 * math.sin(t) ** 3
            hy = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            mag = math.sqrt(hx**2 + hy**2) or 1
            angle = math.atan2(hy, hx)
            speed = math.sqrt(hx**2 + hy**2) / 20

        # Account for terminal char aspect ratio (~2:1)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed * 0.5
        particles.append(Particle(x, y, vx, vy, color))

    # Add a few sparks with different color
    alt_color = random.choice(COLORS)
    for _ in range(8):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.8, 1.5)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed * 0.4
        p = Particle(x, y, vx, vy, alt_color)
        p.max_age = random.randint(5, 10)
        particles.append(p)

    return particles


def render(rockets, particles, width, height):
    """Build a frame buffer and print it."""
    # frame[row][col]
    frame = [[" "] * (width - 1) for _ in range(height - 1)]

    def put(x, y, ch, color):
        col = int(round(x)) - 1
        row = int(round(y)) - 1
        if 0 <= row < len(frame) and 0 <= col < len(frame[0]):
            frame[row][col] = color + ch + RESET

    # Draw rocket trails
    for rocket in rockets:
        for i, (tx, ty) in enumerate(rocket.trail):
            ch = TRAIL_CHARS[min(i, len(TRAIL_CHARS)-1)]
            put(tx, ty, ch, rocket.color)
        if not rocket.exploded:
            put(rocket.x, rocket.y, "^", rocket.color)

    # Draw particles
    for p in particles:
        if p.is_alive():
            ch = p.draw_char()
            if ch != " ":
                put(p.x, p.y, ch, p.color)

    # Print frame using cursor positioning to avoid flicker
    output = ["\033[H"]  # move to home
    for row in frame:
        output.append("".join(row))
        output.append("\n")
    sys.stdout.write("".join(output))
    sys.stdout.flush()


def main():
    signal.signal(signal.SIGINT, lambda *_: (
        sys.stdout.write(SHOW_CURSOR + RESET + "\n"),
        sys.stdout.flush(),
        sys.exit(0)
    ))

    width, height = get_terminal_size()
    clear_screen()
    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    rockets = []
    particles = []
    tick = 0
    launch_interval = random.randint(8, 20)

    try:
        while True:
            width, height = get_terminal_size()

            # Launch new rockets periodically
            if tick % launch_interval == 0:
                x = random.randint(5, width - 5)
                color = random.choice(COLORS)
                rockets.append(Rocket(x, height - 2, color))
                # Occasionally launch multiple at once
                if random.random() < 0.3:
                    x2 = random.randint(5, width - 5)
                    rockets.append(Rocket(x2, height - 2, random.choice(COLORS)))
                launch_interval = random.randint(10, 25)

            # Update rockets
            new_rockets = []
            for rocket in rockets:
                rocket.update()
                if rocket.is_done():
                    particles.extend(explode(rocket.x, rocket.y, rocket.color, width, height))
                else:
                    new_rockets.append(rocket)
            rockets = new_rockets

            # Update particles
            particles = [p for p in particles if p.is_alive()]
            for p in particles:
                p.update()

            # Render
            render(rockets, particles, width, height)

            tick += 1
            time.sleep(0.05)

    finally:
        sys.stdout.write(SHOW_CURSOR + RESET)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
