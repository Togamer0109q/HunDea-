# ?? HunDea v3 - Multi-Store Free Games Hunter

Bot inteligente que detecta juegos gratis de m?ltiples tiendas y los clasifica autom?ticamente por calidad.

## ? Caracter?sticas v3.0

? **M?ltiples tiendas**
- Epic Games Store ?
- IsThereAnyDeal (Steam, GOG, Humble, Ubisoft, etc.) ??
- CheapShark (13+ tiendas adicionales) ??
- Xbox Store (gratis + deals) ??
- PlayStation Store (deals) ??
- Nintendo eShop (deals) ??
- RAWG para reviews externas ?

?? **Sistema de Ofertas** ??
- Detecta ofertas con **30%+** descuento (m?x **99%**)
- **100%** se clasifica como GRATIS autom?ticamente
- Solo juegos de calidad (score m?nimo configurable)

? **Sistema de puntuaci?n inteligente**
- Reviews de usuarios
- Popularidad
- Metacritic
- Score de 0.0 a 5.0

? **4 canales de Discord (principales)**
- **Premium** (Score 3.5+): Juegos GRATIS de calidad comprobada
- **Bajos** (Score <3.5): Juegos GRATIS sin reviews o calidad dudosa
- **Deals** (30%+ off, score configurable): Ofertas con descuento
- **Free Weekends**: Juegos gratis temporalmente

? **Automatizado 24/7**
- Se ejecuta cada 3 horas en GitHub Actions
- Cache inteligente (no repite juegos)
- Webhooks seguros

---

## ?? Instalaci?n

### 1. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 2. Obt?n tu RAWG API Key (IMPORTANTE)

**?Por qu??** RAWG proporciona reviews y ratings para juegos de todas las tiendas.

1. Ve a: https://rawg.io/apidocs
2. Click en **Get API Key** (arriba derecha)
3. Crea cuenta gratis
4. Copia tu API key
5. GitHub Settings ? Secrets ? **New repository secret**
   - Name: `RAWG_API_KEY`
   - Value: [tu API key]

### 3. Configura los webhooks de Discord

**Canal #gamesdeals (Premium)**
- Juegos GRATIS con score 3.5+
- Copiar webhook ? GitHub Secret: `DISCORD_WEBHOOK`

**Canal #gameslowers (Bajos)**
- Juegos GRATIS con score <3.5
- Copiar webhook ? GitHub Secret: `DISCORD_WEBHOOK2`

**Canal #gamedeals (Ofertas)**
- Ofertas 30%+ con score m?nimo configurable
- Copiar webhook ? GitHub Secret: `HUN_DEA_DESCUENTOS`

**Canal #xfreeweekends**
- Free weekends de Steam
- Copiar webhook ? GitHub Secret: `DISCORD_WEBHOOK3`

**Opcionales**
- Canal #allgames (todos): `DISCORD_WEBHOOK_ALL`
- Canal #status (workflow): `DISCORD_WEBHOOK_STATUS`

---

## ?? Uso

### Modo local (testing)

```bash
python hundea_v3.py
```

### Modo autom?tico (GitHub Actions)

Se ejecuta solo cada 3 horas. Tambi?n puedes ejecutarlo manualmente:

1. Ve a **Actions** en GitHub
2. **HunDea v3 - Multi-Store Hunter**
3. **Run workflow**

---

## ?? Sistema de puntuaci?n

```
Score = Reviews (0-3pts) + Popularidad (0-1.5pts) + Metacritic (0-0.5pts)

4.5 - 5.0 ??? Excelente
3.5 - 4.4 ??   Muy bueno
2.0 - 3.4 ?     Aceptable
0.0 - 1.9 ??     Dudoso
```

**Clasificaci?n:**
- **3.5+** ? Canal Premium
- **<3.5** ? Canal Bajos

---

## ?? Estructura del proyecto

```
HunDeaBot/
??? hundea_v3.py              ? Script principal v3
??? hundea_v2.py              ? Script principal v2 (compatibilidad)
??? hundea.py                 ? Script v1 (legacy)
??? modules/
?   ??? epic_hunter.py        ? Detector de Epic Games
?   ??? steam_hunter.py       ? Detector de Steam + Free Weekends
?   ??? xbox_hunter.py        ? Xbox Store (gratis + deals)
?   ??? nintendo_hunter.py    ? Nintendo eShop (gratis + deals)
?   ??? platprices_hunter.py  ? PlayStation Store (deals)
?   ??? scoring.py            ? Sistema de puntuaci?n
?   ??? discord_notifier.py   ? Notificaciones a Discord
??? config.json               ? Configuraci?n
??? cache.json                ? Cache de juegos anunciados
??? requirements.txt          ? Dependencias
??? .github/workflows/
    ??? hunt-games.yml        ? Automatizaci?n

```

---

## ?? Preview de mensajes

### Canal Premium
```
?? ?JUEGO GRATIS de CALIDAD! @FreeGame!

??? Hogwarts Legacy
?? Tienda: Epic Games
?? Score HunDea: 4.8/5.0
? 92% Positivas (120,000 reviews)
? Disponible hasta: mi?rcoles, 18 de diciembre...
```

### Canal Bajos
```
?? Juego gratis (calidad no verificada)

?? Unknown Indie Game
?? Tienda: Itch.io
?? Score HunDea: 2.1/5.0
?? Insuficientes reviews
```

### Canal Free Weekends
```
? ?GRATIS ESTE FIN DE SEMANA!

? GTA V
?? Tienda: Steam
?? Score HunDea: 4.5/5.0
? 88% Positivas (500,000 reviews)
?? Solo hasta el domingo 23:59
```

---

## ?? Pr?ximas caracter?sticas

- [ ] Soporte para Prime Gaming
- [ ] Metacritic scraping
- [ ] Filtros personalizados por usuario
- [ ] Estad?sticas mensuales

---

## ?? Changelog

### v3.0.0 (Actual)
- ?? Nintendo eShop (gratis + deals)
- ?? Xbox Store (gratis + deals)
- ?? PlayStation Store (deals) con fallback regional
- ?? Ofertas 30-99% (100% se mueve a gratis)
- ? Free Weekends mejorado con filtros anti F2P
- ?? Soporte LATAM (MX) para Steam

### v2.7.0
- ?? Integraci?n de CheapShark API
- ?? 13+ tiendas adicionales (Steam, GOG, Epic, GMG, Fanatical, etc.)
- ?? M?s ofertas detectadas autom?ticamente
- ??? Doble cobertura: ITAD + CheapShark
- ? Reviews de Steam integradas desde CheapShark

### v2.6.0
- ?? Sistema de ofertas con descuento (70%+, 3.6+)
- ?? Nuevo canal #gamedeals para ofertas
- ?? IsThereAnyDeal API integrado (13+ tiendas)
- ? Soporte multi-tienda (Epic + ITAD)
- ? Sistema de puntuaci?n inteligente
- ? 4 canales de Discord
- ? Arquitectura modular

---

Creado con ?? para la comunidad gamer
