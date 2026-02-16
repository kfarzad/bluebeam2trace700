import subprocess
import sys

required_packages = ["pyyaml", "pandas", "pyautogui", "pynput"]

for pkg in required_packages:
    print(f"Installing {pkg}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])