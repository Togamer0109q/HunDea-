"""
🤖 Web-Powered Deal Investigator - Supreme AI
────────────────────────────────────────────────

Bot que usa búsquedas web inteligentes para:
- Investigar ofertas en tiempo real
- Verificar precios en múltiples tiendas
- Detectar reviews y opiniones
- Comparar con históricos
- Generar reportes automáticos

Usa Claude's web_search en producción.

Author: HunDeaBot Team  
Version: 3.0.0 - WEB-POWERED AI
"""

import logging
import re
from typing import Dict, List, Optional
from datetime import datetime
import statistics


class WebPoweredInvestigator:
    """
    Investigador supremo que usa web search para verificar deals.
    """
    
    # Search patterns
    SEARCH_PATTERNS = {
        'price_check': '"{game_title}" price history',
        'deal_verify': '"{game_title}" ${price} deal real or fake',
        'store_compare': '"{game_title}" cheapest price',
        'reviews': '"{game_title}" review score metacritic',
        'historical': '"{game_title}" historical low price'
    }
    
    def __init__(self, web_search_func=None, logger=None):
        """
        Initialize investigator.
        
        Args:
            web_search_func: Function to perform web searches
            logger: Logger instance
        """
        self.web_search = web_search_func
        self.logger = logger or logging.getLogger(__name__)
        
        self.investigation_cache = {}
        self.stats = {
            'investigations': 0,
            'searches_performed': 0,
            'fake_detected': 0,
            'verified_real': 0
        }
    
    # ═══════════════════════════════════════════════════════════
    # WEB INVESTIGATION
    # ═══════════════════════════════════════════════════════════
    
    def investigate_deal(self, game_title: str, current_price: float,
                        claimed_original: float, store: str = "Unknown") -> Dict:
        """
        Investiga un deal usando búsquedas web inteligentes.
        
        Args:
            game_title: Nombre del juego
            current_price: Precio actual
            claimed_original: Precio "original" claimed
            store: Tienda donde está la oferta
            
        Returns:
            Dict con investigación completa
        """
        self.logger.info(f"🔍 Investigating: {game_title} at ${current_price}")
        self.stats['investigations'] += 1
        
        investigation = {
            'game_title': game_title,
            'current_price': current_price,
            'claimed_original': claimed_original,
            'store': store,
            'timestamp': datetime.now().isoformat(),
            'searches': {},
            'findings': {},
            'verdict': {}
        }
        
        # 1. Price History Search
        price_history = self._search_price_history(game_title, current_price)
        investigation['searches']['price_history'] = price_history
        
        # 2. Store Comparison
        store_comparison = self._search_store_comparison(game_title, current_price)
        investigation['searches']['store_comparison'] = store_comparison
        
        # 3. Deal Verification
        deal_verification = self._search_deal_verification(
            game_title, 
            current_price,
            claimed_original
        )
        investigation['searches']['deal_verification'] = deal_verification
        
        # 4. Game Quality Check (reviews)
        quality_check = self._search_game_quality(game_title)
        investigation['searches']['quality_check'] = quality_check
        
        # 5. Analyze findings
        findings = self._analyze_findings(investigation['searches'])
        investigation['findings'] = findings
        
        # 6. Generate verdict
        verdict = self._generate_web_verdict(findings, investigation)
        investigation['verdict'] = verdict
        
        # Update stats
        if verdict['category'] == 'verified_real':
            self.stats['verified_real'] += 1
        elif verdict['category'] == 'fake':
            self.stats['fake_detected'] += 1
        
        return investigation
    
    def _search_price_history(self, game_title: str, current_price: float) -> Dict:
        """
        Busca historial de precios del juego.
        """
        query = self.SEARCH_PATTERNS['price_check'].format(game_title=game_title)
        
        self.logger.info(f"🔍 Searching: {query}")
        
        # Placeholder para demostración
        # En producción, usar web_search tool
        if self.web_search:
            try:
                results = self.web_search(query)
                self.stats['searches_performed'] += 1
                
                # Extract price info from results
                historical_low = self._extract_price_from_text(results)
                
                return {
                    'query': query,
                    'found': historical_low is not None,
                    'historical_low': historical_low,
                    'sources': self._extract_sources(results),
                    'confidence': 0.8 if historical_low else 0.3
                }
            except Exception as e:
                self.logger.error(f"Price history search failed: {e}")
        
        # Fallback / Mock
        return {
            'query': query,
            'found': False,
            'note': 'Would use web_search here',
            'mock_data': {
                'historical_low': current_price * 0.7,  # Mock: 30% cheaper historical
                'typical_price': current_price * 1.2
            },
            'confidence': 0.5
        }
    
    def _search_store_comparison(self, game_title: str, current_price: float) -> Dict:
        """
        Compara precios entre diferentes tiendas.
        """
        query = self.SEARCH_PATTERNS['store_compare'].format(game_title=game_title)
        
        self.logger.info(f"🔍 Searching: {query}")
        
        if self.web_search:
            try:
                results = self.web_search(query)
                self.stats['searches_performed'] += 1
                
                # Extract competitor prices
                competitor_prices = self._extract_competitor_prices(results)
                
                return {
                    'query': query,
                    'found': len(competitor_prices) > 0,
                    'competitor_prices': competitor_prices,
                    'lowest_found': min(competitor_prices) if competitor_prices else None,
                    'confidence': 0.85 if competitor_prices else 0.4
                }
            except Exception as e:
                self.logger.error(f"Store comparison failed: {e}")
        
        # Fallback
        return {
            'query': query,
            'found': False,
            'note': 'Would use web_search here',
            'mock_data': {
                'steam_price': current_price * 1.1,
                'gog_price': current_price * 1.05,
                'epic_price': current_price
            },
            'confidence': 0.5
        }
    
    def _search_deal_verification(self, game_title: str, price: float,
                                  original: float) -> Dict:
        """
        Busca si el deal es real o fake.
        """
        query = self.SEARCH_PATTERNS['deal_verify'].format(
            game_title=game_title,
            price=price
        )
        
        self.logger.info(f"🔍 Searching: {query}")
        
        if self.web_search:
            try:
                results = self.web_search(query)
                self.stats['searches_performed'] += 1
                
                # Analyze sentiment and keywords
                is_legit = self._analyze_deal_legitimacy(results)
                
                return {
                    'query': query,
                    'found': True,
                    'appears_legit': is_legit,
                    'confidence': 0.75
                }
            except Exception as e:
                self.logger.error(f"Deal verification failed: {e}")
        
        # Fallback
        discount = ((original - price) / original) * 100
        appears_suspicious = discount > 85  # >85% discount suspicious
        
        return {
            'query': query,
            'found': False,
            'note': 'Would use web_search here',
            'heuristic': {
                'discount_percent': discount,
                'appears_suspicious': appears_suspicious
            },
            'confidence': 0.6
        }
    
    def _search_game_quality(self, game_title: str) -> Dict:
        """
        Busca calidad del juego (reviews, scores).
        """
        query = self.SEARCH_PATTERNS['reviews'].format(game_title=game_title)
        
        self.logger.info(f"🔍 Searching: {query}")
        
        if self.web_search:
            try:
                results = self.web_search(query)
                self.stats['searches_performed'] += 1
                
                # Extract review scores
                scores = self._extract_review_scores(results)
                
                return {
                    'query': query,
                    'found': scores is not None,
                    'review_scores': scores,
                    'confidence': 0.9 if scores else 0.4
                }
            except Exception as e:
                self.logger.error(f"Quality check failed: {e}")
        
        # Fallback
        return {
            'query': query,
            'found': False,
            'note': 'Would use web_search here',
            'confidence': 0.5
        }
    
    # ═══════════════════════════════════════════════════════════
    # DATA EXTRACTION FROM SEARCH RESULTS
    # ═══════════════════════════════════════════════════════════
    
    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """Extract price from search results text."""
        # Pattern: $XX.XX or XX.XX USD
        price_patterns = [
            r'\$(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*USD',
            r'price:\s*\$?(\d+\.?\d*)'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    return float(matches[0])
                except:
                    continue
        
        return None
    
    def _extract_competitor_prices(self, text: str) -> List[float]:
        """Extract competitor prices from results."""
        prices = []
        
        # Find all price mentions
        price_pattern = r'\$(\d+\.?\d*)'
        matches = re.findall(price_pattern, text)
        
        for match in matches:
            try:
                price = float(match)
                if 0.99 <= price <= 99.99:  # Reasonable game price range
                    prices.append(price)
            except:
                continue
        
        return list(set(prices))  # Unique prices
    
    def _extract_sources(self, text: str) -> List[str]:
        """Extract source domains from results."""
        # Pattern for URLs
        url_pattern = r'https?://([a-zA-Z0-9.-]+)'
        matches = re.findall(url_pattern, text)
        
        return list(set(matches[:5]))  # Top 5 unique domains
    
    def _extract_review_scores(self, text: str) -> Optional[Dict]:
        """Extract review scores from results."""
        scores = {}
        
        # Metacritic pattern
        metacritic_pattern = r'metacritic[:\s]+(\d+)'
        mc_match = re.search(metacritic_pattern, text, re.IGNORECASE)
        if mc_match:
            scores['metacritic'] = int(mc_match.group(1))
        
        # Steam pattern
        steam_pattern = r'steam[:\s]+(\d+)%'
        steam_match = re.search(steam_pattern, text, re.IGNORECASE)
        if steam_match:
            scores['steam'] = int(steam_match.group(1))
        
        return scores if scores else None
    
    def _analyze_deal_legitimacy(self, text: str) -> bool:
        """
        Analiza texto para determinar si deal parece legítimo.
        """
        text_lower = text.lower()
        
        # Positive indicators
        positive_keywords = [
            'legitimate', 'real deal', 'verified', 'confirmed',
            'official', 'authentic', 'genuine'
        ]
        
        # Negative indicators
        negative_keywords = [
            'fake', 'scam', 'fraud', 'too good to be true',
            'suspicious', 'inflated price', 'misleading'
        ]
        
        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)
        
        return positive_count > negative_count
    
    # ═══════════════════════════════════════════════════════════
    # ANALYSIS & VERDICT
    # ═══════════════════════════════════════════════════════════
    
    def _analyze_findings(self, searches: Dict) -> Dict:
        """
        Analiza todos los resultados de búsqueda.
        """
        findings = {
            'price_checks': [],
            'quality_indicators': [],
            'red_flags': [],
            'confidence_score': 0.0
        }
        
        # Analyze price history
        if searches['price_history'].get('found'):
            historical = searches['price_history'].get('historical_low')
            if historical:
                findings['price_checks'].append(
                    f"Historical low: ${historical}"
                )
        
        # Analyze store comparison
        if searches['store_comparison'].get('found'):
            competitors = searches['store_comparison'].get('competitor_prices', [])
            if competitors:
                avg_price = statistics.mean(competitors)
                findings['price_checks'].append(
                    f"Market average: ${avg_price:.2f}"
                )
        
        # Analyze deal verification
        if searches['deal_verification'].get('appears_legit') == False:
            findings['red_flags'].append("Deal appears suspicious based on web search")
        
        # Analyze quality
        if searches['quality_check'].get('found'):
            scores = searches['quality_check'].get('review_scores', {})
            if scores:
                avg_score = statistics.mean(scores.values())
                findings['quality_indicators'].append(
                    f"Average review score: {avg_score}/100"
                )
        
        # Calculate overall confidence
        confidences = [s.get('confidence', 0.5) for s in searches.values()]
        findings['confidence_score'] = statistics.mean(confidences)
        
        return findings
    
    def _generate_web_verdict(self, findings: Dict, investigation: Dict) -> Dict:
        """
        Genera veredicto final basado en investigación web.
        """
        confidence = findings['confidence_score']
        red_flags = len(findings['red_flags'])
        
        # Determine category
        if confidence >= 0.85 and red_flags == 0:
            category = 'verified_real'
            verdict_msg = "✅ VERIFICADO - Deal confirmado por múltiples fuentes web"
        elif confidence >= 0.70 and red_flags <= 1:
            category = 'probably_real'
            verdict_msg = "✅ PROBABLE REAL - Fuentes indican deal legítimo"
        elif confidence >= 0.50:
            category = 'uncertain'
            verdict_msg = "⚠️  INCIERTO - Información insuficiente"
        else:
            category = 'fake'
            verdict_msg = "❌ SOSPECHOSO - No recomendado"
        
        # Generate detailed report
        report = []
        report.append(f"Confianza: {confidence:.0%}")
        report.append(f"Fuentes consultadas: {self.stats['searches_performed']}")
        
        if findings['price_checks']:
            report.append("\nVerificaciones de precio:")
            for check in findings['price_checks']:
                report.append(f"  ✓ {check}")
        
        if findings['quality_indicators']:
            report.append("\nIndicadores de calidad:")
            for indicator in findings['quality_indicators']:
                report.append(f"  ✓ {indicator}")
        
        if findings['red_flags']:
            report.append("\n🚩 Red Flags:")
            for flag in findings['red_flags']:
                report.append(f"  ⚠️  {flag}")
        
        return {
            'category': category,
            'verdict': verdict_msg,
            'confidence': confidence,
            'red_flags_count': red_flags,
            'report': '\n'.join(report),
            'recommendation': self._generate_web_recommendation(category, confidence)
        }
    
    def _generate_web_recommendation(self, category: str, confidence: float) -> str:
        """Generate recommendation based on web investigation."""
        if category == 'verified_real':
            return "✅ Comprar - Deal verificado por múltiples fuentes confiables"
        elif category == 'probably_real':
            return "👍 Probablemente seguro - Verificar precio en tienda oficial"
        elif category == 'uncertain':
            return "⚠️  Investigar más - Buscar reviews antes de comprar"
        else:
            return "🚫 Evitar - Deal sospechoso, esperar confirmación"
    
    def get_stats(self) -> Dict:
        """Get investigation statistics."""
        return self.stats


