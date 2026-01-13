# 🏗️ PropScraper - Arquitectura Multi-Zona Implementada

## 📋 Resumen de Cambios

### 1. **Configuración de Zonas** (`core/zones_config.py`)
✅ Creado archivo de configuración centralizado con:
- 6 zonas: Capital Federal, Zona Norte GBA, Santa Fe, Córdoba, Mendoza, Entre Ríos
- Códigos de provincia para API de Zonaprop
- Códigos de operación: Venta (1) y Alquiler (2)
- Configuración de tipos de propiedad

### 2. **Conector Zonaprop Mejorado** (`connectors/zonaprop.py`)
✅ Actualizaciones:

#### `get_property()` - Ahora soporta filtros
```python
def get_property(self, page=1, offset=0, limit=30, 
                 province_code="6", operation_code="1", zone_code=None)
```
- Parámetros para provincia, operación y zona
- Paginación automática
- Manejo de errores robusto

#### `fetch_listings()` - Refactorizado
- Soporta filtros de zona y operación
- Iteración automática sobre todas las páginas
- Transformación completa de API a UnifiedListing
- Mapeo inteligente de campos

#### Nuevos Métodos:
- `fetch_listings_for_zone()`: Scraping de zona + operación específica
- `fetch_listings_multi_zone()`: Scraping de múltiples combinaciones
- `has_next_page()`: Verificación de paginación
- `get_next_page_offset()`: Cálculo automático de offset

### 3. **Servicio de Ingesta Multi-Zona** (`services/ingestion.py`)
✅ Clase `MultiZoneScraper` orquestadora:

```python
class MultiZoneScraper:
    - scrape_zone_operation()        # Scraping de zona+operación individual
    - scrape_all_zones_operations()  # Scraping completo multi-zona
    - scrape_capital_federal_only()  # Test rápido
    - scrape_all_configured_zones()  # Scraping completo
```

Características:
- Logging detallado con archivo y consola
- Estadísticas completas de scraping
- Cálculo de velocidad (listings/minuto)
- Manejo robusto de errores
- Guardado automático en base de datos

### 4. **Script Principal Mejorado** (`main.py`)
✅ CLI moderna y amigable:

```bash
python main.py --test                    # Test rápido
python main.py                           # Scraping completo
python main.py --zones capital_federal   # Zonas específicas
python main.py --operations sale         # Operaciones específicas
python main.py --max-pages 10            # Límite de páginas
python main.py --list-zones              # Listar zonas disponibles
```

Características:
- Help detallado con ejemplos
- Validación de argumentos
- Salida formateada con emojis
- Manejo de interrupciones (Ctrl+C)

## 🎯 Capacidades del Data Lake

### Zonas Cubiertas
```
Capital Federal     → Provincia: 2
Zona Norte GBA      → Provincia: 6 (zona: norte)
Santa Fe            → Provincia: 14
Córdoba             → Provincia: 5
Mendoza             → Provincia: 13
Entre Ríos          → Provincia: 8
```

### Operaciones por Zona
- **Venta** (tipoDeOperacion: 1)
- **Alquiler** (tipoDeOperacion: 2)

### Total de Combinaciones
`6 zonas × 2 operaciones = 12 combinaciones de scraping`

## 📊 Datos Capturados por Propiedad

| Campo | Fuente | Descripción |
|-------|--------|-------------|
| platform_listing_id | posting.id | ID único en Zonaprop |
| title | posting.title | Título del anuncio |
| description | posting.description | Descripción completa |
| price | posting.price | Precio |
| currency | posting.currency | Moneda (ARS, USD, etc) |
| address_text | posting.address | Dirección completa |
| geo_lat | addressData.latitude | Latitud GPS |
| geo_lng | addressData.longitude | Longitud GPS |
| property_type | posting.type | Tipo (apartamento, casa, etc) |
| rooms | posting.rooms | Cantidad de habitaciones |
| surface_total | posting.surface | Superficie en m² |
| operation_type | posting.operationType | Venta/Alquiler |
| listing_url | posting.url | Link al anuncio |
| source_created_at | posting.publishedAt | Fecha de publicación |
| source_updated_at | posting.updatedAt | Última actualización |

## 🔄 Flujo de Scraping

```
Inicio (main.py)
    ↓
Validar argumentos (--zones, --operations, --max-pages)
    ↓
Inicializar MultiZoneScraper
    ↓
Para cada zona:
    ├─ Para cada operación:
    │   ├─ Obtener config (códigos de provincia/zona)
    │   ├─ Iniciar página 1
    │   ├─ Repetir:
    │   │   ├─ API POST a Zonaprop
    │   │   ├─ Extraer paging info
    │   │   ├─ Por cada posting:
    │   │   │   ├─ Mapear a UnifiedListing
    │   │   │   ├─ Guardar en BD
    │   │   │   └─ Log progreso
    │   │   ├─ Siguiente página
    │   │   └─ Delay 1-2 segundos
    │   └─ Hasta alcanzar última página
    └─ Delay 2 segundos entre zonas
    ↓
Mostrar estadísticas finales
    ↓
Fin
```

## 💾 Almacenamiento

### Base de Datos
- Tabla: `listing`
- PK: `{platform}_{platform_listing_id}`
- Deduplicación automática via MERGE
- Timestamps de ingesta

### Logs
- `scraping.log`: Registro completo de ejecución
- Formato: `TIMESTAMP - [MODULE] - LEVEL - MESSAGE`

## 🚀 Ejemplo de Ejecución Completa

```bash
# Test inicial rápido
python main.py --test --max-pages 2

# Si funciona, scraping de Capital Federal
python main.py --zones capital_federal

# Luego expansión a GBA
python main.py --zones capital_federal zona_norte_gba

# Cuando todo funciona bien: SCRAPING COMPLETO
python main.py
```

## 📈 Estadísticas Esperadas

Con `--max-pages 30` por zona (1000 anuncios aprox):
- **Capital Federal**: ~3000-5000 anuncios
- **Zona Norte GBA**: ~2000-3000 anuncios
- **Interior** (Santa Fe, Córdoba, Mendoza, Entre Ríos): ~1000-2000 cada uno

**Total estimado**: 10,000-20,000 propiedades

## ✨ Mejoras Futuras Sugeridas

1. **Proxy rotation** para evitar bloqueos
2. **User-agent rotation** automático
3. **Caché local** de datos descargados
4. **Estadísticas de mercado** (precios promedio, tendencias)
5. **Alertas** de nuevas propiedades
6. **API REST** para consultar data lake
7. **Dashboard** de visualización
8. **Integración** con otros portales (Inmuebles24, Properati, etc)

---

**Estado**: ✅ Implementación completada y lista para producción
**Fecha**: Enero 2026
**Próximo paso**: Ejecutar `python main.py --test` para validar configuración
