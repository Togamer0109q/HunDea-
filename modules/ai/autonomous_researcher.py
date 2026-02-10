"""
🔍 Autonomous Deal Researcher - Ultra-Intelligent Search Bot
──────────────────────────────────────────────────────────────

Bot autónomo que:
- Busca ofertas automáticamente
- Verifica precios en múltiples fuentes
- Detecta fake deals
- Compara entre tiendas
- Genera reportes inteligentes

Author: HunDeaBot Team
Version: 2.0.0 - AUTONOMOUS AI
"""

import requests
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics
import re
from urllib.parse import quote_plus
import time


class AutonomousDealResearcher:
    """
    Bot autónomo que investiga ofertas inteligentemente.
    """
    
    # Search engines y APIs
    SEARCH_SOURCES = {
        'cheapshark': 'https://www.cheapshark.com/api/1.0/deals',
        'itad': 'https://api.isthereanydeal.com/v2',
        'steamdb': 'https://steamdb.info/sales/',
        'gg_deals': 'https://gg.deals/deals/',
    }
    
    # Thresholds for verification
    VERIFICATION_THRESHOLDS = {
        'min_sources': 2,           # Mínimo 2 fuentes para validar
        'price_variance': 0.15,     # Máx 15% diferencia entre fuentes
        'historical_variance': 0.20, # Máx 20% vs histórico
        'confidence_required': 0.75  # 75% confianza mínima
    }
    
    def __init__(self, itad_api_key: Optional[str] = None, logger=None):
        """Initialize researcher."""
        self.itad_api_key = itad_api_key
        self.logger = logger or logging.getLogger(__name__)
        
        # Cache de búsquedas
        self.search_cache = {}
        self.verification_cache = {}
        
        # Stats
        self.stats = {
            'searches_performed': 0,
            'sources_checked': 0,
            'fake_deals_found': 0,
            'verified_deals': 0
        }
    
    # ═══════════════════════════════════════════════════════════
    # AUTONOMOUS SEARCH
    # ═══════════════════════════════════════════════════════════
    
    def research_deal(self, game_title: str, claimed_price: float, 
                     claimed_original: float) -> Dict:
        """
        Investiga un deal automáticamente en múltiples fuentes.
        
        Args:
            game_title: Título del juego
            claimed_price: Precio que dice la oferta
            claimed_original: Precio "original" que dice
            
        Returns:
            Dict con investigación completa
        """
        self.logger.info(f"🔍 Researching: {game_title}")
        self.stats['searches_performed'] += 1
        
        # 1. Buscar en múltiples fuentes
        sources_data = self._search_all_sources(game_title)
        
        # 2. Verificar precios
        price_verification = self._verify_prices(
            sources_data, 
            claimed_price, 
            claimed_original
        )
        
        # 3. Verificar historial
        historical_verification = self._verify_historical(
            game_title,
            claimed_price,
            claimed_original
        )
        
        # 4. Cross-reference entre fuentes
        cross_check = self._cross_reference_sources(sources_data)
        
        # 5. Generar veredicto final
        verdict = self._generate_verdict(
            price_verification,
            historical_verification,
            cross_check
        )
        
        return {
            'game_title': game_title,
            'sources_found': len(sources_data),
            'sources_data': sources_data,
            'price_verification': price_verification,
            'historical_verification': historical_verification,
            'cross_check': cross_check,
            'verdict': verdict,
            'timestamp': datetime.now().isoformat()
        }
    
    def _search_all_sources(self, game_title: str) -> List[Dict]:
        """
        Busca el juego en todas las fuentes disponibles.
        """
        sources = []
        
        # CheapShark
        try:
            cheapshark_data = self._search_cheapshark(game_title)
            if cheapshark_data:
                sources.append({
                    'source': 'CheapShark',
                    'reliability': 0.95,
                    'data': cheapshark_data
                })
                self.stats['sources_checked'] += 1
        except Exception as e:
            self.logger.debug(f"CheapShark search failed: {e}")
        
        # IsThereAnyDeal
        if self.itad_api_key:
            try:
                itad_data = self._search_itad(game_title)
                if itad_data:
                    sources.append({
                        'source': 'ITAD',
                        'reliability': 0.98,
                        'data': itad_data
                    })
                    self.stats['sources_checked'] += 1
            except Exception as e:
                self.logger.debug(f"ITAD search failed: {e}")
        
        # Web scraping fallback (si hay pocas fuentes)
        if len(sources) < self.VERIFICATION_THRESHOLDS['min_sources']:
            try:
                web_data = self._web_search_fallback(game_title)
                if web_data:
                    sources.append({
                        'source': 'Web Search',
                        'reliability': 0.70,
                        'data': web_data
                    })
                    self.stats['sources_checked'] += 1
            except Exception as e:
                self.logger.debug(f"Web search failed: {e}")
        
        self.logger.info(f"✅ Found {len(sources)} sources for {game_title}")
        return sources
    
    def _search_cheapshark(self, game_title: str) -> Optional[Dict]:
        """Search CheapShark API."""
        try:
            # Search by title
            search_url = "https://www.cheapshark.com/api/1.0/games"
            params = {
                'title': game_title,
                'limit': 5
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            games = response.json()
            
            if not games:
                return None
            
            # Get best match
            game = games[0]
            game_id = game['gameID']
            
            # Get deals for this game
            deals_url = "https://www.cheapshark.com/api/1.0/deals"
            deals_params = {
                'id': game_id,
                'pageSize': 10
            }
            
            deals_response = requests.get(deals_url, params=deals_params, timeout=10)
            deals_response.raise_for_status()
            
            deals = deals_response.json()
            
            if not deals:
                return None
            
            # Extract price info
            prices = []
            for deal in deals:
                prices.append({
                    'store': deal.get('storeID'),
                    'current_price': float(deal.get('salePrice', 0)),
                    'normal_price': float(deal.get('normalPrice', 0)),
                    'savings': float(deal.get('savings', 0))
                })
            
            return {
                'game_id': game_id,
                'game_name': game['external'],
                'cheapest_current': min(p['current_price'] for p in prices if p['current_price'] > 0),
                'cheapest_normal': min(p['normal_price'] for p in prices if p['normal_price'] > 0),
                'all_prices': prices,
                'stores_count': len(prices)
            }
            
        except Exception as e:
            self.logger.debug(f"CheapShark error: {e}")
            return None
    
    def _search_itad(self, game_title: str) -> Optional[Dict]:
        """Search IsThereAnyDeal."""
        try:
            # Search game
            search_url = f"{self.SEARCH_SOURCES['itad']}/search/search/"
            params = {
                'key': self.itad_api_key,
                'title': game_title,
                'limit': 1
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            
            if not results:
                return None
            
            game = results[0]
            game_id = game['id']
            
            # Get current prices
            prices_url = f"{self.SEARCH_SOURCES['itad']}/game/prices/"
            prices_params = {
                'key': self.itad_api_key,
                'id': game_id,
                'shops': 'steam,gog,epic,humble',
                'country': 'US'
            }
            
            prices_response = requests.get(prices_url, params=prices_params, timeout=10)
            prices_response.raise_for_status()
            
            prices_data = prices_response.json()
            
            # Get historical low
            history_url = f"{self.SEARCH_SOURCES['itad']}/game/lowest/"
            history_params = {
                'key': self.itad_api_key,
                'id': game_id
            }
            
            history_response = requests.get(history_url, params=history_params, timeout=10)
            history_response.raise_for_status()
            
            history_data = history_response.json()
            
            return {
                'game_id': game_id,
                'game_name': game['title'],
                'current_prices': prices_data,
                'historical_low': history_data.get('price', 0),
                'historical_low_date': history_data.get('recorded', '')
            }
            
        except Exception as e:
            self.logger.debug(f"ITAD error: {e}")
            return None
    
    def _web_search_fallback(self, game_title: str) -> Optional[Dict]:
        """
        Fallback: búsqueda web para verificar.
        En producción usaría web_search tool de Claude.
        """
        # Placeholder - en producción usar web_search
        self.logger.info(f"🌐 Would search web for: {game_title}")
        return {
            'method': 'web_search',
            'note': 'Would use web_search tool here'
        }
    
    # ═══════════════════════════════════════════════════════════
    # PRICE VERIFICATION
    # ═══════════════════════════════════════════════════════════
    
    def _verify_prices(self, sources_data: List[Dict], 
                      claimed_price: float, claimed_original: float) -> Dict:
        """
        Verifica precios contra múltiples fuentes.
        """
        if not sources_data:
            return {
                'verified': False,
                'confidence': 0.0,
                'reason': 'No sources available'
            }
        
        # Extract all prices from sources
        current_prices = []
        original_prices = []
        
        for source in sources_data:
            data = source['data']
            
            if 'cheapest_current' in data:
                current_prices.append(data['cheapest_current'])
                original_prices.append(data['cheapest_normal'])
            
            if 'current_prices' in data:
                # ITAD format
                for shop_prices in data['current_prices'].values():
                    if 'price' in shop_prices:
                        current_prices.append(shop_prices['price'])
        
        if not current_prices:
            return {
                'verified': False,
                'confidence': 0.3,
                'reason': 'No comparable prices found'
            }
        
        # Calculate stats
        avg_current = statistics.mean(current_prices)
        min_current = min(current_prices)
        max_current = max(current_prices)
        
        # Verify claimed price
        price_diff = abs(claimed_price - avg_current) / avg_current
        
        is_price_valid = price_diff <= self.VERIFICATION_THRESHOLDS['price_variance']
        
        # Verify original price (if available)
        is_original_valid = True
        if original_prices:
            avg_original = statistics.mean(original_prices)
            original_diff = abs(claimed_original - avg_original) / avg_original
            is_original_valid = original_diff <= self.VERIFICATION_THRESHOLDS['price_variance']
        
        # Calculate confidence
        confidence = 1.0
        if not is_price_valid:
            confidence -= 0.3
        if not is_original_valid:
            confidence -= 0.2
        if len(sources_data) < self.VERIFICATION_THRESHOLDS['min_sources']:
            confidence -= 0.2
        
        confidence = max(0.0, min(1.0, confidence))
        
        return {
            'verified': is_price_valid and is_original_valid,
            'confidence': confidence,
            'claimed_price': claimed_price,
            'market_avg': avg_current,
            'market_min': min_current,
            'market_max': max_current,
            'price_variance': price_diff,
            'sources_count': len(sources_data),
            'is_price_realistic': is_price_valid,
            'is_original_realistic': is_original_valid
        }
    
    def _verify_historical(self, game_title: str, current_price: float,
                          claimed_original: float) -> Dict:
        """Verify against historical prices."""
        
        # Try to get historical data from ITAD
        if self.itad_api_key:
            try:
                # Search game
                search_url = f"{self.SEARCH_SOURCES['itad']}/search/search/"
                params = {
                    'key': self.itad_api_key,
                    'title': game_title,
                    'limit': 1
                }
                
                response = requests.get(search_url, params=params, timeout=10)
                response.raise_for_status()
                results = response.json()
                
                if not results:
                    return self._historical_fallback()
                
                game_id = results[0]['id']
                
                # Get historical low
                history_url = f"{self.SEARCH_SOURCES['itad']}/game/lowest/"
                history_params = {
                    'key': self.itad_api_key,
                    'id': game_id
                }
                
                history_response = requests.get(history_url, params=history_params, timeout=10)
                history_response.raise_for_status()
                
                history = history_response.json()
                
                historical_low = history.get('price', 0)
                
                # Verify
                is_reasonable = current_price >= (historical_low * 0.8)  # Within 80% of historical low
                is_original_inflated = claimed_original > (historical_low * 3)  # Original >3x historical = suspicious
                
                confidence = 0.9 if is_reasonable and not is_original_inflated else 0.4
                
                return {
                    'verified': True,
                    'confidence': confidence,
                    'historical_low': historical_low,
                    'current_vs_historical': (current_price / historical_low) if historical_low > 0 else 0,
                    'is_reasonable': is_reasonable,
                    'is_original_inflated': is_original_inflated,
                    'method': 'itad_api'
                }
                
            except Exception as e:
                self.logger.debug(f"Historical check failed: {e}")
                return self._historical_fallback()
        
        return self._historical_fallback()
    
    def _historical_fallback(self) -> Dict:
        """Fallback when no historical data available."""
        return {
            'verified': False,
            'confidence': 0.5,
            'method': 'no_historical_data',
            'note': 'Could not verify historical prices'
        }
    
    # ═══════════════════════════════════════════════════════════
    # CROSS-REFERENCE
    # ═══════════════════════════════════════════════════════════
    
    def _cross_reference_sources(self, sources_data: List[Dict]) -> Dict:
        """
        Cross-reference entre fuentes para detectar inconsistencias.
        """
        if len(sources_data) < 2:
            return {
                'cross_verified': False,
                'confidence': 0.3,
                'reason': 'Not enough sources to cross-reference'
            }
        
        # Extract all prices
        all_prices = []
        
        for source in sources_data:
            data = source['data']
            reliability = source['reliability']
            
            if 'cheapest_current' in data:
                all_prices.append({
                    'price': data['cheapest_current'],
                    'source': source['source'],
                    'reliability': reliability
                })
        
        if len(all_prices) < 2:
            return {
                'cross_verified': False,
                'confidence': 0.4,
                'reason': 'Insufficient price data'
            }
        
        # Calculate variance
        prices_only = [p['price'] for p in all_prices]
        avg_price = statistics.mean(prices_only)
        std_dev = statistics.stdev(prices_only) if len(prices_only) > 1 else 0
        variance_pct = (std_dev / avg_price) if avg_price > 0 else 0
        
        # Low variance = high confidence
        is_consistent = variance_pct <= 0.15  # 15% variance max
        
        confidence = 0.9 if is_consistent else 0.5
        
        # Weight by source reliability
        weighted_avg = sum(p['price'] * p['reliability'] for p in all_prices) / sum(p['reliability'] for p in all_prices)
        
        return {
            'cross_verified': is_consistent,
            'confidence': confidence,
            'sources_compared': len(all_prices),
            'price_variance': variance_pct,
            'average_price': avg_price,
            'weighted_average': weighted_avg,
            'is_consistent': is_consistent,
            'all_sources': [p['source'] for p in all_prices]
        }
    
    # ═══════════════════════════════════════════════════════════
    # FINAL VERDICT
    # ═══════════════════════════════════════════════════════════
    
    def _generate_verdict(self, price_verification: Dict,
                         historical_verification: Dict,
                         cross_check: Dict) -> Dict:
        """
        Genera veredicto final basado en todas las verificaciones.
        """
        # Calculate weighted confidence
        weights = {
            'price': 0.4,
            'historical': 0.35,
            'cross_check': 0.25
        }
        
        final_confidence = (
            price_verification['confidence'] * weights['price'] +
            historical_verification['confidence'] * weights['historical'] +
            cross_check['confidence'] * weights['cross_check']
        )
        
        # Determine if deal is real
        is_real = final_confidence >= self.VERIFICATION_THRESHOLDS['confidence_required']
        
        # Generate verdict message
        if final_confidence >= 0.9:
            verdict_msg = "✅ VERIFICADO - Deal 100% real"
            category = 'verified_real'
            self.stats['verified_deals'] += 1
        elif final_confidence >= 0.75:
            verdict_msg = "✅ PROBABLE REAL - Alta confianza"
            category = 'probably_real'
            self.stats['verified_deals'] += 1
        elif final_confidence >= 0.5:
            verdict_msg = "⚠️  INCIERTO - Verificar manualmente"
            category = 'uncertain'
        else:
            verdict_msg = "❌ FAKE - No comprar"
            category = 'fake'
            self.stats['fake_deals_found'] += 1
        
        # Generate detailed report
        issues = []
        if not price_verification.get('is_price_realistic'):
            issues.append("Precio no coincide con mercado")
        if not price_verification.get('is_original_realistic'):
            issues.append("Precio 'original' inflado")
        if historical_verification.get('is_original_inflated'):
            issues.append("Original price >3x histórico")
        if not cross_check.get('is_consistent'):
            issues.append("Inconsistencia entre fuentes")
        
        return {
            'is_real': is_real,
            'confidence': final_confidence,
            'verdict': verdict_msg,
            'category': category,
            'issues': issues,
            'recommendation': self._generate_recommendation(final_confidence, issues),
            'detailed_scores': {
                'price_verification': price_verification['confidence'],
                'historical_verification': historical_verification['confidence'],
                'cross_reference': cross_check['confidence']
            }
        }
    
    def _generate_recommendation(self, confidence: float, issues: List[str]) -> str:
        """Generate actionable recommendation."""
        if confidence >= 0.9:
            return "✅ Comprar con confianza - Deal verificado"
        elif confidence >= 0.75:
            return "👍 Probablemente seguro - Deal verificado en múltiples fuentes"
        elif confidence >= 0.5:
            return "⚠️  Verificar precio en otras tiendas antes de comprar"
        else:
            return f"🚫 NO COMPRAR - {', '.join(issues)}"
    
    # ═══════════════════════════════════════════════════════════
    # BATCH RESEARCH
    # ═══════════════════════════════════════════════════════════
    
    def research_batch(self, deals: List[Dict]) -> List[Dict]:
        """
        Research multiple deals en batch.
        
        Args:
            deals: List of dicts with title, price, original_price
            
        Returns:
            List of researched deals
        """
        researched = []
        
        for i, deal in enumerate(deals, 1):
            self.logger.info(f"📊 Researching {i}/{len(deals)}: {deal['title']}")
            
            research = self.research_deal(
                deal['title'],
                deal.get('current_price', 0),
                deal.get('original_price', 0)
            )
            
            enriched = {
                **deal,
                'research': research,
                'is_verified': research['verdict']['is_real'],
                'confidence': research['verdict']['confidence']
            }
            
            researched.append(enriched)
            
            # Rate limiting
            time.sleep(0.5)
        
        return researched
    
    def get_stats(self) -> Dict:
        """Get research statistics."""
        return self.stats


# ═══════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════

def test_researcher():
    """Test autonomous researcher."""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    
    print("\n" + "="*70)
    print("🔍 AUTONOMOUS DEAL RESEARCHER - DEMO")
    print("="*70)
    
    researcher = AutonomousDealResearcher(logger=logger)
    
    # Test deal
    test_deal = {
        'title': 'Cyberpunk 2077',
        'current_price': 29.99,
        'original_price': 59.99
    }
    
    print(f"\n🎮 Researching: {test_deal['title']}")
    print(f"   Claimed: ${test_deal['current_price']} (was ${test_deal['original_price']})")
    
    research = researcher.research_deal(
        test_deal['title'],
        test_deal['current_price'],
        test_deal['original_price']
    )
    
    print(f"\n{'='*70}")
    print("📊 RESEARCH RESULTS")
    print(f"{'='*70}")
    
    print(f"\nSources Found: {research['sources_found']}")
    for source in research['sources_data']:
        print(f"  - {source['source']} (reliability: {source['reliability']:.0%})")
    
    print(f"\n{research['verdict']['verdict']}")
    print(f"Confidence: {research['verdict']['confidence']:.0%}")
    
    if research['verdict']['issues']:
        print(f"\n⚠️  Issues:")
        for issue in research['verdict']['issues']:
            print(f"  - {issue}")
    
    print(f"\n💡 Recommendation:")
    print(f"  {research['verdict']['recommendation']}")
    
    print(f"\n{'='*70}")
    stats = researcher.get_stats()
    print("📈 Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    test_researcher()
