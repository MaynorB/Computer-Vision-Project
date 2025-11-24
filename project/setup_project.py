#!/usr/bin/env python3
"""
setup_project.py

Creates a minimal project layout for offline COLMAP work and optionally prunes
unused folders.

Usage:
    python setup_project.py --name project
    python setup_project.py --name project --prune --yes

Options:
    --name    Project root name (default: "project")
    --prune   Detect and remove folders in the project root that are NOT in the
              allowed list. (Dry-run unless --yes specified.)
    --yes     Confirm deletion when --prune is used.
"""

import os
import argparse
import shutil

ALLOWED_FOLDERS = {
    "colmap_workspace",
    os.path.join("colmap_workspace", "images"),
    os.path.join("colmap_workspace", "sparse"),
    os.path.join("colmap_workspace", "dense"),
    "output",
    "scripts",
}

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"[+] Created: {path}")
    else:
        print(f"[✓] Exists:  {path}")

def find_candidate_prune(root):
    # List only immediate children of root
    entries = [e for e in os.listdir(root)]
    candidates = []
    for e in entries:
        full = os.path.join(root, e)
        if os.path.isdir(full):
            # normalized relative path for comparison
            rel = os.path.normpath(e)
            if rel not in [os.path.normpath(x) for x in ALLOWED_FOLDERS]:
                candidates.append(full)
    return candidates

def remove_paths(paths, yes=False):
    if not paths:
        print("[✓] Nothing to remove.")
        return
    print("\n[!] The following directories are candidate for removal:")
    for p in paths:
        print("   -", p)
    if not yes:
        print("\n[!] Run with --yes to actually remove them, or re-run with --prune --yes to force.")
        return
    # perform deletion
    for p in paths:
        try:
            shutil.rmtree(p)
            print(f"[removed] {p}")
        except Exception as exc:
            print(f"[error] Failed to remove {p}: {exc}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="project", help="Project root folder name")
    parser.add_argument("--prune", action="store_true", help="Detect and remove unused folders")
    parser.add_argument("--yes", action="store_true", help="Confirm deletion when pruning")
    args = parser.parse_args()

    root = args.name
    print(f"\n=== Setting up project at: {root} ===\n")
    # Directories to be created
    dirs = [
        root,
        os.path.join(root, "colmap_workspace"),
        os.path.join(root, "colmap_workspace", "images"),  # main place to drop images
        os.path.join(root, "colmap_workspace", "sparse"),
        os.path.join(root, "colmap_workspace", "dense"),
        os.path.join(root, "output"),
        os.path.join(root, "scripts"),
    ]

    for d in dirs:
        create_dir(d)

    # Create README if missing
    readme_path = os.path.join(root, "README.md")
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write("# Project\n\n")
            f.write("Place your images into `colmap_workspace/images/` then run the COLMAP pipeline.\n")
        print("[+] Created README.md")
    else:
        print("[✓] README.md exists")

    # Prune unused folders (safe, requires explicit confirmation via --yes)
    if args.prune:
        candidates = find_candidate_prune(root)
        remove_paths(candidates, yes=args.yes)

    print("\n=== Setup complete ===")
    print("Drop images into:")
    print(f"  {os.path.join(root, 'colmap_workspace', 'images')}\n")
    print("Then run your pipeline script in scripts/ (e.g. test2.py).\n")

if __name__ == "__main__":
    main()
