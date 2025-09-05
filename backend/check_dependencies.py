"""
Dependency checker script for P&ID Analyzer

This script checks for all required dependencies and offers to install any missing ones.
Run this script before starting the server to ensure all dependencies are installed.
"""

import sys
import os
import subprocess
import importlib.util
from typing import List, Dict, Tuple, Set

# Required packages with their installation commands
REQUIREMENTS = {
    # Core dependencies
    "fastapi": "pip install fastapi",
    "uvicorn": "pip install uvicorn",
    "opencv-python-headless": "pip install opencv-python-headless",
    "numpy": "pip install numpy",
    "pytesseract": "pip install pytesseract",
    "pillow": "pip install pillow",
    "pydantic": "pip install pydantic",
    "python-multipart": "pip install python-multipart",
    "pandas": "pip install pandas",
    "requests": "pip install requests",
    
    # YOLO dependencies
    "torch": "pip install torch",
    "torchvision": "pip install torchvision",
    "ultralytics": "pip install ultralytics",
    
    # RAG dependencies
    "sentence-transformers": "pip install sentence-transformers",
    "openai": "pip install openai",
}

# Optional packages
OPTIONAL_PACKAGES = {
    "onnxruntime": "pip install onnxruntime",
    "easyocr": "pip install easyocr",
    "pymupdf": "pip install pymupdf",
}

def is_package_installed(package_name: str) -> bool:
    """Check if a package is installed."""
    return importlib.util.find_spec(package_name) is not None

def get_package_version(package_name: str) -> str:
    """Get the version of an installed package."""
    try:
        package = __import__(package_name)
        return getattr(package, "__version__", "unknown")
    except (ImportError, AttributeError):
        return "unknown"

def check_dependencies() -> Tuple[Set[str], Set[str], Dict[str, str]]:
    """Check which dependencies are installed and which are missing."""
    installed = set()
    missing = set()
    versions = {}
    
    print("Checking required dependencies...")
    for package in REQUIREMENTS:
        package_name = package.split('[')[0]  # Handle packages with extras like 'package[extra]'
        if is_package_installed(package_name):
            installed.add(package)
            versions[package] = get_package_version(package_name)
            print(f"✅ {package} (version: {versions[package]})")
        else:
            missing.add(package)
            print(f"❌ {package} (not installed)")
    
    print("\nChecking optional dependencies...")
    for package in OPTIONAL_PACKAGES:
        package_name = package.split('[')[0]
        if is_package_installed(package_name):
            installed.add(package)
            versions[package] = get_package_version(package_name)
            print(f"✅ {package} (version: {versions[package]})")
        else:
            print(f"⚠️ {package} (optional, not installed)")
    
    return installed, missing, versions

def install_dependencies(packages: List[str]) -> None:
    """Install missing dependencies."""
    if not packages:
        print("No packages to install.")
        return
    
    print(f"Installing {len(packages)} missing packages...")
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call(REQUIREMENTS[package].split())
            print(f"✅ Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")

def verify_pytorch_installation() -> None:
    """Verify PyTorch installation and print GPU availability."""
    if not is_package_installed("torch"):
        print("PyTorch is not installed.")
        return
    
    import torch
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU device: {torch.cuda.get_device_name(0)}")

def check_external_dependencies() -> None:
    """Check external dependencies like Tesseract OCR."""
    # Check Tesseract
    try:
        import pytesseract
        tesseract_path = pytesseract.pytesseract.tesseract_cmd
        print(f"Tesseract path: {tesseract_path}")
        if os.path.exists(tesseract_path):
            print("✅ Tesseract OCR is installed and properly configured")
        else:
            print("⚠️ Tesseract OCR path is set but the executable was not found")
    except (ImportError, AttributeError):
        print("❌ pytesseract is not installed or properly configured")

def main():
    """Main function to check and optionally install dependencies."""
    print("=" * 50)
    print("P&ID Analyzer Dependency Checker")
    print("=" * 50)
    
    installed, missing, versions = check_dependencies()
    
    print("\nChecking external dependencies...")
    check_external_dependencies()
    
    if "torch" in installed:
        print("\nVerifying PyTorch installation...")
        verify_pytorch_installation()
    
    if missing:
        print("\n" + "=" * 50)
        print(f"{len(missing)} required packages are missing:")
        for package in missing:
            print(f"  - {package}")
        
        install_choice = input("\nDo you want to install the missing packages? (y/n): ")
        if install_choice.lower() == 'y':
            install_dependencies(list(missing))
            print("\nDependency installation completed.")
            print("Please restart this script to verify all installations.")
        else:
            print("\nSkipping installation.")
            print("Note: The application may not function properly without all required dependencies.")
    else:
        print("\n✅ All required dependencies are installed!")
        print("\nYou can now start the P&ID Analyzer with:")
        print("  python -m uvicorn backend.main:app --reload --port 8000")
    
    print("\nOptional: Install any missing optional dependencies for additional features:")
    for package, command in OPTIONAL_PACKAGES.items():
        if not is_package_installed(package.split('[')[0]):
            print(f"  {command}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
