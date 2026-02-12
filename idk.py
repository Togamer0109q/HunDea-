import os
import shutil
from pathlib import Path

print("\n" + "="*70)
print("🐛 APLICANDO PARCHE DE DEBUG")
print("="*70 + "\n")

# Backup
backup_path = Path('hundea_v3_ultra.py.backup')
original_path = Path('hundea_v3_ultra.py')

if not backup_path.exists():
    shutil.copy(original_path, backup_path)
    print("✅ Backup creado: hundea_v3_ultra.py.backup")
else:
    print("ℹ️  Backup ya existe")

# Leer archivo original
with open(original_path) as f:
    content = f.read()

# PARCHE 1: Agregar logging al inicio de _send_notifications
old_send_start = '''    def _send_notifications(self, deals: List[Dict]):
        """Send Discord notifications."""
        logger.info(f"\\n📤 Sending {len(deals)} notifications...")'''

new_send_start = '''    def _send_notifications(self, deals: List[Dict]):
        """Send Discord notifications."""
        logger.info(f"\\n📤 Sending {len(deals)} notifications...")
        logger.debug(f"🔍 DEBUG: Console notifier: {self.console_notifier}")
        logger.debug(f"🔍 DEBUG: PC notifier: {self.pc_notifier}")'''

content = content.replace(old_send_start, new_send_start)

# PARCHE 2: Agregar logging en loop de platform
old_platform_loop = '''            # Send by platform
            for platform, platform_deals in by_platform.items():
                count = len(platform_deals)
                logger.info(f"   {platform}: {count} deals")'''

new_platform_loop = '''            # Send by platform
            for platform, platform_deals in by_platform.items():
                count = len(platform_deals)
                logger.info(f"   {platform}: {count} deals")
                logger.debug(f"🔍 DEBUG: Platform '{platform}' with {count} deals")
                logger.debug(f"🔍 DEBUG: First deal: {platform_deals[0] if platform_deals else 'None'}")'''

content = content.replace(old_platform_loop, new_platform_loop)

# PARCHE 3: Agregar logging en console notifier
old_console = '''                # Console deals
                if platform in ['playstation', 'xbox', 'nintendo']:
                    if self.console_notifier:'''

new_console = '''                # Console deals
                if platform in ['playstation', 'xbox', 'nintendo']:
                    logger.debug(f"🔍 DEBUG: Console platform detected: {platform}")
                    if self.console_notifier:
                        logger.debug(f"🔍 DEBUG: Console notifier is available")'''

content = content.replace(old_console, new_console)

# PARCHE 4: Agregar logging antes de llamar send_deals
old_send_deals = '''                        if console_deals:
                            self.console_notifier.send_deals(console_deals)'''

new_send_deals = '''                        if console_deals:
                            logger.debug(f"🔍 DEBUG: Calling console_notifier.send_deals() with {len(console_deals)} deals")
                            result = self.console_notifier.send_deals(console_deals)
                            logger.debug(f"🔍 DEBUG: send_deals result: {result}")'''

content = content.replace(old_send_deals, new_send_deals)

# PARCHE 5: Agregar logging en PC notifier
old_pc = '''                # PC deals
                else:
                    if self.pc_notifier:'''

new_pc = '''                # PC deals
                else:
                    logger.debug(f"🔍 DEBUG: PC platform detected: {platform}")
                    if self.pc_notifier:
                        logger.debug(f"🔍 DEBUG: PC notifier is available")'''

content = content.replace(old_pc, new_pc)

# PARCHE 6: Agregar logging en PC send_deals
old_pc_send = '''                        self.pc_notifier.send_deals(pc_deals)'''

new_pc_send = '''                        logger.debug(f"🔍 DEBUG: Calling pc_notifier.send_deals() with {len(pc_deals)} deals")
                        result = self.pc_notifier.send_deals(pc_deals)
                        logger.debug(f"🔍 DEBUG: send_deals result: {result}")'''

content = content.replace(old_pc_send, new_pc_send)

# PARCHE 7: Cambiar nivel de logging a DEBUG
old_logging = '''logging.basicConfig(
    level=logging.INFO,'''

new_logging = '''logging.basicConfig(
    level=logging.DEBUG,'''

content = content.replace(old_logging, new_logging)

# Guardar archivo parcheado
with open(original_path, 'w') as f:
    f.write(content)

print("\n✅ Parches aplicados:")
print("   1. Logging al inicio de _send_notifications")
print("   2. Logging en loop de plataformas")
print("   3. Logging en detección de consolas")
print("   4. Logging antes de send_deals (console)")
print("   5. Logging en detección de PC")
print("   6. Logging antes de send_deals (PC)")
print("   7. Nivel de logging cambiado a DEBUG")

print("\n🚀 Ahora ejecuta:")
print("   python hundea_v3_ultra.py")
print()
print("Verás logs detallados tipo:")
print("   🔍 DEBUG: Console notifier: <ConsoleNotifier...>")
print("   🔍 DEBUG: Platform 'playstation' with 5 deals")
print("   🔍 DEBUG: Calling console_notifier.send_deals()...")
print()
print("💡 Para restaurar el original:")
print("   copy hundea_v3_ultra.py.backup hundea_v3_ultra.py")
print()
print("="*70 + "\n")