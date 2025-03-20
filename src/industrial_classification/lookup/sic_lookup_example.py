"""This module provides example usage of the SICLookup and SICRephraseLookup classes.

Classes:
    SICLookup: Provides methods for looking up SIC codes and their divisions.
    SICRephraseLookup: Provides methods for rephrasing SIC descriptions.

Example Usage:
    - Demonstrates how to use SICLookup to retrieve SIC code information.
    - Demonstrates how to use SICRephraseLookup to rephrase SIC
      descriptions and process JSON responses.
"""

from typing import Any

from industrial_classification.lookup.sic_lookup import SICLookup, SICRephraseLookup

# Example usage of SICLookup
print("Example usage of SICLookup")
sic_lookup = SICLookup(
    data_path="src/industrial_classification/data/example_sic_lookup_data.csv"
)
result = sic_lookup.lookup("Gamekeeper")
print(result)

print("\n")
print("Example usage of SICLookup with code division")
sic_lookup = SICLookup(
    data_path="src/industrial_classification/data/example_sic_lookup_data.csv"
)
result = sic_lookup.lookup_code_division("01700")
print(result)

print("\n")
print("Example usage of SICLookup with unique code division")
sic_lookup = SICLookup(
    data_path="src/industrial_classification/data/example_sic_lookup_data.csv"
)
result_list: list[dict[str, Any]] = sic_lookup.unique_code_divisions(
    [{"sic_code": "01700"}, {"sic_code": "01120"}, {"sic_code": "31010"}]
)
print(result_list)

print("\n")
print("Example usage of SICRephraseLookup with lookup")
# Example usage of SICRephraseLookup
sic_rephrase_lookup = SICRephraseLookup(
    data_path="src/industrial_classification/data/example_rephrased_sic_data.csv"
)

# Retrieve reviewed description for a specific SIC code
rephrased_result = sic_rephrase_lookup.lookup("01300")
print(rephrased_result)

print("\n")
print("Example usage of SICRephraseLookup with process_json")
# Process a JSON response to rephrase SIC descriptions
input_json = {
    "sic_code": "01300",
    "sic_candidates": [{"sic_code": "01110"}, {"sic_code": "01120"}],
}
processed_json = sic_rephrase_lookup.process_json(input_json)
print(processed_json)
