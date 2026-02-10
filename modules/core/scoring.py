"""
🎮 Sistema de Puntuación - HunDeaBot
────────────────────────────────────

Calcula el score de cada juego basado en reviews y popularidad.
Proporciona integración con RAWG para enriquecimiento de datos.
"""

from typing import Dict, Optional
import logging
from ..reviews_externas import ReviewsExternas

logger = logging.getLogger(__name__)

def get_rawg_data(title: str, api_key: str) -> Optional[Dict]:
    """
    Función puente para obtener datos de RAWG de forma sencilla.
    """
    try:
        reviews_ext = ReviewsExternas(api_key=api_key)
        rawg_info = reviews_ext.buscar_reviews(title)
        
        if not rawg_info:
            return None
            
        return {
            'rating': (rawg_info.get('reviews_percent', 0) or 0) / 20.0,  # 0-100 to 0-5
            'metacritic': rawg_info.get('metacritic'),
            'ratings_count': rawg_info.get('reviews_count', 0),
            'genres': [{'name': rawg_info.get('genre', 'Unknown')}]
        }
    except Exception as e:
        return None

class SistemaScoring:
    """
    Sistema de puntuación para clasificar juegos
    Score: 0.0 - 5.0
    """

    def __init__(self, logger=None):
        # Optional logger; scoring is mostly static.
        self.logger = logger or logging.getLogger(__name__)
    
    @staticmethod
    def calcular_score(juego_info: Dict) -> float:
        """Calcula el score total de un juego con sistema híbrido."""
        
        # Sistema híbrido para RAWG
        if juego_info.get('fuente') == 'RAWG' and 'reviews_percent' in juego_info:
            reviews_count = juego_info.get('reviews_count', 0) or 0
            percent = juego_info.get('reviews_percent', 0) or 0
            
            # CASO 1: Muchas reviews (1000+) - Muy confiable
            if reviews_count >= 1000:
                base_score = (percent / 100.0) * 5.0
                
                if reviews_count >= 10000:
                    base_score += 0.3
                elif reviews_count >= 5000:
                    base_score += 0.2
                
                if juego_info.get('metacritic'):
                    meta = juego_info['metacritic']
                    if meta >= 85:
                        base_score += 0.2
                    elif meta >= 75:
                        base_score += 0.1
                
                return min(base_score, 5.0)
            
            # CASO 2: Reviews moderadas (50-999) y buenas (70%+)
            elif reviews_count >= 50 and percent >= 70:
                base_score = 2.5 + ((percent - 70) / 30.0) * 2.0
                
                if reviews_count >= 500:
                    base_score += 0.4
                elif reviews_count >= 200:
                    base_score += 0.3
                elif reviews_count >= 100:
                    base_score += 0.2
                else:
                    base_score += 0.1
                
                return min(base_score, 4.8)
            
            return 3.0 if percent >= 75 else 2.0
        
        # Fallback para otras fuentes
        score = 0.0
        reviews_percent = juego_info.get('reviews_percent')
        try:
            percent_val = float(reviews_percent) if reviews_percent is not None else 0.0
        except (TypeError, ValueError):
            percent_val = 0.0
        score += (percent_val / 100.0) * 3.5

        count = juego_info.get('reviews_count') or 0
        if isinstance(count, (int, float)):
            count = int(count)
        if count > 10000: score += 1.5
        elif count > 1000: score += 1.0
        elif count > 100: score += 0.5
            
        return min(score, 5.0)

    @staticmethod
    def obtener_estrellas(score: float) -> str:
        if score >= 4.5: return "⭐⭐⭐"
        elif score >= 3.5: return "⭐⭐"
        elif score >= 2.0: return "⭐"
        return "⚠️"
