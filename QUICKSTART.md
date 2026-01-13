# 🚀 GUÍA DE INICIO RÁPIDO - PropScraper Multi-Zona

## ¿Qué es PropScraper?

PropScraper es un **scraper de inmuebles argentino** que recolecta datos de propiedades en venta y alquiler de múltiples zonas del país para crear un **data lake** de propiedades.

### Zonas que cubre:
- ✅ Capital Federal
- ✅ Zona Norte GBA  
- ✅ Santa Fe
- ✅ Córdoba
- ✅ Mendoza
- ✅ Entre Ríos

### Tipos de datos:
- ✅ **Ventas** (tipoDeOperacion: 1)
- ✅ **Alquileres** (tipoDeOperacion: 2)

---

## 📥 INSTALACIÓN (Una vez)

```bash
# 1. Ir a la carpeta del proyecto
cd c:\Users\Juan\Desktop\PropScrape\PropScraper

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Verificar instalación
python propscrape/main.py --list-zones
```

---

## 🎯 PRIMEROS PASOS

### 1️⃣ Test Rápido (COMIENZA AQUÍ)
```bash
python propscrape/main.py --test
```
**Qué hace**: Scraping rápido de Capital Federal (5 páginas, ~150 propiedades)
**Tiempo**: ~2-3 minutos
**Resultado**: Verifica que todo funciona correctamente

### 2️⃣ Scraping de Capital Federal Completo
```bash
python propscrape/main.py --zones capital_federal
```
**Qué hace**: Scraping de todas las propiedades en Capital Federal (venta + alquiler)
**Tiempo**: ~10-15 minutos
**Resultado**: ~5000-10000 propiedades

### 3️⃣ Expandir a Zona Norte
```bash
python propscrape/main.py --zones capital_federal zona_norte_gba
```
**Qué hace**: Capital Federal + Zona Norte GBA completo
**Tiempo**: ~20-30 minutos
**Resultado**: ~10000-15000 propiedades

### 4️⃣ SCRAPING COMPLETO (generar data lake)
```bash
python propscrape/main.py
```
**Qué hace**: Todas las zonas × ventas y alquileres
**Tiempo**: 1-2 horas (según velocidad de internet)
**Resultado**: 100,000+ propiedades en la BD

---

## 📊 EJEMPLOS DE USO

### Casos de uso específicos

**Solo Capital Federal:**
```bash
python propscrape/main.py --zones capital_federal
```

**Solo CABA y Santa Fe:**
```bash
python propscrape/main.py --zones capital_federal santa_fe
```

**Solo VENTAS de todo el país:**
```bash
python propscrape/main.py --operations sale
```

**Solo ALQUILERES de todo el país:**
```bash
python propscrape/main.py --operations rent
```

**Provincias del interior (Santa Fe, Córdoba, Mendoza, Entre Ríos):**
```bash
python propscrape/main.py --zones santa_fe cordoba mendoza entre_rios
```

**Con límite de páginas (para testing):**
```bash
python propscrape/main.py --max-pages 5
```

**Sin guardar en BD (solo ver datos):**
```bash
python propscrape/main.py --test --no-db
```

---

## 🎓 EJEMPLOS INTERACTIVOS

Ejecutar ejemplos paso a paso:
```bash
python examples.py
```

Menú con 10 ejemplos diferentes:
1. Test rápido
2. Solo Buenos Aires
3. Solo ventas
4. Solo alquileres
5. Interior
6. Scraping completo
7. Zona por zona
8. Sin guardar BD
9. Páginas limitadas
10. Personalizado

---

## 📈 ¿QUÉ SE SCRAPEEA?

Por cada propiedad:
```
✓ Precio y moneda
✓ Ubicación (dirección + GPS)
✓ Tipo de propiedad (apto, casa, etc)
✓ Habitaciones y superficie
✓ URLs del anuncio
✓ Fechas de publicación
✓ Descripción completa
```

**Total de datos capturados por propiedad: ~18 campos**

---

## 📊 ESTRUCTURA DE CARPETAS

```
PropScraper/
├── propscrape/
│   ├── main.py              ← ¡EJECUTA ESTO!
│   ├── core/
│   │   ├── zones_config.py  ← Configuración de zonas
│   │   ├── database.py
│   │   ├── models.py
│   │   └── config.py
│   ├── connectors/
│   │   ├── zonaprop.py      ← Conector Zonaprop
│   │   ├── base.py
│   │   └── mercadolibre.py
│   └── services/
│       └── ingestion.py     ← Orquestador multi-zona
├── examples.py              ← Ejemplos interactivos
├── SCRAPING_GUIDE.md        ← Guía completa
├── ARCHITECTURE.md          ← Arquitectura técnica
└── requirements.txt         ← Dependencias
```

