#!/usr/bin/env python3
"""
Launcher script for the Kaizen Group Assignment System UI
"""

import subprocess
import sys
import os

def main():
    print("🏋️ Starting Kaizen Group Assignment System...")
    print("📱 Opening web interface...")
    
    # Check if streamlit is installed
    try:
        import streamlit
        print(f"✅ Streamlit version {streamlit.__version__} found")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    
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