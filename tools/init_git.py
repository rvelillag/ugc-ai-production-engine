import subprocess
from pathlib import Path

gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
build/
dist/
*.egg-info/

# OS / Editor
.DS_Store
Thumbs.db
.vscode/
.idea/
*.swp

# Temporary / Scratch
scratch/
.tempmediaStorage/
*.log
"""

with open(".gitignore", "w", encoding="utf-8") as f:
    f.write(gitignore_content)

print("Created .gitignore")
subprocess.run(["git", "init"], check=True)
subprocess.run(["git", "add", "."], check=True)
res = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
print(res.stdout[:500])
