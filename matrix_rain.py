#!/usr/bin/env python3
"""
Matrix Rain Effect
==================
A terminal-based Matrix-style digital rain animation.
Uses only the standard library - no dependencies needed.

Usage: python3 matrix_rain.py
Press Ctrl+C to exit.
"""

import os
import random
import time
import shutil

CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*(){}[]|;:<>?"

def matrix_rain():
    cols, rows = shutil.get_terminal_size()
    drops = [random.randint(-rows, 0) for _ in range(cols)]
    trail_lengths = [random.randint(5, 20) for _ in range(cols)]

    GREEN = "\033[32m"
    BRIGHT_GREEN = "\033[92m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    print("\033[?25l", end="")  # hide cursor
    print("\033[2J", end="")    # clear screen

    try:
        while True:
            screen = []
            for row in range(rows):
                line = []
                for col in range(cols):
                    drop_pos = drops[col]
                    trail = trail_lengths[col]

                    if row == drop_pos:
                        line.append(f"{BRIGHT_GREEN}{random.choice(CHARS)}{RESET}")
                    elif drop_pos - trail < row < drop_pos:
                        fade = (drop_pos - row) / trail
                        if fade > 0.5:
                            line.append(f"{GREEN}{random.choice(CHARS)}{RESET}")
                        else:
                            line.append(f"{DIM}{GREEN}{random.choice(CHARS)}{RESET}")
                    else:
                        line.append(" ")
                screen.append("".join(line))

            print("\033[H" + "\n".join(screen), end="", flush=True)

            for i in range(cols):
                drops[i] += 1
                if drops[i] - trail_lengths[i] > rows:
                    drops[i] = random.randint(-10, 0)
                    trail_lengths[i] = random.randint(5, 20)

            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\033[?25h")  # show cursor
        print(RESET)
        print("\033[2J\033[H")  # clear screen

if __name__ == "__main__":
    matrix_rain()
