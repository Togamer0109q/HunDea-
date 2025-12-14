import requests
from datetime import datetime
import json
import os

# 🎮 HunDea - Epic Games Free Hunter v1.0
# Bot cazador de juegos gratis de Epic Games

def cargar_config():
    """
    Carga la configuración desde config.json
    """
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró config.json")
        print("💡 Crea un archivo config.json con tu webhook de Discord")
        return None
    except json.JSONDecodeError:
        print("❌ Error al leer config.json - verifica que sea JSON válido")
        return None


def cargar_cache():
    """
    Carga los juegos ya anunciados para no repetirlos
    """
    try:
        with open('cache.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"juegos_anunciados": []}


def guardar_cache(cache):
    """
    Guarda los juegos anunciados en cache.json
    """
    with open('cache.json', 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def obtener_juegos_gratis():
    """
    Consulta la API de Epic Games y devuelve los juegos gratis actuales
    """
    url = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions"
    
    try:
        print("🔍 Consultando Epic Games Store...")
        response = requests.get(url, params={'locale': 'es-ES', 'country': 'CO'}, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        juegos_gratis = []
        
        elementos = data.get('data', {}).get('Catalog', {}).get('searchStore', {}).get('elements', [])
        
        for juego in elementos:
            promociones = juego.get('promotions')
            if not promociones:
                continue
                
            ofertas = promociones.get('promotionalOffers', [])
            if not ofertas:
                continue
            
            for oferta in ofertas:
                for detalle in oferta.get('promotionalOffers', []):
                    precio = detalle.get('discountSetting', {}).get('discountPercentage', 0)
                    
                    if precio == 0:
                        # Construir URL del juego
                        slug = ''
                        mappings = juego.get('catalogNs', {}).get('mappings', [])
                        if mappings:
                            slug = mappings[0].get('pageSlug', '')
                        
                        if not slug:
                            slug = juego.get('productSlug', '')
                        
                        info_juego = {
                            'titulo': juego.get('title', 'Sin título'),
                            'descripcion': juego.get('description', 'Sin descripción'),
                            'inicio': detalle.get('startDate'),
                            'fin': detalle.get('endDate'),
                            'url': f"https://store.epicgames.com/es-ES/p/{slug}" if slug else "https://store.epicgames.com/es-ES/free-games",
                            'imagen': None,
                            'id': juego.get('id', '')
                        }
                        
                        # Buscar la mejor imagen
                        imagenes = juego.get('keyImages', [])
                        for img in imagenes:
                            if img.get('type') in ['DieselStoreFrontWide', 'OfferImageWide']:
                                info_juego['imagen'] = img.get('url')
                                break
                        
                        if not info_juego['imagen'] and imagenes:
                            info_juego['imagen'] = imagenes[0].get('url')
                        
                        juegos_gratis.append(info_juego)
        
        print(f"✅ Se encontraron {len(juegos_gratis)} juego(s) gratis")
        return juegos_gratis
    
    except requests.exceptions.Timeout:
        print("❌ Tiempo de espera agotado al consultar Epic Games")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al consultar Epic Games: {e}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return []


def formatear_fecha(fecha_str):
    """
    Convierte la fecha ISO a formato legible en español
    """
    try:
        fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
        meses = {
            1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
            5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
            9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
        }
        return f"{fecha.day} de {meses[fecha.month]}, {fecha.hour:02d}:{fecha.minute:02d}"
    except:
        return "Fecha no disponible"


def enviar_a_discord(juego, webhook_url):
    """
    Envía un embed bonito a Discord con la info del juego gratis
    """
    try:
        # Crear el embed para Discord
        embed = {
            "title": f"🎁 {juego['titulo']} es GRATIS",
            "description": juego['descripcion'][:200] + "..." if len(juego['descripcion']) > 200 else juego['descripcion'],
            "url": juego['url'],
            "color": 0x00D9FF,  # Color azul de Epic
            "fields": [
                {
                    "name": "⏰ Disponible hasta",
                    "value": formatear_fecha(juego['fin']),
                    "inline": False
                }
            ],
            "footer": {
                "text": "HunDea • Free Games Hunter"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Agregar imagen si existe
        if juego['imagen']:
            embed["image"] = {"url": juego['imagen']}
        
        # Payload completo
        payload = {
            "content": "🎮 **¡Nuevo juego GRATIS en Epic Games!**",
            "embeds": [embed]
        }
        
        # Enviar al webhook
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.status_code == 204:
            print(f"✅ Alerta enviada a Discord: {juego['titulo']}")
            return True
        else:
            print(f"⚠️ Discord respondió con código {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error al enviar a Discord: {e}")
        return False


def mostrar_juegos_consola(juegos):
    """
    Muestra los juegos en la terminal
    """
    if not juegos:
        print("\n😔 No hay juegos gratis disponibles ahora mismo\n")
        return
    
    print(f"\n{'='*60}")
    print(f"🎁 ¡{len(juegos)} juego(s) GRATIS en Epic Games!")
    print(f"{'='*60}\n")
    
    for i, juego in enumerate(juegos, 1):
        print(f"🎮 {i}. {juego['titulo']}")
        print(f"⏰ Hasta: {formatear_fecha(juego['fin'])}")
        print(f"🔗 {juego['url']}")
        print(f"{'-'*60}")


def main():
    """
    Función principal de HunDea
    """
    print("\n" + "="*60)
    print("🎮 HunDea - Epic Games Free Hunter v1.0")
    print("="*60 + "\n")
    
    # Cargar configuración
    config = cargar_config()
    if not config:
        print("\n💡 Tip: Crea config.json con este formato:")
        print(json.dumps({"webhook_url": "tu_webhook_aqui", "enviar_discord": True}, indent=2))
        print("\n⚠️ Continuando en modo solo consola...\n")
    
    # Cargar cache
    cache = cargar_cache()
    
    # Obtener juegos gratis
    juegos = obtener_juegos_gratis()
    
    if not juegos:
        print("\n✅ No hay juegos gratis nuevos por ahora")
        return
    
    # Mostrar en consola
    mostrar_juegos_consola(juegos)
    
    # Si hay configuración, enviar a Discord
    if config and config.get('enviar_discord', False):
        webhook_url = config.get('webhook_url', '')
        
        if not webhook_url or webhook_url == "tu_webhook_aqui":
            print("\n⚠️ No hay webhook configurado. Solo mostrando en consola.")
        else:
            print("\n📤 Enviando alertas a Discord...\n")
            
            juegos_nuevos = 0
            for juego in juegos:
                # Verificar si ya fue anunciado
                if juego['id'] in cache['juegos_anunciados']:
                    print(f"⏭️ Saltando {juego['titulo']} (ya fue anunciado)")
                    continue
                
                # Enviar a Discord
                if enviar_a_discord(juego, webhook_url):
                    cache['juegos_anunciados'].append(juego['id'])
                    juegos_nuevos += 1
            
            # Guardar cache actualizado
            guardar_cache(cache)
            
            if juegos_nuevos > 0:
                print(f"\n🎉 {juegos_nuevos} alerta(s) nueva(s) enviada(s) a Discord")
            else:
                print("\n✅ Todos los juegos ya habían sido anunciados")
    
    print("\n" + "="*60)
    print("✅ Búsqueda completada!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
