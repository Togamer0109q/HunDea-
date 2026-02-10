#!/usr/bin/env python3
"""
🧪 Test de Integración - CheapShark + ITAD + Epic
Prueba rápida de todas las fuentes integradas
"""

import sys
import os
sys.path.insert(0, '.')

from modules.epic_hunter import EpicHunter
from modules.itad_hunter import IsThereAnyDealHunter
from modules.cheapshark_hunter import CheapSharkHunter
from modules.scoring import SistemaScoring
from modules.reviews_externas import ReviewsExternas
import json
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*_args, **_kwargs):
        return False

def test_integracion_completa():
    print("\n" + "="*70)
    print("🧪 TEST DE INTEGRACIÓN COMPLETA")
    print("="*70 + "\n")
    
    # Cargar config
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except:
        config = {'deals_descuento_minimo': 70, 'deals_precio_maximo': 10}
    
    load_dotenv()

    # Inicializar todos los hunters
    print("🚀 Inicializando hunters...")
    epic_hunter = EpicHunter()
    itad_hunter = IsThereAnyDealHunter()
    cheapshark_hunter = CheapSharkHunter()
    scoring = SistemaScoring()
    
    # Reviews externas
    rawg_api_key = os.getenv('RAWG_API_KEY') or config.get('rawg_api_key')
    reviews_externas = ReviewsExternas(api_key=rawg_api_key)
    
    print("\n" + "─"*70)
    print("📦 PARTE 1: JUEGOS GRATIS")
    print("─"*70 + "\n")
    
    # 1. Epic Games
    print("🎮 Epic Games...")
    juegos_epic = epic_hunter.obtener_juegos_gratis()
    
    # 2. ITAD
    print("\n🌟 IsThereAnyDeal...")
    juegos_itad = itad_hunter.obtener_juegos_gratis()
    
    # 3. CheapShark
    print("\n🦈 CheapShark...")
    juegos_cheapshark = cheapshark_hunter.obtener_juegos_gratis()
    
    # Combinar todos
    todos_juegos = juegos_epic + juegos_itad + juegos_cheapshark
    
    print(f"\n📊 Total juegos gratis: {len(todos_juegos)}")
    print(f"   • Epic: {len(juegos_epic)}")
    print(f"   • ITAD: {len(juegos_itad)}")
    print(f"   • CheapShark: {len(juegos_cheapshark)}")
    
    # Mostrar algunos ejemplos
    if todos_juegos:
        print("\n🎮 Ejemplos de juegos gratis encontrados:\n")
        for i, juego in enumerate(todos_juegos[:5], 1):
            score = scoring.calcular_score(juego)
            estrellas = scoring.obtener_estrellas(score)
            print(f"{i}. {estrellas} {juego['titulo']}")
            print(f"   🏪 {juego.get('tienda', 'N/A')} | 📊 {score:.1f}/5.0")
            if juego.get('reviews_percent'):
                print(f"   ⭐ {juego['reviews_percent']}% ({juego['reviews_count']:,} reviews)")
            print()
    
    print("\n" + "─"*70)
    print("💰 PARTE 2: OFERTAS CON DESCUENTO")
    print("─"*70 + "\n")
    
    descuento_min = config.get('deals_descuento_minimo', 70)
    precio_max = config.get('deals_precio_maximo', 10)
    
    # 1. ITAD Ofertas
    print(f"💎 IsThereAnyDeal (ofertas {descuento_min}%+)...")
    ofertas_itad = itad_hunter.obtener_ofertas_descuento(descuento_min)
    
    # 2. CheapShark Ofertas
    print(f"\n🦈 CheapShark (ofertas {descuento_min}%+, max ${precio_max})...")
    ofertas_cheapshark = cheapshark_hunter.obtener_ofertas_descuento(descuento_min, precio_max)
    
    # Combinar ofertas
    todas_ofertas = ofertas_itad + ofertas_cheapshark
    
    print(f"\n📊 Total ofertas: {len(todas_ofertas)}")
    print(f"   • ITAD: {len(ofertas_itad)}")
    print(f"   • CheapShark: {len(ofertas_cheapshark)}")
    
    # Clasificar ofertas por calidad
    ofertas_premium = []
    ofertas_regulares = []
    score_minimo = config.get('deals_score_minimo', 3.6)
    
    for oferta in todas_ofertas:
        score = scoring.calcular_score(oferta)
        oferta['score'] = score
        oferta['estrellas'] = scoring.obtener_estrellas(score)
        
        if score >= score_minimo:
            ofertas_premium.append(oferta)
        else:
            ofertas_regulares.append(oferta)
    
    print(f"\n💎 Ofertas Premium ({score_minimo}+): {len(ofertas_premium)}")
    print(f"💰 Ofertas Regulares (<{score_minimo}): {len(ofertas_regulares)}")
    
    # Mostrar ofertas premium
    if ofertas_premium:
        print(f"\n🏆 TOP 5 OFERTAS PREMIUM:\n")
        # Ordenar por score
        ofertas_premium.sort(key=lambda x: x['score'], reverse=True)
        
        for i, oferta in enumerate(ofertas_premium[:5], 1):
            print(f"{i}. {oferta['estrellas']} {oferta['titulo']}")
            print(f"   🏪 {oferta.get('tienda', 'N/A')} | 📊 {oferta['score']:.1f}/5.0")
            print(f"   💸 ${oferta.get('precio_actual', 0):.2f} (era ${oferta.get('precio_regular', 0):.2f})")
            print(f"   📊 -{oferta.get('descuento_porcentaje', 0)}% descuento")
            if oferta.get('reviews_percent'):
                print(f"   ⭐ {oferta['reviews_percent']}% ({oferta['reviews_count']:,} reviews)")
            print()
    
    print("─"*70)
    print("📈 RESUMEN FINAL")
    print("─"*70 + "\n")
    
    print(f"🎮 Juegos Gratis Totales: {len(todos_juegos)}")
    print(f"💰 Ofertas Totales: {len(todas_ofertas)}")
    print(f"💎 Ofertas de Calidad: {len(ofertas_premium)}")
    
    # Estadísticas por fuente
    print("\n📊 Desglose por fuente:")
    fuentes_gratis = {}
    fuentes_ofertas = {}
    
    for juego in todos_juegos:
        fuente = juego.get('fuente', 'Desconocido')
        fuentes_gratis[fuente] = fuentes_gratis.get(fuente, 0) + 1
    
    for oferta in todas_ofertas:
        fuente = oferta.get('fuente', 'Desconocido')
        fuentes_ofertas[fuente] = fuentes_ofertas.get(fuente, 0) + 1
    
    print("\n   Juegos Gratis:")
    for fuente, count in fuentes_gratis.items():
        print(f"   • {fuente}: {count}")
    
    print("\n   Ofertas:")
    for fuente, count in fuentes_ofertas.items():
        print(f"   • {fuente}: {count}")
    
    # Tiendas únicas
    tiendas = set()
    for item in todos_juegos + todas_ofertas:
        if item.get('tienda'):
            tiendas.add(item['tienda'])
    
    print(f"\n🏪 Tiendas cubiertas: {len(tiendas)}")
    for tienda in sorted(tiendas):
        print(f"   • {tienda}")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETADO!")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        test_integracion_completa()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrumpido\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
