#!/usr/bin/env python3
"""
🎮 HunDea v3 - Multi-Store Free Games Hunter
Bot inteligente que detecta juegos gratis de múltiples tiendas
y los clasifica por calidad

Threshold: 3.5+ = Premium, <3.5 = Bajos
"""

import json
import sys
from datetime import datetime, timezone
from modules.epic_hunter import EpicHunter
from modules.steam_hunter import SteamHunter
from modules.itad_hunter import IsThereAnyDealHunter
from modules.cheapshark_hunter import CheapSharkHunter
from modules.itch_hunter import ItchHunter
from modules.platprices_hunter import PlatPricesHunter
from modules.xbox_hunter import XboxHunter
from modules.nintendo_hunter import NintendoHunter
from modules.scoring import SistemaScoring
from modules.discord_notifier import DiscordNotifier
from modules.reviews_externas import ReviewsExternas
from modules.status_notifier import StatusNotifier

def cargar_config():
    """Carga configuración"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró config.json")
        return None
    except json.JSONDecodeError:
        print("❌ Error al leer config.json")
        return None

def cargar_cache():
    """Carga cache de juegos anunciados"""
    try:
        with open('cache.json', 'r', encoding='utf-8') as f:
            cache = json.load(f)
            if not isinstance(cache, dict):
                return {"juegos_anunciados": [], "weekend_anunciados": {}}
            if 'juegos_anunciados' not in cache or not isinstance(cache['juegos_anunciados'], list):
                cache['juegos_anunciados'] = []
            if 'weekend_anunciados' not in cache or not isinstance(cache['weekend_anunciados'], dict):
                cache['weekend_anunciados'] = {}
            return cache
    except FileNotFoundError:
        return {"juegos_anunciados": [], "weekend_anunciados": {}}

def guardar_cache(cache):
    """Guarda cache"""
    with open('cache.json', 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def iso_a_timestamp(fecha_str):
    """Convierte fecha ISO a timestamp Unix"""
    try:
        if not fecha_str:
            return None
        fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
        return int(fecha.timestamp())
    except Exception:
        return None

def normalizar_titulo(titulo):
    """
    Normaliza títulos para comparación
    Elimina caracteres especiales, artículos, etc.
    """
    import re
    
    # Convertir a minúsculas
    titulo = titulo.lower().strip()
    
    # Extraer contenido de paréntesis y agregarlo al título
    # "Rustler (Grand Theft Horse)" → "Rustler Grand Theft Horse"
    parentesis_content = re.findall(r'\(([^)]*)\)', titulo)
    for contenido in parentesis_content:
        titulo = titulo.replace(f'({contenido})', contenido)
    
    # Eliminar caracteres especiales comunes
    titulo = titulo.replace('-', ' ')
    titulo = titulo.replace(':', ' ')
    titulo = titulo.replace('_', ' ')
    
    # Eliminar palabras comunes al final
    sufijos = [' es gratis', ' is free', ' gratis', ' free']
    for sufijo in sufijos:
        if titulo.endswith(sufijo):
            titulo = titulo[:-len(sufijo)]
    
    # Eliminar artículos al inicio
    articulos_inicio = ['the ', 'a ', 'an ', 'el ', 'la ', 'los ', 'las ']
    for articulo in articulos_inicio:
        if titulo.startswith(articulo):
            titulo = titulo[len(articulo):]
            break
    
    # Eliminar artículos en medio (con espacios a los lados)
    for articulo in [' the ', ' a ', ' an ', ' el ', ' la ', ' los ', ' las ']:
        titulo = titulo.replace(articulo, ' ')
    
    # Eliminar espacios múltiples
    titulo = ' '.join(titulo.split())
    
    return titulo.strip()

def eliminar_duplicados(juegos_lista):
    """
    Elimina juegos duplicados basándose en el título normalizado
    Mantiene el que tenga mejor información (más reviews o mejor precio)
    
    Args:
        juegos_lista (list): Lista de juegos
    
    Returns:
        list: Lista sin duplicados
    """
    vistos = {}
    
    for juego in juegos_lista:
        # Normalizar título para comparación
        titulo_norm = normalizar_titulo(juego['titulo'])
        
        # Si no lo hemos visto, agregarlo
        if titulo_norm not in vistos:
            vistos[titulo_norm] = juego
        else:
            # Ya existe, decidir cuál mantener
            juego_existente = vistos[titulo_norm]
            
            # Para ofertas, mantener el de mejor precio
            if juego.get('precio_actual') is not None:
                if juego['precio_actual'] < juego_existente.get('precio_actual', float('inf')):
                    vistos[titulo_norm] = juego
            # Para juegos gratis, mantener el que tenga más reviews
            elif juego.get('reviews_count', 0) > juego_existente.get('reviews_count', 0):
                vistos[titulo_norm] = juego
    
    return list(vistos.values())

def main():
    """Función principal de HunDea v3"""
    
    print("\n" + "="*70)
    print("🎮 HunDea v3 - Multi-Store Free Games Hunter")
    print("="*70 + "\n")
    
    # Cargar configuración
    config = cargar_config()
    if not config:
        print("⚠️ Continuando en modo solo consola...")
        config = {}
    
    # Inicializar notificador de status
    status_webhook = config.get('webhook_status')
    status_notifier = StatusNotifier(status_webhook) if status_webhook else None
    
    # Notificar inicio del workflow
    if status_notifier:
        status_notifier.notificar_inicio()
        print("📡 Notificación de inicio enviada\n")
    
    try:
        # Cargar cache
        cache = cargar_cache()
        
        # Inicializar detectores
        epic_hunter = EpicHunter()
        steam_cc = config.get('steam_cc', 'us')
        steam_lang = config.get('steam_lang', 'english')
        steam_hunter = SteamHunter(cc=steam_cc, lang=steam_lang)
        itad_hunter = IsThereAnyDealHunter()
        cheapshark_hunter = CheapSharkHunter()
        itch_hunter = ItchHunter()
        ps_region = config.get('ps_region', 'en-us')
        platprices_hunter = PlatPricesHunter(region=ps_region)

        xbox_market = config.get('xbox_market', 'US')
        xbox_language = config.get('xbox_language', 'en-US')
        xbox_hunter = XboxHunter(market=xbox_market, language=xbox_language)

        nintendo_region = config.get('nintendo_region', 'MX')
        nintendo_lang = config.get('nintendo_lang', 'es')
        nintendo_hunter = NintendoHunter(region=nintendo_region, lang=nintendo_lang)
        scoring = SistemaScoring()
        
        # Reviews externas con API key si está configurado
        rawg_api_key = config.get('rawg_api_key')
        reviews_externas = ReviewsExternas(api_key=rawg_api_key)
        
        if rawg_api_key:
            print("✅ RAWG API key configurada")
        else:
            print("⚠️ RAWG API key no configurada (reviews limitadas)")
        
        # Recolectar juegos de todas las tiendas
        todos_juegos = []
        
        # Epic Games
        juegos_epic = epic_hunter.obtener_juegos_gratis()
        
        # Buscar reviews externas para juegos de Epic
        for juego in juegos_epic:
            if 'reviews_count' not in juego or not juego.get('reviews_count'):
                print(f"   🔍 Buscando reviews para: {juego['titulo']}")
                reviews = reviews_externas.buscar_reviews(juego['titulo'], 'Epic Games')
                if reviews:
                    juego.update(reviews)
        
        todos_juegos.extend(juegos_epic)
        
        # IsThereAnyDeal (múltiples tiendas) - GRATIS
        print("\n🌟 Buscando juegos GRATIS en múltiples tiendas con ITAD...")
        juegos_itad = itad_hunter.obtener_juegos_gratis()
        
        # Buscar reviews externas para juegos de ITAD
        for juego in juegos_itad:
            if 'reviews_count' not in juego or not juego.get('reviews_count'):
                print(f"   🔍 Buscando reviews para: {juego['titulo']}")
                reviews = reviews_externas.buscar_reviews(juego['titulo'], juego['tienda'])
                if reviews:
                    juego.update(reviews)
        
        todos_juegos.extend(juegos_itad)
        
        # CheapShark - Juegos Gratis
        print("\n🦈 Buscando juegos GRATIS en CheapShark...")
        juegos_cheapshark = cheapshark_hunter.obtener_juegos_gratis()
        
        # Buscar reviews para juegos de CheapShark
        for juego in juegos_cheapshark:
            if not juego.get('reviews_count'):
                print(f"   🔍 Buscando reviews para: {juego['titulo']}")
                reviews = reviews_externas.buscar_reviews(juego['titulo'], juego['tienda'])
                if reviews:
                    juego.update(reviews)
        
        todos_juegos.extend(juegos_cheapshark)
        
        # Itch.io - Juegos indie gratis
        print("\n🔴 Buscando juegos indie gratis en Itch.io...")
        juegos_itch = itch_hunter.obtener_juegos_gratis()
        
        # Buscar reviews para juegos de Itch.io
        for juego in juegos_itch:
            if not juego.get('reviews_count'):
                print(f"   🔍 Buscando reviews para: {juego['titulo']}")
                reviews = reviews_externas.buscar_reviews(juego['titulo'], 'Itch.io')
                if reviews:
                    juego.update(reviews)
        
        todos_juegos.extend(juegos_itch)
        
        # PlatPrices - PlayStation deals
        print("\n🎮 Buscando deals de PlayStation (PlatPrices)...")
        juegos_playstation = platprices_hunter.obtener_juegos_gratis()
        
        # Buscar reviews para PlayStation
        for juego in juegos_playstation:
            if not juego.get('reviews_count'):
                print(f"   🔍 Buscando reviews para: {juego['titulo']}")
                reviews = reviews_externas.buscar_reviews(juego['titulo'], 'PlayStation')
                if reviews:
                    juego.update(reviews)
        
        todos_juegos.extend(juegos_playstation)
        
        # Xbox - Microsoft Store
        print("\n🎮 Buscando juegos gratis de Xbox (Microsoft Store)...")
        juegos_xbox = xbox_hunter.obtener_juegos_gratis()
        
        # Buscar reviews para Xbox
        for juego in juegos_xbox:
            if not juego.get('reviews_count'):
                print(f"   🔍 Buscando reviews para: {juego['titulo']}")
                reviews = reviews_externas.buscar_reviews(juego['titulo'], 'Xbox')
                if reviews:
                    juego.update(reviews)
        
        todos_juegos.extend(juegos_xbox)

        # Nintendo - eShop
        print("\n🎮 Buscando juegos gratis de Nintendo eShop...")
        juegos_nintendo = nintendo_hunter.obtener_juegos_gratis()
        
        # Buscar reviews para Nintendo
        for juego in juegos_nintendo:
            if not juego.get('reviews_count'):
                print(f"   🔍 Buscando reviews para: {juego['titulo']}")
                reviews = reviews_externas.buscar_reviews(juego['titulo'], 'Nintendo')
                if reviews:
                    juego.update(reviews)
        
        todos_juegos.extend(juegos_nintendo)
        
        # Eliminar duplicados en juegos gratis
        print(f"\n🗑️ Eliminando duplicados en juegos gratis...")
        juegos_antes = len(todos_juegos)
        todos_juegos = eliminar_duplicados(todos_juegos)
        duplicados_removidos = juegos_antes - len(todos_juegos)
        if duplicados_removidos > 0:
            print(f"   ✅ Removidos {duplicados_removidos} duplicado(s)")
            print(f"   📊 Total juegos únicos: {len(todos_juegos)}")
        
        # IsThereAnyDeal - OFERTAS CON DESCUENTO
        descuento_minimo = config.get('deals_descuento_minimo', 30)
        descuento_maximo = config.get('deals_descuento_maximo', 99)
        precio_maximo_deals = config.get('deals_precio_maximo', 10)
        
        print(f"\n💰 Buscando OFERTAS con {descuento_minimo}%+ descuento en ITAD...")
        ofertas_itad = itad_hunter.obtener_ofertas_descuento(descuento_minimo)
        
        # Buscar reviews para ofertas de ITAD
        for juego in ofertas_itad:
            if 'reviews_count' not in juego or not juego.get('reviews_count'):
                print(f"   🔍 Buscando reviews para: {juego['titulo']}")
                reviews = reviews_externas.buscar_reviews(juego['titulo'], juego['tienda'])
                if reviews:
                    juego.update(reviews)
        
        # CheapShark - Ofertas con Descuento
        print(f"\n🦈 Buscando OFERTAS con {descuento_minimo}%+ descuento en CheapShark...")
        ofertas_cheapshark = cheapshark_hunter.obtener_ofertas_descuento(descuento_minimo, precio_maximo_deals)
        
        # Buscar reviews para ofertas de CheapShark
        for juego in ofertas_cheapshark:
            if not juego.get('reviews_count'):
                print(f"   🔍 Buscando reviews para: {juego['titulo']}")
                reviews = reviews_externas.buscar_reviews(juego['titulo'], juego['tienda'])
                if reviews:
                    juego.update(reviews)
        
        # Combinar todas las ofertas
        ofertas_itad.extend(ofertas_cheapshark)

        # PlayStation - Ofertas con Descuento (PlatPrices)
        print(f"\n🎮 Buscando OFERTAS con {descuento_minimo}%+ descuento en PlayStation (PlatPrices)...")
        ofertas_playstation = platprices_hunter.obtener_ofertas_descuento(descuento_minimo, descuento_maximo)
        
        # Buscar reviews para ofertas de PlayStation
        for juego in ofertas_playstation:
            if not juego.get('reviews_count'):
                print(f"   🔍 Buscando reviews para: {juego['titulo']}")
                reviews = reviews_externas.buscar_reviews(juego['titulo'], 'PlayStation')
                if reviews:
                    juego.update(reviews)
        ofertas_itad.extend(ofertas_playstation)

        # Xbox - Ofertas con Descuento
        print(f"\n🎮 Buscando OFERTAS con {descuento_minimo}%+ descuento en Xbox Store...")
        ofertas_xbox = xbox_hunter.obtener_ofertas_descuento(descuento_minimo, descuento_maximo)
        
        # Buscar reviews para ofertas de Xbox
        for juego in ofertas_xbox:
            if not juego.get('reviews_count'):
                print(f"   🔍 Buscando reviews para: {juego['titulo']}")
                reviews = reviews_externas.buscar_reviews(juego['titulo'], 'Xbox')
                if reviews:
                    juego.update(reviews)
        ofertas_itad.extend(ofertas_xbox)

        # Nintendo - Ofertas con Descuento
        print(f"\n🎮 Buscando OFERTAS con {descuento_minimo}%+ descuento en Nintendo eShop...")
        ofertas_nintendo = nintendo_hunter.obtener_ofertas_descuento(descuento_minimo, descuento_maximo)
        
        # Buscar reviews para ofertas de Nintendo
        for juego in ofertas_nintendo:
            if not juego.get('reviews_count'):
                print(f"   🔍 Buscando reviews para: {juego['titulo']}")
                reviews = reviews_externas.buscar_reviews(juego['titulo'], 'Nintendo')
                if reviews:
                    juego.update(reviews)
        ofertas_itad.extend(ofertas_nintendo)
        
        # Eliminar duplicados ANTES de separar 100%
        print(f"\n🗑️ Eliminando duplicados en ofertas...")
        ofertas_antes = len(ofertas_itad)
        ofertas_itad = eliminar_duplicados(ofertas_itad)
        duplicados_removidos = ofertas_antes - len(ofertas_itad)
        if duplicados_removidos > 0:
            print(f"   ✅ Removidos {duplicados_removidos} duplicado(s) en ofertas")

        # Filtrar descuentos fuera de rango (máximo para deals pagados)
        ofertas_filtradas = []
        for oferta in ofertas_itad:
            descuento = oferta.get('descuento_porcentaje', 0) or 0
            if descuento >= 100:
                ofertas_filtradas.append(oferta)
            elif descuento_maximo and descuento > descuento_maximo:
                continue
            else:
                ofertas_filtradas.append(oferta)
        ofertas_itad = ofertas_filtradas
        
        # Separar ofertas 100% descuento (son GRATIS)
        print(f"\n🎁 Separando ofertas 100% descuento como GRATIS...")
        ofertas_100 = []
        ofertas_con_descuento = []
        
        for oferta in ofertas_itad:
            if oferta.get('descuento_porcentaje', 0) >= 100:
                # 100% descuento = GRATIS
                oferta['tipo'] = 'gratis'
                ofertas_100.append(oferta)
            else:
                ofertas_con_descuento.append(oferta)
        
        if ofertas_100:
            print(f"   🎉 {len(ofertas_100)} oferta(s) 100% movidas a canal GRATIS")
            # Eliminar duplicados antes de agregar a todos_juegos
            todos_juegos_temp = todos_juegos + ofertas_100
            todos_juegos = eliminar_duplicados(todos_juegos_temp)
            print(f"   📊 Total juegos después de merge: {len(todos_juegos)}")
        
        # Actualizar lista de ofertas (sin las 100%)
        ofertas_itad = ofertas_con_descuento
        
        # Eliminar duplicados en ofertas finales
        print(f"\n🗑️ Eliminando duplicados finales...")
        ofertas_antes = len(ofertas_itad)
        ofertas_itad = eliminar_duplicados(ofertas_itad)
        duplicados_removidos = ofertas_antes - len(ofertas_itad)
        if duplicados_removidos > 0:
            print(f"   ✅ Removidos {duplicados_removidos} duplicado(s)")
            print(f"   📊 Total ofertas únicas: {len(ofertas_itad)}")
        
        # Steam (temporalmente desactivado - requiere mejor implementación)
        # juegos_steam = steam_hunter.obtener_juegos_gratis()
        # todos_juegos.extend(juegos_steam)
        
        # Free Weekends (Steam)
        free_weekends = steam_hunter.obtener_free_weekends()
        
        print(f"\n📊 Total encontrado: {len(todos_juegos)} juego(s) gratis")
        print(f"💰 Ofertas: {len(ofertas_itad)} oferta(s) con descuento")
        print(f"⏰ Free Weekends: {len(free_weekends)} juego(s)\n")
        
        if not todos_juegos and not free_weekends and not ofertas_itad:
            print("✅ No hay juegos gratis ni ofertas nuevas por ahora\n")
            
            # Notificar éxito (aunque no haya juegos nuevos)
            if status_notifier:
                status_notifier.notificar_exito(0, 0, 0)
            
            return
        
        # Procesar juegos regulares
        juegos_premium = []
        juegos_bajos = []
        
        # Procesar ofertas con descuento (solo las de calidad 3.6+)
        ofertas_calidad = []
        score_minimo_deals = config.get('deals_score_minimo', 3.6)
        
        for juego in todos_juegos:
            # Calcular score
            score = scoring.calcular_score(juego)
            clasificacion = scoring.clasificar_juego(score)
            estrellas = scoring.obtener_estrellas(score)
            descripcion = scoring.obtener_descripcion_score(score)
            
            # Agregar info de score
            juego['score'] = score
            juego['clasificacion'] = clasificacion
            juego['estrellas'] = estrellas
            juego['descripcion_score'] = descripcion
            
            # Clasificar
            if clasificacion == 'premium':
                juegos_premium.append(juego)
            else:
                juegos_bajos.append(juego)
            
            # Mostrar en consola
            print(f"{estrellas} {juego['titulo']}")
            print(f"   🏪 {juego['tienda']} | 📊 {score:.1f}/5.0 ({descripcion})")
            if 'reviews_percent' in juego:
                print(f"   ⭐ {juego['reviews_percent']}% ({juego['reviews_count']:,} reviews)")
            print(f"   🔗 {juego['url']}")
            print(f"   {'─'*60}")
        
        # Procesar ofertas con descuento
        for juego in ofertas_itad:
            score = scoring.calcular_score(juego)
            estrellas = scoring.obtener_estrellas(score)
            
            juego['score'] = score
            juego['estrellas'] = estrellas
            
            # Solo ofertas de calidad 3.6+
            if score >= score_minimo_deals:
                ofertas_calidad.append(juego)
                
                print(f"💰 {juego['titulo']}")
                print(f"   🏪 {juego['tienda']} | 📊 {score:.1f}/5.0 ({estrellas})")
                print(f"   💸 -{juego.get('descuento_porcentaje', 0)}% | ${juego.get('precio_actual', 0):.2f}")
                if juego.get('reviews_percent'):
                    print(f"   ⭐ {juego['reviews_percent']}% ({juego['reviews_count']:,} reviews)")
                print(f"   🔗 {juego['url']}")
                print(f"   {'─'*60}")
        
        # Mostrar resumen
        print(f"\n📈 Resumen:")
        print(f"   ⭐ Premium (3.5+): {len(juegos_premium)} juego(s)")
        print(f"   ⚠️  Bajos (<3.5): {len(juegos_bajos)} juego(s)")
        print(f"   💰 Ofertas Calidad (3.6+): {len(ofertas_calidad)} oferta(s)")
        print(f"   ⏰ Free Weekends: {len(free_weekends)} juego(s)\n")
        
        # Enviar a Discord si está configurado
        enviados_premium = 0
        enviados_bajos = 0
        enviados_deals = 0
        
        if config.get('enviar_discord'):
            webhook_premium = config.get('webhook_premium')
            webhook_bajos = config.get('webhook_bajos')
            webhook_weekends = config.get('webhook_weekends')
            webhook_deals = config.get('webhook_deals')
            webhook_todos = config.get('webhook_todos')
            rol_id = config.get('rol_id')
            rol_todos = config.get('rol_todos')
            rol_deals = config.get('rol_deals')
            
            if not all([webhook_premium, webhook_bajos, webhook_weekends]):
                print("⚠️ Faltan webhooks configurados. Solo mostrando en consola.\n")
            else:
                print("📤 Enviando alertas a Discord...\n")
                
                notifier = DiscordNotifier(
                    webhook_premium,
                    webhook_bajos,
                    webhook_weekends,
                    webhook_deals=webhook_deals,
                    webhook_todos=webhook_todos,
                    rol_premium=config.get('rol_premium'),
                    rol_bajos=config.get('rol_bajos'),
                    rol_weekends=config.get('rol_weekends'),
                    rol_deals=config.get('rol_deals'),
                    rol_todos=config.get('rol_todos')
                )
                
                # Enviar juegos premium
                for juego in juegos_premium:
                    if juego['id'] not in cache['juegos_anunciados']:
                        if notifier.enviar_juego_premium(juego, juego['score'], juego['estrellas']):
                            cache['juegos_anunciados'].append(juego['id'])
                            enviados_premium += 1
                    else:
                        print(f"⏭️  Saltando {juego['titulo']} (ya anunciado)")
                
                # Enviar juegos bajos
                for juego in juegos_bajos:
                    if juego['id'] not in cache['juegos_anunciados']:
                        if notifier.enviar_juego_bajos(juego, juego['score']):
                            cache['juegos_anunciados'].append(juego['id'])
                            enviados_bajos += 1
                    else:
                        print(f"⏭️  Saltando {juego['titulo']} (ya anunciado)")
                
                # Enviar free weekends (deduplicación por ventana activa)
                now_ts = int(datetime.now(timezone.utc).timestamp())
                weekend_cache = cache.setdefault('weekend_anunciados', {})
                expirados = [
                    k for k, v in weekend_cache.items()
                    if isinstance(v, (int, float)) and now_ts >= v
                ]
                for k in expirados:
                    del weekend_cache[k]

                for juego in free_weekends:
                    weekend_key = juego['id']
                    fin_ts = iso_a_timestamp(juego.get('fin')) or juego.get('fin_ts_estimada')
                    if not fin_ts:
                        fin_ts = now_ts + (4 * 24 * 60 * 60)

                    cache_fin = weekend_cache.get(weekend_key)
                    if cache_fin and now_ts < cache_fin:
                        print(f"⏭️  Saltando {juego['titulo']} (free weekend activo)")
                        continue

                    score = scoring.calcular_score(juego)
                    estrellas = scoring.obtener_estrellas(score)
                    if notifier.enviar_free_weekend(juego, score, estrellas):
                        weekend_cache[weekend_key] = fin_ts
                
                # Enviar ofertas con descuento
                if webhook_deals:
                    for juego in ofertas_calidad:
                        deal_id = f"{juego['id']}_deal"
                        if deal_id not in cache['juegos_anunciados']:
                            if notifier.enviar_oferta_descuento(juego, juego['score'], juego['estrellas']):
                                cache['juegos_anunciados'].append(deal_id)
                                enviados_deals += 1
                        else:
                            print(f"⏭️  Saltando oferta {juego['titulo']} (ya anunciado)")
                
                # Guardar cache
                guardar_cache(cache)
                
                total_enviados = enviados_premium + enviados_bajos + enviados_deals
                if total_enviados > 0:
                    print(f"\n🎉 {total_enviados} alerta(s) enviada(s) a Discord")
                    print(f"   • Premium: {enviados_premium}")
                    print(f"   • Bajos: {enviados_bajos}")
                    print(f"   • Ofertas: {enviados_deals}")
                else:
                    print("\n✅ Todos los juegos ya habían sido anunciados")
        
        print("\n" + "="*70)
        print("✅ Búsqueda completada!")
        print("="*70 + "\n")
        
        # Notificar éxito
        if status_notifier:
            status_notifier.notificar_exito(
                enviados_premium, 
                enviados_bajos, 
                len(todos_juegos)
            )
            print("📡 Notificación de éxito enviada\n")
    
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        
        # Notificar error
        if status_notifier:
            status_notifier.notificar_error(str(e))
        
        raise

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrumpido por el usuario\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}\n")
        sys.exit(1)
