"""
🚀 AUTO-INTEGRATOR - Actualiza ULTRA bot con VR + mejoras
───────────────────────────────────────────────────────────

Este script actualiza hundea_v3_ultra.py automáticamente para incluir:
- VR Hunter
- Mejoras a hunters existentes
- Nueva configuración

Author: HunDeaBot Team  
Version: 1.0.0
"""

import os
import sys
from pathlib import Path


def integrate_vr_hunter():
    """Integrate VR Hunter into mega aggregator."""
    
    print("\n🔧 INTEGRATING VR HUNTER...")
    print("="*60)
    
    # Read mega_api_aggregator.py
    aggregator_file = Path('modules/mega_api_aggregator.py')
    
    if not aggregator_file.exists():
        print("❌ mega_api_aggregator.py not found!")
        return False
    
    with open(aggregator_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already integrated
    if 'VRHunter' in content:
        print("✅ VR Hunter already integrated!")
        return True
    
    # Add import
    import_line = "from modules.vr_hunter import VRHunter\n"
    
    # Find where to insert (after other imports)
    insert_pos = content.find("from modules.itch_hunter import ItchHunter")
    if insert_pos > 0:
        # Find end of line
        insert_pos = content.find('\n', insert_pos) + 1
        content = content[:insert_pos] + import_line + content[insert_pos:]
        print("✅ Added VR Hunter import")
    
    # Add hunter initialization
    init_code = """
        # VR Platforms
        try:
            self.hunters['vr'] = VRHunter(logger=self.logger)
            self.logger.info("✅ VR hunter loaded (SteamVR, Quest, PSVR2, Viveport)")
        except Exception as e:
            self.logger.warning(f"⚠️  VR hunter failed: {e}")
"""
    
    # Find where to insert in _init_hunters
    init_pos = content.find("# Consoles")
    if init_pos > 0:
        content = content[:init_pos] + init_code + "\n        " + content[init_pos:]
        print("✅ Added VR Hunter initialization")
    
    # Save updated file
    with open(aggregator_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ mega_api_aggregator.py updated!")
    return True


def update_config():
    """Update config.json with VR settings."""
    
    print("\n🔧 UPDATING CONFIG...")
    print("="*60)
    
    import json
    
    config_file = Path('config.json')
    
    if not config_file.exists():
        print("⚠️  config.json not found, skipping")
        return False
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Add VR webhook if not exists
    if 'vr_deals' not in config.get('webhooks', {}):
        if 'webhooks' not in config:
            config['webhooks'] = {}
        config['webhooks']['vr_deals'] = 'YOUR_VR_WEBHOOK_HERE'
        print("✅ Added VR webhook placeholder")
    
    # Add VR features if not exists
    if 'enable_vr_hunting' not in config.get('features', {}):
        if 'features' not in config:
            config['features'] = {}
        config['features']['enable_vr_hunting'] = True
        config['features']['enable_steamvr'] = True
        config['features']['enable_meta_quest'] = True
        config['features']['enable_psvr2'] = True
        config['features']['enable_viveport'] = True
        print("✅ Added VR features")
    
    # Add VR filters if not exists
    if 'vr' not in config.get('filters', {}):
        if 'filters' not in config:
            config['filters'] = {}
        config['filters']['vr'] = {
            'min_discount': 20,
            'exclude_dlc': False,
            'max_price': 999999
        }
        print("✅ Added VR filters")
    
    # Save updated config
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ config.json updated!")
    return True


def create_run_script():
    """Create easy run script."""
    
    print("\n🔧 CREATING RUN SCRIPT...")
    print("="*60)
    
    script_content = """#!/usr/bin/env python3
\"\"\"
🚀 HunDeaBot V3.5 ULTRA + VR - Easy Launcher
\"\"\"

import sys

print()
print("╔═══════════════════════════════════════════════════════════╗")
print("║  🚀 HUNDEABOT V3.5 ULTRA + VR                            ║")
print("╚═══════════════════════════════════════════════════════════╝")
print()

print("Select mode:")
print("1. 🥽 Test VR Hunter only")
print("2. 🚀 Run ULTRA bot (all sources + VR)")
print("3. 🧠 Test AI Validator")
print("4. ⚡ Quick test")
print()

choice = input("Choose (1-4): ").strip()

if choice == '1':
    print("\\n🥽 Testing VR Hunter...\\n")
    import modules.vr_hunter
    modules.vr_hunter.test_vr_hunter()
    
elif choice == '2':
    print("\\n🚀 Running ULTRA bot...\\n")
    import hundea_v3_ultra
    hundea_v3_ultra.main()
    
elif choice == '3':
    print("\\n🧠 Testing AI...\\n")
    import test_ai_validator
    test_ai_validator.main()
    
elif choice == '4':
    print("\\n⚡ Quick test...\\n")
    import quick_test
    
else:
    print("❌ Invalid choice")
    sys.exit(1)
"""
    
    with open('run_vr.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ Created run_vr.py")
    return True


def main():
    """Main integration process."""
    
    print()
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  🚀 HUNDEABOT AUTO-INTEGRATOR                            ║")
    print("║  VR Hunter + Mejoras + Config                            ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    
    success = True
    
    # Step 1: Integrate VR Hunter
    if not integrate_vr_hunter():
        success = False
    
    # Step 2: Update config
    if not update_config():
        print("⚠️  Config update skipped")
    
    # Step 3: Create run script
    if not create_run_script():
        success = False
    
    # Summary
    print()
    print("="*60)
    if success:
        print("✅ INTEGRATION COMPLETE!")
        print()
        print("Next steps:")
        print("1. Test VR Hunter:")
        print("   python modules/vr_hunter.py")
        print()
        print("2. Run ULTRA bot:")
        print("   python hundea_v3_ultra.py")
        print()
        print("3. Or use launcher:")
        print("   python run_vr.py")
    else:
        print("⚠️  Some steps failed - check messages above")
    
    print("="*60)
    print()


if __name__ == "__main__":
    main()
