# 🔐 GitHub Secrets - Setup Completo

## 📋 Secrets Necesarios

Tu workflow de GitHub Actions necesita estos secrets configurados:

### ✅ Secrets Actuales

| Secret Name | Descripción | Canal Discord |
|-------------|-------------|---------------|
| `DISCORD_WEBHOOK` | Webhook premium | **xpremium** ⭐ |
| `DISCORD_WEBHOOK2` | Webhook bajos | **xgameslowers** ⚠️ |
| `DISCORD_WEBHOOK3` | Webhook weekends | **xfreeweekends** 🆓 |
| `DISCORD_WEBHOOK_STATUS` | Webhook status | **xestados** 📊 |
| `DISCORD_WEBHOOK_ALL` | Webhook todos | **xalldeals** 💎 |
| `RAWG_API_KEY` | API key de RAWG | - |

### 🆕 Nuevo Secret para v2.6

| Secret Name | Descripción | Canal Discord |
|-------------|-------------|---------------|
| **`HUN_DEA_DESCUENTOS`** | Webhook descuentos | **xdescuentos** 💰 |

---

## 🚀 Cómo Agregar el Nuevo Secret

### Paso 1: Ve a Settings
1. Abre tu repositorio en GitHub
2. Click en **Settings** (⚙️)

### Paso 2: Navega a Secrets
1. En el menú lateral: **Secrets and variables**
2. Click en **Actions**

### Paso 3: Crear el Secret
1. Click en **New repository secret**
2. Llenar:
   ```
   Name: HUN_DEA_DESCUENTOS
   Secret: [Pega el webhook de tu canal xdescuentos]
   ```
3. Click **Add secret** ✅

---

## 📝 Obtener el Webhook de Discord

### En el canal #xdescuentos:

1. Click en ⚙️ (Settings del canal)
2. **Integrations** → **Webhooks**
3. Si ya existe "El de los carnotes Hundea":
   - Click en el webhook
   - **Copy Webhook URL**
4. Si no existe:
   - **New Webhook**
   - Nombre: "HunDea Descuentos Bot"
   - **Copy Webhook URL**

**URL tiene este formato:**
```
https://discord.com/api/webhooks/1234567890/ABC...XYZ
```

---

## ✅ Verificar Secrets Configurados

### Lista Completa de Secrets

Deberías tener **7 secrets** en total:

```
✅ DISCORD_WEBHOOK           → xpremium
✅ DISCORD_WEBHOOK2          → xgameslowers
✅ DISCORD_WEBHOOK3          → xfreeweekends
✅ DISCORD_WEBHOOK_STATUS    → xestados
✅ DISCORD_WEBHOOK_ALL       → xalldeals
✅ HUN_DEA_DESCUENTOS        → xdescuentos 🆕
✅ RAWG_API_KEY              → API de RAWG
```

### Verificación Visual en GitHub

En **Settings → Secrets and variables → Actions** deberías ver:

```
Repository secrets (7)

DISCORD_WEBHOOK              Updated X days ago
DISCORD_WEBHOOK2             Updated X days ago
DISCORD_WEBHOOK3             Updated X days ago
DISCORD_WEBHOOK_ALL          Updated X days ago
DISCORD_WEBHOOK_STATUS       Updated X days ago
HUN_DEA_DESCUENTOS           Updated just now 🆕
RAWG_API_KEY                 Updated X days ago
```

---

## 🔄 Roles de Discord

También necesitas actualizar el rol para menciones de descuentos.

### Obtener ID del Rol

1. **Settings del servidor** → **Roles**
2. Busca el rol para descuentos (ejemplo: @GameDeals)
3. Click derecho → **Copy ID**

### Actualizar Workflow

En `.github/workflows/hunt-games.yml`, busca:

```python
"rol_deals": "TU_ROL_DESCUENTOS_AQUI",
```

Reemplaza con el ID que copiaste:

```python
"rol_deals": "1234567890123456",
```

---

## 🧪 Test del Setup

### Test Manual del Workflow

1. Ve a **Actions** en GitHub
2. Selecciona **HunDea v2 - Multi-Store Hunter**
3. Click **Run workflow** dropdown
4. Click **Run workflow** (verde)

### Verificar Logs

