# 🎯 Cambios v2.7.1 - Mejoras de Ofertas

## ✨ Cambios Implementados

### 1. ✅ Workflow Actualizado
- Precio máximo: $10 → **$20 USD**
- Score mínimo: 3.6 → **2.5**
- Más ofertas detectadas en GitHub Actions

### 2. 🎁 Ofertas 100% = GRATIS
- Las ofertas con 100% descuento ahora van al **canal de juegos GRATIS**
- Ya no aparecen en el canal de descuentos
- Ejemplo: Viewfinder 100% off → Canal #premium o #gameslowers

### 3. 🖼️ Imágenes Agregadas
- Discord notifier ahora soporta `imagen_url` (CheapShark)
- Las ofertas mostrarán la imagen del juego
- Funciona con ambos campos: `imagen` y `imagen_url`

---

## 📊 Resultados Esperados

**Antes:**
- Ofertas 100% iban a canal #descuentos ❌
- Sin imágenes en ofertas de CheapShark ❌
- GitHub Actions con filtros muy restrictivos ❌

**Ahora:**
- Ofertas 100% van a canal #premium/#gameslowers ✅
- Con imágenes en todas las ofertas ✅  
- Filtros más permisivos (20 USD, score 2.5) ✅

---

## 🧪 Próximas Pruebas

1. Ejecutar localmente:
```bash
python hundea_v2.py
```

2. Verificar:
   - [ ] Viewfinder (100%) va a canal gratis
   - [ ] Ofertas tienen imágenes
   - [ ] Se detectan más ofertas (40%+, <$20)

3. Commit y push a GitHub

---

## 🚀 Para Commit

Archivos modificados:
- `hundea_v2.py` - Separación de ofertas 100%
- `modules/discord_notifier.py` - Soporte imagen_url
- `.github/workflows/hunt-games.yml` - Config actualizada

Mensaje de commit:
```
🎁 v2.7.1 - Ofertas 100% como GRATIS + Imágenes

- Move 100% discount deals to free games channel
- Add image support for all deals (imagen_url)
- Update GitHub Actions config: $20 max, score 2.5
- More permissive filters for better deal detection
```
