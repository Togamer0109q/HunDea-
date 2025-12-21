# 🎮 HunDea v2 - Multi-Store Free Games Hunter

Bot inteligente que detecta juegos gratis de múltiples tiendas y los clasifica automáticamente por calidad.

## ✨ Características v2.6

✅ **Múltiples tiendas**
- Epic Games Store ✅
- IsThereAnyDeal (Steam, GOG, Humble, Uplay, etc.) 🌟
- 13+ tiendas soportadas vía ITAD
- RAWG para reviews externas ✅

💰 **Sistema de Ofertas** 🆕 NUEVO
- Detecta ofertas con 70%+ descuento
- Solo juegos de calidad (3.6+ score)
- Notificaciones en canal dedicado

✅ **Sistema de puntuación inteligente**
- Reviews de usuarios
- Popularidad
- Metacritic
- Score de 0.0 a 5.0

✅ **4 canales de Discord**
- **Premium** (Score 3.7+): Juegos GRATIS de calidad comprobada
- **Bajos** (Score <3.7): Juegos GRATIS sin reviews o calidad dudosa
- **Deals** (70%+ off, 3.6+ score): Ofertas con descuento 🆕
- **Free Weekends**: Juegos gratis temporalmente

✅ **Automatizado 24/7**
- Se ejecuta cada 3 horas en GitHub Actions
- Cache inteligente (no repite juegos)
- Webhooks seguros

---

## 🚀 Instalación

### 1. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 2. Obtén tu RAWG API Key (IMPORTANTE)

**¿Por qué?** RAWG proporciona reviews y ratings para juegos de todas las tiendas.

1. Ve a: https://rawg.io/apidocs
2. Click en **Get API Key** (arriba derecha)
3. Crea cuenta gratis
4. Copia tu API key
5. GitHub Settings → Secrets → **New repository secret**
   - Name: `RAWG_API_KEY`
   - Value: [tu API key]

### 3. Configura los 3 webhooks de Discord

**Canal #gamesdeals (Premium)**
- Juegos GRATIS con score 3.7+ 
- Copiar webhook → GitHub Secret: `DISCORD_WEBHOOK`

**Canal #gameslowers (Bajos)**
- Juegos GRATIS con score <3.7
- Copiar webhook → GitHub Secret: `DISCORD_WEBHOOK2`

**Canal #gamedeals (Ofertas)** 🆕
- Ofertas 70%+ con score 3.6+
- Copiar webhook → GitHub Secret: `DISCORD_WEBHOOK_DEALS`

**Canal #xfreeweekends**
- Free weekends de Steam
- Copiar webhook → GitHub Secret: `DISCORD_WEBHOOK3`

### 3. Configura el rol a mencionar

Obtén el ID del rol en Discord y agrégalo en el workflow.

---

## 🎯 Uso

### Modo local (testing)

```bash
python hundea_v2.py
```

### Modo automático (GitHub Actions)

Se ejecuta solo cada 3 horas. También puedes ejecutarlo manualmente:

1. Ve a **Actions** en GitHub
2. **HunDea v2 - Multi-Store Hunter**
3. **Run workflow**

---

## 📊 Sistema de puntuación

```
Score = Reviews (0-3pts) + Popularidad (0-1.5pts) + Metacritic (0-0.5pts)

4.5 - 5.0 ⭐⭐⭐ Excelente
3.7 - 4.4 ⭐⭐   Muy bueno
2.0 - 3.6 ⭐     Aceptable
0.0 - 1.9 ⚠️     Dudoso
```

**Clasificación:**
- **3.7+** → Canal Premium
- **<3.7** → Canal Bajos

---

## 📁 Estructura del proyecto

```
HunDeaBot/
├── hundea_v2.py              ← Script principal v2
├── hundea.py                 ← Script v1 (legacy)
├── modules/
│   ├── epic_hunter.py        ← Detector de Epic Games
│   ├── steam_hunter.py       ← Detector de Steam
│   ├── scoring.py            ← Sistema de puntuación
│   └── discord_notifier.py   ← Notificaciones a Discord
├── config.json               ← Configuración
├── cache.json                ← Cache de juegos anunciados
├── requirements.txt          ← Dependencias
└── .github/workflows/
    └── hunt-games.yml        ← Automatización

```

---

## 🎨 Preview de mensajes

### Canal Premium
```
🎮 ¡JUEGO GRATIS de CALIDAD! @FreeGame!

⭐⭐⭐ Hogwarts Legacy
🏪 Tienda: Epic Games
📊 Score HunDea: 4.8/5.0
⭐ 92% Positivas (120,000 reviews)
⏰ Disponible hasta: miércoles, 18 de diciembre...
```

### Canal Bajos
```
⚠️ Juego gratis (calidad no verificada)

⚠️ Unknown Indie Game
🏪 Tienda: Itch.io
📊 Score HunDea: 2.1/5.0
📊 Insuficientes reviews
```

### Canal Free Weekends
```
⏰ ¡GRATIS ESTE FIN DE SEMANA!

⏰ GTA V
🏪 Tienda: Steam
📊 Score HunDea: 4.5/5.0
⭐ 88% Positivas (500,000 reviews)
🕒 Solo hasta el domingo 23:59
```

---

## 🔧 Próximas características v3

- [x] Soporte para GOG (vía ITAD)
- [x] Soporte para Itch.io (vía ITAD)
- [x] Soporte para Humble Store (vía ITAD)
- [x] Soporte para Ubisoft Connect (vía ITAD)
- [ ] Soporte para Prime Gaming
- [x] Integración con RAWG API para más reviews
- [ ] Metacritic scraping
- [ ] Filtros personalizados por usuario
- [ ] Estadísticas mensuales

---

## 📝 Changelog

### v2.6.0 (Actual)
- 💰 Sistema de ofertas con descuento (70%+, 3.6+)
- 🆕 Nuevo canal #gamedeals para ofertas
- 🌟 IsThereAnyDeal API integrado (13+ tiendas)
- ✅ Soporte multi-tienda (Epic + ITAD)
- ✅ Sistema de puntuación inteligente
- ✅ 4 canales de Discord
- ✅ Arquitectura modular

### v2.5.0
- 🌟 IsThereAnyDeal API integrado (13+ tiendas)
- ✅ Soporte multi-tienda (Epic + ITAD)
- ✅ Sistema de puntuación inteligente
- ✅ 3 canales de Discord
- ✅ Arquitectura modular
- ✅ Free Weekends de Steam

### v2.0.0
- ✅ Soporte multi-tienda (Epic + Steam)
- ✅ Sistema de puntuación inteligente
- ✅ 3 canales de Discord
- ✅ Arquitectura modular
- ✅ Free Weekends de Steam

### v1.0.0
- ✅ Soporte para Epic Games
- ✅ Notificaciones a Discord
- ✅ Cache de juegos
- ✅ Automatización GitHub Actions

---

Creado con ❤️ para la comunidad gamer
