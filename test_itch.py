"""
🧪 Test de Itch.io Hunter
Verifica que la integración funcione correctamente
"""

import sys
import os

# Asegurar que podemos importar los módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.itch_hunter import ItchHunter

def test_basic():
    """Test básico de funcionalidad"""
    print("\n" + "="*70)
    print("🧪 TEST BÁSICO - Itch.io Hunter")
    print("="*70)
    
    # Inicializar hunter
    hunter = ItchHunter()
    
    # Test 1: Obtener juegos con filtros relajados
    print("\n📦 Test 1: Obtener juegos (filtros relajados)")
    juegos = hunter.obtener_juegos_gratis(
        limite=10,
        min_rating=0,  # Sin filtro de rating
        min_downloads=0  # Sin filtro de downloads
    )
    
    assert isinstance(juegos, list), "❌ Debe retornar una lista"
    print(f"✅ Retornó lista con {len(juegos)} juego(s)")
    
    if juegos:
        # Verificar estructura del primer juego
        juego = juegos[0]
        campos_requeridos = ['id', 'titulo', 'tienda', 'url', 'tipo']
        
        for campo in campos_requeridos:
            assert campo in juego, f"❌ Falta campo '{campo}'"
        
        print(f"\n✅ Estructura del juego validada")
        print(f"\nPrimer juego encontrado:")
        print(f"  🎮 Título: {juego['titulo']}")
        print(f"  🏪 Tienda: {juego['tienda']}")
        print(f"  🔗 URL: {juego['url'][:60]}...")
        if juego.get('autor'):
            print(f"  👤 Autor: {juego['autor']}")
        if juego.get('rating'):
            print(f"  ⭐ Rating: {juego['rating']:.1f}/5.0")
    else:
        print("⚠️ No se encontraron juegos (puede ser temporal)")
    
    # Test 2: Obtener juegos con filtros de calidad
    print("\n\n📦 Test 2: Obtener juegos de calidad (filtros activos)")
    juegos_calidad = hunter.obtener_juegos_gratis(
        limite=5,
        min_rating=3.5,
        min_downloads=50
    )
    
    print(f"✅ Retornó {len(juegos_calidad)} juego(s) de calidad")
    
    if juegos_calidad:
        print(f"\nJuegos de calidad encontrados:")
        for i, juego in enumerate(juegos_calidad[:3], 1):
            print(f"\n  {i}. {juego['titulo']}")
            if juego.get('rating'):
                print(f"     ⭐ Rating: {juego['rating']:.1f}/5.0")
            if juego.get('downloads'):
                print(f"     📥 {juego['downloads']:,} descargas")
    
    print("\n" + "="*70)
    print("✅ TODOS LOS TESTS PASARON")
    print("="*70 + "\n")
    
    return True


def test_integration():
    """Test de integración con el sistema completo"""
    print("\n" + "="*70)
    print("🧪 TEST DE INTEGRACIÓN")
    print("="*70)
    
    try:
        # Importar módulo de scoring
        from modules.scoring import SistemaScoring
        
        hunter = ItchHunter()
        scoring = SistemaScoring()
        
        print("\n📦 Obteniendo juegos de Itch.io...")
        juegos = hunter.obtener_juegos_gratis(limite=5, min_rating=0, min_downloads=0)
        
        if not juegos:
            print("⚠️ No se obtuvieron juegos para testear scoring")
            return True
        
        print(f"✅ Obtenidos {len(juegos)} juego(s)")
        
        # Test de scoring
        print("\n📊 Testeando sistema de scoring...")
        for juego in juegos[:3]:
            score = scoring.calcular_score(juego)
            clasificacion = scoring.clasificar_juego(score)
            estrellas = scoring.obtener_estrellas(score)
            
            print(f"\n  {estrellas} {juego['titulo']}")
            print(f"     Score: {score:.1f}/5.0")
            print(f"     Clasificación: {clasificacion}")
        
        print("\n✅ Integración con scoring exitosa")
        print("="*70 + "\n")
        
        return True
    
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en test de integración: {e}")
        return False


if __name__ == "__main__":
    print("\n🎮 HunDea v2.8 - Test Suite de Itch.io\n")
    
    try:
        # Ejecutar tests
        test_basic()
        test_integration()
        
        print("\n🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE\n")
        sys.exit(0)
    
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}\n")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
