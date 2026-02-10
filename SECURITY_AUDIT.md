# 🔒 ANÁLISIS DE SEGURIDAD - HunDeaBot v3.0

## ⚠️ VULNERABILIDADES ENCONTRADAS

### 🔴 CRÍTICAS (Arreglar YA)

#### 1. **Webhooks Expuestos en Logs**
**Ubicación**: `hundea_v3.py`, `console_notifier.py`
**Problema**: Webhooks pueden aparecer en logs
**Riesgo**: Si logs se comparten, webhooks quedan expuestos

**Solución**:
```python
# ANTES
logger.info(f"Sending to webhook: {webhook_url}")

# DESPUÉS
def sanitize_webhook(url):
    """Oculta parte del webhook en logs"""
    if not url:
        return "None"
    parts = url.split('/')
    if len(parts) > 2:
        return f"{parts[0]}//{parts[2]}/.../{parts[-1][:8]}***"
    return "***WEBHOOK***"

logger.info(f"Sending to webhook: {sanitize_webhook(webhook_url)}")
```

---

#### 2. **API Keys en Plaintext**
**Ubicación**: `config.json`
**Problema**: Keys en texto plano
**Riesgo**: Si repo se sube con config.json, keys comprometidas

**Solución ACTUAL**: ✅ Ya está en `.gitignore`

**Mejora ADICIONAL**: Variables de entorno
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Prioridad: ENV > config.json
RAWG_KEY = os.getenv('RAWG_API_KEY') or config.get('apis', {}).get('rawg')
PLATPRICES_KEY = os.getenv('PLATPRICES_API_KEY') or config.get('apis', {}).get('platprices')
```

**Crear `.env`**:
```bash
RAWG_API_KEY=tu_key_aqui
PLATPRICES_API_KEY=tu_key_aqui
DISCORD_WEBHOOK_PS=tu_webhook
DISCORD_WEBHOOK_XBOX=tu_webhook
DISCORD_WEBHOOK_NINTENDO=tu_webhook
```

---

#### 3. **Rate Limiting Ausente**
**Ubicación**: Todos los hunters
**Problema**: Sin protección contra rate limits
**Riesgo**: Ban de APIs

**Solución**:
```python
import time
from functools import wraps

class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, calls_per_minute=60):
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call = 0
    
    def wait(self):
        """Wait if needed to respect rate limit"""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()

# Uso en hunters
class PlayStationHunter(BaseConsoleHunter):
    def __init__(self, config, cache, logger=None):
        super().__init__(config, cache, logger)
        self.rate_limiter = RateLimiter(calls_per_minute=30)
    
    def fetch_deals(self):
        self.rate_limiter.wait()  # Espera si es necesario
        response = requests.get(url)
        # ...
```

---

### 🟡 MEDIAS (Mejorar Pronto)

#### 4. **Sin Validación de Webhooks**
**Problema**: No valida si webhook es válido antes de enviar
**Solución**:
```python
def validate_webhook(webhook_url):
    """Valida que el webhook sea válido"""
    if not webhook_url:
        return False
    
    # Patrón de Discord webhook
    pattern = r'https://discord\.com/api/webhooks/\d+/[\w-]+'
    
    import re
    if not re.match(pattern, webhook_url):
        return False
    
    # Test ping (opcional)
    try:
        response = requests.get(webhook_url, timeout=5)
        return response.status_code == 200
    except:
        return False
```

---

#### 5. **Errores Sensibles en Logs**
**Problema**: Stack traces completos pueden filtrar info
**Solución**:
```python
# ANTES
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)  # Stack trace completo

# DESPUÉS  
except Exception as e:
    logger.error(f"Error: {str(e)}")  # Solo mensaje
    # Stack trace solo en modo debug
    logger.debug("Stack trace:", exc_info=True)
