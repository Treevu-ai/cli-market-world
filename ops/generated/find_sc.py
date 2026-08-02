import os, sys

# Search common locations
search_paths = [
    r"C:\Users\acuba",
    r"C:\Python314",
]

for base in search_paths:
    for root, dirs, files in os.walk(base):
        # Skip node_modules, .git, etc
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.obsidian']]
        for f in files:
            if f == 'store_credentials.py':
                print(os.path.join(root, f))
        # Limit depth
        if root.count(os.sep) - base.count(os.sep) > 4:
            dirs.clear()
