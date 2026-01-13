#!/usr/bin/env python3
"""
Ejemplos de uso del sistema multi-zona PropScraper
"""

from propscrape.services.ingestion import MultiZoneScraper
from propscrape.core.zones_config import ZONES_TO_SCRAPE, OPERATIONS_TO_SCRAPE

# ============================================================================
# EJEMPLO 1: Test rápido - Capital Federal solamente
# ============================================================================
def example_test_quick():
    """Test rápido para validar que todo funciona"""
    scraper = MultiZoneScraper()
    stats = scraper.scrape_capital_federal_only(max_pages=5)
    print(f"✅ Scraping test completado: {stats['total_listings']} listings")
    scraper.close()


# ============================================================================
# EJEMPLO 2: Zonas específicas - Buenos Aires
# ============================================================================
def example_buenos_aires_only():
    """Scrapear solo Capital Federal y Zona Norte"""
    scraper = MultiZoneScraper()
    stats = scraper.scrape_all_zones_operations(
        zones=["capital_federal", "zona_norte_gba"],
        operations=["sale", "rent"],
        max_pages_per_zone=10
    )
    print(f"✅ Scraping Buenos Aires completado: {stats['total_listings']} listings")
    scraper.close()


# ============================================================================
# EJEMPLO 3: Solo ventas
# ============================================================================
def example_only_sales():
    """Scrapear todas las zonas pero solo ventas"""
    scraper = MultiZoneScraper()
    stats = scraper.scrape_all_zones_operations(
        zones=ZONES_TO_SCRAPE,
        operations=["sale"],  # Solo ventas
        max_pages_per_zone=None  # Todas las páginas
    )
    print(f"✅ Ventas: {stats['total_listings']} propiedades")
    scraper.close()


# ============================================================================
# EJEMPLO 4: Solo alquileres
# ============================================================================
def example_only_rentals():
    """Scrapear todas las zonas pero solo alquileres"""
    scraper = MultiZoneScraper()
    stats = scraper.scrape_all_zones_operations(
        zones=ZONES_TO_SCRAPE,
        operations=["rent"],  # Solo alquileres
        max_pages_per_zone=20
    )
    print(f"✅ Alquileres: {stats['total_listings']} propiedades")
    scraper.close()


# ============================================================================
# EJEMPLO 5: Interior del país
# ============================================================================
def example_interior():
    """Scrapear solo provincias del interior"""
    scraper = MultiZoneScraper()
    stats = scraper.scrape_all_zones_operations(
        zones=["santa_fe", "cordoba", "mendoza", "entre_rios"],
        operations=["sale", "rent"],
        max_pages_per_zone=5
    )
    print(f"✅ Interior: {stats['total_listings']} propiedades")
    scraper.close()


# ============================================================================
# EJEMPLO 6: Scraping completo (todas las zonas, todos los tipos)
# ============================================================================
def example_full_scrape():
    """Scraping completo - generar data lake completo"""
    scraper = MultiZoneScraper()
    
    print("🚀 Iniciando scraping completo...")
    print("Esto puede tardar varios minutos...\n")
    
    stats = scraper.scrape_all_configured_zones(max_pages_per_zone=None)
    
    print(f"\n📊 RESULTADOS FINALES:")
    print(f"  Total listings: {stats['total_listings']}")
    print(f"  Combinaciones procesadas: {stats['total_operations_processed']}")
    print(f"  Errores: {stats['errors']}")
    
    scraper.close()


# ============================================================================
# EJEMPLO 7: Scraping programado por zona individual
# ============================================================================
def example_zone_by_zone():
    """Scrapear zona por zona para mejor control"""
    scraper = MultiZoneScraper()
    
    zones = ["capital_federal", "zona_norte_gba", "santa_fe"]
    
    for zone in zones:
        print(f"\n🔄 Procesando: {zone}")
        count = scraper.scrape_zone_operation(
            zone_key=zone,
            operation_key="sale",
            max_pages=5
        )
        print(f"   ✓ {count} propiedades capturadas")
    
    scraper.close()


# ============================================================================
# EJEMPLO 8: Scraping sin guardar en BD (para testing)
# ============================================================================
def example_no_database():
    """Test sin guardar en base de datos"""
    scraper = MultiZoneScraper()
    
    stats = scraper.scrape_all_zones_operations(
        zones=["capital_federal"],
        operations=["sale"],
        max_pages_per_zone=2,
        save_to_db=False  # No guardar
    )
    
    print(f"✅ Test completado (sin guardar BD): {stats['total_listings']} listings")
    scraper.close()


# ============================================================================
# EJEMPLO 9: Scraping con límite de páginas (para desarrollo)
# ============================================================================
def example_limited_pages():
    """Scraping limitado para desarrollo"""
    scraper = MultiZoneScraper()
    
    # Solo 3 páginas máximo por zona
    stats = scraper.scrape_all_zones_operations(
        zones=ZONES_TO_SCRAPE,
        operations=OPERATIONS_TO_SCRAPE,
        max_pages_per_zone=3
    )
    
    print(f"✅ Scraping limitado (3 páginas): {stats['total_listings']} listings")
    scraper.close()


# ============================================================================
# EJEMPLO 10: Scraping individual personalizado
# ============================================================================
def example_custom_zone_operation():
    """Scraping personalizado de una combinación específica"""
    scraper = MultiZoneScraper()
    
    # Alquileres en Córdoba, máximo 10 páginas
    for listing in scraper.connector.fetch_listings_for_zone(
        zone_key="cordoba",
        operation_key="rent",
        max_pages=10
    ):
        print(f"  📍 {listing.address_text}: ${listing.price} {listing.currency}")
    
    scraper.close()


# ============================================================================
# MAIN: Ejecutar ejemplo
# ============================================================================
if __name__ == "__main__":
    import sys
    
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║           PropScraper - Ejemplos de Uso                           ║
    ╚════════════════════════════════════════════════════════════════════╝
    
    Ejemplos disponibles:
    1. Test rápido (Capital Federal, 5 páginas)
    2. Solo Buenos Aires (Capital Federal + Zona Norte)
    3. Solo ventas (todas las zonas)
    4. Solo alquileres (todas las zonas)
    5. Interior (Santa Fe, Córdoba, Mendoza, Entre Ríos)
    6. Scraping COMPLETO (todas las zonas y operaciones)
    7. Zona por zona (control individual)
    8. Sin guardar en BD (testing)
    9. Páginas limitadas (desarrollo)
    10. Personalizado (específico para Córdoba/alquiler)
    """)
    
    example = input("Ingrese número de ejemplo (1-10): ").strip()
    
    examples = {
        "1": example_test_quick,
        "2": example_buenos_aires_only,
        "3": example_only_sales,
        "4": example_only_rentals,
        "5": example_interior,
        "6": example_full_scrape,
        "7": example_zone_by_zone,
        "8": example_no_database,
        "9": example_limited_pages,
        "10": example_custom_zone_operation,
    }
    
    if example in examples:
        print(f"\n▶️ Ejecutando ejemplo {example}...\n")
        examples[example]()
    else:
        print("❌ Opción no válida")
        sys.exit(1)