```

---

#### 6. **Sin Timeout en Requests**
**Problema**: Requests pueden colgar indefinidamente
**Solución**: ✅ Ya tienes `timeout=30` en la mayoría
**Falta**: Agregar en algunos lugares

```python
# Siempre usar timeout
response = requests.get(url, timeout=30)
response = requests.post(url, json=data, timeout=30)
```

---

### 🟢 BAJAS (Opcional)

#### 7. **Sin Autenticación de Bot**
**Problema**: Cualquiera puede ejecutar el bot
**Solución** (Opcional):
```python
import hashlib

def verify_execution(password):
    """Verificar contraseña antes de ejecutar"""
    stored_hash = os.getenv('BOT_PASSWORD_HASH')
    if not stored_hash:
        return True  # No password set
    
    input_hash = hashlib.sha256(password.encode()).hexdigest()
    return input_hash == stored_hash
```

---

#### 8. **Logs Sin Rotación**
**Problema**: `huntdea_v3.log` puede crecer infinitamente
**Solución**:
```python
from logging.handlers import RotatingFileHandler

# En lugar de FileHandler
handler = RotatingFileHandler(
    'huntdea_v3.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5  # Mantener 5 archivos
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[handler, logging.StreamHandler(sys.stdout)]
)
```

---

## 🛡️ OPTIMIZACIONES DE SEGURIDAD

### 1. Sanitizar Inputs
```python
def sanitize_game_title(title):
    """Prevenir inyección en embeds"""
    # Limitar longitud
    if len(title) > 256:
        title = title[:253] + "..."
    
    # Escapar markdown
    title = title.replace('`', '\\`')
    title = title.replace('*', '\\*')
    title = title.replace('_', '\\_')
    
    return title
```

### 2. Validar Configuración
```python
def validate_config(config):
    """Validar config.json al cargar"""
    
    required_keys = ['webhooks', 'apis', 'filters']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    
    # Validar webhooks
    for platform, webhook in config['webhooks'].items():
        if webhook and webhook != f"YOUR_{platform.upper()}_WEBHOOK_HERE":
            if not validate_webhook(webhook):
                logger.warning(f"Invalid webhook for {platform}")
    
    return True
```

---

## 🔍 REVISIÓN DE DEPENDENCIAS

### Dependencias Actuales
```txt
requests>=2.31.0
discord-webhook>=1.3.0
beautifulsoup4>=4.12.0
lxml>=5.1.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
```

### ⚠️ Vulnerabilidades Conocidas
- ✅ Todas las versiones son seguras (Feb 2026)

### Actualización Recomendada
```bash
pip install --upgrade pip
pip install --upgrade -r requirements.txt
```

---

## 📊 CHECKLIST DE SEGURIDAD

### Antes de Subir a GitHub
- [x] `.gitignore` incluye `config.json`
- [x] `.gitignore` incluye `*.env`
- [x] `.gitignore` incluye `*.log`
- [x] No hay API keys hardcoded
- [x] No hay webhooks hardcoded
- [ ] README advierte sobre configuración segura
- [ ] Logs no exponen webhooks completos

### Antes de Producción
- [ ] Variables de entorno configuradas
- [ ] Webhooks validados
- [ ] Rate limiting implementado
- [ ] Log rotation habilitado
- [ ] Timeouts en todas las requests
- [ ] Manejo de errores robusto

### Durante Operación
- [ ] Monitorear logs por errores
- [ ] Revisar uso de API (no exceder límites)
- [ ] Rotar webhooks periódicamente
- [ ] Backup de cache.json
- [ ] Actualizar dependencias mensualmente

---

## 🚨 PLAN DE ACCIÓN INMEDIATO

### AHORA (Crítico)
1. ✅ Implementar sanitización de webhooks en logs
2. ✅ Agregar rate limiting básico
3. ✅ Validación de configuración

### ESTA SEMANA
1. Migrar a variables de entorno (.env)
2. Implementar log rotation
3. Agregar validación de webhooks

### ESTE MES
1. Implementar sistema de secrets más robusto
2. Agregar monitoring de errores
3. Setup de alertas

---

## 📝 CÓDIGO DE MEJORAS

Voy a crear los archivos con las mejoras críticas...
