"""Module for testing the structure and integrity of the SICmeta dictionary.

This module contains unit tests to validate that the SICmeta dictionary
follows the expected structure, including key types, value types, and
the presence of required fields. It also ensures that optional fields,
if present, conform to the expected data types.
"""

import pytest

from industrial_classification.meta.sic_meta import SICmeta


@pytest.mark.sic_meta
def test_sic_meta_structure():
    """Test the structure and integrity of the SICmeta dictionary.

    This test validates that the SICmeta dictionary adheres to the expected
    structure and data types. It checks the following:

    - SICmeta is a dictionary.
    - Each key in SICmeta is a string.
    - Each value in SICmeta is a dictionary.
    - Required fields ('title') are present and of the correct type.
    - Optional fields ('detail', 'includes', 'excludes'), if present, conform
      to the expected data types.

    Raises:
        AssertionError: If any of the above conditions are not met.
    """
    # Ensure SICmeta is a dictionary
    assert isinstance(SICmeta, dict), "SICmeta should be a dictionary"

    for code, metadata in SICmeta.items():
        # Ensure each key is a string
        assert isinstance(code, str), f"Key '{code}' should be a string"

        # Ensure each value is a dictionary
        assert isinstance(
            metadata, dict
        ), f"Value for key '{code}' should be a dictionary"

        # Check required fields in metadata
        assert "title" in metadata, f"Key '{code}' is missing 'title'"
        assert isinstance(
            metadata["title"], str
        ), f"'title' for key '{code}' should be a string"

        if "detail" in metadata:
            assert isinstance(
                metadata["detail"], str
            ), f"'detail' for key '{code}' should be a string"

        if "includes" in metadata:
            assert isinstance(
                metadata["includes"], list
            ), f"'includes' for key '{code}' should be a list"
            for item in metadata["includes"]:
                assert isinstance(
                    item, str
                ), f"Items in 'includes' for key '{code}' should be strings"

        if "excludes" in metadata:
            assert isinstance(
                metadata["excludes"], list
            ), f"'excludes' for key '{code}' should be a list"
            for item in metadata["excludes"]:
                assert isinstance(
                    item, str
                ), f"Items in 'excludes' for key '{code}' should be strings"
