"""
🔍 Security Validator - HunDeaBot
──────────────────────────────────

Valida la configuración de seguridad del bot antes de ejecutar.

Usage:
    python validate_security.py
"""

import os
import sys
import json
from pathlib import Path


def check_file_exists(filepath, required=True):
    """Check if file exists."""
    exists = Path(filepath).exists()
    status = "✅" if exists else ("❌" if required else "⚠️")
    req_text = "(Required)" if required else "(Optional)"
    print(f"  {status} {filepath} {req_text}")
    return exists


def check_gitignore():
    """Validate .gitignore protection."""
    print("\n🔒 Checking .gitignore protection...")
    
    gitignore_path = Path('.gitignore')
    if not gitignore_path.exists():
        print("  ❌ .gitignore not found!")
        return False
    
    with open(gitignore_path, 'r') as f:
        content = f.read()
    
    required_entries = [
        'config.json',
        '.env',
        '*.log',
        'cache.json'
    ]
    
    all_good = True
    for entry in required_entries:
        if entry in content:
            print(f"  ✅ {entry} is ignored")
        else:
            print(f"  ❌ {entry} NOT in .gitignore!")
            all_good = False
    
    return all_good


def check_env_file():
    """Check .env configuration."""
    print("\n🌍 Checking environment variables...")
    
    env_path = Path('.env')
    if not env_path.exists():
        print("  ⚠️  .env not found (using config.json instead)")
        return True
    
    # Try loading .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("  ✅ .env loaded successfully")
        
        # Check critical vars
        critical_vars = [
            'DISCORD_WEBHOOK_PLAYSTATION',
            'DISCORD_WEBHOOK_XBOX', 
            'DISCORD_WEBHOOK_NINTENDO'
        ]
        
        found_any = False
        for var in critical_vars:
            value = os.getenv(var)
            if value and not value.startswith('your_'):
                print(f"  ✅ {var} configured")
                found_any = True
            else:
                print(f"  ⚠️  {var} not configured")
        
        if not found_any:
            print("  ⚠️  No webhooks configured in .env")
            return True
        
        return True
        
    except ImportError:
        print("  ⚠️  python-dotenv not installed")
        print("     Install: pip install python-dotenv")
        return True
    except Exception as e:
        print(f"  ❌ Error loading .env: {e}")
        return False


def check_config_file():
    """Check config.json."""
    print("\n⚙️  Checking config.json...")
    
    config_path = Path('config.json')
    if not config_path.exists():
        print("  ⚠️  config.json not found")
        print("     Run: cp config_v3.example.json config.json")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("  ✅ config.json loaded successfully")
        
        # Check webhooks
        webhooks = config.get('webhooks', {})
        configured_webhooks = 0
        
        for platform, webhook in webhooks.items():
            if webhook and not webhook.startswith('YOUR_'):
                configured_webhooks += 1
                print(f"  ✅ {platform} webhook configured")
        
        if configured_webhooks == 0:
            print("  ⚠️  No webhooks configured")
        
        # Check APIs
        apis = config.get('apis', {})
        rawg_key = apis.get('rawg')
        
        if rawg_key and not rawg_key.startswith('YOUR_'):
            print("  ✅ RAWG API key configured")
        else:
            print("  ⚠️  RAWG API key not configured (optional but recommended)")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON in config.json: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error reading config.json: {e}")
        return False


def check_sensitive_files():
    """Check for sensitive files that shouldn't be committed."""
    print("\n🔐 Checking for sensitive files...")
    
    sensitive_files = [
        'config.json',
        '.env',
        'cache.json',
        'huntdea_v3.log'
    ]
    
    all_safe = True
    for filepath in sensitive_files:
        if Path(filepath).exists():
            print(f"  ⚠️  {filepath} exists (make sure it's in .gitignore)")
        else:
            print(f"  ✅ {filepath} not found (safe)")
    
    return all_safe


def check_dependencies():
    """Check required dependencies."""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        'requests',
        'beautifulsoup4',
        'lxml'
    ]
    
    optional_packages = [
        'python-dotenv',
        'discord-webhook'
    ]
    
    all_good = True
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package} installed")
        except ImportError:
            print(f"  ❌ {package} NOT installed (REQUIRED)")
            all_good = False
    
    for package in optional_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package} installed")
        except ImportError:
            print(f"  ⚠️  {package} not installed (optional)")
    
    return all_good


def check_security_module():
    """Check if security module exists."""
    print("\n🛡️  Checking security module...")
    
    security_path = Path('modules/core/security.py')
    if not security_path.exists():
        print("  ❌ security.py not found!")
        return False
    
    try:
        from modules.core import security
        print("  ✅ Security module loaded")
        
        # Check key functions
        required_funcs = [
            'sanitize_webhook',
            'validate_webhook',
            'sanitize_game_title',
            'RateLimiter'
        ]
        
        for func_name in required_funcs:
            if hasattr(security, func_name):
                print(f"  ✅ {func_name} available")
            else:
                print(f"  ❌ {func_name} missing!")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error loading security module: {e}")
        return False


def check_git_status():
    """Check git status for sensitive files."""
    print("\n📋 Checking git status...")
    
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'status', '--short'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            output = result.stdout
            
            # Check for sensitive files in git status
            sensitive_patterns = ['config.json', '.env', '.log']
            found_issues = []
            
            for line in output.split('\n'):
                for pattern in sensitive_patterns:
                    if pattern in line:
                        found_issues.append(line.strip())
            
            if found_issues:
                print("  ⚠️  Sensitive files in git status:")
                for issue in found_issues:
                    print(f"     {issue}")
                print("  💡 Run: git rm --cached <file>")
                return False
            else:
                print("  ✅ No sensitive files in git status")
                return True
        else:
            print("  ⚠️  Not a git repository")
            return True
            
    except FileNotFoundError:
        print("  ⚠️  Git not found (skip check)")
        return True
    except Exception as e:
        print(f"  ⚠️  Could not check git status: {e}")
        return True


def main():
    """Run all security checks."""
    print("="*60)
    print("🔍 HunDeaBot Security Validator")
    print("="*60)
    
    checks = [
        ("File Structure", lambda: all([
            check_file_exists('hundea_v3.py'),
            check_file_exists('modules/consoles/base_console_hunter.py'),
            check_file_exists('modules/core/security.py'),
        ])),
        ("GitIgnore Protection", check_gitignore),
        ("Environment Variables", check_env_file),
        ("Configuration", check_config_file),
        ("Sensitive Files", check_sensitive_files),
        ("Dependencies", check_dependencies),
        ("Security Module", check_security_module),
        ("Git Status", check_git_status),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"\n❌ Error in {check_name}: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Security Check Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {check_name}")
    
    print(f"\n🎯 Score: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✅ All security checks passed!")
        print("🚀 Your bot is ready to run securely!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} checks failed")
        print("📝 Please fix the issues above before running the bot")
        return 1


if __name__ == "__main__":
    sys.exit(main())
