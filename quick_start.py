#!/usr/bin/env python3
"""
⚡ Quick Start - Prueba rápida de ITAD
"""

print("\n" + "="*70)
print("⚡ QUICK START - IsThereAnyDeal Test")
print("="*70 + "\n")

print("🔍 Importando módulos...")
try:
    from modules.itad_hunter import IsThereAnyDealHunter
    print("✅ IsThereAnyDeal Hunter cargado\n")
except ImportError as e:
    print(f"❌ Error al importar: {e}")
    print("💡 Ejecuta desde la carpeta raíz del proyecto\n")
    exit(1)

print("📦 Inicializando hunter...")
hunter = IsThereAnyDealHunter()

print("\n🔍 Buscando juegos gratis (esto puede tomar 10-20 segundos)...\n")
juegos = hunter.obtener_juegos_gratis()

if not juegos:
    print("💤 No se encontraron juegos gratis en este momento")
    print("💡 Esto es normal, no siempre hay ofertas activas\n")
    exit(0)

print(f"\n✨ ¡Encontrados {len(juegos)} juego(s) gratis!\n")
print("─" * 70 + "\n")

for i, juego in enumerate(juegos, 1):
    print(f"{i}. {juego['tienda_emoji']} {juego['titulo']}")
    print(f"   🏪 {juego['tienda']}")
    print(f"   🔗 {juego['url']}")
    print(f"   ⏰ {juego['fecha_fin']}")
    print()

print("─" * 70)
print(f"\n🎉 ¡Éxito! ITAD está funcionando correctamente")
print(f"📊 Total: {len(juegos)} juego(s) de {len(set(j['tienda'] for j in juegos))} tienda(s)\n")

print("💡 Próximos pasos:")
print("   1. python test_itad.py          ← Test completo con reviews")
print("   2. python hundea_v2.py          ← Ejecución completa")
print("   3. git add . && git push        ← Subir cambios\n")

print("="*70 + "\n")
