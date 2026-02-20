#!/usr/bin/env python3
"""
💰 Quick Test - Sistema de Ofertas
Prueba rápida del nuevo sistema de deals
"""

print("\n" + "="*70)
print("💰 QUICK TEST - Sistema de Ofertas con Descuento")
print("="*70 + "\n")

print("📦 Importando módulos...")
try:
    from modules.itad_hunter import IsThereAnyDealHunter
    from modules.scoring import SistemaScoring
    print("✅ Módulos cargados\n")
except ImportError as e:
    print(f"❌ Error al importar: {e}")
    print("💡 Ejecuta desde la carpeta raíz del proyecto\n")
    exit(1)

print("🔧 Inicializando hunter y scoring...")
hunter = IsThereAnyDealHunter()
scoring = SistemaScoring()

# Configuración
DESCUENTO_MIN = 30
SCORE_MIN = 3.6

print(f"\n⚙️  Configuración:")
print(f"   • Descuento mínimo: {DESCUENTO_MIN}%")
print(f"   • Score mínimo: {SCORE_MIN}/5.0")

print(f"\n💰 Buscando ofertas con {DESCUENTO_MIN}%+ descuento...")
print("   (Esto puede tomar 15-30 segundos)\n")

ofertas = hunter.obtener_ofertas_descuento(descuento_minimo=DESCUENTO_MIN)

if not ofertas:
    print("💤 No se encontraron ofertas con estos criterios")
    print("💡 Esto puede ser normal, las grandes ofertas son poco frecuentes\n")
    print("🎯 Prueba:")
    print("   • Bajar descuento_minimo a 60%")
    print("   • Esperar a una gran sale (Steam, GOG, etc.)")
    print("\n" + "="*70 + "\n")
    exit(0)

print(f"\n✨ ¡Encontradas {len(ofertas)} oferta(s)!\n")
print("─" * 70 + "\n")

# Procesar ofertas
ofertas_calidad = []

for i, juego in enumerate(ofertas, 1):
    # Calcular score
    score = scoring.calcular_score(juego)
    estrellas = scoring.obtener_estrellas(score)
    
    # Filtrar por calidad
    if score >= SCORE_MIN:
        ofertas_calidad.append(juego)
        
        print(f"{i}. 💰 {juego['titulo']}")
        print(f"   🏪 {juego.get('tienda_emoji', '')} {juego['tienda']}")
        
        # Precio
        precio_actual = juego.get('precio_actual', 0)
        precio_regular = juego.get('precio_regular', 0)
        descuento = juego.get('descuento_porcentaje', 0)
        
        print(f"   💸 ~~${precio_regular:.2f}~~ → ${precio_actual:.2f} (-{descuento}%)")
        print(f"   📊 Score: {score:.1f}/5.0 {estrellas}")
        
        if juego.get('reviews_percent'):
            print(f"   ⭐ {juego['reviews_percent']}% ({juego['reviews_count']:,} reviews)")
        
        print(f"   🔗 {juego['url'][:60]}...")
        print()

print("─" * 70)

# Resumen
print(f"\n📈 RESUMEN:")
print(f"   💰 Total encontrado: {len(ofertas)} oferta(s)")
print(f"   ✅ Con calidad {SCORE_MIN}+: {len(ofertas_calidad)} oferta(s)")
print(f"   ❌ Filtradas: {len(ofertas) - len(ofertas_calidad)} oferta(s)")

if ofertas_calidad:
    # Mejor oferta
    mejor = max(ofertas_calidad, key=lambda x: scoring.calcular_score(x))
    print(f"\n🏆 MEJOR OFERTA:")
    print(f"   {mejor['titulo']}")
    print(f"   Score: {scoring.calcular_score(mejor):.1f}/5.0")
    print(f"   Descuento: -{mejor.get('descuento_porcentaje', 0)}%")
    
    # Tiendas representadas
    tiendas = set(j['tienda'] for j in ofertas_calidad)
    print(f"\n🏪 Tiendas con ofertas de calidad ({len(tiendas)}):")
    for tienda in sorted(tiendas):
        count = sum(1 for j in ofertas_calidad if j['tienda'] == tienda)
        print(f"   • {tienda}: {count} oferta(s)")

print("\n💡 Próximos pasos:")
if ofertas_calidad:
    print("   1. Configurar webhook_deals en config.json")
    print("   2. python hundea_v3.py          ← Ejecución completa")
    print("   3. Verificar notificaciones en Discord")
else:
    print("   1. Bajar thresholds para test:")
    print("      deals_descuento_minimo: 60")
    print("      deals_score_minimo: 3.0")
    print("   2. Intentar nuevamente")
    print("   3. O esperar a grandes sales (Steam, GOG)")

print("\n" + "="*70 + "\n")

# Estado final
if ofertas_calidad:
    print("🎉 ¡Sistema de ofertas funcionando correctamente!")
else:
    print("⚠️  Sistema funcional, pero sin ofertas de calidad ahora")
    print("    (Normal si no hay sales activas)")

print("\n" + "="*70 + "\n")
