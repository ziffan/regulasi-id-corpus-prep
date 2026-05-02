import os

HEADER = """# Copyright 2026 Ziffany Firdinal
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
"""

TARGET_DIRS = ["regulasi_id_corpus_prep", "tests"]

def add_header(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if HEADER in content:
        # print(f"Skipping {file_path}: Header already exists")
        return

    new_content = HEADER + "\n" + content
    
    # Handle shebang
    if content.startswith("#!"):
        lines = content.split("\n")
        shebang = lines[0]
        rest = "\n".join(lines[1:])
        new_content = shebang + "\n\n" + HEADER + "\n" + rest

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Added header to {file_path}")

def main():
    for target_dir in TARGET_DIRS:
        if not os.path.exists(target_dir):
            continue
            
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith(".py"):
                    add_header(os.path.join(root, file))

if __name__ == "__main__":
    main()
