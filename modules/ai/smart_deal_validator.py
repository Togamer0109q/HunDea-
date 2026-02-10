"""
🧠 Smart Deal Validator - AI-Powered Deal Verification
───────────────────────────────────────────────────────

Sistema inteligente que detecta ofertas REALES vs FAKE usando:
- Verificación de historial de precios
- Detección de patrones sospechosos
- Scoring de confiabilidad
- ML básico para clasificación

Author: HunDeaBot Team
Version: 1.0.0 - AI POWERED
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics
try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    def load_dotenv(*_args, **_kwargs):
        return False


class SmartDealValidator:
    """
    Validador inteligente de ofertas con detección de fake deals.
    """
    
    # Patrones sospechosos
    SUSPICIOUS_PATTERNS = {
        'fake_discount_threshold': 0.9,  # 90%+ de descuento es sospechoso
        'price_inflation_ratio': 1.5,     # Precio "original" 50%+ más alto que histórico
        'too_good_to_be_true': 95,       # 95%+ descuento = probablemente fake
        'minimum_price_history_days': 30, # Mínimo 30 días de historia para validar
    }
    
    # Scoring weights
    WEIGHTS = {
        'price_history': 0.4,      # 40% del score
        'discount_realism': 0.3,   # 30% del score
        'seller_reputation': 0.2,   # 20% del score
        'pattern_detection': 0.1    # 10% del score
    }
    
    def __init__(self, itad_api_key: Optional[str] = None, logger=None):
        """
        Initialize validator.
        
        Args:
            itad_api_key: IsThereAnyDeal API key (opcional)
            logger: Logger instance
        """
        if not itad_api_key:
            load_dotenv()
        self.itad_api_key = itad_api_key or os.getenv("ITAD_API_KEY")
        self.logger = logger or logging.getLogger(__name__)
        
        # Stats for ML (simple)
        self.deal_stats = {
            'total_validated': 0,
            'fake_detected': 0,
            'real_confirmed': 0,
            'suspicious': 0
        }
    
    #  ═══════════════════════════════════════════════════════════
    # PRICE HISTORY VALIDATION
    # ═══════════════════════════════════════════════════════════
    
    def check_price_history(self, game_title: str, current_price: float, 
                           claimed_original: float) -> Dict:
        """
        Verifica el historial de precios para detectar fake discounts.
        
        Args:
            game_title: Nombre del juego
            current_price: Precio actual en oferta
            claimed_original: Precio "original" que dice la tienda
            
        Returns:
            Dict con análisis de historial
        """
        try:
            if not self.itad_api_key:
                self.logger.warning("⚠️  No ITAD API key - usando heurísticas")
                return self._heuristic_price_check(current_price, claimed_original)
            
            # Buscar juego en ITAD
            game_data = self._search_itad_game(game_title)
            
            if not game_data:
                self.logger.warning(f"⚠️  Game not found in ITAD: {game_title}")
                return self._heuristic_price_check(current_price, claimed_original)
            
            # Obtener historial de precios
            history = self._get_price_history(game_data['id'])
            
            if not history:
                return self._heuristic_price_check(current_price, claimed_original)
            
            # Analizar historial
            analysis = self._analyze_price_history(
                history, 
                current_price, 
                claimed_original
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"❌ Price history check failed: {e}")
            return {
                'is_valid': False,
                'confidence': 0.0,
                'reason': f'Error: {str(e)}',
                'method': 'error'
            }
    
    def _search_itad_game(self, game_title: str) -> Optional[Dict]:
        """Buscar juego en ITAD."""
        try:
            url = "https://api.isthereanydeal.com/v2/search/search/"
            
            params = {
                'key': self.itad_api_key,
                'title': game_title,
                'limit': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                return data[0]
            
            return None
            
        except Exception as e:
            self.logger.debug(f"ITAD search error: {e}")
            return None
    
    def _get_price_history(self, game_id: str) -> Optional[Dict]:
        """Obtener historial de precios de ITAD."""
        try:
            url = f"https://api.isthereanydeal.com/v2/game/history/"
            
            params = {
                'key': self.itad_api_key,
                'id': game_id,
                'shops': 'steam,gog,epic,humble',  # Tiendas confiables
                'since': int((datetime.now() - timedelta(days=365)).timestamp())
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.debug(f"Price history error: {e}")
            return None
    
    def _analyze_price_history(self, history: Dict, current_price: float, 
                               claimed_original: float) -> Dict:
        """
        Analiza el historial para detectar fake discounts.
        
        Returns:
            Dict con is_valid, confidence, reason
        """
        try:
            prices = []
            
            # Extract all historical prices
            for shop_data in history.values():
                for price_point in shop_data:
                    prices.append(price_point['price'])
            
            if not prices:
                return self._heuristic_price_check(current_price, claimed_original)
            
            # Calcular estadísticas
            avg_price = statistics.mean(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            # Verificar si el "precio original" es inflado
            is_inflated = claimed_original > (max_price * self.SUSPICIOUS_PATTERNS['price_inflation_ratio'])
            
            # Verificar si el precio actual es razonable
            is_reasonable_discount = current_price >= (min_price * 0.8)  # Mínimo 80% del lowest
            
            # Calcular confidence
            if is_inflated:
                confidence = 0.2  # Baja confianza - precio inflado
                reason = f"Precio 'original' ${claimed_original:.2f} inflado. Histórico máx: ${max_price:.2f}"
                is_valid = False
            elif not is_reasonable_discount:
                confidence = 0.5  # Media - demasiado barato
                reason = f"Precio ${current_price:.2f} sospechosamente bajo. Mín histórico: ${min_price:.2f}"
                is_valid = True  # Puede ser real pero sospechoso
            else:
                confidence = 0.9  # Alta confianza
                reason = f"Precio válido. Rango histórico: ${min_price:.2f}-${max_price:.2f}"
                is_valid = True
            
            return {
                'is_valid': is_valid,
                'confidence': confidence,
                'reason': reason,
                'method': 'price_history',
                'stats': {
                    'historical_min': min_price,
                    'historical_max': max_price,
                    'historical_avg': avg_price,
                    'current': current_price,
                    'claimed_original': claimed_original,
                    'is_inflated': is_inflated
                }
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'confidence': 0.0,
                'reason': f'Analysis error: {str(e)}',
                'method': 'error'
            }
    
    def _heuristic_price_check(self, current_price: float, 
                               claimed_original: float) -> Dict:
        """
        Verificación heurística sin historial de precios.
        """
        # Evitar divisiÃ³n por cero si no hay precio original
        if claimed_original <= 0:
            return {
                'is_valid': True,
                'confidence': 0.5,
                'reason': "Precio original desconocido",
                'method': 'heuristic',
                'discount_percent': 0
            }

        # Calcular descuento claimed
        discount = ((claimed_original - current_price) / claimed_original) * 100
        
        # Detectar patrones sospechosos
        is_suspicious = False
        reason = ""
        
        # Descuento demasiado alto
        if discount >= self.SUSPICIOUS_PATTERNS['too_good_to_be_true']:
            is_suspicious = True
            reason = f"Descuento {discount:.0f}% demasiado alto - probablemente fake"
            confidence = 0.1
        
        # Descuento muy alto
        elif discount >= 80:
            is_suspicious = True
            reason = f"Descuento {discount:.0f}% sospechoso - verificar"
            confidence = 0.4
        
        # Precio muy bajo
        elif current_price < 1.0:
            reason = f"Precio ${current_price:.2f} muy bajo - puede ser bundle/error"
            confidence = 0.6
        
        # Parece razonable
        else:
            reason = f"Descuento {discount:.0f}% parece razonable"
            confidence = 0.7
        
        return {
            'is_valid': not is_suspicious,
            'confidence': confidence,
            'reason': reason,
            'method': 'heuristic',
            'discount_percent': discount
        }
    
    # ═══════════════════════════════════════════════════════════
    # PATTERN DETECTION
    # ═══════════════════════════════════════════════════════════
    
    def detect_fake_patterns(self, deal: Dict) -> Dict:
        """
        Detecta patrones que indican ofertas falsas.
        
        Args:
            deal: Dict con info del deal
            
        Returns:
            Dict con flags sospechosas
        """
        flags = []
        score = 1.0  # Start with perfect score
        
        title = deal.get('title', '').lower()
        current_price = deal.get('current_price', 0)
        original_price = deal.get('original_price', 0)
        discount = deal.get('discount_percent', 0)
        
        # Pattern 1: Descuento extremo
        if discount >= 95:
            flags.append("extreme_discount")
            score -= 0.3
        
        # Pattern 2: Precio sospechosamente bajo
        if current_price < 0.99:
            flags.append("suspiciously_low_price")
            score -= 0.2
        
        # Pattern 3: Precio "original" número redondo sospechoso
        if original_price in [99.99, 199.99, 299.99, 499.99]:
            flags.append("round_original_price")
            score -= 0.1
        
        # Pattern 4: Título con muchos buzzwords
        buzzwords = ['ultimate', 'deluxe', 'premium', 'gold', 'platinum', 'edition']
        if sum(1 for word in buzzwords if word in title) >= 3:
            flags.append("excessive_buzzwords")
            score -= 0.1
        
        # Pattern 5: DLC demasiado caro originalmente
        if 'dlc' in title and original_price > 50:
            flags.append("overpriced_dlc")
            score -= 0.2
        
        score = max(0.0, min(1.0, score))  # Clamp to 0-1
        
        return {
            'suspicious_flags': flags,
            'pattern_score': score,
            'is_suspicious': len(flags) >= 2,
            'flags_count': len(flags)
        }
    
    # ═══════════════════════════════════════════════════════════
    # COMPREHENSIVE VALIDATION
    # ═══════════════════════════════════════════════════════════
    
    def validate_deal(self, deal: Dict) -> Dict:
        """
        Validación completa del deal.
        
        Args:
            deal: Dict con info del deal
            
        Returns:
            Dict con validación completa y score
        """
        try:
            self.deal_stats['total_validated'] += 1
            
            # Extract info
            title = deal.get('title', 'Unknown')
            current_price = deal.get('current_price', 0)
            original_price = deal.get('original_price', 0)
            discount = deal.get('discount_percent', 0)
            
            # 1. Price history check
            price_check = self.check_price_history(title, current_price, original_price)
            
            # 2. Pattern detection
            pattern_check = self.detect_fake_patterns(deal)
            
            # 3. Calculate comprehensive score
            final_score = (
                price_check['confidence'] * self.WEIGHTS['price_history'] +
                pattern_check['pattern_score'] * self.WEIGHTS['pattern_detection'] +
                0.7 * self.WEIGHTS['discount_realism'] +  # Default middle score
                0.8 * self.WEIGHTS['seller_reputation']   # Default good score
            )
            
            # 4. Determine if deal is REAL or FAKE
            is_real = final_score >= 0.6  # 60%+ = probably real
            is_suspicious = pattern_check['is_suspicious'] or price_check['confidence'] < 0.5
            
            # 5. Generate verdict
            if final_score >= 0.8:
                verdict = "✅ REAL DEAL - Confiable"
                category = 'real'
                self.deal_stats['real_confirmed'] += 1
            elif final_score >= 0.6:
                verdict = "⚠️  PROBABLE REAL - Verificar"
                category = 'probably_real'
            elif final_score >= 0.4:
                verdict = "🔍 SOSPECHOSO - Investigar"
                category = 'suspicious'
                self.deal_stats['suspicious'] += 1
            else:
                verdict = "❌ FAKE DEAL - Evitar"
                category = 'fake'
                self.deal_stats['fake_detected'] += 1
            
            result = {
                'is_real': is_real,
                'is_suspicious': is_suspicious,
                'confidence_score': final_score,
                'verdict': verdict,
                'category': category,
                
                'analysis': {
                    'price_history': price_check,
                    'pattern_detection': pattern_check,
                    'discount_analysis': {
                        'claimed_discount': discount,
                        'current_price': current_price,
                        'original_price': original_price,
                        'is_realistic': discount < 90
                    }
                },
                
                'recommendations': self._generate_recommendations(
                    final_score, 
                    price_check, 
                    pattern_check
                )
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Validation error: {e}")
            return {
                'is_real': False,
                'is_suspicious': True,
                'confidence_score': 0.0,
                'verdict': "❌ ERROR - No se pudo validar",
                'category': 'error',
                'error': str(e)
            }
    
    def _generate_recommendations(self, score: float, price_check: Dict, 
                                 pattern_check: Dict) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if score < 0.4:
            recommendations.append("🚨 NO COMPRAR - Alto riesgo de fake deal")
        
        if price_check.get('stats', {}).get('is_inflated'):
            recommendations.append("⚠️  Precio 'original' inflado artificialmente")
        
        if len(pattern_check.get('suspicious_flags', [])) > 0:
            recommendations.append(f"🔍 Patrones sospechosos: {', '.join(pattern_check['suspicious_flags'])}")
        
        if score >= 0.8:
            recommendations.append("✅ Deal verificado - Seguro para comprar")
        
        if price_check['method'] == 'heuristic':
            recommendations.append("💡 Verificar precio en CamelCamelCamel o ITAD manualmente")
        
        return recommendations
    
    # ═══════════════════════════════════════════════════════════
    # BATCH VALIDATION
    # ═══════════════════════════════════════════════════════════
    
    def validate_batch(self, deals: List[Dict]) -> List[Dict]:
        """
        Valida múltiples deals en batch.
        
        Args:
            deals: List of deal dicts
            
        Returns:
            List of validated deals con scoring
        """
        validated = []
        
        for deal in deals:
            validation = self.validate_deal(deal)
            
            # Merge validation into deal
            enriched_deal = {
                **deal,
                'validation': validation,
                'is_verified': validation['is_real'],
                'trust_score': validation['confidence_score']
            }
            
            validated.append(enriched_deal)
        
        self.logger.info(f"✅ Validated {len(deals)} deals")
        self.logger.info(f"   Real: {self.deal_stats['real_confirmed']}")
        self.logger.info(f"   Suspicious: {self.deal_stats['suspicious']}")
        self.logger.info(f"   Fake: {self.deal_stats['fake_detected']}")
        
        return validated
    
    def get_stats(self) -> Dict:
        """Get validation statistics."""
        return {
            **self.deal_stats,
            'fake_rate': (self.deal_stats['fake_detected'] / max(1, self.deal_stats['total_validated'])) * 100
        }


# ═══════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════

def test_validator():
    """Test smart validator."""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    
    print("\n🧪 Testing Smart Deal Validator")
    print("="*60)
    
    validator = SmartDealValidator(logger=logger)
    
    # Test deals
    test_deals = [
        {
            'title': 'Cyberpunk 2077',
            'current_price': 19.99,
            'original_price': 59.99,
            'discount_percent': 67
        },
        {
            'title': 'Fake Game Ultimate Deluxe Premium Gold Edition',
            'current_price': 0.99,
            'original_price': 299.99,
            'discount_percent': 99
        },
        {
            'title': 'Among Us',
            'current_price': 3.99,
            'original_price': 4.99,
            'discount_percent': 20
        }
    ]
    
    for i, deal in enumerate(test_deals, 1):
        print(f"\n{i}. {deal['title']}")
        print(f"   ${deal['current_price']} (was ${deal['original_price']}) - {deal['discount_percent']}% OFF")
        
        validation = validator.validate_deal(deal)
        
        print(f"\n   {validation['verdict']}")
        print(f"   Confidence: {validation['confidence_score']:.0%}")
        
        if validation.get('recommendations'):
            print(f"\n   Recommendations:")
            for rec in validation['recommendations']:
                print(f"   - {rec}")
    
    print("\n" + "="*60)
    print("📊 Validation Stats:")
    stats = validator.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    test_validator()
