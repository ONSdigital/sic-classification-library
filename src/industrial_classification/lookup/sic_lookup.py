"""This module provides the `SICLookup` and `SICRephraseLookup` classes, which facilitate
the lookup of Standard Industrial Classification (SIC) codes based on descriptions and
rephrased descriptions. It also handles preprocessing of SIC data and provides metadata
for the classifications.

Classes:
    SICLookup: A class for loading SIC data, performing lookups, and managing metadata.
    SICRephraseLookup: A class for performing rephrased lookups of SIC codes.

"""

from typing import Any, Optional, Union

import pandas as pd

from industrial_classification.meta.sic_meta import SicMeta
from industrial_classification.utils.constants import FOUR_DIGITS


class SICLookup:
    """A class for performing lookups of SIC codes based on descriptions.

    Attributes:
        data (pd.DataFrame): The SIC data loaded from a CSV file.
        lookup_dict (dict[str, str]): A dictionary mapping descriptions to SIC codes.
        meta (SicMeta): Metadata for SIC classifications.

    Methods:
        lookup(description: str, similarity: bool = False) -> dict[str, Any]:
            Looks up an SIC code based on the given description.
    """

    def __init__(
        self,
        data_path: str = "src/industrial_classification/data/example_sic_lookup_data.csv",
    ):
        """Initialises the SICLookup class by loading SIC data from a CSV file.

        Args:
            data_path (str): The path to the CSV file containing SIC data.
        """
        # Load data and store descriptions in lowercase
        self.data: pd.DataFrame = pd.read_csv(data_path)
        self.data["description"] = self.data["description"].str.lower()

        # Some codes are 4 digits because they come from the 0x class
        # prepend a 0 to make 5 digits
        self.data["label"] = self.data["label"].apply(
            lambda x: f"0{x}" if len(str(x)) == FOUR_DIGITS else str(x)
        )

        self.lookup_dict: dict[str, str] = self.data.set_index("description").to_dict()[
            "label"
        ]
        self.meta: SicMeta = SicMeta(retrofit_keys=True)

    def lookup(self, description: str, similarity: bool = False) -> dict[str, Any]:
        """Looks up an SIC code based on the given description.

        Args:
            description (str): The description to look up.
            similarity (bool, optional): Whether to perform a similarity-based lookup.
                                         Defaults to False.

        Returns:
            dict[str, Any]: A dictionary containing the matching SIC code and metadata.
        """
        description = description.lower()

        matching_code: Optional[str] = self.lookup_dict.get(description)
        matching_code_meta: Optional[dict[str, Any]] = None
        division_meta: Optional[dict[str, Any]] = None

        # Extract the first 2 digits of the code as code_division
        matching_code_division: Optional[str] = None
        if matching_code:
            matching_code_division = matching_code[:2]
            # Lookup the meta data for the code
            matching_code_meta = self.meta.get_meta_by_code(matching_code)
            division_meta = self.meta.get_meta_by_code(matching_code_division)
            print(matching_code_meta)

        if not matching_code:
            matching_code = None

        potential_matches: dict[str, Any] = {}

        if similarity:
            # Check if the description is mentioned elsewhere in the dataset
            matches = self.data[
                self.data["description"].str.contains(description, na=False)
            ]
            potential_codes = matches["label"].unique()

            if len(potential_codes) == 1 and potential_codes[0] == matching_code:
                potential_codes = []  # Set it as an empty list instead of a dictionary
                potential_descriptions = []
                matches = []

            else:
                potential_codes = potential_codes.tolist()
                potential_descriptions = matches["description"].unique().tolist()

            division_codes = list({str(code)[:2] for code in potential_codes})

            # Get meta data associated with each division code
            divisions = [
                {
                    "code": division_code,
                    "meta": self.meta.get_meta_by_code(division_code),
                }
                for division_code in division_codes
            ]

            # Return the potential labels
            potential_matches = {
                "descriptions_count": len(matches),
                "descriptions": potential_descriptions,
                "codes_count": len(potential_codes),
                "codes": potential_codes,
                "divisions_count": len(division_codes),
                "divisions": divisions,
            }

        response: dict[str, Any] = {
            "description": description,
            "code": matching_code,
            "code_meta": matching_code_meta,
            "code_division": matching_code_division,
            "code_division_meta": division_meta,
        }
        if similarity:
            response["potential_matches"] = potential_matches

        return response

    def lookup_code_division(
        self, code: str
    ) -> dict[str, Optional[Union[str, dict[str, Any]]]]:
        """Retrieve code division from SIC code."""
        matching_code_meta: Optional[dict[str, Any]] = self.meta.get_meta_by_code(code)
        division_meta: Optional[dict[str, Any]] = None
        matching_code_division: Optional[str] = None
        if matching_code_meta:
            matching_code_division = code[:2]
            division_meta = self.meta.get_meta_by_code(matching_code_division)
        return {
            "code_division": matching_code_division,
            "code_division_meta": division_meta,
        }

    def unique_code_divisions(
        self, sic_candidates: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Retrieve unique code divisions from SIC candidates."""
        unique_divisions: dict[str, dict[str, Any]] = {}

        for candidate in sic_candidates:
            division_info = self.lookup_code_division(candidate["sic_code"])
            code_division = division_info["code_division"]

            # Only add unique divisions
            if isinstance(code_division, str) and code_division not in unique_divisions:
                unique_divisions[code_division] = division_info

        return list(unique_divisions.values())


class SICRephraseLookup:
    """A class for performing rephrased lookups of SIC codes based on descriptions.

    This class extends the functionality of SIC lookups by allowing for
    rephrased or alternative descriptions to be matched to SIC codes.

    Attributes:
        rephrase_dict (dict[str, str]): A dictionary mapping rephrased descriptions
            to their corresponding SIC codes.
        meta (SicMeta): Metadata for SIC classifications.

    Methods:
        rephrase_lookup(description: str) -> dict[str, Any]:
            Looks up an SIC code based on a rephrased description.
        add_rephrase_mapping(original: str, rephrased: str) -> None:
            Adds a new rephrase mapping to the lookup dictionary.
    """

    def __init__(
        self,
        data_path: str = "src/industrial_classification/data/example_rephrased_sic_data.csv",
    ):
        # Load SIC rephrased descriptions and treat SIC column as string
        self.data: pd.DataFrame = pd.read_csv(data_path, dtype={"sic_code": str})

        # Create a lookup dictionary for quick access
        self.lookup_dict: dict[str, str] = self.data.set_index("sic_code")[
            "reviewed_description"
        ].to_dict()

    def lookup(self, sic_code: Union[str, int]) -> dict[str, Union[str, Any]]:
        """Retrieve reviewed description for the given SIC code."""
        sic_code = str(sic_code)

        if sic_code in self.lookup_dict:
            return {
                "sic_code": sic_code,
                "reviewed_description": self.lookup_dict[sic_code],
            }

        return {"sic_code": sic_code, "error": "SIC code not found"}

    def process_json(self, input_json: dict[str, Any]) -> dict[str, Any]:
        """Process a JSON response to rephrase SIC descriptions."""
        # Update main SIC description
        rephrased_sic_description: Optional[dict[str, Union[str, Any]]] = None

        rephrased_sic_description = (
            self.lookup(input_json["sic_code"])
            if input_json["sic_code"] is not None
            else None
        )

        if rephrased_sic_description:
            input_json["sic_description"] = rephrased_sic_description[
                "reviewed_description"
            ]
        else:
            input_json["sic_description"] = None

        # Update SIC candidates
        for candidate in input_json["sic_candidates"]:
            rephrased_descriptive = self.lookup(candidate["sic_code"])
            if rephrased_descriptive:
                candidate["sic_descriptive"] = rephrased_descriptive[
                    "reviewed_description"
                ]

        return input_json
