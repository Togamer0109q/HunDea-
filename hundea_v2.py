#!/usr/bin/env python3
"""
🎮 HunDea v2 - Multi-Store Free Games Hunter
Bot inteligente que detecta juegos gratis de múltiples tiendas
y los clasifica por calidad

Threshold: 3.5+ = Premium, <3.5 = Bajos
"""

import json
import sys
from modules.epic_hunter import EpicHunter
from modules.steam_hunter import SteamHunter
from modules.itad_hunter import IsThereAnyDealHunter
from modules.cheapshark_hunter import CheapSharkHunter
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
            return json.load(f)
    except FileNotFoundError:
        return {"juegos_anunciados": []}

def guardar_cache(cache):
    """Guarda cache"""
    with open('cache.json', 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def eliminar_duplicados(juegos_lista):
    """
    Elimina juegos duplicados basándose en el título
    Mantiene el que tenga mejor información (más reviews o mejor precio)
    
    Args:
        juegos_lista (list): Lista de juegos
    
    Returns:
        list: Lista sin duplicados
    """
    vistos = {}
    
    for juego in juegos_lista:
        titulo = juego['titulo'].lower().strip()
        
        # Si no lo hemos visto, agregarlo
        if titulo not in vistos:
            vistos[titulo] = juego
        else:
            # Ya existe, decidir cuál mantener
            juego_existente = vistos[titulo]
            
            # Para ofertas, mantener el de mejor precio
            if juego.get('precio_actual') is not None:
                if juego['precio_actual'] < juego_existente.get('precio_actual', float('inf')):
                    vistos[titulo] = juego
            # Para juegos gratis, mantener el que tenga más reviews
            elif juego.get('reviews_count', 0) > juego_existente.get('reviews_count', 0):
                vistos[titulo] = juego
    
    return list(vistos.values())

def main():
    """Función principal de HunDea v2"""
    
    print("\n" + "="*70)
    print("🎮 HunDea v2 - Multi-Store Free Games Hunter")
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
        steam_hunter = SteamHunter()
        itad_hunter = IsThereAnyDealHunter()
        cheapshark_hunter = CheapSharkHunter()
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
        
        # Eliminar duplicados en juegos gratis
        print(f"\n🗑️ Eliminando duplicados en juegos gratis...")
        juegos_antes = len(todos_juegos)
        todos_juegos = eliminar_duplicados(todos_juegos)
        duplicados_removidos = juegos_antes - len(todos_juegos)
        if duplicados_removidos > 0:
            print(f"   ✅ Removidos {duplicados_removidos} duplicado(s)")
            print(f"   📊 Total juegos únicos: {len(todos_juegos)}")
        
        # IsThereAnyDeal - OFERTAS CON DESCUENTO
        descuento_minimo = config.get('deals_descuento_minimo', 70)
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
            todos_juegos.extend(ofertas_100)
        
        # Actualizar lista de ofertas (sin las 100%)
        ofertas_itad = ofertas_con_descuento
        
        # Eliminar duplicados (mantener el de mejor precio)
        print(f"\n🗑️ Eliminando duplicados...")
        ofertas_antes = len(ofertas_itad)
        ofertas_itad = eliminar_duplicados(ofertas_itad)
        duplicados_removidos = ofertas_antes - len(ofertas_itad)
        if duplicados_removidos > 0:
            print(f"   ✅ Removidos {duplicados_removidos} duplicado(s)")
            print(f"   📊 Total ofertas únicas: {len(ofertas_itad)}")
        
        # Steam (temporalmente desactivado - requiere mejor implementación)
        # juegos_steam = steam_hunter.obtener_juegos_gratis()
        # todos_juegos.extend(juegos_steam)
        
        # Free Weekends (temporalmente desactivado)
        # free_weekends = steam_hunter.obtener_free_weekends()
        free_weekends = []
        
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
                
                # Enviar free weekends
                for juego in free_weekends:
                    weekend_id = f"{juego['id']}_weekend"
                    if weekend_id not in cache['juegos_anunciados']:
                        score = scoring.calcular_score(juego)
                        estrellas = scoring.obtener_estrellas(score)
                        if notifier.enviar_free_weekend(juego, score, estrellas):
                            cache['juegos_anunciados'].append(weekend_id)
                    else:
                        print(f"⏭️  Saltando {juego['titulo']} (ya anunciado)")
                
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
