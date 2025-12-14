# 🎮 HunDea - Epic Games Free Hunter

Bot cazador de juegos gratis de Epic Games que envía alertas bonitas a Discord.

## 🚀 Instalación

### 1. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 2. Configura tu webhook de Discord

**¿Cómo obtener un webhook?**

1. Ve a tu servidor de Discord
2. Click derecho en el canal donde quieres las notificaciones
3. **Editar canal** → **Integraciones** → **Webhooks**
4. **Crear webhook** → Copia la URL

**Edita `config.json`:**

```json
{
  "webhook_url": "https://discord.com/api/webhooks/tu_webhook_real_aqui",
  "enviar_discord": true
}
```

⚠️ **Importante:** Cambia `"enviar_discord"` a `true` para activar las notificaciones.

## 🎯 Uso

### Modo básico (solo ver en consola)

```bash
python hundea.py
```

Esto te mostrará los juegos gratis actuales en la terminal.

### Modo Discord (enviar alertas)

1. Asegúrate de tener configurado `config.json` correctamente
2. Ejecuta: `python hundea.py`
3. Las alertas se enviarán automáticamente a Discord

## 📁 Estructura del proyecto

```
HunDeaBot/
├── hundea.py          ← Script principal
├── config.json        ← Configuración (webhook)
├── cache.json         ← Juegos ya anunciados (evita repetidos)
├── requirements.txt   ← Dependencias Python
└── README.md          ← Este archivo
```

## 🔧 Características

✅ Consulta la API oficial de Epic Games  
✅ Detecta juegos 100% gratis  
✅ Envía embeds bonitos a Discord  
✅ Sistema de cache (no repite juegos)  
✅ Fechas en español  
✅ Manejo de errores  

## 🤖 Automatización (próximamente)

Puedes programar HunDea para que se ejecute automáticamente cada X horas usando:

- **Windows:** Programador de tareas
- **Linux/Mac:** Cron jobs
- **GitHub Actions:** Gratis en la nube

## 📝 Notas

- El script NO es interactivo, solo envía alertas cuando encuentra juegos nuevos
- Los juegos ya anunciados se guardan en `cache.json` para no repetirlos
- Puedes ejecutarlo manualmente cuando quieras

## 🐛 Problemas comunes

**"No se encontró config.json"**
- Asegúrate de ejecutar el script desde la carpeta `HunDeaBot`

**"Discord respondió con código XXX"**
- Verifica que tu webhook sea válido
- Asegúrate de que el canal del webhook todavía existe

**"Error al consultar Epic Games"**
- Verifica tu conexión a internet
- Epic puede estar en mantenimiento

## 💡 Próximas versiones

- [ ] Soporte para múltiples webhooks
- [ ] Filtros personalizados (géneros, ratings)
- [ ] Integración con Claude para descripciones mejoradas
- [ ] Panel web para configuración

---

Creado con ❤️ para la comunidad gamer
