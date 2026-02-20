"""
Sistema de puntuación para HunDea v3
Calcula el score de cada juego basado en reviews y popularidad
Versión mejorada con sistema híbrido inteligente
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
        Calcula el score total de un juego con sistema híbrido
        
        Args:
            juego_info (dict): Información del juego con reviews
        
        Returns:
            float: Score entre 0.0 y 5.0
        """
        
        # Sistema híbrido para RAWG
        if juego_info.get('fuente') == 'RAWG' and 'reviews_percent' in juego_info:
            reviews_count = juego_info.get('reviews_count', 0)
            percent = juego_info['reviews_percent']
            
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
            
            # CASO 2: Reviews moderadas (50-999) y buenas (70%+) - Dar beneficio
            elif reviews_count >= 50 and percent >= 70:
                # Score base: 70% = 3.5, 80% = 4.0, 90% = 4.5
                base_score = 2.5 + ((percent - 70) / 30.0) * 2.0
                
                # Bonus por cantidad
                if reviews_count >= 500:
                    base_score += 0.4
                elif reviews_count >= 200:
                    base_score += 0.3
                elif reviews_count >= 100:
                    base_score += 0.2
                else:
                    base_score += 0.1
                
                return min(base_score, 4.8)
            
            # CASO 3: Pocas reviews (10-49) - Muy conservador
            elif reviews_count >= 10:
                if percent >= 75:
                    return 3.5  # Aceptable pero incierto
                elif percent >= 65:
                    return 3.0
                else:
                    return 2.5
            
            # CASO 4: Muy pocas reviews (<10) - Dudoso
            else:
                return 2.0 if percent >= 70 else 1.5
        
        # Sistema para Steam o fuentes con reviews nativas
        score = 0.0
        
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
        if score >= 3.5:  # Bajado de 3.7 a 3.5
            return 'premium'
        elif score > 0:
            return 'bajos'
        else:
            return 'desconocido'
    
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
        elif score >= 3.5:  # Bajado de 3.7 a 3.5
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
        elif score >= 3.5:  # Bajado de 3.7 a 3.5
            return "Bueno"
        elif score >= 3.0:
            return "Aceptable"
        elif score >= 2.0:
            return "Regular"
        elif score > 0:
            return "Dudoso"
        else:
            return "Sin reviews"