---

## 📋 REFERENCIA RÁPIDA DE COMANDOS

| Comando | Descripción |
|---------|-------------|
| `python main.py --test` | Test rápido (Capital Federal, 5 páginas) |
| `python main.py` | Scraping completo (todas las zonas) |
| `python main.py --zones capital_federal` | Solo Capital Federal |
| `python main.py --zones capital_federal zona_norte_gba` | CABA + Zona Norte |
| `python main.py --operations sale` | Solo ventas |
| `python main.py --operations rent` | Solo alquileres |
| `python main.py --max-pages 10` | Máximo 10 páginas por zona |
| `python main.py --list-zones` | Listar zonas disponibles |
| `python main.py --no-db` | No guardar en BD |
| `python examples.py` | Ejecutar ejemplos interactivos |

---

## ⏱️ TIEMPOS ESTIMADOS

| Operación | Tiempo | Propiedades |
|-----------|--------|------------|
| `--test` | 2-3 min | ~150 |
| Capital Federal | 10-15 min | ~5000 |
| CABA + Zona Norte | 20-30 min | ~10000 |
| Una provincia interior | 5-10 min | ~2000 |
| Scraping COMPLETO | 1-2 horas | ~100000+ |

---

## 🔧 CONFIGURACIÓN

### Cambiar límite de páginas
```bash
# Máximo 20 páginas por zona
python main.py --max-pages 20

# Unlimitado (todas las páginas disponibles)
python main.py --max-pages 999
```

### Ver zonas disponibles
```bash
python main.py --list-zones

# Output:
# Available zones:
#   capital_federal      - Capital Federal            (Ciudad Autónoma de Buenos Aires)
#   zona_norte_gba       - Zona Norte GBA             (Zona Norte del Gran Buenos Aires)
#   santa_fe             - Santa Fe                   (Provincia de Santa Fe)
#   cordoba              - Córdoba                    (Provincia de Córdoba)
#   mendoza              - Mendoza                    (Provincia de Mendoza)
#   entre_rios           - Entre Ríos                 (Provincia de Entre Ríos)
```

---

## 📝 FLUJO RECOMENDADO

```
1. Instalar dependencias
   └─ pip install -r requirements.txt

2. Validar configuración
   └─ python main.py --list-zones

3. Test rápido
   └─ python main.py --test

4. Si funciona → Expandir
   ├─ Capital Federal
   ├─ + Zona Norte
   ├─ + Interior
   └─ SCRAPING COMPLETO

5. Monitorear logs
   └─ tail scraping.log
```

---

## 📊 EJEMPLOS DE SALIDA

### Test rápido
```
================================================================================
PropScraper - Real Estate Data Lake Builder
================================================================================
Mode: QUICK TEST (Capital Federal only)
Save to database: Yes
Max pages per zone: 5
================================================================================

🚀 Starting quick test scrape...

[zonaprop] Starting: Capital Federal - Venta
[zonaprop] ✓ Processed 10 listings
[zonaprop] ✓ Processed 20 listings
...
[zonaprop] Completed: Capital Federal - Venta (150 listings)

✅ Scraping completed successfully!

Results:
  Total listings: 150
  Combinations processed: 1
  Errors: 0
```

---

## 🐛 TROUBLESHOOTING

### "No module named 'propscrape'"
```bash
# Instalar dependencias
pip install -r requirements.txt
```

### Error de conexión a API
- Verificar conexión a internet
- La cookie de Cloudflare puede haber expirado
- Revisar `scraping.log` para detalles

### Base de datos llena
- Las propiedades se deduplicar automáticamente
- Se puede ejecutar `python main.py --no-db` para solo ver datos

### Muy lento
- Internet lento: aumentar `--max-pages` a 5
- API saturada: esperar unos minutos

---

## 📞 PRÓXIMOS PASOS

1. ✅ Ejecutar: `python main.py --test`
2. ✅ Si funciona: `python main.py --zones capital_federal`
3. ✅ Expandir a otras zonas según necesidad
4. ✅ Revisar `SCRAPING_GUIDE.md` para uso avanzado
5. ✅ Ver `ARCHITECTURE.md` para detalles técnicos

---

## 📄 DOCUMENTACIÓN

- **SCRAPING_GUIDE.md** - Guía completa de scraping
- **ARCHITECTURE.md** - Arquitectura del sistema
- **examples.py** - Ejemplos interactivos
- **requirements.txt** - Dependencias del proyecto

---

**¡Listo para generar tu data lake de inmuebles! 🚀**

Ejecuta ahora:
```bash
python propscrape/main.py --test
```
