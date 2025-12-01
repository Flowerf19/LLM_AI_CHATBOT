#!/usr/bin/env python3
"""
Setup Script for Discord LLM Chatbot
Handles virtual environment creation and dependency installation
"""

import os
import sys
import subprocess
import argparse
import shutil

def run_command(command, description, quiet=False):
    """Run a shell command and handle errors"""
    if not quiet:
        print(f"🔧 {description}...")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if not quiet:
            print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        if not quiet:
            print(f"❌ {description} failed:")
            print(f"Error: {e.stderr}")
        return False

def create_venv(venv_path="venv"):
    """Create Python virtual environment"""
    if os.path.exists(venv_path):
        print(f"⚠️  Virtual environment '{venv_path}' already exists")
        return True

    # Use sys.executable to ensure we use the same python interpreter
    python_cmd = sys.executable
    return run_command(f'"{python_cmd}" -m venv {venv_path}', "Creating virtual environment")

def activate_venv(venv_path="venv"):
    """Get the activation command for the virtual environment"""
    if sys.platform == "win32":
        return f"{venv_path}\\Scripts\\activate"
    else:
        return f"source {venv_path}/bin/activate"

def install_requirements(requirements_file="requirements.txt", venv_path="venv"):
    """Install Python requirements"""
    if not os.path.exists(requirements_file):
        print(f"⚠️  Requirements file '{requirements_file}' not found")
        return False

    # Activate venv and install requirements
    activate_cmd = activate_venv(venv_path)
    install_cmd = f"{activate_cmd} && pip install -r {requirements_file}"

    return run_command(install_cmd, f"Installing requirements from {requirements_file}")

def detect_hardware():
    """Detect hardware capabilities and suggest requirement files"""
    suggestions = []
    print("\n🔍 Detecting hardware...")

    # 1. Check for NVIDIA GPU
    if shutil.which('nvidia-smi'):
        print("   ✅ NVIDIA GPU detected (nvidia-smi found)")
        suggestions.append(('requirements-gpu-cuda.txt', 'NVIDIA CUDA Support'))
    
    # 2. Check for AMD GPU (ROCm)
    # Simple check for rocm-smi or hipcc
    if shutil.which('rocm-smi') or os.path.exists('/opt/rocm'):
        print("   ✅ AMD GPU detected (ROCm found)")
        suggestions.append(('requirements-gpu-rocm.txt', 'AMD ROCm Support'))

    # 3. Check for Intel GPU/NPU
    is_intel = False
    if sys.platform == "win32":
        try:
            # Check for Intel in VideoController
            cmd = 'wmic path win32_VideoController get name'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if 'Intel' in result.stdout:
                is_intel = True
        except Exception:
            pass
    elif sys.platform == "linux":
        try:
            # Check lspci for Intel VGA/Display
            cmd = 'lspci | grep -i "Intel.*Display"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if result.stdout.strip():
                is_intel = True
        except Exception:
            pass

    if is_intel:
        print("   ✅ Intel GPU/NPU detected")
        suggestions.append(('requirements-gpu-intel.txt', 'Intel GPU Support'))
        suggestions.append(('requirements-npu.txt', 'Intel NPU Support (OpenVINO)'))

    if not suggestions:
        print("   ℹ️  No specific accelerator hardware detected (using CPU)")
    
    return suggestions

def setup_project(venv_path="venv", requirements_file="requirements.txt", auto_detect=False):
    """Complete project setup"""
    print("🚀 Setting up Discord LLM Chatbot")
    print("=" * 40)

    # Create virtual environment
    if not create_venv(venv_path):
        return False

    # Install core requirements
    if not install_requirements(requirements_file, venv_path):
        return False

    # Hardware detection and additional installations
    if auto_detect:
        suggestions = detect_hardware()
        if suggestions:
            print("\n💡 Suggested hardware optimizations:")
            for i, (req_file, desc) in enumerate(suggestions, 1):
                print(f"   {i}. {desc} ({req_file})")
            
            response = input("\nDo you want to install these optimizations? [Y/n] ").strip().lower()
            if response in ('', 'y', 'yes'):
                for req_file, desc in suggestions:
                    install_requirements(req_file, venv_path)
            else:
                print("Skipping hardware optimizations.")

    print("\n" + "=" * 40)
    print("✅ Setup completed successfully!")
    print("\nTo activate the virtual environment:")
    if sys.platform == "win32":
        print(f"    {venv_path}\\Scripts\\activate")
    else:
        print(f"    source {venv_path}/bin/activate")

    print("\nTo run the bot:")
    print("    python src/bot.py")

    print("\nDon't forget to:")
    print("    1. Create a .env file with your Discord bot token")
    print("    2. Configure your API keys (Gemini, DeepSeek)")
    print("    3. Set up bot permissions in Discord Developer Portal")

    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Setup Discord LLM Chatbot project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/setup.py                    # Setup with default settings
  python scripts/setup.py --auto             # Setup with auto hardware detection
  python scripts/setup.py --venv myenv      # Custom venv name
        """
    )

    parser.add_argument(
        "--venv",
        default="venv",
        help="Virtual environment name (default: venv)"
    )

    parser.add_argument(
        "--req",
        default="requirements.txt",
        help="Requirements file to install (default: requirements.txt)"
    )

    parser.add_argument(
        "--skip-venv",
        action="store_true",
        help="Skip virtual environment creation"
    )

    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-detect hardware and suggest optimizations"
    )

    args = parser.parse_args()

    try:
        if args.skip_venv:
            # Only install requirements
            success = install_requirements(args.req, args.venv)
            if success and args.auto:
                suggestions = detect_hardware()
                if suggestions:
                    print("\n💡 Suggested hardware optimizations:")
                    for i, (req_file, desc) in enumerate(suggestions, 1):
                        print(f"   {i}. {desc} ({req_file})")
                    response = input("\nDo you want to install these optimizations? [Y/n] ").strip().lower()
                    if response in ('', 'y', 'yes'):
                        for req_file, desc in suggestions:
                            install_requirements(req_file, args.venv)
        else:
            # Full setup
            success = setup_project(args.venv, args.req, args.auto)

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n🛑 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()