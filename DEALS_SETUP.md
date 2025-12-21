# 🚀 Setup Rápido - Canal de Ofertas (#gamedeals)

## ⚡ Setup en 5 Minutos

### 1️⃣ Crear Canal en Discord (1 min)

**En tu servidor de Discord:**

1. Click derecho en la categoría donde quieres el canal
2. **Create Channel**
3. Configuración:
   ```
   Nombre: gamedeals
   Tipo: Text Channel
   Tema: 💰 Ofertas con 70%+ descuento en juegos de calidad (3.6+)
   ```
4. Click **Create Channel**

**Permisos recomendados:**
- ✅ Ver canal (todos)
- ✅ Leer historial de mensajes (todos)
- ❌ Enviar mensajes (solo bot/mods)
- ❌ Reaccionar (todos, opcional)

---

### 2️⃣ Crear Webhook (1 min)

**En el canal recién creado:**

1. Click en ⚙️ (Settings del canal)
2. **Integrations** → **Webhooks**
3. **New Webhook**
4. Configurar:
   ```
   Nombre: HunDea Deals Bot
   Avatar: (opcional, sube una imagen de descuento 💰)
   ```
5. **Copy Webhook URL**
6. **Save Changes**

**URL copiada:**
```
https://discord.com/api/webhooks/1234567890/ABC...XYZ
```

---

### 3️⃣ Crear Rol para Menciones (2 min)

**Opcional pero recomendado:**

1. Server Settings → **Roles**
2. **Create Role**
3. Configurar:
   ```
   Nombre: GameDeals
   Color: Naranja/Amarillo (#FFA500)
   Permisos: Default
   ```
4. Habilitar: **Mentionable**
5. **Save Changes**
6. Click derecho en el rol → **Copy ID**

**ID copiado:**
```
1234567890123456
```

---

### 4️⃣ Actualizar config.json (1 min)

**Edita tu config.json local:**

```json
{
  "webhook_premium": "https://discord.com/api/webhooks/...",
  "webhook_bajos": "https://discord.com/api/webhooks/...",
  "webhook_weekends": "https://discord.com/api/webhooks/...",
  "webhook_deals": "https://discord.com/api/webhooks/1234567890/ABC...XYZ",
  "rawg_api_key": "tu_key_aqui",
  "enviar_discord": true,
  "rol_id": "...",
  "rol_deals": "1234567890123456",
  "deals_descuento_minimo": 70,
  "deals_score_minimo": 3.6
}
```

**Parámetros nuevos:**
- `webhook_deals`: URL del webhook del canal #gamedeals
- `rol_deals`: ID del rol a mencionar (opcional)
- `deals_descuento_minimo`: Porcentaje mínimo (70 = 70%)
- `deals_score_minimo`: Score mínimo (3.6 = buena calidad)

---

### 5️⃣ Test Local (30 seg)

**Verifica que funciona:**

```bash
python test_deals.py
```

**Resultado esperado:**
```
💰 QUICK TEST - Sistema de Ofertas con Descuento
⚙️  Configuración:
   • Descuento mínimo: 70%
   • Score mínimo: 3.6/5.0

💰 Buscando ofertas...

✨ ¡Encontradas X oferta(s)!

1. 💰 Witcher 3: Wild Hunt
   🏪 🟣 GOG
   💸 ~~$49.99~~ → $9.99 (-80%)
   📊 Score: 4.7/5.0 ⭐⭐⭐

🎉 ¡Sistema de ofertas funcionando correctamente!
```

---

## 🌐 GitHub Actions (Opcional)

Si usas GitHub Actions, agrega el secret:

1. GitHub → Tu repo → **Settings**
2. **Secrets and variables** → **Actions**
3. **New repository secret**
4. Configurar:
   ```
   Name: DISCORD_WEBHOOK_DEALS
   Value: https://discord.com/api/webhooks/1234567890/ABC...XYZ
   ```
5. **Add secret**

**Luego actualiza tu workflow** `.github/workflows/hunt-games.yml`:

```yaml
env:
  DISCORD_WEBHOOK: ${{ secrets.DISCORD_WEBHOOK }}
  DISCORD_WEBHOOK2: ${{ secrets.DISCORD_WEBHOOK2 }}
  DISCORD_WEBHOOK3: ${{ secrets.DISCORD_WEBHOOK3 }}
  DISCORD_WEBHOOK_DEALS: ${{ secrets.DISCORD_WEBHOOK_DEALS }}  # 👈 NUEVO
  RAWG_API_KEY: ${{ secrets.RAWG_API_KEY }}
```

Y modifica tu script para leer el env var:

