#!/usr/bin/env python3
"""
🧪 Test de Normalización y Deduplicación
Verifica que los duplicados se eliminen correctamente
"""

import sys
sys.path.insert(0, '.')

# Importar funciones desde hundea_v2
from hundea_v2 import normalizar_titulo, eliminar_duplicados

def test_normalizacion():
    """Test de normalización de títulos"""
    print("\n" + "="*70)
    print("🧪 TEST - Normalización de Títulos")
    print("="*70 + "\n")
    
    casos_test = [
        ("Rustler - Grand Theft Horse es GRATIS", "Rustler (Grand Theft Horse)", True),
        ("The Witcher 3", "Witcher 3", True),
        ("Grand Theft Auto V", "GTA V", False),  # No debería coincidir (muy diferentes)
        ("Viewfinder", "Viewfinder", True),
        ("XCOM 2", "xcom 2", True),
        ("The Last of Us", "Last of Us", True),
    ]
    
    exitos = 0
    fallos = 0
    
    for titulo1, titulo2, deberia_coincidir in casos_test:
        norm1 = normalizar_titulo(titulo1)
        norm2 = normalizar_titulo(titulo2)
        
        coincide = norm1 == norm2
        resultado = "✅" if coincide == deberia_coincidir else "❌"
        
        print(f"{resultado} Test:")
        print(f"   Título 1: '{titulo1}'")
        print(f"   Normalizado: '{norm1}'")
        print(f"   Título 2: '{titulo2}'")
        print(f"   Normalizado: '{norm2}'")
        print(f"   Coincide: {coincide} (esperado: {deberia_coincidir})")
        
        if coincide == deberia_coincidir:
            exitos += 1
        else:
            fallos += 1
        print()
    
    print("="*70)
    print(f"✅ Éxitos: {exitos}")
    print(f"❌ Fallos: {fallos}")
    print("="*70 + "\n")

def test_deduplicacion():
    """Test de deduplicación"""
    print("\n" + "="*70)
    print("🧪 TEST - Deduplicación de Juegos")
    print("="*70 + "\n")
    
    # Simular juegos duplicados como Rustler
    juegos = [
        {
            'id': 'epic_rustler',
            'titulo': 'Rustler - Grand Theft Horse es GRATIS',
            'tienda': 'Epic Games',
            'reviews_count': 3089,
            'reviews_percent': 85.2
        },
        {
            'id': 'cheapshark_rustler',
            'titulo': 'Rustler (Grand Theft Horse)',
            'tienda': 'Epic Games',
            'reviews_count': 1121,
            'reviews_percent': 79
        },
        {
            'id': 'epic_rustler_2',
            'titulo': 'Rustler - Grand Theft Horse',
            'tienda': 'Epic Games',
            'reviews_count': 3089,
            'reviews_percent': 85.2
        }
    ]
    
    print(f"📊 Juegos originales: {len(juegos)}")
    for juego in juegos:
        print(f"   • {juego['titulo']} ({juego['reviews_count']} reviews)")
    
    # Deduplicar
    unicos = eliminar_duplicados(juegos)
    
    print(f"\n📊 Después de deduplicar: {len(unicos)}")
    for juego in unicos:
        print(f"   ✅ {juego['titulo']} ({juego['reviews_count']} reviews)")
    
    if len(unicos) == 1:
        print(f"\n✅ DEDUPLICACIÓN CORRECTA - Se mantiene el de más reviews")
        print(f"   Seleccionado: {unicos[0]['titulo']}")
        print(f"   Reviews: {unicos[0]['reviews_count']}")
    else:
        print(f"\n❌ ERROR - Deberían quedar solo 1 juego, hay {len(unicos)}")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    test_normalizacion()
    test_deduplicacion()
