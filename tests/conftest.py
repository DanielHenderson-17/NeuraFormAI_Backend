import sys
from pathlib import Path

# Add root dir to sys.path so imports like `chat_ui.x` work
sys.path.append(str(Path(__file__).resolve().parent.parent))
