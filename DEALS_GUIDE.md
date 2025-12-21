# 💰 HunDea v2.6 - Sistema de Ofertas con Descuento

## 🎯 Nueva Funcionalidad

HunDea ahora no solo detecta juegos **100% gratis**, sino también **ofertas con descuentos significativos** en juegos de calidad.

---

## 🏪 Canal Nuevo: #gamedeals

### Criterios de Selección
1. **Descuento mínimo:** 70% (configurable)
2. **Score mínimo:** 3.6/5.0 (configurable)
3. **Solo juegos de calidad verificada**

### ¿Por qué 70% y 3.6?
- **70% de descuento:** Asegura que sean ofertas realmente significativas
- **3.6 de score:** Filtra juegos de calidad demostrada (entre Premium y Bajos)
- **Resultado:** Solo las mejores ofertas en tu Discord

---

## ⚙️ Configuración

### 1. Crear el Canal en Discord
```
Nombre: #gamedeals
Descripción: 💰 Ofertas con descuento (70%+) en juegos de calidad (3.6+)
Permisos: Igual que #gamesdeals
```

### 2. Crear el Webhook
1. Settings del canal → Integrations → Webhooks
2. New Webhook
3. Nombre: "HunDea Deals"
4. Copy Webhook URL

### 3. Actualizar config.json

```json
{
  "webhook_premium": "...",
  "webhook_bajos": "...",
  "webhook_weekends": "...",
  "webhook_deals": "TU_WEBHOOK_DE_DEALS_AQUI",
  "rawg_api_key": "...",
  "enviar_discord": true,
  "rol_id": "...",
  "rol_deals": "TU_ROL_DEALS_AQUI",
  "deals_descuento_minimo": 70,
  "deals_score_minimo": 3.6
}
```

### 4. GitHub Secrets (si usas Actions)
```
DISCORD_WEBHOOK_DEALS = tu_webhook_aqui
```

---

## 📊 Formato del Mensaje

### Ejemplo de Notificación
```
💰 ¡GRAN DESCUENTO (-85%)! @GameDeals

💸 Cyberpunk 2077
🏪 🔵 Steam
💰 ~~$59.99~~ → **$8.99**
📊 Descuento: -85%
📊 Score HunDea: 4.2/5.0 ⭐⭐⭐
⭐ Reviews: 82% Positivas (350,000 reviews)
⏰ Disponible hasta: Viernes, 25 de diciembre...
🔗 [Ir a la oferta]
```

---

## 🎮 Casos de Uso

### Juego Gratis vs Oferta

#### Juego Gratis (Score 4.2)
- Canal: **#gamesdeals** (Premium)
- Precio: $0.00
- Acción: "¡GRATIS!"

#### Mismo Juego con 80% Descuento
- Canal: **#gamedeals** (Deals)
- Precio: ~~$59.99~~ → $11.99
- Acción: "¡GRAN DESCUENTO!"

### ¿Cuándo se notifica?

✅ **SÍ se notifica:**
- Witcher 3: -80%, Score 4.5 → ✅
- Dark Souls III: -75%, Score 4.2 → ✅
- Sekiro: -70%, Score 4.7 → ✅

❌ **NO se notifica:**
- Bad Game: -90%, Score 2.1 → ❌ (Score bajo)
- Good Game: -50%, Score 4.5 → ❌ (Descuento insuficiente)
- Amazing Game: -85%, Score 3.5 → ❌ (Score justo por debajo)

---

## 🔧 Configuración Avanzada

### Ajustar Descuento Mínimo

```json
"deals_descuento_minimo": 80  // Solo 80%+
```

Opciones recomendadas:
- **60%**: Más ofertas, menos selectivo
- **70%**: Balance (RECOMENDADO)
- **80%**: Muy selectivo, pocas ofertas
- **90%**: Extremadamente raro

### Ajustar Score Mínimo

```json
"deals_score_minimo": 4.0  // Solo juegos excelentes
```

Opciones recomendadas:
- **3.0**: Incluye juegos aceptables
- **3.6**: Balance (RECOMENDADO)
- **4.0**: Solo muy buenos juegos
- **4.5**: Solo obras maestras

---

## 📈 Estadísticas Esperadas

### Frecuencia de Ofertas

**Con configuración por defecto (70%, 3.6):**
- **Diarias:** 1-3 ofertas
- **Semanales:** 8-15 ofertas
- **Mensuales:** 40-80 ofertas

