#!/usr/bin/env python3
"""
Wordle - Terminal Edition
=========================
The classic word-guessing game in your terminal!

How to play:
  - Guess the 5-letter word in 6 tries
  - After each guess, tiles change color:
      [G] Green  = correct letter, correct position
      [Y] Yellow = correct letter, wrong position
      [.] Gray   = letter not in word

Usage:
  python3 wordle.py

No external dependencies required.
"""

import random
import sys
import os

# ANSI color codes
GREEN  = "\033[42m\033[30m"
YELLOW = "\033[43m\033[30m"
GRAY   = "\033[100m\033[37m"
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

WORD_LIST = [
    "apple", "brave", "crane", "dwarf", "ember", "flair", "gloom", "haste",
    "inbox", "joust", "karma", "latch", "mirth", "noble", "ozone", "pixel",
    "quart", "rivet", "shale", "thorn", "umbra", "venom", "whelp", "xenon",
    "yacht", "zonal", "abide", "blunt", "crimp", "dowel", "expel", "flint",
    "gripe", "hound", "irony", "jovial","knack", "lucid", "mulch", "nerve",
    "onset", "plumb", "quirk", "regal", "snout", "trove", "unfed", "vigor",
    "witch", "extol", "zebra", "ample", "blaze", "churn", "depot", "enact",
    "frost", "gavel", "helix", "ivory", "jewel", "knave", "lunar", "mince",
    "notch", "oxide", "prism", "queen", "rogue", "spire", "tithe", "untie",
    "vouch", "waltz", "expunge","yearn", "zilch", "abyss", "bloom", "cleft",
    "douse", "elbow", "fudge", "groan", "hutch", "inept", "judge", "kneel",
    "leach", "marsh", "night", "ought", "perch", "quill", "ranch", "scald",
    "torch", "usurp", "voila", "wring", "exact", "young", "zones", "adorn",
    "brisk", "civic", "drool", "ethic", "fable", "guile", "havoc", "inlet",
    "joker", "koala", "lofty", "maple", "nudge", "octet", "plank", "raspy",
    "savvy", "twirl", "ultra", "vying", "woken", "oxbow", "yeild", "zingy",
    "acute", "bland", "crisp", "digit", "eerie", "filth", "gruff", "hinge",
    "icily", "jazzy", "kinky", "lyric", "moody", "nifty", "offal", "putty",
    "quota", "rusty", "slump", "tacky", "unfair","valor", "windy", "expat",
    "zesty", "aloft", "boxer", "clown", "delta", "eject", "floss", "graze",
    "hippo", "icing", "jumpy", "knobs", "llama", "metro", "nymph", "optic",
    "prone", "query", "risky", "stump", "tryst", "upend", "valve", "whirl",
    "exert", "yolks", "zippy", "angel", "brood", "creed", "delta", "envoy",
    "fewer", "glare", "hover", "imply", "joust", "knock", "light", "muted",
    "north", "other", "proud", "rapid", "slick", "tasks", "urban", "visit",
    "water", "exist", "years", "zones",
]

# Deduplicate and keep only 5-letter words
WORD_LIST = list({w.lower() for w in WORD_LIST if len(w) == 5})

VALID_GUESSES = set(WORD_LIST)  # In a real game this would be much larger

MAX_ATTEMPTS = 6
WORD_LENGTH = 5


def clear_line():
    print("\033[A\033[K", end="")


def color_guess(guess, target):
    """Return colored string showing correctness of each letter."""
    result = []
    target_chars = list(target)
    guess_chars = list(guess)
    colors = [GRAY] * WORD_LENGTH

    # First pass: mark greens
    for i in range(WORD_LENGTH):
        if guess_chars[i] == target_chars[i]:
            colors[i] = GREEN
            target_chars[i] = None
            guess_chars[i] = None

    # Second pass: mark yellows
    for i in range(WORD_LENGTH):
        if guess_chars[i] is not None:
            if guess_chars[i] in target_chars:
                colors[i] = YELLOW
                target_chars[target_chars.index(guess_chars[i])] = None

    # Build display
    for i, letter in enumerate(guess):
        result.append(f"{colors[i]} {letter.upper()} {RESET}")

    return "".join(result)


