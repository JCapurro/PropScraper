# PropScrape Data Lake - Documentación Técnica

## 📊 Descripción General

El **PropScrape Data Lake** es un repositorio unificado de datos inmobiliarios que consolida información de múltiples plataformas (Zonaprop, MercadoLibre, Properati, etc.) en un solo esquema normalizado y flexible.

**Ventajas clave:**
- ✅ **Queries cross-platform**: Compare precios entre todas las plataformas
- ✅ **Detección de duplicados**: Encuentre la misma propiedad publicada en múltiples sitios
- ✅ **Análisis unificado**: Tendencias de mercado general
- ✅ **Búsquedas geoespaciales**: "Propiedades a menos de 2km del Obelisco"
- ✅ **Text search**: "Departamentos con balcón y terraza"

---

## 🗄️ Arquitectura

```
propscrape (Database)
├── listings_current      # Colección principal de listings
│   ├── Zonaprop listings
│   ├── MercadoLibre listings
│   └── Properati listings (futuro)
└── ingestion_runs        # Historial de ejecuciones de scraping
```

### Base de Datos

- **Nombre**: `propscrape`
- **Motor**: MongoDB
- **URI**: `mongodb://localhost:27017/`

---

## 📐 Schema del Data Lake

### Colección: `listings_current`

#### Campos Requeridos

| Campo | Tipo | Descripción | Validación |
|-------|------|-------------|------------|
| `platform` | string | Plataforma de origen | Enum: ["zonaprop", "mercadolibre", "properati", "argenprop"] |
| `platform_listing_id` | string | ID único en la plataforma | - |
| `listing_url` | string | URL del listing | - |
| `operation_type` | string | Tipo de operación | Enum: ["sale", "rent"] |
| `property_type` | string | Tipo de propiedad | apartment, house, ph, etc. |
| `currency` | string | Moneda | Enum: ["ARS", "USD", "EUR"] |
| `status` | string | Estado del listing | Enum: ["active", "delisted", "paused", "sold", "rented"] |

#### Campos Opcionales

**Pricing:**
- `price` (float, ≥0): Precio del listing
- `expenses` (float, ≥0): Expensas mensuales

**Ubicación:**
- `address_text` (string): Dirección en texto
- `geo_lat` (float, -90 to 90): Latitud
- `geo_lng` (float, -180 to 180): Longitud
- `geo_location` (GeoJSON Point): Para queries geoespaciales

**Detalles:**
- `surface_total` (float, ≥0): Superficie total (m²)
- `surface_covered` (float, ≥0): Superficie cubierta (m²)
- `rooms` (int, ≥0): Número de ambientes
- `bedrooms` (int, ≥0): Dormitorios
- `bathrooms` (int, ≥0): Baños

**Contenido:**
- `title` (string): Título del listing
- `description` (string): Descripción completa
- `images` (array[string]): Array de URLs de imágenes
- `agent_publisher` (string): Agente inmobiliario

**Timestamps:**
- `source_created_at` (datetime): Fecha de creación en la plataforma
- `source_updated_at` (datetime): Última actualización en la plataforma
- `ingested_at` (datetime): Timestamp de ingesta en PropScrape

#### Ejemplo de Documento

```json
{
  "_id": ObjectId("..."),
  "platform": "zonaprop",
  "platform_listing_id": "12345678",
  "listing_url": "https://www.zonaprop.com.ar/propiedades/12345678",
  "operation_type": "sale",
  "property_type": "apartment",
  "price": 150000.0,
  "currency": "USD",
  "expenses": 25000.0,
  "address_text": "Avenida Santa Fe 1234, Palermo, CABA",
  "geo_lat": -34.5883,
  "geo_lng": -58.4098,
  "geo_location": {
    "type": "Point",
    "coordinates": [-58.4098, -34.5883]
  },
  "surface_total": 85.0,
  "surface_covered": 75.0,
  "rooms": 3,
  "bedrooms": 2,
  "bathrooms": 2,
  "title": "Departamento de 3 ambientes en Palermo",
  "description": "Hermoso departamento luminoso...",
  "images": ["https://...", "https://..."],
  "agent_publisher": "Inmobiliaria XYZ",
  "status": "active",
  "source_created_at": ISODate("2026-01-10T14:30:00Z"),
  "source_updated_at": ISODate("2026-01-15T10:15:00Z"),
  "ingested_at": ISODate("2026-01-18T18:40:00Z")
}
```

---

## 🔍 Índices Optimizados

