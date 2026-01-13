# PropScraper - Multi-Zone Real Estate Data Lake Builder

Sistema completo de scraping para recolectar datos de propiedades inmobiliarias de Argentina de múltiples zonas y operaciones (venta/alquiler).

## 🎯 Características

- **Multi-zona**: Scraping de Capital Federal, Zona Norte GBA, Santa Fe, Córdoba, Mendoza, Entre Ríos
- **Multi-operación**: Captura ventas y alquileres por separado
- **Paginación automática**: Itera sobre todas las páginas disponibles
- **Data Lake**: Almacenamiento en base de datos con versionado
- **Logging detallado**: Monitoreo completo del proceso de scraping
- **CLI intuitiva**: Interfaz de línea de comandos fácil de usar
- **Modo test**: Pruebas rápidas antes de ejecutar scrapes completos

## 📊 Zonas Configuradas

| Zona | Código | Descripción |
|------|--------|-------------|
| Capital Federal | capital_federal | Ciudad Autónoma de Buenos Aires |
| Zona Norte GBA | zona_norte_gba | Zona Norte del Gran Buenos Aires |
| Santa Fe | santa_fe | Provincia de Santa Fe |
| Córdoba | cordoba | Provincia de Córdoba |
| Mendoza | mendoza | Provincia de Mendoza |
| Entre Ríos | entre_rios | Provincia de Entre Ríos |

## 🚀 Inicio Rápido

### Instalación de dependencias

```bash
pip install -r requirements.txt
```

### Uso básico

#### 1. **Test rápido** (Capital Federal, 5 páginas)
```bash
python propscrape/main.py --test
```

#### 2. **Scraping completo** (todas las zonas, todas las páginas)
```bash
python propscrape/main.py
```

#### 3. **Zonas específicas**
```bash
# Solo Capital Federal y Zona Norte
python propscrape/main.py --zones capital_federal zona_norte_gba

# Solo Santa Fe
python propscrape/main.py --zones santa_fe
```

#### 4. **Operaciones específicas**
```bash
# Solo ventas
python propscrape/main.py --operations sale

# Solo alquileres
python propscrape/main.py --operations rent
```

#### 5. **Limitar páginas** (útil para pruebas)
```bash
# Máximo 10 páginas por zona
python propscrape/main.py --max-pages 10

# Test con 3 páginas
python propscrape/main.py --test --max-pages 3
```

#### 6. **Test sin guardar en BD**
```bash
# Prueba rápida sin escribir en la base de datos
python propscrape/main.py --test --no-db
```

#### 7. **Listar zonas disponibles**
```bash
python propscrape/main.py --list-zones
```

## 📋 Ejemplos Comunes

### Generar base de datos inicial
```bash
# Comienza con test rápido
python propscrape/main.py --test

# Si todo funciona, scraping completo
python propscrape/main.py
```

### Actualización periódica
```bash
# Scraping diario de Capital Federal
python propscrape/main.py --zones capital_federal

# Scraping semanal de todas las zonas
python propscrape/main.py
```

### Desarrollo y debugging
```bash
# Test sin guardar, máximo 2 páginas
python propscrape/main.py --test --max-pages 2 --no-db

# Solo Córdoba, máximo 5 páginas, sin guardar
python propscrape/main.py --zones cordoba --max-pages 5 --no-db
```

## 📁 Estructura del Proyecto

```
propscrape/
├── main.py                  # Script principal CLI
├── core/
│   ├── config.py           # Configuración general
│   ├── database.py         # Gestión de base de datos
│   ├── models.py           # Modelos de datos
│   └── zones_config.py     # Configuración de zonas
├── connectors/
│   ├── base.py            # Clase base para conectores
│   ├── zonaprop.py        # Conector Zonaprop (multi-zona)
│   └── mercadolibre.py    # Conector MercadoLibre
└── services/
    └── ingestion.py        # Servicio de ingesta multi-zona
```

## 🔧 Configuración

### Zonas (`core/zones_config.py`)

Cada zona está configurada con:
- **zone_key**: Identificador único
- **display_name**: Nombre legible
- **province_code**: Código de provincia para API
- **zone_code**: Código de zona (si aplica)
- **description**: Descripción

### Operaciones

- **sale** (Venta, código API: "1")
- **rent** (Alquiler, código API: "2")

## 📊 Datos Capturados

Por cada propiedad se captura:
- Precio y moneda
- Ubicación (dirección, coordenadas GPS)
- Tipo de propiedad
- Cantidad de habitaciones
- Superficie total
- URLs y enlaces
- Timestamps de publicación/actualización
- Título y descripción

## 📈 Estadísticas y Logging

Durante la ejecución se registran:
- Zonas procesadas
- Número de anuncios por zona
- Errores encontrados
- Tiempo total de ejecución
- Velocidad de scraping (anuncios/minuto)

Logs guardados en:
- **Console**: Salida en tiempo real
- **Archivo**: `scraping.log`

## ⚙️ Opciones Avanzadas

### Combinaciones personalizadas
```bash
# Santa Fe y Córdoba, solo ventas
python propscrape/main.py --zones santa_fe cordoba --operations sale

# Capital Federal y GBA, solo alquileres, máximo 20 páginas
python propscrape/main.py --zones capital_federal zona_norte_gba \
    --operations rent --max-pages 20
```

### Scripting automatizado
```bash
# Script para scraping diario
#!/bin/bash
cd /ruta/a/PropScraper
python propscrape/main.py >> logs/scraping_$(date +%Y%m%d).log 2>&1
```

## 🐛 Troubleshooting

### Error de conexión a API
- Verificar conexión a internet
- Verificar que la cookie de Cloudflare sea válida
- Revisar el archivo `scraping.log`

### Base de datos llena
- Implementar política de retención de datos
- Hacer backup antes de ejecutar scraping completo

### Límite de velocidad de API
- El sistema incluye delays automáticos entre requests
- Se respeta el límite de 30 propiedades por página
- Delay de 1-2 segundos entre páginas/zonas

## 📝 Desarrollo

### Agregar nueva zona
1. Agregar entrada en `ZONES_CONFIG` en `core/zones_config.py`
2. Incluir en `ZONES_TO_SCRAPE`
3. Usar `--zones nombre_nueva_zona`

### Agregar nuevo conector
1. Heredar de `BaseConnector`
2. Implementar `fetch_listings()`
3. Registrar en `ingestion.py`

## 📄 Licencia

Proyecto PropScraper - 2026

## ✉️ Contacto

Para preguntas o mejoras, consultar la documentación interna.
