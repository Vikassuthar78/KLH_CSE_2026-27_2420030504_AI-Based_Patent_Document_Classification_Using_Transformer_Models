"""
HCX-Patent run script
Launch the backend server
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(str(backend_dir))
    
    # Set environment variables
    env = os.environ.copy()
    env.setdefault("DATASET_ROOT", r"D:\ALT-PROJECT\DATA")
    env.setdefault("PROJECT_ROOT", str(Path(__file__).parent))
    env.setdefault("DEVICE", "cpu")
    env.setdefault("DEBUG", "true")
    
    print("=" * 60)
    print("HCX-Patent Backend Server")
    print("=" * 60)
    print(f"Dataset root: {env['DATASET_ROOT']}")
    print(f"Project root: {env['PROJECT_ROOT']}")
    print(f"Device: {env['DEVICE']}")
    print()
    
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "app.main:app", 
         "--host", "127.0.0.1", "--port", "8000", "--reload"],
        env=env,
        cwd=str(backend_dir)
    )


if __name__ == "__main__":
    main()

