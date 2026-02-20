"""
🎁 GamerPower Hunter - Solo JUEGOS COMPLETOS
Busca SOLO juegos gratis completos (NO keys, codes, DLCs)
"""

import requests
from datetime import datetime


class GamerPowerHunter:
    """
    Busca SOLO juegos completos en GamerPower
    FILTRA: Keys, Codes, DLCs, Skins, Packs, etc.
    """
    
    def __init__(self):
        self.api_url = "https://www.gamerpower.com/api/giveaways"
        
        # BLACKLIST - Filtrar toda esta basura
        self.spam_keywords = [
            'key giveaway',
            'gift code',
            'gift pack',
            'gift key',
            'promo code',
            'bonus code',
            'invite code',
            'free code',
            'starter pack',
            'starter kit',
            'beginner pack',
            'in-game pack',
            'supply drop',
            'emblem',
            'skin',
            'decal',
            'sleeve',
            'emote',
            'bundle key',
            'dlc',
            'content pack',
            'booster',
            'credits',
            'gold',
            'points',
            'primogems',
            'mobile app',
            'chrome extension',
            'card pack',
            'card sleeve'
        ]
    
    def obtener_juegos_gratis(self):
        """
        Obtiene SOLO juegos completos de GamerPower
        
        Returns:
            list: Lista de JUEGOS (no basura)
        """
        juegos_reales = []
        spam_bloqueado = 0
        
        try:
            print("🔍 Consultando GamerPower API...")
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            for item in data:
                try:
                    title = item.get('title', 'Unknown')
                    description = item.get('description', '')
                    giveaway_type = item.get('type', '')
                    
                    # FILTRO AGRESIVO - Bloquear toda la basura
                    title_lower = title.lower()
                    desc_lower = description.lower()
                    type_lower = giveaway_type.lower()
                    
                    # Verificar si es SPAM
                    es_spam = False
                    for keyword in self.spam_keywords:
                        if keyword in title_lower or keyword in type_lower:
                            es_spam = True
                            break
                    
                    if es_spam:
                        spam_bloqueado += 1
                        continue
                    
                    # Solo JUEGOS COMPLETOS (Game type)
                    if giveaway_type.lower() not in ['game', 'early access', 'beta']:
                        spam_bloqueado += 1
                        continue
                    
                    # Verificar plataformas válidas
                    platforms = item.get('platforms', '')
                    if 'Android' in platforms and 'iOS' in platforms and 'PC' not in platforms:
                        # Solo móvil, probablemente basura
                        spam_bloqueado += 1
                        continue
                    
                    # Si pasó todos los filtros, es un juego real
                    url = item.get('open_giveaway_url') or item.get('gamerpower_url', '')
                    image = item.get('image', None)
                    end_date = item.get('end_date', None)
                    worth = item.get('worth', 'N/A')
                    
                    # Crear info del juego
                    info = {
                        'id': f"gamerpower_{item.get('id', title.replace(' ', '_'))}",
                        'titulo': title,
                        'descripcion': f"{description[:150]}... | Worth: {worth}" if description else f"Worth: {worth}",
                        'inicio': datetime.now().isoformat(),
                        'fin': end_date if end_date != 'N/A' else None,
                        'url': url,
                        'imagen': image,
                        'tienda': f"GamerPower ({platforms})"
                    }
                    
                    juegos_reales.append(info)
                    
                except Exception as e:
                    continue
            
            print(f"✅ GamerPower: {len(juegos_reales)} juego(s) REALES encontrados")
            print(f"   🚫 Bloqueados: {spam_bloqueado} keys/codes/basura")
            return juegos_reales
            
        except Exception as e:
            print(f"❌ Error al consultar GamerPower: {e}")
            return []


# Test
if __name__ == "__main__":
    hunter = GamerPowerHunter()
    juegos = hunter.obtener_juegos_gratis()
    print(f"\n🎮 Total JUEGOS REALES: {len(juegos)}")
    for juego in juegos:
        print(f"  ✅ {juego['titulo']}")