### Índices Básicos

1. **platform** - Filtrarpor plataforma
2. **platform_listing_id** - Lookups rápidos
3. **(platform, platform_listing_id)** - Índice compuesto ÚNICO (previene duplicados)
4. **operation_type** - Filtrar sale/rent
5. **status** - Filtrar active/delisted

### Índices de Query Optimization

6. **(operation_type, property_type, price)** - Búsquedas comunes
7. **source_created_at** - Análisis temporal
8. **ingested_at DESC** - Listings más recientes

### Índices Avanzados

9. **geo_location (2dsphere)** - Queries geoespaciales
10. **(title, description) TEXT** - Full-text search en español

### Performance

Los índices mejoran la performance de queries entre **10x y 100x**:
- Query sin índice: ~5000ms
- Query con índice: ~50ms

---

## 🚀 Uso del Data Lake

### Inicialización

```bash
# Inicializar data lake (crear índices, validaciones)
python scripts/init_datalake.py
```

Esto creará:
- Colecciones necesarias
- Todos los índices optimizados
- Validaciones de schema
- Verificará la configuración

### Ingestión de Datos

```bash
# Ingestar de Zonaprop (todas las zonas configuradas)
python -m propscrape.services.ingestion

# Ingestar zona específica
python -m propscrape.services.ingestion --zones capital_federal --max-pages 5
```

### Queries de Ejemplo

```bash
# Ejecutar queries avanzados de ejemplo
python scripts/query_examples.py
```

Incluye 6 queries de ejemplo:
1. Top 10 propiedades más baratas (cross-platform)
2. Detectar duplicados entre plataformas
3. Análisis de precios por zona
4. Búsqueda geoespacial (cerca de un punto)
5. Full-text search
6. Análisis temporal de ingestas

### Verificación de Calidad

```bash
# Generar reporte de calidad de datos
python scripts/data_quality_check.py
```

Analiza:
- Coordenadas faltantes
- Precios faltantes o anómalos
- Completitud por plataforma
- Frescura de datos
- Distribución por plataforma/operación

---

## 💡 Ejemplos de Queries

### 1. Top 10 Más Baratos (Cross-Platform)

```python
collection.find({
    "operation_type": "sale",
    "price": {"$ne": None, "$gt": 0}
}).sort("price", 1).limit(10)
```

### 2. Detectar Duplicados Entre Plataformas

```python
collection.aggregate([
    {"$group": {
        "_id": {
            "lat": {"$round": ["$geo_lat", 3]},
            "lng": {"$round": ["$geo_lng", 3]},
            "rooms": "$rooms"
        },
        "platforms": {"$addToSet": "$platform"},
        "count": {"$sum": 1}
    }},
    {"$match": {
        "count": {"$gt": 1},
        "platforms.1": {"$exists": True}
    }}
])
```

### 3. Búsqueda Geoespacial (2km del Obelisco)

```python
collection.aggregate([
    {"$geoNear": {
        "near": {
            "type": "Point",
            "coordinates": [-58.3816, -34.6037]  # Obelisco
        },
        "distanceField": "distance",
        "maxDistance": 2000,  # 2km en metros
        "spherical": True
    }},
    {"$limit": 10}
])
```

### 4. Full-Text Search

```python
collection.find(
    {"$text": {"$search": "balcón terraza"}},
    {"score": {"$meta": "textScore"}}
).sort([("score", {"$meta": "textScore"})])
```

### 5. Comparar Precios Entre Plataformas

```python
collection.aggregate([
    {"$match": {"operation_type": "sale"}},
    {"$group": {
        "_id": "$platform",
        "avg_price": {"$avg": "$price"},
        "min_price": {"$min": "$price"},
        "max_price": {"$max": "$price"}
    }}
])
```

---

## 🔐 Validaciones de Schema

El data lake usa **JSON Schema Validation** de MongoDB para garantizar calidad de datos.

**Nivel de validación**: `moderate`
- Documentos existentes no son validados
- Nuevos inserts/updates deben pasar validación

**Acción**: `error`
- Rechaza documentos inválidos

### Reglas Principales

- `platform` debe ser uno de: "zonaprop", "mercadolibre", "properati", "argenprop"
- `operation_type` debe ser: "sale" o "rent"
- `price` debe ser ≥ 0 (si existe)
- `geo_lat` debe estar entre -90 y 90
- `geo_lng` debe estar entre -180 y 180
- `currency` debe ser: "ARS", "USD" o "EUR"

---

