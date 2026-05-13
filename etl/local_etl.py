import pandas as pd
import os
from pathlib import Path
import shutil
import logging
from dataclasses import dataclass
import sqlalchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class TelecomETL:
    raw_dir: Path
    staging_dir: Path
    processed_dir: Path
    db_uri: str

    def extract_transform_load(self, logger: logging.Logger):
        logger.info(f"Raw directory: {self.raw_dir}")
        logger.info(f"Staging directory: {self.staging_dir}")
        logger.info(f"Processed directory: {self.processed_dir}")

        # Create directories if they don't exist
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        if not self.raw_dir.exists():
            logger.info(f"Raw directory does not exist: {self.raw_dir}")
            return

        files_processed = 0
        engine = sqlalchemy.create_engine(self.db_uri)

        for file in os.listdir(self.raw_dir):
            if file.startswith('events_') and file.endswith('.json'):
                file_path = self.raw_dir / file
                staging_path = self.staging_dir / file

                try:
                    logger.info(f"Processing file: {file}")
                    shutil.move(file_path, staging_path)

                    # Extract
                    df = pd.read_json(staging_path)
                    logger.info(f"Extracted {len(df)} rows from {file}")

                    # Transform
                    if 'imsi' in df.columns:
                        df['imsi'] = df['imsi'].str.replace('IMSI_', '', regex=False)
                    logger.info(f"Transformed {len(df)} rows")

                    # Load
                    df.to_sql('eventos', con=engine, if_exists='append', index=False)
                    logger.info(f"Data loaded successfully: {len(df)} rows")

                    # Move file to processed
                    shutil.move(staging_path, self.processed_dir / file)
                    logger.info(f"File moved to processed: {file}")
                    files_processed += 1

                except Exception as e:
                    logger.error(f"Error processing file {file}: {e}")
                    # Keep it in staging if it failed after moving there

        logger.info(f"ETL process completed. Files processed: {files_processed}")

def setup_logging() -> None:
    """Configures logging to output to both a file and the console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("etl_process.log"),
            logging.StreamHandler()
        ]
    )   

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting ETL process...")

    # Configuration from environment variables or defaults
    raw_dir = Path(os.getenv("RAW_DATA_DIR", "data/raw"))
    staging_dir = Path(os.getenv("STAGING_DATA_DIR", "data/staging"))
    processed_dir = Path(os.getenv("PROCESSED_DATA_DIR", "data/processed"))

    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "telecom_analytics")

    db_uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    etl_obj = TelecomETL(
        raw_dir=raw_dir,
        staging_dir=staging_dir,
        processed_dir=processed_dir,
        db_uri=db_uri
    )
    etl_obj.extract_transform_load(logger)

if __name__ == "__main__":
    main()
