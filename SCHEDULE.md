# 🕐 HORARIO DE EJECUCIÓN - HunDeaBot v3.0

## 📅 Configuración Actual

**Inicio:** 12:00 PM (mediodía) hora Colombia  
**Frecuencia:** Cada 3 horas  
**Ejecuciones diarias:** 8 veces

---

## 🇨🇴 Horario Colombia (UTC-5)

| # | Hora Colombia | Descripción |
|---|--------------|-------------|
| 1 | **12:00 PM** | 🌞 Mediodía - Primera ejecución |
| 2 | **3:00 PM**  | 🌤️ Tarde |
| 3 | **6:00 PM**  | 🌆 Atardecer |
| 4 | **9:00 PM**  | 🌙 Noche |
| 5 | **12:00 AM** | 🌃 Medianoche |
| 6 | **3:00 AM**  | 🌌 Madrugada |
| 7 | **6:00 AM**  | 🌅 Amanecer |
| 8 | **9:00 AM**  | ☀️ Mañana |

Luego vuelve a **12:00 PM** y repite el ciclo.

---

## 🌍 Horario UTC (GitHub Actions)

GitHub Actions usa hora UTC, por eso está configurado así:

| Hora Colombia | Hora UTC | Cron |
|---------------|----------|------|
| 12:00 PM | 17:00 (5:00 PM) | `17` |
| 3:00 PM  | 20:00 (8:00 PM) | `20` |
| 6:00 PM  | 23:00 (11:00 PM) | `23` |
| 9:00 PM  | 02:00 (2:00 AM) | `2` |
| 12:00 AM | 05:00 (5:00 AM) | `5` |
| 3:00 AM  | 08:00 (8:00 AM) | `8` |
| 6:00 AM  | 11:00 (11:00 AM) | `11` |
| 9:00 AM  | 14:00 (2:00 PM) | `14` |

**Cron configurado:** `0 2,5,8,11,14,17,20,23 * * *`

---

## 📊 Cobertura del Día

```
          Colombia Time
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
00:00 ════════════════════ 24:00
  │     │     │     │     │
 12AM  6AM  12PM  6PM  12AM
  ●     ●     ●     ●     ●
  
● = Ejecución del bot (8 por día)
```

---

## 🎯 Ventajas de Este Horario

✅ **Cobertura completa 24/7**  
✅ **Primera ejecución a mediodía** (12 PM)  
✅ **Cubre horarios pico de ofertas** (12 PM - 9 PM)  
✅ **Detecta ofertas nocturnas** (12 AM - 9 AM)  
✅ **8 oportunidades diarias** para encontrar juegos/ofertas

---

## 🔄 Ejemplo de Ciclo Semanal

**Lunes:**
- 12:00 PM → Ejecuta ✅
- 3:00 PM → Ejecuta ✅
- 6:00 PM → Ejecuta ✅
- ... continúa cada 3 horas

**Martes, Miércoles, etc:**
- Mismo patrón todos los días
- Sin excepciones (fines de semana incluidos)

---

## ⚙️ Configuración en Código

### Archivo: `.github/workflows/hunt-games.yml`

```yaml
on:
  schedule:
    # Horario Colombia: 12PM, 3PM, 6PM, 9PM, 12AM, 3AM, 6AM, 9AM
    # Horario UTC: 5PM, 8PM, 11PM, 2AM, 5AM, 8AM, 11AM, 2PM
    - cron: '0 2,5,8,11,14,17,20,23 * * *'
```

### Formato Cron Explicado

```
0 2,5,8,11,14,17,20,23 * * *
│ │                    │ │ │
│ │                    │ │ └─ Día de la semana (cualquiera)
│ │                    │ └─── Mes (cualquiera)
│ │                    └───── Día del mes (cualquiera)
│ └────────────────────────── Horas (2, 5, 8, 11, 14, 17, 20, 23 UTC)
└──────────────────────────── Minuto (00)
```

---

## 📝 Notas Importantes

### ⚠️ Hora UTC
GitHub Actions **siempre** usa UTC, no hora local. La conversión ya está hecha en el cron.

### ⏰ Precisión
- Los workflows pueden tener hasta **10 minutos de retraso**
- GitHub no garantiza ejecución exacta al segundo
- Esto es normal y no afecta la funcionalidad

### 🔧 Ejecución Manual
Puedes ejecutar el bot manualmente en cualquier momento:
1. Ve a: **Actions** → **HunDea v3 - Multi-Store Hunter**
2. Click en **Run workflow**
3. Click en **Run workflow** (confirmar)

---

## 📊 Estadísticas Esperadas

Con 8 ejecuciones diarias:

| Métrica | Cantidad |
|---------|----------|
| Ejecuciones/día | 8 |
| Ejecuciones/semana | 56 |
| Ejecuciones/mes | ~240 |
| Juegos detectados/día | 3-8 |
| Ofertas detectadas/día | 30-50 |

---

## 🧪 Probar el Horario

### Ver Próximas Ejecuciones
1. Ve a tu repositorio en GitHub
2. **Actions** → **HunDea v3 - Multi-Store Hunter**
3. Verás la próxima ejecución programada

### Verificar en Logs
Cada ejecución quedará registrada con:
- Hora exacta de ejecución
- Juegos encontrados
- Ofertas detectadas
- Mensajes enviados

---

## 🔄 Cambiar el Horario (Si es Necesario)

Si quieres cambiar el horario en el futuro:

1. Edita `.github/workflows/hunt-games.yml`
2. Modifica la línea del cron
3. Usa: https://crontab.guru/ para ayuda
4. Recuerda: GitHub usa **UTC** (Colombia + 5 horas)

---

**Configuración:** ✅ Completa  
**Estado:** 🟢 Activa después del próximo push  
**Próxima ejecución:** A las 12:00 PM Colombia (17:00 UTC)

Última actualización: 29 de diciembre, 2025
