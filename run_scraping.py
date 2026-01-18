"""
Script ejecutable para scraping completo de Zonaprop
Usa batch inserts optimizados (1500 propiedades por batch)
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from propscrape.services.ingestion import MultiZoneScraper
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraping.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Scrape propiedades de Zonaprop')
    parser.add_argument('--max-pages', type=int, default=None, 
                        help='Máximo de páginas por zona/operación (default: todas)')
    parser.add_argument('--zones', nargs='+', 
                        help='Zonas específicas a scrapear (default: todas)')
    parser.add_argument('--batch-size', type=int, default=500,
                        help='Tamaño del batch para inserts (default: 500)')
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("SCRAPING DE ZONAPROP - OPTIMIZADO CON BATCH INSERTS")
    print("=" * 80)
    print(f"\nConfiguración:")
    print(f"  Max páginas: {args.max_pages or 'SIN LÍMITE'}")
    print(f"  Zonas: {args.zones or 'TODAS'}")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Database: RealStates")
    print(f"  Collection: DataLake")
    print("\n" + "=" * 80 + "\n")
    
    # Create scraper with batch optimization
    scraper = MultiZoneScraper(batch_size=args.batch_size)
    
    try:
        # Determine zones
        if args.zones:
            zones = args.zones
        else:
            from propscrape.core.zones_config import ZONES_TO_SCRAPE
            zones = ZONES_TO_SCRAPE
        
        # Run scraping
        stats = scraper.scrape_all_zones_operations(
            zones=zones,
            operations=["sale", "rent"],
            max_pages_per_zone=args.max_pages,
            save_to_db=True
        )
        
        print("\n✓ SCRAPING COMPLETADO EXITOSAMENTE")
        print(f"\nLos datos están en: RealStates.DataLake")
        print(f"Puedes verificar con MongoDB Compass: mongodb://localhost:27017/\n")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠ Scraping interrumpido por usuario")
        logger.info("Guardando datos del buffer...")
        scraper.flush_batch()
        return 130
        
    except Exception as e:
        logger.error(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        scraper.close()

if __name__ == "__main__":
    sys.exit(main())
