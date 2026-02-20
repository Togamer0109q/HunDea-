# 🚀 Setup Rápido - HunDea v3

## ✅ Checklist de configuración

### 1. RAWG API Key (5 minutos)

📍 **Página:** https://rawg.io/apidocs

**Pasos:**
1. Click en "Get API Key" (arriba derecha)
2. Crear cuenta (email + contraseña)
3. Verificar email
4. Copiar API key de tu dashboard
5. Ir a GitHub → Settings → Secrets and variables → Actions
6. **New repository secret**
   - Name: `RAWG_API_KEY`
   - Value: [pegar tu key]

---

### 2. Verificar que los 3 webhooks estén configurados

✅ `DISCORD_WEBHOOK` - Canal Premium (#gamesdeals)  
✅ `DISCORD_WEBHOOK2` - Canal Bajos (#gameslowers)  
✅ `DISCORD_WEBHOOK3` - Canal Weekends (#xfreeweekends)

---

### 3. Probar localmente (opcional)

Edita `config.json` local y agrega tu RAWG key:

```json
{
  "webhook_premium": "TU_WEBHOOK",
  "webhook_bajos": "TU_WEBHOOK",
  "webhook_weekends": "TU_WEBHOOK",
  "enviar_discord": false,
  "rol_id": "1449938401649496176",
  "rawg_api_key": "TU_RAWG_KEY_AQUI"
}
```

Luego ejecuta:
```bash
python hundea_v3.py
```

Deberías ver:
```
✅ RAWG API key configurada
🔍 Buscando reviews para: Hogwarts Legacy
   ℹ️ Reviews encontradas en RAWG: 84.2% (15,234 ratings)
⭐⭐⭐ Hogwarts Legacy
   🏪 Epic Games | 📊 4.3/5.0 (Muy bueno)
```

---

### 4. Subir a GitHub

```bash
git add .
git commit -m "🎉 HunDea v3 release"
git push
```

---

### 5. Ejecutar el workflow

1. Ve a Actions en GitHub
2. HunDea v3 - Multi-Store Hunter
3. Run workflow
4. ¡Espera los resultados en Discord! 🎮

---

## ❓ Troubleshooting

**"⚠️ RAWG API key no configurada"**
→ Falta agregar `RAWG_API_KEY` en GitHub Secrets

**"Sin reviews"**
→ RAWG no encontró el juego, o el nombre no coincide

**"Error al consultar Steam"**
→ Normal por ahora, Steam está desactivado temporalmente

---

## 🌟 Novedades v2.5 - IsThereAnyDeal

**¡Ahora con 13+ tiendas soportadas!**

IsThereAnyDeal API ahora está integrado y NO requiere API key adicional.
Busca juegos gratis en:
- Steam
- GOG
- Humble Store
- Epic Games (duplicado con Epic Hunter)
- Itch.io
- Microsoft Store
- Ubisoft Connect
- EA Origin
- Y más...

**Cómo probar ITAD:**

```bash
python test_itad.py
```

Esto te mostrará todos los juegos gratis encontrados en múltiples tiendas.

---

## 🎯 Próximos pasos

Una vez funcionando con Epic + ITAD + RAWG:
- [x] Agregar GOG (vía ITAD) ✅
- [x] Agregar Itch.io bundles (vía ITAD) ✅
- [x] Agregar Humble Store (vía ITAD) ✅
- [ ] Mejorar matching de nombres de juegos
- [ ] Agregar Prime Gaming
- [ ] Sistema de notificaciones por juego específico