# ═══════════════════════════════════════════════════════════
# DEMO/TESTING
# ═══════════════════════════════════════════════════════════

def demo_investigator():
    """Demo of web-powered investigator."""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    
    print("\n" + "="*70)
    print("🤖 WEB-POWERED DEAL INVESTIGATOR - DEMO")
    print("="*70)
    print("\nEste sistema busca en la web para verificar ofertas.")
    print("En producción, usaría Claude's web_search tool.\n")
    
    # Mock web_search function
    def mock_web_search(query):
        logger.info(f"[MOCK] Web searching: {query}")
        return f"Sample results for: {query}. Price $29.99 on Steam. Metacritic 85."
    
    investigator = WebPoweredInvestigator(
        web_search_func=mock_web_search,
        logger=logger
    )
    
    # Test deal
    test_deal = {
        'title': 'Cyberpunk 2077',
        'current_price': 29.99,
        'claimed_original': 59.99,
        'store': 'Steam'
    }
    
    print(f"🎮 Investigating Deal:")
    print(f"   Game: {test_deal['title']}")
    print(f"   Price: ${test_deal['current_price']} (was ${test_deal['claimed_original']})")
    print(f"   Store: {test_deal['store']}")
    
    investigation = investigator.investigate_deal(
        test_deal['title'],
        test_deal['current_price'],
        test_deal['claimed_original'],
        test_deal['store']
    )
    
    print(f"\n{'='*70}")
    print("📊 INVESTIGATION REPORT")
    print(f"{'='*70}")
    
    print(f"\n{investigation['verdict']['verdict']}")
    print(f"\n{investigation['verdict']['report']}")
    print(f"\n💡 Recommendation:")
    print(f"  {investigation['verdict']['recommendation']}")
    
    print(f"\n{'='*70}")
    print("📈 Statistics:")
    stats = investigator.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    demo_investigator()