```python
# En hundea_v2.py o similar
import os

config = {
    "webhook_premium": os.getenv('DISCORD_WEBHOOK'),
    "webhook_bajos": os.getenv('DISCORD_WEBHOOK2'),
    "webhook_weekends": os.getenv('DISCORD_WEBHOOK3'),
    "webhook_deals": os.getenv('DISCORD_WEBHOOK_DEALS'),  # 👈 NUEVO
    # ...
}
```

---

## 🧪 Verificación Completa

### Checklist de Funcionamiento

- [ ] Canal #gamedeals creado ✅
- [ ] Webhook configurado ✅
- [ ] Rol creado (opcional) ✅
- [ ] config.json actualizado ✅
- [ ] `python test_deals.py` exitoso ✅
- [ ] `python hundea_v2.py` ejecuta sin errores ✅
- [ ] Primera notificación recibida en Discord ✅

---

## 🎯 Ajustar Configuración

### Más Ofertas (Menos Selectivo)

```json
{
  "deals_descuento_minimo": 60,  // 60% en vez de 70%
  "deals_score_minimo": 3.0      // 3.0 en vez de 3.6
}
```

**Resultado:** 2-3x más ofertas diarias

### Menos Ofertas (Muy Selectivo)

```json
{
  "deals_descuento_minimo": 85,  // 85% en vez de 70%
  "deals_score_minimo": 4.5      // 4.5 en vez de 3.6
}
```

**Resultado:** Solo las mejores ofertas (raras)

### Balance Recomendado (Default)

```json
{
  "deals_descuento_minimo": 70,  // Sweet spot
  "deals_score_minimo": 3.6      // Buena calidad
}
```

**Resultado:** 1-3 ofertas diarias de calidad

---

## 💡 Tips y Trucos

### 1. Organizar Canales

Estructura recomendada:

```
📁 🎮 GAMING
   ├─ #gamesdeals (Gratis Premium)
   ├─ #gameslowers (Gratis Bajos)
   ├─ #gamedeals (Ofertas) 👈 NUEVO
   └─ #xfreeweekends (Temporales)
```

### 2. Roles y Menciones

Crea roles separados para cada tipo:

- `@FreeGames` → #gamesdeals
- `@FreeLowers` → #gameslowers
- `@GameDeals` → #gamedeals 👈 NUEVO
- `@FreeWeekends` → #xfreeweekends

**Ventaja:** Usuarios eligen qué notificaciones recibir

### 3. Emojis en Discord

Agrega reacciones automáticas:

```
💰 = Oferta interesante
🔥 = Oferta increíble (90%+)
❤️ = Ya compré
👀 = En mi watchlist
```

---

## 📊 Qué Esperar

### Primera Semana

**Lunes a Viernes:**
- 1-2 ofertas diarias (normal)
- Descuentos 70-80% (común)

**Fin de Semana:**
- 3-5 ofertas (weekend sales)
- Descuentos 75-85% (común)

### Eventos Especiales

**Steam Sales (Verano/Invierno):**
- 5-10 ofertas diarias
- Descuentos 80-90%
- Duración: ~2 semanas

**Black Friday:**
- 10-15 ofertas diarias
- Descuentos 75-95%
- Duración: ~1 semana

**Ofertas Flash:**
- Aleatorias
- Descuentos 85-95%
- Duración: 24-48 horas

---

## ❓ Troubleshooting

### "No recibo notificaciones"

1. **Verifica webhook:**
   ```bash
   # Test manual
   curl -X POST "TU_WEBHOOK_URL" \
     -H "Content-Type: application/json" \
     -d '{"content": "Test de webhook"}'
   ```

2. **Verifica config.json:**
   ```json
   "webhook_deals": "https://discord.com/api/webhooks/..."  // ✅ Correcto
   "webhook_deals": "TU_WEBHOOK_AQUI"  // ❌ Incorrecto (placeholder)
   ```

3. **Ejecuta test:**
   ```bash
   python test_deals.py
   ```

### "Demasiadas/Pocas notificaciones"

Ajusta thresholds en `config.json`:

**Demasiadas:** Sube los valores
```json
"deals_descuento_minimo": 80,  // En vez de 70
"deals_score_minimo": 4.0      // En vez de 3.6
```

**Muy pocas:** Baja los valores
```json
"deals_descuento_minimo": 60,  // En vez de 70
"deals_score_minimo": 3.0      // En vez de 3.6
```

### "Formato de mensaje incorrecto"

Verifica versión de `discord_notifier.py`:

```bash
grep "enviar_oferta_descuento" modules/discord_notifier.py
```

Debe existir la función `enviar_oferta_descuento`.

---

## 🎉 ¡Listo!

Tu canal de ofertas está configurado y listo para usar.

**Próximos pasos:**
1. Monitorear primera semana
2. Ajustar thresholds según preferencia
3. ¡Disfrutar de ofertas increíbles! 💰

---

**Última actualización:** Diciembre 2024  
**Versión:** v2.6.0  
**Tiempo total de setup:** ~5 minutos
