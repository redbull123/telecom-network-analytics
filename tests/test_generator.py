import pytest
from unittest.mock import MagicMock, patch, mock_open
from data_generator.generator import EventGenerator, Event, EventType, ResultType
import logging

@pytest.fixture
def logger():
    return logging.getLogger("test_logger")

@pytest.fixture
def generator():
    return EventGenerator()

def test_is_peak_hour(generator):
    assert generator._is_peak_hour(7) is True
    assert generator._is_peak_hour(12) is True
    assert generator._is_peak_hour(17) is True
    assert generator._is_peak_hour(3) is False
    assert generator._is_peak_hour(10) is False

def test_generate_event(generator, logger):
    event = generator.generate_event(logger)
    assert isinstance(event, Event)
    assert event.event_id == "event_1"
    assert event.event_type in [et.value for et in EventType]
    assert event.result in [rt.value for rt in ResultType]
    assert event.imsi.startswith("IMSI_")
    assert isinstance(event.cell_id, int)

def test_generate_events(generator, logger):
    num_events = 5
    events = generator.generate_events(num_events, logger)
    assert len(events) == num_events
    assert events[0].event_id == "event_1"
    assert events[4].event_id == "event_5"

def test_event_to_dict(logger):
    event = Event(
        event_id="test_id",
        timestamp="2024-01-01T00:00:00",
        event_type="attach",
        result="success",
        cause_code="0_success",
        imsi="12345",
        cell_id=1,
        enodeb_id=1,
        mme_id=1,
        tracking_area=1,
        duration_ms=100,
        rat_type="LTE",
        apn="internet",
        plmn_id="23410"
    )
    d = event.to_dict(logger)
    assert d["event_id"] == "test_id"
    assert d["imsi"] == "12345"
    assert d["plmn_id"] == "23410"

def test_save_to_json_mocked(generator, logger):
    events = [generator.generate_event(logger)]
    with patch("builtins.open", mock_open()) as mocked_file:
        with patch("json.dump") as mock_json_dump:
            generator.save_to_json(events, "test.json", logger)
            mock_json_dump.assert_called_once()
            mocked_file.assert_called_once_with("test.json", 'w')
