# install_packages.py
import sys
import subprocess
import importlib

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Successfully installed {package}")
        return True
    except Exception as e:
        print(f"✗ Failed to install {package}: {e}")
        return False

def check_package(package):
    try:
        importlib.import_module(package)
        print(f"✓ {package} is already installed")
        return True
    except ImportError:
        return False

print("=" * 50)
print("PASSWORD STRENGTH PROJECT - PACKAGE INSTALLATION")
print("=" * 50)

# List of required packages
packages = [
    'flask',
    'pandas', 
    'numpy',
    'scikit-learn',
    'joblib'
]

print("\nChecking and installing packages...")

success_count = 0
for package in packages:
    if not check_package(package):
        if install_package(package):
            success_count += 1
    else:
        success_count += 1

print(f"\n" + "=" * 50)
print(f"INSTALLATION SUMMARY: {success_count}/{len(packages)} packages ready")
print("=" * 50)

if success_count == len(packages):
    print("🎉 All packages installed successfully!")
    print("You can now run the project.")
else:
    print("⚠️ Some packages failed to install. The project might not work properly.")

input("\nPress Enter to exit...")