## 📊 Modelo Pydantic

El modelo `UnifiedListing` en `propscrape/core/models.py` proporciona:

### Validaciones Automáticas
- Tipos estrictos con `Literal` para enums
- Rangos numéricos (ge=0, le=90, etc.)
- Validación de coordenadas (lat y lng juntos o ambos None)

### Métodos Útiles

```python
listing = UnifiedListing(...)

# Generar GeoJSON Point
geo_point = listing.to_geojson_point()
# {"type": "Point", "coordinates": [-58.4098, -34.5883]}

# Dump con campo geo_location
data = listing.model_dump_with_geo()
# Incluye automáticamente 'geo_location' si hay coordenadas
```

---

## 🛠️ Mantenimiento

### Actualizar Índices

Si agregas nuevos campos que necesitan índices:

```python
from propscrape.core.mongo_db import listings_collection

# Crear nuevo índice
listings_collection.create_index("nuevo_campo")
```

### Agregar Nueva Plataforma

1. Actualizar enum en `UnifiedListing`:
```python
platform: Literal["zonaprop", "mercadolibre", "properati", "nueva_plataforma"]
```

2. Actualizar schema validator en `schema_validator.py`:
```python
"platform": {
    "enum": ["zonaprop", "mercadolibre", "properati", "nueva_plataforma"]
}
```

3. Re-aplicar validaciones:
```bash
python scripts/init_datalake.py
```

### Migrar Datos Existentes para geo_location

Si tienes documentos con `geo_lat`/`geo_lng` pero sin `geo_location`:

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["propscrape"]
collection = db["listings_current"]

# Update all documents with coordinates
collection.update_many(
    {
        "geo_lat": {"$ne": None},
        "geo_lng": {"$ne": None},
        "geo_location": {"$exists": False}
    },
    [{
        "$set": {
            "geo_location": {
                "type": "Point",
                "coordinates": ["$geo_lng", "$geo_lat"]
            }
        }
    }]
)
```

---

## 📈 Best Practices

### 1. Usar Upserts

Siempre usar upserts para evitar duplicados:

```python
collection.update_one(
    {"platform": "zonaprop", "platform_listing_id": "123"},
    {"$set": listing_data},
    upsert=True
)
```

### 2. Incluir geo_location

Al guardar listings, usar `model_dump_with_geo()`:

```python
listing = UnifiedListing(...)
data = listing.model_dump_with_geo()
data['ingested_at'] = datetime.now(timezone.utc)

collection.update_one(
    {"platform": data["platform"], "platform_listing_id": data["platform_listing_id"]},
    {"$set": data},
    upsert=True
)
```

### 3. Monitorear Calidad

Ejecutar regularmente el check de calidad:

```bash
# Diario o semanal
python scripts/data_quality_check.py > quality_report_$(date +%Y%m%d).txt
```

### 4. Backup Regular

```bash
# Backup de MongoDB
mongodump --db propscrape --out /backups/propscrape_$(date +%Y%m%d)

# Restore
mongorestore --db propscrape /backups/propscrape_20260118/propscrape
```

---

## 🔧 Troubleshooting

### Error: "Text index already exists"

Si ves este error al crear índices:
```
Drop the old text index first:
db.listings_current.dropIndex("text_search_title_description")
```

### Performance lento en queries geoespaciales

Verificar que el índice 2dsphere existe:
```
db.listings_current.getIndexes()
```

Si no existe, recrear:
```bash
python scripts/init_datalake.py
```

### Documentos rechazados por validación

Si los inserts fallan por validación, revisar:
1. Campos requeridos están presentes
2. Valores están en rangos válidos
3. platform/operation_type/currency están en los enums permitidos

---

## 📚 Referencias

- **MongoDB Geospatial**: https://docs.mongodb.com/manual/geospatial-queries/
- **MongoDB Text Search**: https://docs.mongodb.com/manual/text-search/
- **Pydantic Validation**: https://docs.pydantic.dev/latest/

---

## ✅ Checklist de Deployment

- [ ] MongoDB instalado y corriendo
- [ ] Base de datos `propscrape` creada
- [ ] Ejecutado `python scripts/init_datalake.py`
- [ ] Índices verificados (geoespacial, text, etc.)
- [ ] Validaciones aplicadas
- [ ] Primera ingesta ejecutada
- [ ] Queries de ejemplo funcionando
- [ ] Backup configurado

---

**Versión**: 1.0  
**Última actualización**: 2026-01-18  
**Autor**: PropScrape Team
