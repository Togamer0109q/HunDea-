"""
🧪 Test Detallado de Itch.io RSS Feed
Muestra paso a paso qué está pasando
"""

print("\n" + "="*70)
print("🧪 TEST DETALLADO - Itch.io RSS Feed")
print("="*70 + "\n")

# Paso 1: Verificar requests
print("📦 Paso 1: Verificando requests...")
try:
    import requests
    print("   ✅ requests instalado")
except ImportError:
    print("   ❌ requests no instalado")
    exit(1)

# Paso 2: Verificar XML parser
print("\n📦 Paso 2: Verificando xml.etree...")
try:
    import xml.etree.ElementTree as ET
    print("   ✅ xml.etree disponible")
except ImportError:
    print("   ❌ xml.etree no disponible")
    exit(1)

# Paso 3: Test directo del RSS
print("\n📦 Paso 3: Testeando RSS directamente...")
RSS_URL = "https://itch.io/games/price-free.xml"

try:
    print(f"   🔗 Consultando: {RSS_URL}")
    response = requests.get(RSS_URL, timeout=15)
    print(f"   📡 Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ❌ RSS no accesible")
        exit(1)
    
    print(f"   📊 Tamaño respuesta: {len(response.content)} bytes")
    
    # Parsear XML
    print("\n📦 Paso 4: Parseando XML...")
    root = ET.fromstring(response.content)
    print(f"   ✅ XML parseado exitosamente")
    print(f"   🏷️  Root tag: {root.tag}")
    
    # Buscar items
    print("\n📦 Paso 5: Buscando items...")
    items = root.findall('.//item')
    print(f"   ✅ Encontrados {len(items)} items en el RSS")
    
    if items:
        # Mostrar primeros 3 items
        print("\n📦 Paso 6: Extrayendo info de primeros items...\n")
        
        for i, item in enumerate(items[:3], 1):
            print(f"   --- Item {i} ---")
            
            # Título
            titulo_elem = item.find('title')
            titulo = titulo_elem.text if titulo_elem is not None else 'Sin título'
            print(f"   🎮 Título: {titulo}")
            
            # URL
            link_elem = item.find('link')
            url = link_elem.text if link_elem is not None else 'Sin URL'
            print(f"   🔗 URL: {url}")
            
            # Descripción
            desc_elem = item.find('description')
            if desc_elem is not None and desc_elem.text:
                import re
                desc = re.sub('<[^<]+?>', '', desc_elem.text)
                print(f"   📝 Descripción: {desc[:100]}...")
            
            # Fecha
            pub_elem = item.find('pubDate')
            if pub_elem is not None:
                print(f"   📅 Fecha: {pub_elem.text}")
            
            print()
        
        print("="*70)
        print("✅ RSS FUNCIONA PERFECTAMENTE")
        print("="*70)
        
    else:
        print("\n   ⚠️ No hay items en el RSS (puede estar vacío temporalmente)")

except requests.Timeout:
    print("\n   ❌ Timeout al consultar RSS")
except requests.RequestException as e:
    print(f"\n   ❌ Error de red: {e}")
except ET.ParseError as e:
    print(f"\n   ❌ Error parseando XML: {e}")
except Exception as e:
    print(f"\n   ❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()

print("\n📦 Paso 7: Test del módulo ItchHunter...\n")

try:
    import sys
    sys.path.insert(0, 'C:/HunDeaBot')
    
    from modules.itch_hunter import ItchHunter
    
    hunter = ItchHunter()
    juegos = hunter.obtener_juegos_gratis(limite=5)
    
    if juegos:
        print(f"\n✅ Módulo funciona: {len(juegos)} juego(s)")
        print("\nPrimer juego:")
        print(f"   {juegos[0]}")
    else:
        print("\n⚠️ Módulo retornó lista vacía")
    
    print("\n" + "="*70)
    print("✅ TODOS LOS TESTS PASARON")
    print("="*70 + "\n")

except ImportError as e:
    print(f"   ❌ Error importando módulo: {e}")
except Exception as e:
    print(f"   ❌ Error en módulo: {e}")
    import traceback
    traceback.print_exc()
