#!/usr/bin/env python3
"""
Launcher script for the Kaizen Group Assignment System UI
"""

import subprocess
import sys
import os

def main():
    # Configure console output to support UTF-8 (emojis) on Windows
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    print("🏋️ Starting Kaizen Group Assignment System...")
    print("📱 Opening web interface...")
    
    # Check if all required dependencies are installed
    print("📦 Checking dependencies...")
    dependencies = {
        "streamlit": "streamlit",
        "pandas": "pandas",
        "openpyxl": "openpyxl",
        "plotly": "plotly",
        "pydantic": "pydantic",
        "rich": "rich",
        "dotenv": "python-dotenv",
        "click": "click"
    }
    
    missing_any = False
    for module_name, package_name in dependencies.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_any = True
            break
            
    if missing_any:
        print("❌ Some dependencies are missing. Installing from requirements.txt...")
        try:
            requirements_file = "requirements.txt"
            if os.path.exists(requirements_file):
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
            else:
                # Fallback to installing key packages individually
                packages = list(dependencies.values())
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
            print("✅ All dependencies installed successfully!")
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            print("💡 Trying to continue anyway...")
    else:
        print("✅ All dependencies found")
    
    # Run the Streamlit app
    try:
        # Try the simple version first, fallback to full version
        app_file = "app_simple.py" if os.path.exists("app_simple.py") else "app.py"
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_file,
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error starting the app: {e}")
        print("💡 Make sure you have all dependencies installed:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main() 