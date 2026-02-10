"""
🧪 Test rápido del módulo de consolas
"""
import sys
sys.path.insert(0, 'C:/HunDeaBot')

print("\n" + "="*70)
print("🎮 TEST - Consolas Hunter (PlayStation, Xbox, Nintendo)")
print("="*70 + "\n")

try:
    from modules.consolas_hunter import ConsolasHunter
    
    hunter = ConsolasHunter()
    
    print("📦 Obteniendo ofertas de consolas (límite: 3 por plataforma)...\n")
    ofertas = hunter.obtener_ofertas(limite=3)
    
    if ofertas:
        print(f"\n✅ ÉXITO: {len(ofertas)} oferta(s) encontradas\n")
        
        # Agrupar por plataforma
        por_plataforma = {}
        for oferta in ofertas:
            plat = oferta['tienda']
            if plat not in por_plataforma:
                por_plataforma[plat] = []
            por_plataforma[plat].append(oferta)
        
        # Mostrar por plataforma
        for plataforma, lista in por_plataforma.items():
            print(f"\n{lista[0]['tienda_emoji']} {plataforma} ({len(lista)} oferta(s)):")
            print("─" * 60)
            
            for i, oferta in enumerate(lista[:3], 1):
                print(f"\n  {i}. {oferta['titulo']}")
                if oferta.get('descuento_porcentaje'):
                    print(f"     💰 -{oferta['descuento_porcentaje']}% descuento")
                if oferta.get('precio_actual'):
                    print(f"     💸 ${oferta['precio_actual']:.2f}")
                print(f"     🔗 {oferta['url'][:60]}...")
    else:
        print("\n⚠️ No se encontraron ofertas (puede ser temporal)")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETADO")
    print("="*70 + "\n")

except ImportError as e:
    print(f"❌ Error al importar módulo: {e}")
    print("\n¿feedparser está instalado?")
    print("Ejecuta: pip install feedparser\n")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
