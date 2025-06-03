import sys
import os
from pathlib import Path

# Add the parent directory to the Python path so we can import from main
sys.path.insert(0, str(Path(__file__).parent.parent))
