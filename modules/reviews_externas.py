"""
Sistema de búsqueda de reviews externas
Usa RAWG API (gratuita) para obtener ratings y reviews
"""

import requests
import time

class ReviewsExternas:
    """
    Busca reviews de juegos en bases de datos externas
    """
    
    def __init__(self, api_key=None):
        # RAWG API key (opcional pero recomendado)
        self.api_key = api_key
        self.rawg_url = "https://api.rawg.io/api/games"
        self.cache_busquedas = {}
    
    def buscar_reviews(self, titulo, tienda=None):
        """
        Busca reviews de un juego por nombre
        
        Args:
            titulo (str): Nombre del juego
            tienda (str): Tienda de origen (opcional)
        
        Returns:
            dict: Reviews encontradas o None
        """
        # Revisar cache
        cache_key = titulo.lower().strip()
        if cache_key in self.cache_busquedas:
            return self.cache_busquedas[cache_key]
        
        # Buscar en RAWG
        rawg_reviews = self._buscar_en_rawg(titulo)
        
        if rawg_reviews:
            self.cache_busquedas[cache_key] = rawg_reviews
            return rawg_reviews
        
        return None
    
    def _buscar_en_rawg(self, titulo):
        """
        Busca juego en RAWG API
        
        Args:
            titulo (str): Nombre del juego
        
        Returns:
            dict: Datos de reviews o None
        """
        try:
            # Buscar juego
            params = {
                'search': titulo,
                'page_size': 1
            }
            
            # Agregar API key si existe
            if self.api_key:
                params['key'] = self.api_key
            
            response = requests.get(self.rawg_url, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if not data.get('results'):
                return None
            
            juego = data['results'][0]
            
            # Verificar que sea el juego correcto (similar al título buscado)
            nombre_encontrado = juego.get('name', '').lower()
            nombre_buscado = titulo.lower()
            
            # Si los nombres no son similares, no es el juego correcto
            if not self._nombres_similares(nombre_encontrado, nombre_buscado):
                return None
            
            # Extraer información
            rating = juego.get('rating')  # 0-5
            ratings_count = juego.get('ratings_count', 0)
            metacritic = juego.get('metacritic')
            
            if not rating or ratings_count < 10:
                return None
            
            # Convertir rating de RAWG (0-5) a porcentaje (0-100)
            percent = (rating / 5.0) * 100
            
            reviews_data = {
                'reviews_count': ratings_count,
                'reviews_percent': round(percent, 1),
                'metacritic': metacritic,
                'fuente': 'RAWG'
            }
            
            print(f"   ℹ️ Reviews encontradas en RAWG: {percent:.1f}% ({ratings_count:,} ratings)")
            
            # Pequeño delay para no saturar la API
            time.sleep(0.5)
            
            return reviews_data
            
        except Exception as e:
            print(f"   ⚠️ Error al buscar en RAWG: {e}")
            return None
    
    def _nombres_similares(self, nombre1, nombre2):
        """
        Verifica si dos nombres son similares
        
        Args:
            nombre1 (str): Primer nombre
            nombre2 (str): Segundo nombre
        
        Returns:
            bool: True si son similares
        """
        # Limpiar nombres
        def limpiar(texto):
            # Quitar caracteres especiales y normalizar
            texto = texto.lower().strip()
            # Quitar palabras comunes
            for palabra in ['the', 'a', 'an', ':', '-', '™', '®']:
                texto = texto.replace(palabra, ' ')
            return ' '.join(texto.split())
        
        n1 = limpiar(nombre1)
        n2 = limpiar(nombre2)
        
        # Verificar si uno está contenido en el otro
        if n1 in n2 or n2 in n1:
            return True
        
        # Verificar similitud de palabras
        palabras1 = set(n1.split())
        palabras2 = set(n2.split())
        
        # Si comparten al menos 60% de palabras, son similares
        if len(palabras1) > 0 and len(palabras2) > 0:
            palabras_comunes = palabras1.intersection(palabras2)
            similitud = len(palabras_comunes) / max(len(palabras1), len(palabras2))
            return similitud >= 0.6
        
        return False
