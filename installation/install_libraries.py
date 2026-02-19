import subprocess
import sys

required_packages = ["pyyaml", "pandas", "pyautogui", "pynput"]

for pkg in required_packages:
    print(f"installing {pkg}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

print(f"library installation completed")
input("press ENTER to exit")