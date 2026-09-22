import pytest
from datetime import datetime, timedelta
from src.services.academic_calender_parser import get_full_academic_year 

def normalize(text):
    """Normalize text for comparison (e.g. geresh variations, extra spaces)"""
    return text.replace("״", "\"").replace("׳", "'").replace("״", '"').strip()

# Test the general structure of the function's output
def test_structure_of_result():
    """
    Ensure the output of get_full_academic_year is a dictionary
    containing 'semesters' and 'holidays' as lists.
    """
    data = get_full_academic_year()
    assert isinstance(data, dict), "Output should be a dictionary"
    assert "semesters" in data and "holidays" in data, "Should contain 'semesters' and 'holidays' keys"
    assert isinstance(data["semesters"], list), "'semesters' should be a list"
    assert isinstance(data["holidays"], list), "'holidays' should be a list"

# Test the structure and content of each semester
def test_semester_entries():
    """
    Check that each semester entry has the correct structure and valid dates.
    """
    data = get_full_academic_year()
    for sem in data["semesters"]:
        assert set(sem.keys()) == {"name", "start", "end"}, "Semester structure is invalid"
        assert isinstance(sem["name"], str), "Semester name should be a string"
        assert isinstance(sem["start"], datetime), "Semester start date should be datetime"
        assert isinstance(sem["end"], datetime), "Semester end date should be datetime"
        assert sem["start"] <= sem["end"], "Semester start date should be before end date"

# Test the structure and content of each holiday
def test_holiday_entries():
    """
    Check that each holiday entry has the correct structure and valid dates.
    """
    data = get_full_academic_year()
    for h in data["holidays"]:
        assert set(h.keys()) == {"title", "start", "end"}, "Holiday structure is invalid"
        assert isinstance(h["title"], str), "Holiday title should be a string"
        assert isinstance(h["start"], datetime), "Holiday start date should be datetime"
        assert isinstance(h["end"], datetime), "Holiday end date should be datetime"
        assert h["start"] <= h["end"], "Holiday start date should be before end date"

# Test that semester names include the expected ones
def test_expected_semesters_names():
    """
    Ensure that the expected semester names are present in the result.
    """
    data = get_full_academic_year()
    names = {s["name"] for s in data["semesters"]}
    expected = {"סמסטר א'", "סמסטר ב'", "סמסטר קיץ"}
    assert names.intersection(expected), "Expected semester names not found"

# Test that holiday titles include the expected ones
def test_expected_holidays_titles():
    """
    Ensure that the expected holiday titles are present in the result.
    """
    data = get_full_academic_year()
    titles = {h["title"] for h in data["holidays"]}
    expected = {
        "חופשת פורים",
        "חופשת פסח",
        "יום הזיכרון",
        "יום הזיכרון ויום העצמאות",
        "חופשת חג שבועות",
        "צום י\"ז תמוז",
        "צום ט' באב",
        "יום ירושלים"
    }
    matched = expected.intersection(titles)
    assert matched, f"Expected holiday titles not found. Found: {titles}"

def test_holidays_fall_within_academic_year():
    """
    The calendar is scraped live, so exact dates change every year. Instead of
    hard-coding one year's dates, check that every holiday lies inside the
    academic year described by the scraped semesters.
    """
    result = get_full_academic_year()
    semesters = result["semesters"]
    assert semesters, "No semesters were parsed"
    year_start = min(s["start"] for s in semesters) - timedelta(days=60)
    year_end = max(s["end"] for s in semesters)
    for holiday in result["holidays"]:
        assert year_start <= holiday["start"] <= year_end, (
            f"{holiday['title']} ({holiday['start']:%Y-%m-%d}) is outside the academic year "
            f"{year_start:%Y-%m-%d} - {year_end:%Y-%m-%d}"
        )
