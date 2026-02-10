"""
Quick test de Itch.io Hunter
"""
import sys
sys.path.insert(0, 'C:/HunDeaBot')

from modules.itch_hunter import ItchHunter

print("\n" + "="*70)
print("🧪 QUICK TEST - Itch.io Hunter RSS")
print("="*70)

# Inicializar
hunter = ItchHunter()

# Test básico
print("\n📦 Test: Obtener juegos gratis...")
try:
    juegos = hunter.obtener_juegos_gratis(limite=5)
    
    if juegos:
        print(f"\n✅ ÉXITO: {len(juegos)} juego(s) encontrados\n")
        
        for i, juego in enumerate(juegos, 1):
            print(f"{i}. 🎮 {juego['titulo']}")
            print(f"   🔗 {juego['url']}")
            print(f"   📝 {juego.get('descripcion', 'Sin descripción')[:80]}...")
            print()
    else:
        print("\n⚠️ No se encontraron juegos (puede ser que RSS esté vacío)")
    
    print("="*70)
    print("✅ TEST COMPLETADO")
    print("="*70)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*70)
