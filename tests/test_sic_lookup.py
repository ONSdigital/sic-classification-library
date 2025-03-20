"""Tests for the SICLookup class.

This module contains pytest-based unit tests for the SICLookup class, which
provides functionality for looking up SIC codes and their associated metadata.

Fixtures:
    mock_data: Creates a temporary CSV file with mock SIC data.
    sic_lookup: Creates an instance of SICLookup using the mock data.
"""

# pylint: disable=redefined-outer-name

import pandas as pd
import pytest

from industrial_classification.lookup.sic_lookup import SICLookup
from industrial_classification.utils.constants import MIN_CLASSIFICATION_DIGITS


@pytest.fixture
def mock_data(tmp_path):
    """Creates a temporary CSV file with mock SIC data.

    Args:
        tmp_path (Path): Temporary directory provided by pytest.

    Returns:
        Path: Path to the temporary CSV file.
    """
    data = pd.DataFrame(
        {
            "label": ["12345", "23456", "34567"],
            "description": [
                "test description one",
                "test description two",
                "test description three",
            ],
        }
    )
    file_path = tmp_path / "mock_data.csv"
    data.to_csv(file_path, index=False)
    return file_path


@pytest.fixture
def sic_lookup(mock_data):
    """Creates an instance of SICLookup using the mock data.

    Args:
        mock_data (Path): Path to the mock SIC data CSV file.

    Returns:
        SICLookup: Instance of the SICLookup class.
    """
    return SICLookup(data_path=str(mock_data))


@pytest.mark.sic_lookup
def test_lookup_exact_match(sic_lookup):
    """Tests the lookup method for an exact match.

    Args:
        sic_lookup (SICLookup): Instance of the SICLookup class.
    """
    result = sic_lookup.lookup("test description one")
    assert result["code"] == "12345"
    assert result["description"] == "test description one"


@pytest.mark.sic_lookup
def test_lookup_no_match(sic_lookup):
    """Tests the lookup method when no match is found.

    Args:
        sic_lookup (SICLookup): Instance of the SICLookup class.
    """
    result = sic_lookup.lookup("nonexistent description")
    assert result["code"] is None


@pytest.mark.sic_lookup
def test_lookup_similarity(sic_lookup):
    """Tests the lookup method with similarity enabled.

    Args:
        sic_lookup (SICLookup): Instance of the SICLookup class.
    """
    result = sic_lookup.lookup("test description", similarity=True)
    assert "potential_matches" in result
    assert result["potential_matches"]["descriptions_count"] > 0


@pytest.mark.sic_meta
def test_lookup_code_division(sic_lookup):
    """Tests the lookup_code_division method.

    Args:
        sic_lookup (SICLookup): Instance of the SICLookup class.
    """
    result = sic_lookup.lookup_code_division("12345")
    assert result["code_division"] == "12"
    assert result["code_division_meta"] is not None


@pytest.mark.sic_lookup
def test_unique_code_divisions(sic_lookup):
    """Tests the unique_code_divisions method.

    Args:
        sic_lookup (SICLookup): Instance of the SICLookup class.
    """
    sic_candidates = [
        {"sic_code": "12345"},
        {"sic_code": "23456"},
        {"sic_code": "12345"},
    ]
    result = sic_lookup.unique_code_divisions(sic_candidates)
    assert len(result) == MIN_CLASSIFICATION_DIGITS
    assert any(div["code_division"] == "12" for div in result)
    assert any(div["code_division"] == "23" for div in result)


@pytest.mark.sic_lookup
def test_lookup_no_matching_code_meta(sic_lookup):
    """Tests lookup when no matching code meta is found (lines 96-98)."""
    result = sic_lookup.lookup("nonexistent description")
    assert result["code"] is None
    assert result["code_meta"] is None
    assert result["code_division_meta"] is None


@pytest.mark.sic_lookup
def test_lookup_code_division_no_meta(sic_lookup):
    """Tests lookup_code_division when no metadata is found (lines 192-195)."""
    result = sic_lookup.lookup_code_division("99999")
    assert result["code_division"] == "99"
    assert result["code_division_meta"]["detail"] is None


@pytest.mark.sic_lookup
def test_unique_code_divisions_empty_list(sic_lookup):
    """Tests unique_code_divisions with an empty list (lines 201-209)."""
    result = sic_lookup.unique_code_divisions([])
    assert result == []


@pytest.mark.sic_lookup
def test_unique_code_divisions_with_duplicates(sic_lookup):
    """Tests unique_code_divisions with duplicate SIC codes (lines 214-237)."""
    sic_candidates = [
        {"sic_code": "12345"},
        {"sic_code": "23456"},
        {"sic_code": "12345"},  # Duplicate
    ]
    result = sic_lookup.unique_code_divisions(sic_candidates)
    assert len(result) == MIN_CLASSIFICATION_DIGITS
    assert any(div["code_division"] == "12" for div in result)
    assert any(div["code_division"] == "23" for div in result)
