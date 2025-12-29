#!/usr/bin/env python3
"""
🦈 Test CheapShark Hunter
Prueba completa con scoring y reviews
"""

import sys
sys.path.insert(0, '.')

from modules.cheapshark_hunter import CheapSharkHunter
from modules.scoring import SistemaScoring

def test_completo():
    print("\n" + "="*70)
    print("🦈 TEST COMPLETO - CheapShark + Scoring")
    print("="*70 + "\n")
    
    hunter = CheapSharkHunter()
    scoring = SistemaScoring()
    
    # Test 1: Juegos gratis
    print("📦 Test 1: Juegos Gratis\n")
    juegos = hunter.obtener_juegos_gratis()
    
    if juegos:
        print(f"✅ {len(juegos)} juego(s) gratis encontrados\n")
        print("─" * 70)
        
        for i, juego in enumerate(juegos[:5], 1):
            score = scoring.calcular_score(juego)
            estrellas = scoring.obtener_estrellas(score)
            clasificacion = scoring.clasificar_juego(score)
            
            print(f"\n{i}. {estrellas} {juego['titulo']}")
            print(f"   🏪 {juego['tienda_emoji']} {juego['tienda']}")
            print(f"   📊 Score: {score:.1f}/5.0 ({clasificacion.upper()})")
            
            if juego.get('reviews_percent'):
                print(f"   ⭐ {juego['reviews_percent']}% positivas ({juego['reviews_count']:,} reviews)")
            else:
                print(f"   📊 Sin reviews disponibles")
            
            if juego.get('metacritic'):
                print(f"   🎯 Metacritic: {juego['metacritic']}")
            
            print(f"   🔗 {juego['url'][:60]}...")
        
        print("\n" + "─" * 70)
    else:
        print("💤 No hay juegos gratis en este momento")
    
    # Test 2: Ofertas con descuento
    print("\n\n📦 Test 2: Ofertas con Descuento (70%+)\n")
    ofertas = hunter.obtener_ofertas_descuento(70, 10)
    
    if ofertas:
        print(f"✅ {len(ofertas)} oferta(s) encontradas\n")
        print("─" * 70)
        
        # Clasificar ofertas
        ofertas_premium = []
        ofertas_regulares = []
        
        for oferta in ofertas[:10]:
            score = scoring.calcular_score(oferta)
            estrellas = scoring.obtener_estrellas(score)
            oferta['score'] = score
            oferta['estrellas'] = estrellas
            
            if score >= 3.6:
                ofertas_premium.append(oferta)
            else:
                ofertas_regulares.append(oferta)
        
        # Mostrar ofertas premium
        if ofertas_premium:
            print(f"\n💎 OFERTAS PREMIUM (3.6+): {len(ofertas_premium)}\n")
            for i, oferta in enumerate(ofertas_premium[:5], 1):
                print(f"{i}. {oferta['estrellas']} {oferta['titulo']}")
                print(f"   🏪 {oferta['tienda_emoji']} {oferta['tienda']}")
                print(f"   💸 ${oferta['precio_actual']:.2f} (era ${oferta['precio_regular']:.2f})")
                print(f"   📊 -{oferta['descuento_porcentaje']}% | Score: {oferta['score']:.1f}/5.0")
                
                if oferta.get('reviews_percent'):
                    print(f"   ⭐ {oferta['reviews_percent']}% ({oferta['reviews_count']:,} reviews)")
                print()
        
        # Mostrar ofertas regulares
        if ofertas_regulares and len(ofertas_regulares) > 0:
            print(f"\n💰 OFERTAS REGULARES (<3.6): {len(ofertas_regulares)}\n")
            for i, oferta in enumerate(ofertas_regulares[:3], 1):
                print(f"{i}. {oferta['estrellas']} {oferta['titulo']}")
                print(f"   🏪 {oferta['tienda_emoji']} {oferta['tienda']}")
                print(f"   💸 ${oferta['precio_actual']:.2f} | -{oferta['descuento_porcentaje']}%")
                print()
        
        print("─" * 70)
    else:
        print("💤 No hay ofertas con 70%+ descuento en este momento")
    
    # Resumen
    print("\n\n📊 RESUMEN:")
    print(f"   🎮 Juegos gratis: {len(juegos)}")
    print(f"   💰 Ofertas encontradas: {len(ofertas)}")
    
    if ofertas:
        ofertas_premium = [o for o in ofertas if scoring.calcular_score(o) >= 3.6]
        print(f"   💎 Ofertas premium (3.6+): {len(ofertas_premium)}")
    
    # Tiendas representadas
    if juegos or ofertas:
        todas = juegos + ofertas
        tiendas = set(j['tienda'] for j in todas)
        print(f"\n   🏪 Tiendas con ofertas ({len(tiendas)}):")
        for tienda in sorted(tiendas):
            count = sum(1 for j in todas if j['tienda'] == tienda)
            print(f"      • {tienda}: {count}")
    
    print("\n" + "="*70)
    print("✅ Test completado!")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        test_completo()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrumpido\n")
    except Exception as e:
        print(f"\n❌ Error en test: {e}\n")
        import traceback
        traceback.print_exc()
