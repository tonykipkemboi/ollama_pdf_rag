"""Run script for the Streamlit application."""
import subprocess
import sys
from pathlib import Path

def main():
    """Run the Streamlit application."""
    app_path = Path("src/app/main.py")
    if not app_path.exists():
        print(f"Error: Could not find {app_path}")
        sys.exit(1)
        
    try:
        subprocess.run(["streamlit", "run", str(app_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 