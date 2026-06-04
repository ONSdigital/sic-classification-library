"""Tests for SIC data access utilities."""

# pylint: disable=missing-function-docstring,redefined-outer-name,duplicate-code

from unittest.mock import ANY, patch

import pandas as pd
import pytest

from industrial_classification.data_access import sic_data_access


@pytest.fixture
def mock_sic_index_data():
    return pd.DataFrame(
        {"uk_sic_2007": ["12345", "67890"], "activity": ["Manufacturing", "Retail"]}
    )


@pytest.fixture
def mock_sic_structure_data():
    return pd.DataFrame(
        {
            "description": ["Section A", "Section B"],
            "section": ["A", "B"],
            "most_disaggregated_level": ["Level 1", "Level 2"],
            "level_headings": ["Heading 1", "Heading 2"],
        }
    )


@pytest.fixture
def sic_index_workbook_ref():
    return (
        "test.pkg",
        "uksic2007indexeswithaddendumdecember2022.xlsx",
    )


@patch("industrial_classification.data_access.sic_data_access.files")
@patch("industrial_classification.data_access.sic_data_access.pd.read_excel")
def test_load_sic_index(
    mock_read_excel, mock_files, mock_sic_index_data, sic_index_workbook_ref
):
    mock_files.return_value.joinpath.return_value = "dummy/sic_index.xlsx"
    mock_read_excel.return_value = mock_sic_index_data
    result = sic_data_access.load_sic_index(sic_index_workbook_ref)

    mock_read_excel.assert_called_once_with(
        ANY,
        sheet_name="Alphabetical Index",
        skiprows=2,
        usecols=["UK SIC 2007", "Activity"],
        dtype=str,
    )
    called_args, _ = mock_read_excel.call_args
    assert str(called_args[0]).endswith("sic_index.xlsx")
    mock_files.assert_called_once_with("test.pkg")
    assert result.equals(mock_sic_index_data)


@patch("industrial_classification.data_access.sic_data_access.files")
@patch("industrial_classification.data_access.sic_data_access.pd.read_excel")
def test_load_sic_structure(mock_read_excel, mock_files, mock_sic_structure_data):
    sic_structure_workbook_ref = (
        "test.pkg",
        "publisheduksicsummaryofstructureworksheet.xlsx",
    )
    mock_files.return_value.joinpath.return_value = "dummy/sic_structure.xlsx"
    mock_read_excel.return_value = mock_sic_structure_data
    result = sic_data_access.load_sic_structure(sic_structure_workbook_ref)

    mock_read_excel.assert_called_once_with(
        ANY,
        sheet_name="reworked structure",
        usecols=[
            "Description",
            "SECTION",
            "Most disaggregated level",
            "Level headings",
        ],
        dtype=str,
    )
    called_args, _ = mock_read_excel.call_args
    assert str(called_args[0]).endswith("sic_structure.xlsx")
    mock_files.assert_called_once_with("test.pkg")
    assert result.equals(mock_sic_structure_data)


@patch("industrial_classification.data_access.sic_data_access.load_hierarchy")
@patch("industrial_classification.data_access.sic_data_access.load_sic_structure")
@patch("industrial_classification.data_access.sic_data_access.load_sic_index")
def test_load_sic_hierarchy(
    mock_load_index,
    mock_load_structure,
    mock_load_hierarchy,
    mock_sic_index_data,
    mock_sic_structure_data,
):
    mock_load_index.return_value = mock_sic_index_data
    mock_load_structure.return_value = mock_sic_structure_data
    mock_hierarchy = object()
    mock_load_hierarchy.return_value = mock_hierarchy

    index_ref = ("pkg", "index.xlsx")
    structure_ref = ("pkg", "structure.xlsx")
    result = sic_data_access.load_sic_hierarchy(index_ref, structure_ref)

    mock_load_index.assert_called_once_with(index_ref)
    mock_load_structure.assert_called_once_with(structure_ref)
    mock_load_hierarchy.assert_called_once_with(
        mock_sic_structure_data, mock_sic_index_data
    )
    assert result is mock_hierarchy
