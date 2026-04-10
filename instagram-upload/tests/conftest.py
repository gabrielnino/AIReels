"""
Pytest configuration for instagram-upload tests.
"""
import sys
import os
from pathlib import Path

# Setup paths
test_dir = Path(__file__).parent
module_root = test_dir.parent
project_root = module_root.parent

sys.path.insert(0, str(module_root))
sys.path.insert(0, str(project_root))

print(f"🔧 Pytest config for instagram-upload tests")
print(f"📁 Module root: {module_root}")
