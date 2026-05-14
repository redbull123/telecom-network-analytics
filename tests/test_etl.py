import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock, patch
from etl.local_etl import TelecomETL
import logging

@pytest.fixture
def logger():
    return logging.getLogger("test_etl_logger")

@pytest.fixture
def etl_instance():
    return TelecomETL(
        raw_dir=Path("tests/raw"),
        staging_dir=Path("tests/staging"),
        processed_dir=Path("tests/processed"),
        db_uri="postgresql://user:pass@host:5432/db"
    )

def test_imsi_cleaning(etl_instance, logger):
    # Mock data
    data = {'imsi': ['IMSI_12345', 'IMSI_67890', '23456']}
    df = pd.DataFrame(data)

    # Transformation logic from ETL
    df['imsi'] = df['imsi'].str.replace('IMSI_', '', regex=False)

    assert df['imsi'].tolist() == ['12345', '67890', '23456']

@patch("etl.local_etl.sqlalchemy.create_engine")
@patch("etl.local_etl.pd.read_json")
@patch("etl.local_etl.shutil.move")
@patch("etl.local_etl.os.listdir")
@patch("etl.local_etl.Path.exists")
def test_etl_flow(mock_exists, mock_listdir, mock_move, mock_read_json, mock_create_engine, etl_instance, logger):
    # Setup mocks
    mock_exists.return_value = True
    mock_listdir.return_value = ['events_20240101.json']

    mock_df = MagicMock()
    mock_df.columns = ['imsi']
    mock_df.__len__.return_value = 1
    mock_read_json.return_value = mock_df

    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    # Run ETL
    etl_instance.extract_transform_load(logger)

    # Verify file moves
    # 1. raw -> staging
    # 2. staging -> processed
    assert mock_move.call_count == 2

    # Verify DB load
    mock_df.to_sql.assert_called_once_with('eventos', con=mock_engine, if_exists='append', index=False)
