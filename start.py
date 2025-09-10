#!/usr/bin/env python3
"""
AI RAG Bot Startup Script
This script helps users get started with the AI RAG Bot quickly.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_virtual_environment():
    """Check if virtual environment exists"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found")
        print("Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✅ Virtual environment created")
        except subprocess.CalledProcessError:
            print("❌ Failed to create virtual environment")
            return False
    else:
        print("✅ Virtual environment found")
    return True

def check_dependencies():
    """Check if dependencies are installed"""
    try:
        # Try to import key dependencies
        import flask
        import anthropic
        print("✅ Core dependencies are installed")
        return True
    except ImportError:
        print("⚠️  Dependencies not installed or incomplete")
        return False

def check_api_key():
    """Check if API key is configured"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
        if "your_anthropic_api_key_here" in content:
            print("⚠️  Please configure your Anthropic API key in .env file")
            return False
        elif "ANTHROPIC_API_KEY=" in content:
            print("✅ API key configuration found")
            return True
    
    print("⚠️  API key not configured")
    return False

def install_dependencies():
    """Install dependencies"""
    print("Installing dependencies...")
    try:
        # Determine the correct pip path
        if os.name == 'nt':  # Windows
            pip_path = "venv\\Scripts\\pip"
        else:  # macOS/Linux
            pip_path = "venv/bin/pip"
        
        subprocess.run([pip_path, "install", "-r", "requirements_simple.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_api_key_config():
    """Help user configure API key"""
    print("\n" + "="*50)
    print("🔑 API KEY CONFIGURATION")
    print("="*50)
    print("To use AI RAG Bot, you need an Anthropic API key.")
    print("\nSteps to get your API key:")
    print("1. Go to https://console.anthropic.com/")
    print("2. Sign up or log in to your account")
    print("3. Navigate to API Keys section")
    print("4. Create a new API key")
    print("5. Copy the API key")
    
    api_key = input("\nPaste your Anthropic API key here (or press Enter to skip): ").strip()
    
    if api_key:
        # Update .env file
        env_content = ""
        with open(".env", "r") as f:
            env_content = f.read()
        
        env_content = env_content.replace("your_anthropic_api_key_here", api_key)
        
        with open(".env", "w") as f:
            f.write(env_content)
        
        print("✅ API key configured successfully!")
        return True
    else:
        print("⚠️  Skipped API key configuration")
        print("You can manually edit the .env file later")
        return False

def start_application():
    """Start the AI RAG Bot application"""
    print("\n" + "="*50)
    print("🚀 STARTING AI RAG BOT")
    print("="*50)
    
    try:
        # Determine the correct python path
        if os.name == 'nt':  # Windows
            python_path = "venv\\Scripts\\python"
        else:  # macOS/Linux
            python_path = "venv/bin/python"
        
        print("Starting the application...")
        print("Once started, open http://localhost:5000 in your browser")
        print("Press Ctrl+C to stop the application")
        print("-" * 50)
        
        subprocess.run([python_path, "app.py"])
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start application: {e}")
        return False
    
    return True

def main():
    """Main startup routine"""
    print("🤖 AI RAG Bot Startup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check/create virtual environment
    if not check_virtual_environment():
        return 1
    
    # Check dependencies
    if not check_dependencies():
        print("Installing dependencies...")
        if not install_dependencies():
            return 1
    
    # Check API key
    api_key_configured = check_api_key()
    if not api_key_configured:
        create_api_key_config()
    
    # Final check
    print("\n" + "="*50)
    print("🔍 FINAL SYSTEM CHECK")
    print("="*50)
    
    all_ready = True
    
    if not check_dependencies():
        print("❌ Dependencies check failed")
        all_ready = False
    
    if not check_api_key():
        print("⚠️  API key not configured - some features may not work")
    
    if all_ready:
        print("✅ System ready!")
        
        start_now = input("\nStart AI RAG Bot now? (y/n): ").lower().strip()
        if start_now in ['y', 'yes', '']:
            start_application()
        else:
            print("\nTo start later, run: python start.py")
            print("Or manually run: python app.py")
    else:
        print("❌ System not ready. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
