import argparse
import sys
import logging
from propscrape.core.database import engine, Base
from propscrape.core.config import settings

# Initialize logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from propscrape.services.ingestion import run_ingestion_job

def init_db():
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized.")

def main():
    parser = argparse.ArgumentParser(description="PropScrape Ingestion Service")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Init DB command
    init_parser = subparsers.add_parser("init-db", help="Initialize database tables")
    
    # Run ingestion command
    run_parser = subparsers.add_parser("run", help="Run ingestion for a platform")
    run_parser.add_argument("--platform", required=True, help="Platform name (zonaprop, mercadolibre)")
    
    args = parser.parse_args()
    
    if args.command == "init-db":
        init_db()
    elif args.command == "run":
        run_ingestion_job(args.platform)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
