"""
🎮 Sistema de Puntuación - HunDeaBot FIXED
──────────────────────────────────────────

Calcula el score de cada juego basado en reviews y popularidad.
Maneja BOTH dicts y dataclasses (ConsoleDeal).

FIXED: Ahora soporta ConsoleDeal objects y dicts
"""

from typing import Dict, Optional, Union, Any
import logging
from dataclasses import is_dataclass, asdict
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
    Sistema de puntuación para clasificar juegos.
    Score: 0.0 - 5.0
    
    FIXED: Ahora maneja tanto dicts como dataclasses.
    """

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    @staticmethod
    def _safe_get(obj: Any, key: str, default=None):
        """
        Safely get value from dict or dataclass.
        
        Args:
            obj: Dict or dataclass instance
            key: Attribute/key name
            default: Default value if not found
            
        Returns:
            Value or default
        """
        if isinstance(obj, dict):
            return obj.get(key, default)
        elif is_dataclass(obj):
            return getattr(obj, key, default)
        else:
            return default
    
    def calcular_score(self, juego_info: Union[Dict, Any]) -> float:
        """
        Calcula el score total de un juego con sistema híbrido.
        
        FIXED: Ahora soporta tanto dicts como ConsoleDeal objects.
        
        Args:
            juego_info: Dict o ConsoleDeal object
            
        Returns:
            Score 0.0 - 5.0
        """
        
        # Get values safely (works with both dict and dataclass)
        fuente = self._safe_get(juego_info, 'fuente')
        reviews_percent = self._safe_get(juego_info, 'reviews_percent', 0)
        reviews_count = self._safe_get(juego_info, 'reviews_count', 0)
        metacritic = self._safe_get(juego_info, 'metacritic')
        
        # Sistema híbrido para RAWG
        if fuente == 'RAWG' and reviews_percent:
            reviews_count = reviews_count or 0
            percent = reviews_percent or 0
            
            # CASO 1: Muchas reviews (1000+) - Muy confiable
            if reviews_count >= 1000:
                base_score = (percent / 100.0) * 5.0
                
                if reviews_count >= 10000:
                    base_score += 0.3
                elif reviews_count >= 5000:
                    base_score += 0.2
                
                if metacritic:
                    if metacritic >= 85:
                        base_score += 0.2
                    elif metacritic >= 75:
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
        
        # Fallback para otras fuentes o ConsoleDeal sin reviews
        score = 0.0
        
        try:
            percent_val = float(reviews_percent) if reviews_percent is not None else 0.0
        except (TypeError, ValueError):
            percent_val = 0.0
        
        score += (percent_val / 100.0) * 3.5

        try:
            count = int(reviews_count) if reviews_count else 0
        except (TypeError, ValueError):
            count = 0
            
        if count > 10000:
            score += 1.5
        elif count > 1000:
            score += 1.0
        elif count > 100:
            score += 0.5
            
        return min(score, 5.0)

    @staticmethod
    def obtener_estrellas(score: float) -> str:
        """Get star rating from score."""
        if score >= 4.5:
            return "⭐⭐⭐"
        elif score >= 3.5:
            return "⭐⭐"
        elif score >= 2.0:
            return "⭐"
        return "⚠️"
