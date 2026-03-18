#!/usr/bin/env python3
"""
Memorable Password Generator
=============================
Generates strong but memorable passwords using a combination of
random words, numbers, and symbols. Also estimates crack time.

Usage:
    python3 password_generator.py              # Generate 1 password
    python3 password_generator.py -n 5         # Generate 5 passwords
    python3 password_generator.py -w 5         # Use 5 words
    python3 password_generator.py --passphrase # Generate a passphrase instead
"""

import argparse
import math
import random
import string
import secrets

ADJECTIVES = [
    "quick", "lazy", "happy", "brave", "calm", "dark", "eager", "fair",
    "gentle", "hollow", "icy", "jolly", "keen", "lively", "mystic",
    "noble", "odd", "proud", "quiet", "royal", "sharp", "tall",
    "vivid", "warm", "young", "zany", "bold", "crisp", "deep", "fierce",
    "golden", "hidden", "iron", "jade", "kind", "lunar", "mighty",
    "neon", "orange", "pale", "rapid", "silver", "tiny", "ultra",
    "violet", "wild", "xenon", "yellow", "zinc", "amber", "blazing",
    "cosmic", "daring", "emerald", "frozen", "gleaming", "hazy",
]

NOUNS = [
    "tiger", "cloud", "river", "stone", "flame", "ghost", "whale",
    "eagle", "frost", "blade", "crown", "dream", "forge", "grove",
    "haven", "ivory", "jewel", "knight", "lotus", "manor", "nexus",
    "orbit", "pearl", "quest", "raven", "spark", "tower", "unity",
    "vault", "wrath", "pixel", "cipher", "delta", "epoch", "falcon",
    "glacier", "harbor", "island", "jungle", "kayak", "lantern",
    "meteor", "nebula", "oasis", "prism", "quartz", "rocket",
    "summit", "thunder", "umbra", "vortex", "wizard", "zenith",
]

VERBS = [
    "runs", "flies", "dives", "leaps", "roars", "glows", "spins",
    "darts", "soars", "burns", "melts", "hides", "seeks", "builds",
    "rides", "jumps", "sails", "drifts", "climbs", "races",
]

SYMBOLS = "!@#$%^&*"


def generate_password(word_count=3):
    parts = []
    for _ in range(word_count):
        adj = secrets.choice(ADJECTIVES).capitalize()
        noun = secrets.choice(NOUNS).capitalize()
        parts.append(f"{adj}{noun}")

    num = secrets.randbelow(900) + 100
    sym = secrets.choice(SYMBOLS)

    password = sym.join(parts) + str(num)
    return password


def generate_passphrase(word_count=5):
    words = []
    all_words = ADJECTIVES + NOUNS + VERBS
    for _ in range(word_count):
        words.append(secrets.choice(all_words))
    separator = secrets.choice(["-", ".", "_", "+"])
    num = secrets.randbelow(90) + 10
    return separator.join(words) + str(num)


def estimate_crack_time(password):
    charset_size = 0
    if any(c in string.ascii_lowercase for c in password):
        charset_size += 26
    if any(c in string.ascii_uppercase for c in password):
        charset_size += 26
    if any(c in string.digits for c in password):
        charset_size += 10
    if any(c in string.punctuation for c in password):
        charset_size += 32

    entropy = len(password) * math.log2(charset_size) if charset_size else 0
    guesses = 2 ** entropy
    rate = 1e12  # 1 trillion guesses/sec (high-end GPU cluster)
    seconds = guesses / rate

    if seconds < 60:
        return f"{seconds:.1f} seconds", entropy
    elif seconds < 3600:
        return f"{seconds/3600:.1f} minutes", entropy
    elif seconds < 86400:
        return f"{seconds/3600:.1f} hours", entropy
    elif seconds < 31536000:
        return f"{seconds/86400:.1f} days", entropy
    elif seconds < 31536000 * 1000:
        return f"{seconds/31536000:.1f} years", entropy
    elif seconds < 31536000 * 1e6:
        return f"{seconds/31536000/1000:.1f} thousand years", entropy
    elif seconds < 31536000 * 1e9:
        return f"{seconds/31536000/1e6:.1f} million years", entropy
    else:
        return f"{seconds/31536000/1e9:.1f} billion years", entropy


def strength_bar(entropy):
    if entropy < 40:
        label, color = "WEAK", "\033[91m"
    elif entropy < 60:
        label, color = "FAIR", "\033[93m"
    elif entropy < 80:
        label, color = "STRONG", "\033[92m"
    else:
        label, color = "VERY STRONG", "\033[96m"

    bars = int(min(entropy / 5, 20))
    return f"{color}[{'█' * bars}{'░' * (20 - bars)}] {label}\033[0m"


def main():
    parser = argparse.ArgumentParser(description="Generate memorable passwords")
    parser.add_argument("-n", "--count", type=int, default=1, help="Number of passwords")
    parser.add_argument("-w", "--words", type=int, default=3, help="Words per password")
    parser.add_argument("--passphrase", action="store_true", help="Generate passphrases")
    args = parser.parse_args()

    print("\n🔐 Memorable Password Generator\n" + "=" * 40)

    for i in range(args.count):
        if args.passphrase:
            pwd = generate_passphrase(args.words)
        else:
            pwd = generate_password(args.words)

        crack_time, entropy = estimate_crack_time(pwd)
        bar = strength_bar(entropy)

        print(f"\n  Password:   {pwd}")
        print(f"  Length:     {len(pwd)} chars")
        print(f"  Entropy:    {entropy:.0f} bits")
        print(f"  Crack time: {crack_time} (at 1T guesses/sec)")
        print(f"  Strength:   {bar}")

    print()


if __name__ == "__main__":
    main()
