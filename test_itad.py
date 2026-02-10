#!/usr/bin/env python3
"""
🧪 Test para IsThereAnyDeal Hunter
Prueba rápida de la integración con ITAD
"""

import sys
import os
sys.path.insert(0, '.')

from modules.itad_hunter import IsThereAnyDealHunter
from modules.reviews_externas import ReviewsExternas
from modules.scoring import SistemaScoring
import json
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*_args, **_kwargs):
        return False

def test_itad_completo():
    """Prueba completa de ITAD + Reviews + Scoring"""
    
    print("\n" + "="*70)
    print("🧪 TEST COMPLETO - IsThereAnyDeal + Reviews + Scoring")
    print("="*70 + "\n")
    
    # 1. Inicializar hunter
    print("📦 Inicializando IsThereAnyDeal Hunter...")
    hunter = IsThereAnyDealHunter()
    
    # 2. Buscar juegos gratis
    print("\n🔍 Buscando juegos gratis en múltiples tiendas...\n")
    juegos = hunter.obtener_juegos_gratis()
    
    if not juegos:
        print("❌ No se encontraron juegos gratis")
        print("💡 Esto puede ser normal si no hay ofertas activas")
        return
    
    # 3. Cargar config para RAWG
    load_dotenv()
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            rawg_key = os.getenv('RAWG_API_KEY') or config.get('rawg_api_key')
    except:
        rawg_key = os.getenv('RAWG_API_KEY')
    
    reviews_ext = ReviewsExternas(api_key=rawg_key)
    scoring = SistemaScoring()
    
    # 4. Procesar cada juego
    print(f"\n📊 Procesando {len(juegos)} juego(s)...\n")
    print("─" * 70)
    
    for i, juego in enumerate(juegos, 1):
        print(f"\n{i}. {juego['tienda_emoji']} {juego['titulo']}")
        print(f"   🏪 Tienda: {juego['tienda']}")
        print(f"   🔗 {juego['url'][:60]}...")
        print(f"   ⏰ Disponible hasta: {juego['fecha_fin']}")
        
        # Buscar reviews
        if not juego.get('reviews_count'):
            print(f"   🔍 Buscando reviews...")
            reviews = reviews_ext.buscar_reviews(juego['titulo'], juego['tienda'])
            if reviews:
                juego.update(reviews)
                print(f"   ✅ Reviews encontradas: {reviews['reviews_count']:,}")
            else:
                print(f"   ⚠️ Sin reviews disponibles")
        
        # Calcular score
        score = scoring.calcular_score(juego)
        estrellas = scoring.obtener_estrellas(score)
        clasificacion = scoring.clasificar_juego(score)
        
        print(f"   📊 Score HunDea: {score:.1f}/5.0 {estrellas}")
        print(f"   🏆 Clasificación: {clasificacion.upper()}")
        
        if juego.get('reviews_count'):
            print(f"   ⭐ {juego['reviews_percent']}% positivas ({juego['reviews_count']:,} reviews)")
        
        print("   " + "─" * 66)
    
    # 5. Resumen
    premium = sum(1 for j in juegos if scoring.clasificar_juego(scoring.calcular_score(j)) == 'premium')
    bajos = len(juegos) - premium
    
    print(f"\n📈 RESUMEN:")
    print(f"   ✨ Total encontrado: {len(juegos)} juego(s)")
    print(f"   ⭐ Premium (3.5+): {premium} juego(s)")
    print(f"   ⚠️  Bajos (<3.5): {bajos} juego(s)")
    
    # 6. Tiendas representadas
    tiendas = set(j['tienda'] for j in juegos)
    print(f"\n🏪 Tiendas representadas ({len(tiendas)}):")
    for tienda in sorted(tiendas):
        count = sum(1 for j in juegos if j['tienda'] == tienda)
        print(f"   • {tienda}: {count} juego(s)")
    
    print("\n" + "="*70)
    print("✅ Test completado!")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        test_itad_completo()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrumpido\n")
    except Exception as e:
        print(f"\n❌ Error en test: {e}\n")
        import traceback
        traceback.print_exc()
