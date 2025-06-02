#!/usr/bin/env python3
"""Automated refactor script for the Crypto Sniping Bot project.

Run from the project root **after** extracting `crypto-sniping-bot.zip`.
The script:
  1. Creates the folders prescribed in `complete-project-setup.md`.
  2. Moves/renames every legacy file into its new home.
  3. Adds missing helper files (e.g. `bot/__init__.py`).
  4. Makes `scripts/demo.sh` executable.

It is idempotent—running it again is safe—so you can test freely.
"""
from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration – original → new path mapping
# ---------------------------------------------------------------------------
FILE_MAP: dict[str, str] = {
    "blockchain-interface.py": "bot/blockchain.py",
    "config-module.py": "bot/config.py",
    "honeypot-checker.py": "bot/honeypot.py",
    "python-bot-main.py": "bot/sniper.py",
    "trading-engine.py": "bot/trading.py",
    "sniper-contract.txt": "contracts/Sniper.sol",
    "contract-tests.js": "tests/contract.test.js",
    "python-tests.py": "tests/test_sniper.py",
    "demo-script.sh": "scripts/demo.sh",
    "deploy-script.js": "scripts/deploy.js",
    "env-example.sh": ".env.example",
    "package-json.json": "package.json",
    "requirements-txt.txt": "requirements.txt",
    "gitignore-file.txt": ".gitignore",
    "readme-file.md": "README.md",
    "crypto-sniper-mvp-plan.md": "docs/crypto-sniper-mvp-plan.md",
}

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent


def ensure_directory(path: Path) -> None:
    """Create parent directories for *path* if they don't already exist."""
    path.parent.mkdir(parents=True, exist_ok=True)


def move(src: Path, dst: Path) -> None:
    """Move *src* to *dst* (overwriting if necessary)."""
    if not src.exists():
        print(f"[WARN] Missing source: {src.relative_to(ROOT)} – skipping")
        return

    ensure_directory(dst)

    if dst.exists():
        # Overwrite only if different path; skip if same file already moved
        if src.samefile(dst):
            return
        print(f"[INFO] Overwriting: {dst.relative_to(ROOT)}")
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()

    shutil.move(src, dst)
    print(f"[OK] {src.relative_to(ROOT)}  →  {dst.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Main routine
# ---------------------------------------------------------------------------

def main() -> None:
    # 1. Move files
    for old, new in FILE_MAP.items():
        move(ROOT / old, ROOT / new)

    # 2. Guarantee bot/__init__.py exists
    init_file = ROOT / "bot/__init__.py"
    ensure_directory(init_file)
    if not init_file.exists():
        init_file.touch()
        print("[OK] Created bot/__init__.py")

    # 3. Ensure scripts/demo.sh is executable
    demo_sh = ROOT / "scripts/demo.sh"
    if demo_sh.exists():
        current = demo_sh.stat().st_mode
        if not (current & stat.S_IXUSR):
            demo_sh.chmod(current | stat.S_IXUSR)
            print("[OK] Marked scripts/demo.sh as executable")

    # 4. Print summary tree (optional)
    print("\nDone! Suggested structure now:\n")
    try:
        from tree import main as tree_main  # if user has 'tree' module installed

        tree_main(str(ROOT))
    except Exception:
        # Fallback: simple walk
        for path in sorted(ROOT.rglob("*")):
            indent = " " * (len(path.relative_to(ROOT).parts) - 1) * 2
            print(f"{indent}{path.name}")


if __name__ == "__main__":
    main()
