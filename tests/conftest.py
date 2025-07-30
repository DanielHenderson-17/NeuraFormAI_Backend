import sys
from pathlib import Path

# Add root dir to sys.path so imports like `chat_ui.x` work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

