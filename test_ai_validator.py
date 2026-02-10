"""
🧠 Test AI Validator - Quick Demo
───────────────────────────────────

Demo rápido del validador inteligente.
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.ai import SmartDealValidator


def main():
    print("\n" + "="*70)
    print("🧠 HUNDEABOT AI - SMART DEAL VALIDATOR")
    print("="*70)
    print("\nEste sistema detecta ofertas REALES vs FAKE usando IA básica.\n")
    
    # Initialize validator (sin ITAD key para demo)
    validator = SmartDealValidator()
    
    # Test deals - ejemplos reales
    test_deals = [
        {
            'title': 'Cyberpunk 2077',
            'current_price': 29.99,
            'original_price': 59.99,
            'discount_percent': 50,
            'description': 'Steam Winter Sale - Oferta legítima'
        },
        {
            'title': 'Elden Ring',
            'current_price': 39.99,
            'original_price': 59.99,
            'discount_percent': 33,
            'description': 'Descuento normal de Steam'
        },
        {
            'title': 'SUPER MEGA ULTIMATE DELUXE GOLD PREMIUM EDITION',
            'current_price': 0.99,
            'original_price': 499.99,
            'discount_percent': 99,
            'description': 'Sitio sospechoso de bundles - FAKE'
        },
        {
            'title': 'GTA V',
            'current_price': 14.99,
            'original_price': 29.99,
            'discount_percent': 50,
            'description': 'Epic Games Sale - Común'
        },
        {
            'title': 'Random DLC Pack',
            'current_price': 0.49,
            'original_price': 199.99,
            'discount_percent': 99,
            'description': 'DLC sobrevalorado - SOSPECHOSO'
        }
    ]
    
    print("🔍 Analizando deals...\n")
    
    # Validate each deal
    for i, deal in enumerate(test_deals, 1):
        print(f"\n{'─'*70}")
        print(f"Deal #{i}: {deal['title']}")
        print(f"{'─'*70}")
        print(f"💰 Precio: ${deal['current_price']} (era ${deal['original_price']})")
        print(f"📊 Descuento: {deal['discount_percent']}%")
        print(f"📝 Contexto: {deal['description']}")
        
        # Validate
        validation = validator.validate_deal(deal)
        
        print(f"\n🤖 ANÁLISIS DE IA:")
        print(f"   {validation['verdict']}")
        print(f"   Confianza: {validation['confidence_score']:.0%}")
        
        # Show analysis
        if validation['analysis']['pattern_detection']['suspicious_flags']:
            print(f"\n   🚩 Flags detectadas:")
            for flag in validation['analysis']['pattern_detection']['suspicious_flags']:
                print(f"      - {flag}")
        
        # Show recommendations
        if validation.get('recommendations'):
            print(f"\n   💡 Recomendaciones:")
            for rec in validation['recommendations']:
                print(f"      {rec}")
    
    # Show stats
    print(f"\n{'='*70}")
    print("📊 ESTADÍSTICAS DE VALIDACIÓN")
    print(f"{'='*70}")
    stats = validator.get_stats()
    print(f"Total validados:     {stats['total_validated']}")
    print(f"✅ Reales:           {stats['real_confirmed']}")
    print(f"🔍 Sospechosos:      {stats['suspicious']}")
    print(f"❌ Fakes:            {stats['fake_detected']}")
    print(f"📈 Fake Rate:        {stats['fake_rate']:.1f}%")
    print(f"{'='*70}")
    
    print(f"\n{'='*70}")
    print("💡 PRÓXIMOS PASOS")
    print(f"{'='*70}")
    print("""
1. Obtener ITAD API key (opcional pero recomendado):
   - https://isthereanydeal.com/dev/app/
   
2. Integrar en hunters:
   - Importar SmartDealValidator
   - Validar deals antes de enviar
   
3. Ver guía completa:
   - AI_VALIDATION_GUIDE.md
    """)
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
