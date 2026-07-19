"""
Quick Start Script - Run this to set up DevPulse in one command
Usage: python quickstart.py
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, description):
    """Run a shell command and report status"""
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, cwd=os.getcwd())
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        return False
    print(f"✅ Success: {description}")
    return True

def main():
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║           🚀 DevPulse Quick Start Setup 🚀            ║
    ║                                                        ║
    ║  This will set up DevPulse on your local machine     ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Verify Python version
    print("\n📝 Checking Python version...")
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required. Current:", sys.version)
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} OK")
    
    # Step 2: Create virtual environment
    venv_path = "venv"
    if not os.path.exists(venv_path):
        print(f"\n📦 Creating virtual environment...")
        if platform.system() == "Windows":
            cmd = f"python -m venv {venv_path}"
        else:
            cmd = f"python3 -m venv {venv_path}"
        if not run_command(cmd, "Create virtual environment"):
            sys.exit(1)
    else:
        print(f"✅ Virtual environment already exists")
    
    # Step 3: Activate venv and install dependencies
    if platform.system() == "Windows":
        pip_cmd = f"{venv_path}\\Scripts\\pip"
    else:
        pip_cmd = f"{venv_path}/bin/pip"
    
    print("\n📚 Installing dependencies...")
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrade pip"):
        sys.exit(1)
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Install packages"):
        sys.exit(1)
    
    # Step 4: Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        print("\n🔑 Creating .env file...")
        env_content = """# DevPulse Environment Configuration

# LLM Provider: gemini or huggingface
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash

# API Keys (get from):
# - Google: https://aistudio.google.com/app/apikey
# - HuggingFace: https://huggingface.co/settings/tokens
GOOGLE_API_KEY=your_google_api_key_here
HF_TOKEN=your_huggingface_token_here

# Mock mode (set to false when you have real API keys)
MOCK_LLM=true

# Data path
DATA_PATH=data/sample_content_data.csv
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Created .env file")
        print("   ⚠️  Update with your API keys before running with MOCK_LLM=false")
    else:
        print("✅ .env file already exists")
    
    # Step 5: Verify project structure
    print("\n📁 Verifying project structure...")
    required_dirs = ["agents", "ui", "data", "utils", "orchestrator", "llm"]
    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ missing")
    
    # Step 6: Summary
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║                  ✅ Setup Complete! ✅                ║
    ╚════════════════════════════════════════════════════════╝
    
    🎯 Next Steps:
    
    1️⃣  Activate virtual environment:
        macOS/Linux:  source venv/bin/activate
        Windows:      venv\\Scripts\\activate
    
    2️⃣  Generate sample data (fetches real HN stories):
        PYTHONPATH=. python data/integrate_data.py
    
    3️⃣  Start the dashboard:
        PYTHONPATH=. python ui/api_server.py
    
    4️⃣  Open in browser:
        http://localhost:5050
    
    📖 Project Structure:
       agents/          → Content analysis agents (analyzer, predictor, etc.)
       ui/              → Web dashboard (HTML/CSS/JS)
       data/            → Data processing & schemas
       utils/           → Helper modules (code parser, sandbox generator, etc.)
       orchestrator/    → Pipeline orchestration & scoring
       llm/             → LLM client (Gemini + HuggingFace)
       config.py        → DevRel configuration & constants
    
    🔗 Useful Links:
       - GitHub: https://github.com/Vikas-Dr/Ai-Agent-Hackathon
       - Google AI Studio: https://aistudio.google.com
       - HuggingFace Hub: https://huggingface.co
    
    ❓ Troubleshooting:
       - If imports fail: Make sure PYTHONPATH=. is set
       - If API fails: Check .env file has correct API keys
       - If port 5050 busy: Change port in ui/api_server.py line ~30
    """)

if __name__ == "__main__":
    main()
