import os
from pathlib import Path

# Get the base directory
base_dir = Path(__file__).parent / "src"

# Rename directories

if (base_dir / "Utils").exists():
    (base_dir / "Utils").rename(base_dir / "utils")
    print("✅ Renamed 'Utils' to 'utils'")

# Create __init__.py files
dirs = [
    "src",
    "src/api",
    "src/api/routes",
    "src/api/schemas",
    "src/config",
    "src/domain",
    "src/domain/entities",
    "src/domain/interfaces",
    "src/domain/services",
    "src/infrastructure",
    "src/infrastructure/database",
    "src/infrastructure/repositories",
    "src/utils"
]

for dir_path in dirs:
    init_file = Path(dir_path) / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        print(f"✅ Created {init_file}")
