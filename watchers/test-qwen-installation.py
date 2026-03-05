"""
Test script to find and verify Qwen Code installation.
Run this to diagnose PATH issues.
"""

import subprocess
import sys
import os
from pathlib import Path

print("=" * 60)
print("QWEN CODE INSTALLATION DIAGNOSTIC")
print("=" * 60)

# Check 1: Is qwen command available?
print("\n1. Checking 'qwen' command...")
try:
    result = subprocess.run(['qwen', '--version'], capture_output=True, text=True, shell=True)
    print(f"   [OK] qwen found: {result.stdout.strip() if result.stdout else 'OK'}")
except FileNotFoundError:
    print("   [FAIL] qwen command not found in PATH")

# Check 2: Is npx available?
print("\n2. Checking 'npx' command...")
try:
    result = subprocess.run(['npx', '--version'], capture_output=True, text=True, shell=True)
    print(f"   [OK] npx version: {result.stdout.strip()}")
except FileNotFoundError:
    print("   [FAIL] npx command not found")

# Check 3: Check npm global bin directory
print("\n3. Checking npm global bin directory...")
try:
    result = subprocess.run(['npm', 'bin', '-g'], capture_output=True, text=True, shell=True)
    npm_bin = result.stdout.strip()
    print(f"   npm global bin: {npm_bin}")
    
    # Check if it's in PATH
    path_env = os.environ.get('PATH', '')
    if npm_bin in path_env:
        print(f"   [OK] npm bin is in PATH")
    else:
        print(f"   [FAIL] npm bin is NOT in PATH")
        print(f"      Add this to your PATH: {npm_bin}")
        
    # Check if qwen exists there
    qwen_path = Path(npm_bin) / 'qwen.cmd' if sys.platform == 'win32' else Path(npm_bin) / 'qwen'
    if qwen_path.exists():
        print(f"   [OK] qwen executable found at: {qwen_path}")
    else:
        print(f"   [FAIL] qwen executable not found at: {qwen_path}")
        
except Exception as e:
    print(f"   [FAIL] Error checking npm bin: {e}")

# Check 4: Check AppData npm directory (Windows)
if sys.platform == 'win32':
    print("\n4. Checking AppData npm directory...")
    appdata = os.environ.get('APPDATA', '')
    npm_path = Path(appdata) / 'npm'
    print(f"   AppData npm path: {npm_path}")
    
    if npm_path.exists():
        print(f"   [OK] Directory exists")
        qwen_cmd = npm_path / 'qwen.cmd'
        if qwen_cmd.exists():
            print(f"   [OK] qwen.cmd found at: {qwen_cmd}")
        else:
            print(f"   [FAIL] qwen.cmd not found")
            
        # List files to see what's there
        print(f"   Files in npm directory:")
        for f in npm_path.glob('qwen*'):
            print(f"      - {f.name}")
    else:
        print(f"   [FAIL] Directory does not exist")

# Check 5: Try running qwen with npx
print("\n5. Testing 'npx @qwen-code/qwen-code@latest --version'...")
try:
    result = subprocess.run(
        ['npx', '@qwen-code/qwen-code@latest', '--version'],
        capture_output=True,
        text=True,
        shell=True,
        timeout=30
    )
    if result.returncode == 0:
        print(f"   [OK] npx works: {result.stdout.strip()}")
    else:
        print(f"   [FAIL] npx failed: {result.stderr.strip()}")
except subprocess.TimeoutExpired:
    print(f"   [WARN] npx timed out (might be downloading)")
except Exception as e:
    print(f"   [FAIL] npx error: {e}")

# Check 6: Current PATH
print("\n6. Current PATH environment:")
path_dirs = os.environ.get('PATH', '').split(os.pathsep)
for i, dir_path in enumerate(path_dirs[:10]):  # Show first 10
    print(f"   {i+1}. {dir_path}")
if len(path_dirs) > 10:
    print(f"   ... and {len(path_dirs) - 10} more directories")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)

print("\nRECOMMENDATIONS:")
print("1. If qwen.cmd exists but isn't found, add its directory to PATH")
print("2. On Windows, the path is usually: %APPDATA%\\npm")
print("3. To add to PATH permanently:")
print("   - Open System Properties > Environment Variables")
print("   - Add the npm bin directory to User or System PATH")
print("4. Restart your terminal after changing PATH")
print("5. Or use 'npx @qwen-code/qwen-code@latest' instead of 'qwen'")
