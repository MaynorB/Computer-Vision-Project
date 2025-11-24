#!/usr/bin/env python3
"""
setup_project.py — Minimal COLMAP project initializer.

This script is meant to LIVE INSIDE the project folder.
It initializes missing subdirectories and can prune unexpected folders.

Usage:
    python setup_project.py
    python setup_project.py --prune --yes
"""

import os
import argparse
import shutil

ALLOWED_FOLDERS = {"colmap_workspace", "output", "scripts", "README.md", "setup_project.py"}


def mkdir(path):
    os.makedirs(path, exist_ok=True)
    print(f"[✓] {path}")


def prune_folders(root, confirm):
    allowed = {os.path.normpath(x) for x in ALLOWED_FOLDERS}
    children = os.listdir(root)
    children = [c for c in children if not c.startswith(".")]  # ignore hidden

    to_remove = [
        os.path.join(root, c)
        for c in children
        if c not in allowed and os.path.isdir(os.path.join(root, c))
    ]

    if not to_remove:
        print("[✓] Nothing to prune.")
        return

    print("\n[!] Folders that would be removed:")
    for p in to_remove:
        print("  -", p)

    if not confirm:
        print("\n[!] Re-run with --yes to delete them.")
        return

    for p in to_remove:
        try:
            shutil.rmtree(p)
            print(f"[removed] {p}")
        except Exception as e:
            print(f"[error] Could not remove {p}: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prune", action="store_true")
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()

    root = os.path.dirname(os.path.abspath(__file__))
    print(f"\n=== Initializing project at: {root} ===\n")

    # Required structure
    dirs = [
        f"{root}/colmap_workspace/images",
        f"{root}/colmap_workspace/sparse",
        f"{root}/colmap_workspace/dense",
        f"{root}/output",
        f"{root}/scripts",
    ]
    for d in dirs:
        mkdir(d)

    # README
    readme = f"{root}/README.md"
    if not os.path.exists(readme):
        with open(readme, "w") as f:
            f.write(
                "# Project\n\n"
                "Place images in `colmap_workspace/images/` and run your pipeline.\n"
            )
        print("[+] README.md created")
    else:
        print("[✓] README.md exists")

    # Prune
    if args.prune:
        prune_folders(root, confirm=args.yes)

    print("\n=== Setup complete ===")
    print(f"Drop images into: {root}/colmap_workspace/images\n")


if __name__ == "__main__":
    main()