**Tiendas más activas:**
1. Steam (sales diarias/semanales)
2. GOG (frecuentes ofertas)
3. Humble Store (bundles + ofertas)
4. Epic Games (mega sales)

---

## 🧪 Testing

### Test Local
```bash
python hundea_v2.py
```

Deberías ver:
```
💰 Buscando OFERTAS con 70%+ descuento...
   🏪 Revisando Steam...
      ✅ Encontrados 2 juego(s) con 70%+ descuento
   🏪 Revisando GOG...
      ✅ Encontrados 1 juego(s) con 70%+ descuento

✨ Total IsThereAnyDeal: 3 juego(s) con descuento únicos

💰 Witcher 3: Wild Hunt
   🏪 GOG | 📊 4.5/5.0 (⭐⭐⭐)
   💸 -80% | $11.99
   ⭐ 95% (450,000 reviews)

📈 Resumen:
   💰 Ofertas Calidad (3.6+): 3 oferta(s)

✅ Oferta enviada: Witcher 3: Wild Hunt (-80%)
```

---

## 🎯 Ventajas del Sistema

### 1. Filtrado Inteligente
- No todas las ofertas son buenas
- Solo notifica ofertas que valen la pena
- Combina descuento + calidad

### 2. Ahorro de Tiempo
- No necesitas buscar ofertas manualmente
- No te pierdes grandes descuentos
- Notificaciones instantáneas

### 3. Ahorro de Dinero
- Compras juegos de calidad con grandes descuentos
- Evitas compras impulsivas de juegos malos
- ROI: Un solo juego justifica el setup

---

## 💡 Casos Reales

### Ejemplo 1: Steam Autumn Sale
```
💰 ¡GRAN DESCUENTO (-80%)!

💸 Red Dead Redemption 2
🏪 Steam
💰 ~~$59.99~~ → $11.99
📊 -80%
📊 Score: 4.6/5.0 ⭐⭐⭐
⭐ 89% Positivas (525,000 reviews)
⏰ Hasta: 3 de diciembre
```

**Ahorro:** $48.00  
**Valor:** Juego AAA por precio indie

### Ejemplo 2: GOG Weekly Deal
```
💰 ¡GRAN DESCUENTO (-85%)!

💸 Cyberpunk 2077
🏪 GOG
💰 ~~$59.99~~ → $8.99
📊 -85%
📊 Score: 4.2/5.0 ⭐⭐⭐
⭐ 82% Positivas (350,000 reviews)
⏰ Sin fecha límite
```

**Ahorro:** $51.00  
**Bonus:** DRM-free en GOG

---

## 🚀 Próximas Mejoras

### En Consideración
- [ ] Alertas por género (RPG, FPS, etc.)
- [ ] Watchlist personalizada
- [ ] Histórico de precios
- [ ] Comparación entre tiendas
- [ ] Predicción de mejores ofertas

---

## ❓ FAQ

**P: ¿Por qué no 100% de ofertas?**  
R: Muchas ofertas pequeñas (10-20%) no son significativas. 70%+ es el sweet spot.

**P: ¿Puedo cambiar los thresholds?**  
R: Sí, edita `config.json`:
```json
"deals_descuento_minimo": 80,  // Tu preferencia
"deals_score_minimo": 4.0      // Tu preferencia
```

**P: ¿Se duplican con juegos gratis?**  
R: No. Los gratis van a #gamesdeals, las ofertas a #gamedeals.

**P: ¿Cuántas ofertas esperaré?**  
R: Con 70%/3.6: ~1-3 diarias, 8-15 semanales.

**P: ¿Puedo desactivarlo?**  
R: Sí, simplemente no configures `webhook_deals` en config.json.

**P: ¿Funciona con todas las tiendas?**  
R: Sí, todas las 13+ tiendas de ITAD están incluidas.

---

## 📞 Soporte

Si tienes problemas:

1. **Verifica config.json:**
   ```json
   "webhook_deals": "https://discord.com/api/webhooks/...",
   "rol_deals": "1234567890",
   "deals_descuento_minimo": 70,
   "deals_score_minimo": 3.6
   ```

2. **Test local:**
   ```bash
   python hundea_v2.py
   ```

3. **Revisa logs:**
   - ¿Se encontraron ofertas?
   - ¿Cumplieron criterios?
   - ¿Se enviaron a Discord?

---

**Versión:** v2.6.0  
**Fecha:** Diciembre 2024  
**Autor:** HunDea Team  
**Licencia:** MIT
