# 🌟 IsThereAnyDeal (ITAD) - Guía Técnica

## ¿Qué es IsThereAnyDeal?

IsThereAnyDeal es un servicio que agrega precios de juegos de múltiples tiendas digitales. Su API **no requiere API key** y es completamente gratuita.

**Website:** https://isthereanydeal.com  
**API Docs:** https://docs.isthereanydeal.com

---

## 🏪 Tiendas Soportadas

HunDea monitorea estas tiendas a través de ITAD:

### Tiendas Prioritarias (monitoreadas activamente)
1. **Steam** 🔵
2. **GOG** 🟣
3. **Epic Games** ⚫ (también con API directa)
4. **Itch.io** 🔴
5. **Humble Store** 🟠
6. **Microsoft Store** 🟢

### Tiendas Secundarias (también disponibles)
- Ubisoft Connect (Uplay)
- EA Origin
- Nuuvem
- Green Man Gaming
- Fanatical
- Gamesplanet
- GamersGate

---

## 🔍 Cómo Funciona

### 1. Búsqueda de Juegos Gratis

ITAD no tiene un endpoint directo de "juegos gratis", así que usamos esta estrategia:

```python
# Buscar en cada tienda
for tienda in ['steam', 'gog', 'epicgames', ...]:
    # Obtener ofertas recientes
    ofertas = buscar_en_tienda(tienda)
    
    # Filtrar solo las que tienen precio = $0.00
    gratis = [o for o in ofertas if o['precio'] == 0]
```

### 2. Eliminación de Duplicados

Muchas veces el mismo juego está gratis en múltiples tiendas. HunDea prioriza:

1. Epic Games (mejor distribución)
2. GOG (DRM-free)
3. Steam (más popular)
4. Otras tiendas

### 3. Integración con RAWG

Después de encontrar juegos gratis, HunDea busca reviews en RAWG:

```python
juego_itad = encontrar_en_itad()  # "Cyberpunk 2077"
reviews = buscar_en_rawg(juego_itad['titulo'])  # Reviews + ratings
juego_final = {**juego_itad, **reviews}  # Combinar
```

---

## ⚡ Rate Limiting

ITAD tiene rate limits (aunque generosos):

- **Límite:** ~300 requests/hora
- **HunDea usa:** ~6-10 requests por ejecución
- **Frecuencia:** Cada 3 horas en GitHub Actions
- **Protección:** Pausa de 0.5s entre requests

**Conclusión:** Muy difícil alcanzar el límite con uso normal.

---

## 📊 Formato de Datos

### Input (de ITAD)
```json
{
  "id": "steamapp123",
  "title": "Game Name",
  "deals": [{
    "shop": {"id": "steam"},
    "price": {"amount": 0},
    "url": "https://...",
    "expiry": 1234567890
  }]
}
```

### Output (formato HunDea)
```python
{
  'id': 'itad_steam_123',
  'titulo': 'Game Name',
  'tienda': 'Steam',
  'tienda_emoji': '🔵',
  'url': 'https://...',
  'fecha_fin': 'Lunes, 25 de diciembre...',
  'imagen_url': 'https://cdn.itad.com/...',
  'tipo': 'gratis',
  'fuente': 'IsThereAnyDeal',
  'reviews_percent': None,  # Se llena después con RAWG
  'reviews_count': None
}
```

---

## 🧪 Testing

### Test Básico
```bash
python test_itad.py
```

Esto mostrará:
- Juegos gratis encontrados
- Reviews de RAWG
- Scores calculados
- Clasificación (Premium/Bajos)

### Test Manual en Python
```python
from modules.itad_hunter import IsThereAnyDealHunter

hunter = IsThereAnyDealHunter()
juegos = hunter.obtener_juegos_gratis()

for juego in juegos:
    print(f"{juego['titulo']} - {juego['tienda']}")
```

---

## ⚠️ Limitaciones Conocidas

### 1. No Todos los Juegos Gratis
ITAD solo incluye juegos que están en su base de datos. Juegos muy nuevos o muy indie pueden no aparecer.

**Solución:** Epic Hunter complementa para Epic Games exclusivos.

### 2. Matching de Nombres
A veces el nombre en ITAD no coincide exactamente con RAWG:
- ITAD: "Grand Theft Auto V"
- RAWG: "GTA V"

**Solución:** ReviewsExternas hace búsqueda fuzzy.

### 3. Ofertas Temporales
ITAD actualiza cada ~30 minutos, puede haber delay.

**Solución:** GitHub Actions ejecuta cada 3 horas, suficiente.

### 4. Imágenes
ITAD proporciona imágenes pero no siempre son de alta calidad.

**Solución:** Discord Embed usa la mejor imagen disponible.

---

## 🔧 Mantenimiento

### Si ITAD Cambia la API

El código está modularizado en `modules/itad_hunter.py`. Cambios comunes:

**Cambio de URL:**
```python
self.base_url = "https://api.isthereanydeal.com"  # Actualizar aquí
```

**Nuevo formato de respuesta:**
```python
def _extraer_info_juego(self, item, deal, tienda_id):
    # Actualizar parseo aquí
```

**Nueva tienda:**
```python
self.tiendas_map['nueva_tienda'] = {
    'nombre': 'Nombre Display',
    'emoji': '🟡'
}
```

---

## 💡 Mejoras Futuras

### 1. Cache de Precios
Guardar precios históricos para detectar tendencias.

### 2. Alertas por Juego Específico
Notificar cuando un juego de wishlist está gratis.

### 3. Comparación de Precios
Mostrar precio normal vs gratis para contexto.

### 4. Estadísticas
- ¿Qué tienda tiene más juegos gratis?
- ¿Cuál es la duración promedio?

---

## 🆘 Troubleshooting

**"No se encontraron juegos gratis"**
- Normal si no hay ofertas activas
- ITAD necesita que el juego tenga precio = $0.00 exacto

**"Timeout en [tienda]"**
- ITAD puede estar lento
- El script continúa con otras tiendas

**"Error al extraer info"**
- ITAD cambió formato de respuesta
- Revisar `_extraer_info_juego()`

**"Duplicados con Epic Hunter"**
- Epic Games aparece en ambos
- La deduplicación prioriza Epic Hunter directo

---

## 📚 Referencias

- **ITAD API v2:** https://docs.isthereanydeal.com/api/v2/
- **ITAD Website:** https://isthereanydeal.com
- **Tiendas soportadas:** https://isthereanydeal.com/about/partners/

---

**Última actualización:** Diciembre 2024  
**Versión HunDea:** v2.5.0