def display_keyboard(guessed_letters):
    """Display keyboard with color hints."""
    rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    print()
    for row in rows:
        print("  ", end="")
        for ch in row:
            if ch in guessed_letters:
                color, _ = guessed_letters[ch]
                print(f"{color} {ch.upper()} {RESET}", end="")
            else:
                print(f"{DIM} {ch.upper()} {RESET}", end="")
        print()
    print()


def play():
    os.system("clear" if os.name != "nt" else "cls")
    target = random.choice(WORD_LIST)
    attempts = []
    guessed_letters = {}  # letter -> (color, priority)
    color_priority = {GREEN: 3, YELLOW: 2, GRAY: 1}

    print(f"\n{BOLD}  W O R D L E  — Terminal Edition{RESET}")
    print(f"  Guess the {WORD_LENGTH}-letter word in {MAX_ATTEMPTS} tries.\n")

    # Draw empty board
    for _ in range(MAX_ATTEMPTS):
        print("  " + "".join(f"[ . ]" for _ in range(WORD_LENGTH)))
    print()

    won = False
    for attempt_num in range(MAX_ATTEMPTS):
        # Move cursor up to the right row
        rows_up = MAX_ATTEMPTS - attempt_num + 2
        print(f"\033[{rows_up}A", end="")

        while True:
            raw = input(f"  Guess {attempt_num+1}/{MAX_ATTEMPTS}: ").strip().lower()
            # Clear the input line
            print("\033[A\033[K", end="")
            if len(raw) != WORD_LENGTH:
                print(f"\033[K  ⚠  Please enter a {WORD_LENGTH}-letter word.", end="\r")
                import time; time.sleep(1)
                print("\033[K", end="\r")
                continue
            if raw not in VALID_GUESSES:
                # Accept any 5-letter alpha string to be lenient
                if not raw.isalpha():
                    print(f"\033[K  ⚠  Letters only, please.", end="\r")
                    import time; time.sleep(1)
                    print("\033[K", end="\r")
                    continue
            break

        attempts.append(raw)

        # Print colored guess in the board row
        colored = color_guess(raw, target)
        print(f"  {colored}\033[K")

        # Move cursor back down
        rows_down = MAX_ATTEMPTS - attempt_num - 1
        if rows_down > 0:
            print(f"\033[{rows_down}B", end="")

        # Update keyboard colors
        target_chars = list(target)
        guess_chars = list(raw)
        temp_colors = [GRAY] * WORD_LENGTH
        temp_target = list(target)

        for i in range(WORD_LENGTH):
            if guess_chars[i] == temp_target[i]:
                temp_colors[i] = GREEN
                temp_target[i] = None
                guess_chars[i] = None
        for i in range(WORD_LENGTH):
            if guess_chars[i] is not None:
                if guess_chars[i] in temp_target:
                    temp_colors[i] = YELLOW
                    temp_target[temp_target.index(guess_chars[i])] = None

        for i, letter in enumerate(raw):
            c = temp_colors[i]
            prev = guessed_letters.get(letter, (GRAY, 0))
            if color_priority[c] > prev[1]:
                guessed_letters[letter] = (c, color_priority[c])

        if raw == target:
            won = True
            break

    # Final output
    print()
    display_keyboard(guessed_letters)

    if won:
        praise = ["Genius!", "Magnificent!", "Impressive!", "Splendid!", "Great!", "Phew!"]
        idx = len(attempts) - 1
        print(f"  {BOLD}{GREEN} {praise[idx]} {RESET}  You got it in {len(attempts)} {'try' if len(attempts)==1 else 'tries'}!\n")
    else:
        print(f"  Better luck next time! The word was {BOLD}{target.upper()}{RESET}.\n")


def main():
    try:
        while True:
            play()
            again = input("  Play again? [y/N] ").strip().lower()
            if again != "y":
                print("  Thanks for playing!\n")
                break
            print()
    except KeyboardInterrupt:
        print("\n\n  Thanks for playing!\n")


if __name__ == "__main__":
    main()
