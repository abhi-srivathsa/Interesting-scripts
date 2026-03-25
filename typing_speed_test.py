#!/usr/bin/env python3
"""
Typing Speed Test
=================
A terminal-based typing speed test that measures your WPM (words per minute)
and accuracy. Choose from different difficulty levels with varying text complexity.

Usage:
    python3 typing_speed_test.py

Controls:
    - Choose a difficulty level (easy/medium/hard)
    - Read the displayed text, then type it as fast and accurately as possible
    - Press Enter when done
    - Press Ctrl+C to quit
"""

import time
import random
import sys
import os

# ANSI color codes
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

TEXTS = {
    "easy": [
        "the cat sat on the mat and looked at the bat",
        "a big red dog ran fast and played in the sun",
        "she sells sea shells by the sea shore on hot days",
        "the quick brown fox jumps over the lazy dog today",
        "all good things come to those who wait and work hard",
    ],
    "medium": [
        "programming is the art of telling another human what one wants the computer to do",
        "the best way to predict the future is to invent it and make it happen",
        "in the middle of difficulty lies opportunity for those who seek it out",
        "a journey of a thousand miles begins with a single step forward in life",
        "success is not final failure is not fatal it is the courage to continue",
    ],
    "hard": [
        "the Byzantine fault-tolerant consensus algorithm ensures distributed systems remain consistent despite arbitrary node failures",
        "polymorphism allows objects of different types to be treated through a uniform interface reducing coupling significantly",
        "the Fibonacci sequence exhibits exponential growth where each term is the sum of its two predecessors",
        "cryptographic hash functions produce fixed-length digests that make preimage attacks computationally infeasible",
        "asynchronous programming paradigms leverage event loops to maximize throughput without blocking execution threads",
    ],
}


def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")


def print_header():
    clear_screen()
    print(f"{BOLD}{CYAN}╔══════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║         ⌨  TYPING SPEED TEST             ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════╝{RESET}")
    print()


def choose_difficulty():
    print(f"{BOLD}Choose difficulty:{RESET}")
    print(f"  {GREEN}1{RESET}. Easy   — short, simple words")
    print(f"  {YELLOW}2{RESET}. Medium — full sentences")
    print(f"  {RED}3{RESET}. Hard   — technical/complex text")
    print()
    while True:
        choice = input(f"{DIM}Enter choice (1-3): {RESET}").strip()
        if choice == "1":
            return "easy"
        elif choice == "2":
            return "medium"
        elif choice == "3":
            return "hard"
        else:
            print(f"{RED}Please enter 1, 2, or 3.{RESET}")


def calculate_accuracy(original, typed):
    """Character-level accuracy vs the target text."""
    if not typed:
        return 0.0
    correct = sum(1 for i, ch in enumerate(original) if i < len(typed) and typed[i] == ch)
    return (correct / len(original)) * 100


def show_comparison(original, typed):
    """Print the original text with correct chars in green and mistakes in red."""
    print(f"\n{BOLD}Comparison (green = correct, red = wrong/missing):{RESET}")
    out = []
    for i, ch in enumerate(original):
        if i >= len(typed):
            out.append(f"{DIM}{ch}{RESET}")
        elif typed[i] == ch:
            out.append(f"{GREEN}{ch}{RESET}")
        else:
            out.append(f"{RED}{typed[i]}{RESET}")
    if len(typed) > len(original):
        for ch in typed[len(original):]:
            out.append(f"{RED}{ch}{RESET}")
    print("  " + "".join(out))


def run_test(difficulty):
    text = random.choice(TEXTS[difficulty])
    word_count = len(text.split())
    diff_color = {"easy": GREEN, "medium": YELLOW, "hard": RED}[difficulty]

    print_header()
    print(f"{BOLD}Difficulty:{RESET} {diff_color}{difficulty.upper()}{RESET}  {DIM}({word_count} words){RESET}")
    print()
    print(f"{BOLD}Text to type:{RESET}")
    print(f"\n  {YELLOW}{text}{RESET}\n")
    print(f"{DIM}Press Enter when you're ready — the timer starts immediately after.{RESET}")
    input()

    print_header()
    print(f"{BOLD}Text:{RESET}  {YELLOW}{text}{RESET}\n")
    print(f"{BOLD}Type now and press Enter when done:{RESET}\n")

    start = time.time()
    try:
        typed = input("  ")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test cancelled.{RESET}")
        return

    elapsed = time.time() - start

    minutes   = elapsed / 60
    raw_wpm   = word_count / minutes if minutes > 0 else 0
    accuracy  = calculate_accuracy(text, typed)
    adj_wpm   = raw_wpm * (accuracy / 100)

    show_comparison(text, typed)

    print(f"\n{BOLD}{CYAN}──────────── RESULTS ────────────{RESET}")
    print(f"  {BOLD}Time:{RESET}          {elapsed:.2f}s")
    print(f"  {BOLD}Raw WPM:{RESET}       {raw_wpm:.1f}")
    print(f"  {BOLD}Accuracy:{RESET}      {accuracy:.1f}%")
    print(f"  {BOLD}Adjusted WPM:{RESET}  {adj_wpm:.1f}")

    if adj_wpm >= 80:
        rating = f"{GREEN}Expert Typist! 🏆{RESET}"
    elif adj_wpm >= 60:
        rating = f"{CYAN}Advanced Typist 🌟{RESET}"
    elif adj_wpm >= 40:
        rating = f"{YELLOW}Intermediate Typist 👍{RESET}"
    elif adj_wpm >= 20:
        rating = f"{YELLOW}Beginner Typist 📝{RESET}"
    else:
        rating = f"{RED}Keep Practicing! 💪{RESET}"

    print(f"  {BOLD}Rating:{RESET}        {rating}")
    print(f"{BOLD}{CYAN}─────────────────────────────────{RESET}\n")


def main():
    try:
        while True:
            print_header()
            difficulty = choose_difficulty()
            run_test(difficulty)
            again = input(f"{DIM}Play again? (y/n): {RESET}").strip().lower()
            if again != "y":
                print(f"\n{CYAN}Thanks for playing! Keep practicing! ⌨{RESET}\n")
                break
    except KeyboardInterrupt:
        print(f"\n\n{CYAN}Goodbye!{RESET}\n")


if __name__ == "__main__":
    main()
