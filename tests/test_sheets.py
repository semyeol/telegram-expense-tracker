import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import Mock, patch, MagicMock
from app.sheets import convert_timestamp, append_transaction


# convert timestamp tests
def test_converts_to_correct_year():
    # Oct 28, 2025, 10:00 AM UTC
    timestamp = 1761652800

    local_time, year, month, day = convert_timestamp(timestamp)

    assert year == 2025
    assert month == 10
    assert day == 28


def test_converts_to_pst_timezone():
    timestamp = 1761652800

    local_time, year, month, day = convert_timestamp(timestamp)

    assert local_time.tzinfo == ZoneInfo("America/Los_Angeles")


# month abbreviation tests
@pytest.mark.parametrize("month_num,expected_abbr", [
    (1, "JAN"),
    (2, "FEB"),
    (3, "MAR"),
    (4, "APR"),
    (5, "MAY"),
    (6, "JUN"),
    (7, "JUL"),
    (8, "AUG"),
    (9, "SEP"),
    (10, "OCT"),
    (11, "NOV"),
    (12, "DEC"),
])
def test_month_abbreviation_matches_sheet_names(month_num, expected_abbr):
    dt = datetime(2025, month_num, 15, tzinfo=ZoneInfo("America/Los_Angeles"))
    actual_abbr = dt.strftime("%b").upper()
    assert actual_abbr == expected_abbr


# append transaction tests
@patch('app.sheets.sheets_service')
@patch('app.sheets.convert_timestamp')
def test_rejects_low_confidence(mock_convert_timestamp, mock_sheets_service):
    # setup
    mock_convert_timestamp.return_value = (Mock(), 2025, 10, 28)

    parsed_data = {
        "description": "Coffee",
        "category": "Eating Out",
        "amount": 5,
        "confidence": 0.85  
    }

    result = append_transaction("fake_spreadsheet_id", 1234567890, parsed_data)

    assert result is False
    mock_sheets_service.spreadsheets.assert_not_called()


@patch('app.sheets.sheets_service')
@patch('app.sheets.convert_timestamp')
def test_accepts_high_confidence(mock_convert_timestamp, mock_sheets_service):
    # setup mock datetime
    mock_time = Mock()
    mock_time.strftime = Mock(side_effect=lambda fmt: "2025-10-28" if fmt == "%Y-%m-%d" else "OCT")
    mock_convert_timestamp.return_value = (mock_time, 2025, 10, 28)

    parsed_data = {
        "description": "Coffee",
        "category": "Eating Out",
        "amount": 5,
        "confidence": 0.95  
    }

    mock_sheets_service.spreadsheets().values().append().execute.return_value = {}

    result = append_transaction("fake_spreadsheet_id", 1234567890, parsed_data)

    assert result is True
    mock_sheets_service.spreadsheets().values().append.assert_called_once()


@patch('app.sheets.sheets_service')
@patch('app.sheets.convert_timestamp')
def test_formats_row_correctly(mock_convert_timestamp, mock_sheets_service):
    mock_time = Mock()
    mock_time.strftime = Mock(side_effect=lambda fmt: "2025-10-28" if fmt == "%Y-%m-%d" else "OCT")
    mock_convert_timestamp.return_value = (mock_time, 2025, 10, 28)

    parsed_data = {
        "description": "Golf",
        "category": "Activity",
        "amount": 22.50,
        "confidence": 0.97
    }

    # mock API
    mock_append = MagicMock()
    mock_sheets_service.spreadsheets().values().append.return_value = mock_append
    mock_append.execute.return_value = {}

    append_transaction("test_id", 1234567890, parsed_data)

    call_kwargs = mock_sheets_service.spreadsheets().values().append.call_args[1]
    expected_row = ["Golf", "Activity", 22.50, "2025-10-28", "Work"]
    assert call_kwargs['body']['values'][0] == expected_row


@patch('app.sheets.sheets_service')
@patch('app.sheets.convert_timestamp')
def test_targets_correct_month_sheet(mock_convert_timestamp, mock_sheets_service):
    mock_time = Mock()
    mock_time.strftime = Mock(side_effect=lambda fmt: "2025-10-28" if fmt == "%Y-%m-%d" else "OCT")
    mock_convert_timestamp.return_value = (mock_time, 2025, 10, 28)

    parsed_data = {
        "description": "Test",
        "category": "Other",
        "amount": 10,
        "confidence": 0.95
    }

    mock_append = MagicMock()
    mock_sheets_service.spreadsheets().values().append.return_value = mock_append
    mock_append.execute.return_value = {}

    append_transaction("test_id", 1234567890, parsed_data)

    call_kwargs = mock_sheets_service.spreadsheets().values().append.call_args[1]
    assert call_kwargs['range'] == "OCT!D:H"