Deberías ver en los logs:

```
✅ config.json creado con 6 webhooks
✅ RAWG API key configurada
✅ Webhook de descuentos configurado

🎮 HunDea v2 - Multi-Store Free Games Hunter
======================================

💰 Buscando OFERTAS con 70%+ descuento...
   🏪 Revisando Steam...
   🏪 Revisando GOG...
   [...]

📈 Resumen:
   ⭐ Premium: X juego(s)
   ⚠️  Bajos: X juego(s)
   💰 Ofertas Calidad: X oferta(s) 🆕
```

---

## 🎯 Configuración Local vs GitHub

### Configuración Local (config.json)

Para desarrollo local, tu `config.json` debería verse así:

```json
{
  "webhook_premium": "https://discord.com/api/webhooks/...",
  "webhook_bajos": "https://discord.com/api/webhooks/...",
  "webhook_weekends": "https://discord.com/api/webhooks/...",
  "webhook_deals": "https://discord.com/api/webhooks/...",
  "webhook_todos": "https://discord.com/api/webhooks/...",
  "webhook_status": "https://discord.com/api/webhooks/...",
  "rawg_api_key": "0ceccc066f9e444dac0b7b7f25a518f0",
  "enviar_discord": true,
  "rol_premium": "1449938401649496176",
  "rol_bajos": "1449942355997360259",
  "rol_weekends": "1449942459894202369",
  "rol_deals": "TU_ROL_AQUI",
  "rol_todos": "1451738702262046750",
  "deals_descuento_minimo": 70,
  "deals_score_minimo": 3.6
}
```

### GitHub Actions (Automático)

El workflow crea automáticamente el `config.json` usando los secrets.

**No necesitas subir config.json al repo** (ya está en .gitignore)

---

## ❓ Troubleshooting

### "Secret not found: HUN_DEA_DESCUENTOS"

**Solución:**
1. Verifica que el nombre sea exacto: `HUN_DEA_DESCUENTOS`
2. No spaces, no typos
3. Espera ~5 minutos después de crear el secret

### "Webhook de descuentos no configurado"

**Solución:**
1. Verifica que el secret tenga un webhook válido
2. Formato correcto: `https://discord.com/api/webhooks/...`

### "No se envían notificaciones a xdescuentos"

**Solución:**
1. Verifica que el bot tenga permisos en el canal
2. Test el webhook manualmente:
   ```bash
   curl -X POST "TU_WEBHOOK" \
     -H "Content-Type: application/json" \
     -d '{"content": "Test"}'
   ```

---

## 📊 Flujo Completo

```
GitHub Actions ejecuta
        ↓
Lee secrets de GitHub
        ↓
Crea config.json automáticamente
        ↓
Ejecuta hundea_v2.py
        ↓
Busca ofertas con ITAD
        ↓
Filtra por 70%+ y 3.6+
        ↓
Envía a Discord via HUN_DEA_DESCUENTOS
        ↓
Notificación en #xdescuentos 💰
```

---

## ✅ Checklist Final

### Pre-Deploy
- [ ] Secret `HUN_DEA_DESCUENTOS` creado en GitHub
- [ ] Webhook de #xdescuentos copiado
- [ ] Rol de descuentos creado (opcional)
- [ ] ID del rol copiado (si aplica)

### Deploy
- [ ] Workflow `.github/workflows/hunt-games.yml` actualizado
- [ ] Commit y push realizados
- [ ] Test manual ejecutado en Actions
- [ ] Logs verificados sin errores

### Post-Deploy
- [ ] Primera notificación recibida en #xdescuentos
- [ ] Formato del mensaje correcto
- [ ] Score y descuento mostrados correctamente
- [ ] Enlaces funcionan

---

## 🎉 ¡Listo!

Con el secret `HUN_DEA_DESCUENTOS` configurado, tu bot automáticamente:

✅ Buscará ofertas cada 3 horas  
✅ Filtrará por 70%+ descuento  
✅ Verificará calidad (3.6+ score)  
✅ Notificará en #xdescuentos  
✅ TODO sin intervención manual  

---

**Última actualización:** Diciembre 2024  
**Versión:** v2.6.0  
**Próxima ejecución automática:** Cada 3 horas
