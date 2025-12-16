"""
Sistema de puntuación para HunDea v2
Calcula el score de cada juego basado en reviews y popularidad
"""

class SistemaScoring:
    """
    Sistema de puntuación para clasificar juegos
    Score: 0.0 - 5.0
    
    3.7+ → Canal Premium
    < 3.7 → Canal Bajos
    """
    
    @staticmethod
    def calcular_score(juego_info):
        """
        Calcula el score total de un juego
        
        Args:
            juego_info (dict): Información del juego con reviews
        
        Returns:
            float: Score entre 0.0 y 5.0
        """
        score = 0.0
        
        # Componente 1: Reviews positivas (0-3 puntos)
        if 'reviews_percent' in juego_info and juego_info['reviews_percent']:
            percent = juego_info['reviews_percent']
            if percent >= 95:
                score += 3.0
            elif percent >= 90:
                score += 2.8
            elif percent >= 85:
                score += 2.5
            elif percent >= 80:
                score += 2.2
            elif percent >= 75:
                score += 2.0
            elif percent >= 70:
                score += 1.7
            elif percent >= 60:
                score += 1.3
            elif percent >= 50:
                score += 1.0
            else:
                score += 0.5
        
        # Componente 2: Cantidad de reviews (0-1.5 puntos)
        if 'reviews_count' in juego_info and juego_info['reviews_count']:
            count = juego_info['reviews_count']
            if count >= 100000:
                score += 1.5
            elif count >= 50000:
                score += 1.3
            elif count >= 10000:
                score += 1.0
            elif count >= 5000:
                score += 0.8
            elif count >= 1000:
                score += 0.5
            elif count >= 100:
                score += 0.3
            else:
                score += 0.1
        
        # Componente 3: Metacritic (0-0.5 puntos bonus)
        if 'metacritic' in juego_info and juego_info['metacritic']:
            meta = juego_info['metacritic']
            if meta >= 90:
                score += 0.5
            elif meta >= 80:
                score += 0.4
            elif meta >= 70:
                score += 0.3
            elif meta >= 60:
                score += 0.2
        
        # Limitar score a 5.0
        return min(score, 5.0)
    
    @staticmethod
    def clasificar_juego(score):
        """
        Clasifica el juego según su score
        
        Args:
            score (float): Score del juego
        
        Returns:
            str: 'premium', 'bajos', o 'desconocido'
        """
        if score >= 3.7:
            return 'premium'
        elif score > 0:
            return 'bajos'
        else:
            return 'desconocido'  # Sin reviews
    
    @staticmethod
    def obtener_estrellas(score):
        """
        Convierte score a representación visual de estrellas
        
        Args:
            score (float): Score del juego
        
        Returns:
            str: Estrellas emoji
        """
        if score >= 4.5:
            return "⭐⭐⭐"
        elif score >= 3.7:
            return "⭐⭐"
        elif score >= 2.0:
            return "⭐"
        else:
            return "⚠️"
    
    @staticmethod
    def obtener_descripcion_score(score):
        """
        Descripción textual del score
        
        Args:
            score (float): Score del juego
        
        Returns:
            str: Descripción
        """
        if score >= 4.5:
            return "Excelente"
        elif score >= 4.0:
            return "Muy bueno"
        elif score >= 3.7:
            return "Bueno"
        elif score >= 3.0:
            return "Aceptable"
        elif score >= 2.0:
            return "Regular"
        elif score > 0:
            return "Dudoso"
        else:
            return "Sin reviews"
