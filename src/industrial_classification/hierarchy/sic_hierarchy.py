"""SIC hierarchy.

Provides a common interface for SIC lookups and navigation.

Usage:

    sic = sic_hierarchy.load_hierarchy(sic_df, sic_index_df)
    sic["01110"].print_all()
"""

import html
import re
from collections.abc import Iterator

import pandas as pd

from industrial_classification.meta import sic_meta as sicDB
from industrial_classification.utils.constants import (
    FIVE_DIGITS,
    FOUR_DIGITS,
    SIX_DIGITS,
)

SEE_CODE_REGEX = re.compile(
    r"(,?\s?see\s(divisions?\s)?)?##\d+(\.\d+(\/\d)?)?", re.IGNORECASE
)

_LEVEL_DICT = {1: "section", 2: "division", 3: "group", 4: "class", 5: "subclass"}


class SicCode:
    """Standard Industrial Classification code.

    The main representation for SIC in this class is the `alpha_code`,
    which we define as:

        * The section character e.g. 'A'
        * Followed by the numeric SIC code e.g. "0111"
        * Padded with 'x' to six characters

    For example: "A0111x"

    The class supports initialisation with section, code and level via
    the factory method `from_section_code_level`.

    For example:
        SicCode.from_section_code_level("A", "0111", "class")

    Note:
        This class is mainly for internal use, beyond some basic checks
        of formatting and consistency it does not validate that a code
        is defined in UK SIC 2007.
    """

    def __init__(self, alpha_code: str):
        SicCode._validate_alpha_code(alpha_code)

        self.alpha_code = alpha_code
        self.n_digits = SicCode._parse_digits(alpha_code)
        self.level_name = _LEVEL_DICT[self.n_digits]
        self._formatted_code = SicCode._format_code(alpha_code)
        self._alpha_code_no_pad = self.alpha_code.replace("x", "")

    @staticmethod
    def from_section_code_level(section, code, level) -> "SicCode":
        """Creates a SicCode instance from section, code, and level.

        Args:
            section (str): The section character (e.g., "A").
            code (str): The numeric SIC code (e.g., "0111").
            level (str): The level name (e.g., "class").

        Returns:
            SicCode: A new instance of SicCode.

        Raises:
            ValueError: If there is a mismatch between code and level or section and code.
        """
        level = level.lower().strip().replace(" ", "")

        if len(code) < FIVE_DIGITS:
            n_digits = len(code)
            if _LEVEL_DICT[n_digits] != level:
                raise ValueError(f"Code/level mismatch: '{code}' -> '{level}'")

        elif len(code) == FIVE_DIGITS:
            if level not in {_LEVEL_DICT[4], _LEVEL_DICT[5]}:
                raise ValueError(f"Code/level mismatch: '{code}' -> '{level}'")

        if level == _LEVEL_DICT[1] and section != code:
            raise ValueError(f"Section/code mismatch: '{section}' - '{code}'")

        match level:
            case "section":
                alpha_code = f"{section}"

            case "class":
                if len(code) == FIVE_DIGITS:
                    if code[4] != "0":
                        raise ValueError(
                            f"4-digit SIC code as 5 digit must end in zero: '{code}'"
                        )
                    code = code[:4]
                alpha_code = f"{section}{code}"

            case _:
                alpha_code = f"{section}{code}"

        pad = 6 - len(alpha_code)
        alpha_code += "x" * pad

        return SicCode(alpha_code)

    def __eq__(self, other):
        """Checks equality between two SicCode instances.

        Args:
            other (SicCode): Another SicCode instance.

        Returns:
            bool: True if equal, False otherwise.
        """
        return self.alpha_code == other.alpha_code

    def __hash__(self):
        """Returns the hash of the SicCode instance.

        Returns:
            int: The hash value.
        """
        return hash(self.alpha_code)

    def __lt__(self, other):
        """Compares two SicCode instances for ordering.

        Args:
            other (SicCode): Another SicCode instance.

        Returns:
            bool: True if this instance is less than the other.
        """
        return self._alpha_code_no_pad < other._alpha_code_no_pad

    @staticmethod
    def _validate_alpha_code(alpha_code: str):
        """Validates the alpha_code format.

        Args:
            alpha_code (str): The alpha_code to validate.

        Raises:
            TypeError: If alpha_code is not a string.
            ValueError: If alpha_code does not meet format requirements.
        """
        if not isinstance(alpha_code, str):
            raise TypeError("SIC code must be a string")

        first_char = alpha_code[0]
        if not (first_char.isalpha() and first_char.isupper()):
            raise ValueError("Alpha SIC code must start with an upper case letter A-Z")

        if len(alpha_code) != SIX_DIGITS:
            raise ValueError("Alpha SIC must be padded to 6 characters")

    @staticmethod
    def _parse_digits(alpha_code: str):
        """Parses the number of digits in the alpha_code.

        Args:
            alpha_code (str): The alpha_code to parse.

        Returns:
            int: The number of digits.

        Raises:
            ValueError: If the alpha_code is invalid.
        """
        alpha_code = alpha_code.replace("x", "")

        if len(alpha_code) == 1:
            n_digits = 1

        else:
            n_digits = len(alpha_code[1:])
            if n_digits == 1:
                raise ValueError(f'Invalid SIC code: "{alpha_code}"')

        return n_digits

    @staticmethod
    def _format_code(alpha_code: str):
        """Formats the alpha_code into a readable string.

        Args:
            alpha_code (str): The alpha_code to format.

        Returns:
            str: The formatted code.

        Raises:
            ValueError: If the code cannot be formatted.
        """
        alpha_code = alpha_code.replace("x", "")

        formatted_code = None

        match len(alpha_code):
            case 1:
                formatted_code = alpha_code
            case 3:
                formatted_code = alpha_code[1:3]
            case 4 | 5:
                formatted_code = f"{alpha_code[1:3]}.{alpha_code[3:]}"
            case 6:
                formatted_code = f"{alpha_code[1:3]}.{alpha_code[3:5]}/{alpha_code[5]}"

        if formatted_code is None:
            raise ValueError(f'Unable to format code: "{alpha_code}"')

        return formatted_code

    def __str__(self):
        return self._formatted_code

    def __repr__(self):
        repr_str = f'SicCode("{self.alpha_code}")'
        return repr_str


class SicNode:
    """Tree data structure where the nodes hold all data associated with a given SIC.

    The SIC hierarchy is represented as several separate trees,
    with each section (e.g. "A", "B", "C") as a root node.
    """

    def __init__(self, sic_code: SicCode, description: str):
        self.sic_code = sic_code
        self.description = description

        self.activities: list[str] = []
        self.sic_meta = None
        self.parent = None
        self.children: list[SicNode] = []

    def __repr__(self):
        return f'SicNode({self.sic_code!r}, "{self.description}")'

    def __str__(self):
        return f'{self.sic_code!s}: "{self.description}"'

    def print_all(self):
        """Prints all information about the SIC hierarchy.

        Prints:
            - The string representation of the SIC hierarchy.
            - The section of the SIC code.
            - The parent of the current SIC hierarchy.
            - The children of the current SIC hierarchy.
            - The detail, includes, and excludes attributes of the SIC meta.
            - The activities associated with the SIC hierarchy.
        """
        print(str(self))

        print(f"Section: {self.sic_code.alpha_code[0]}")
        print(f"Parent: {self.parent}")
        print(f"Children: {[str(child) for child in self.children]}")
        print()
        print(f"detail={self.sic_meta.detail}")
        print(f"includes={self.sic_meta.includes}")
        print(f"excludes={self.sic_meta.excludes}")
        print()
        print("Activities:")
        for activity in self.activities:
            print(f"\t- {activity}")

    def is_leaf(self):
        """Checks if the node is a leaf node.

        Returns:
            bool: True if the node has no children, False otherwise.
        """
        return not self.children

    def numeric_string_padded(self):
        """Generates a numeric string representation of the SIC code, padded if necessary.

        Returns:
            str: The padded numeric string.
        """
        numeric_string = self.sic_code.alpha_code[1:].replace("x", "")

        if self.sic_code.n_digits == FOUR_DIGITS and self.is_leaf():
            numeric_string += "0"

        return numeric_string


class SIC:
    """Main class for SIC lookups.

    Usage:
        | sic = load_hierarchy(sic_df, sic_index_df)
        | sic["01.1"]
        | sic["011"]
        | sic["A011xx"]
    """

    def __init__(self, nodes, code_lookup):
        self.nodes = sorted(nodes, key=lambda node: node.sic_code)
        self._code_lookup = code_lookup

    def __getitem__(self, key):
        return self._code_lookup[key]

    def __iter__(self):
        return iter(self.nodes)

    def __len__(self):
        return len(self.nodes)

    def all_leaf_activities(self) -> Iterator[dict]:
        """Retrieves all activities for 5-digit SIC leaf nodes.

        Returns:
            Iterator[dict]: An iterator of dictionaries containing code and activity text.
        """
        return (
            {"code": node.sic_code, "text": activity}
            for node in self
            if node.is_leaf()
            for activity in node.activities
        )

    def all_leaf_descriptions(self) -> Iterator[dict]:
        """Retrieves all descriptions for 5-digit SIC leaf nodes.

        Returns:
            Iterator[dict]: An iterator of dictionaries containing code and description text.
        """
        return (
            {"code": node.sic_code, "text": node.description}
            for node in self
            if node.is_leaf()
        )

    def all_leaf_text(self) -> pd.DataFrame:
        """Generates a DataFrame of all short text descriptions for 5-digit SIC leaf nodes.

        Returns:
            pd.DataFrame: A DataFrame with columns `code` and `text`.
        """
        description_df = pd.DataFrame(self.all_leaf_descriptions())
        activity_df = pd.DataFrame(self.all_leaf_activities())

        df = pd.concat([description_df, activity_df], ignore_index=True)
        df = df.drop_duplicates()
        df = df.sort_values("code")
        df = df.reset_index(drop=True).copy()

        df["code"] = df["code"].apply(str)

        return df


def _define_codes_and_nodes(
    sic_df,
) -> tuple[list[SicCode], list[SicNode], dict[SicCode, SicNode]]:
    """Defines SIC codes and nodes from a DataFrame.

    Args:
        sic_df (pd.DataFrame): The DataFrame containing SIC data.

    Returns:
        tuple: A tuple containing a list of SicCode, a list of SicNode, and a
               dictionary mapping SicCode to SicNode.
    """
    codes = []
    nodes = []

    code_node_dict = {}

    for description, section, code, level in sic_df[
        ["description", "section", "most_disaggregated_level", "level_headings"]
    ].itertuples(index=False, name=None):
        sic_code = SicCode.from_section_code_level(section, code, level)

        sic_node = SicNode(sic_code, description=description)

        codes.append(sic_code)
        nodes.append(sic_node)
        code_node_dict[sic_code] = sic_node

    return codes, nodes, code_node_dict


def _populate_parent_child_relationships(nodes, code_node_dict):
    """Populates parent/child relationships in SIC nodes.

    Args:
        nodes (list[SicNode]): The list of SIC nodes.
        code_node_dict (dict[SicCode, SicNode]): A dictionary mapping SicCode to SicNode.

    Warning:
        Modifies nodes in place.
    """
    for node in nodes:
        if node.sic_code.n_digits > 1:
            match node.sic_code.n_digits:
                case 2:
                    parent_code = node.sic_code.alpha_code[0]
                case 3:
                    parent_code = node.sic_code.alpha_code[:3]
                case 4:
                    parent_code = node.sic_code.alpha_code[:4]
                case 5:
                    parent_code = node.sic_code.alpha_code[:5]
                case _:
                    raise ValueError(f"No parent found for '{node.sic_code}'")

            pad = 6 - len(parent_code)
            parent_code += "x" * pad
            parent_sic_code = SicCode(parent_code)

            parent_node = code_node_dict[parent_sic_code]

            parent_node.children.append(node)
            node.parent = parent_node


def _populate_sic_meta(nodes, code_node_dict):
    """Populates metadata for SIC nodes.

    Args:
        nodes (list[SicNode]): The list of SIC nodes.
        code_node_dict (dict[SicCode, SicNode]): A dictionary mapping SicCode to SicNode.

    Warning:
        Modifies nodes in place.

    Raises:
        ValueError: If there is a mismatch in SIC data sources.
    """
    if not len(sicDB.sic_meta) == len(nodes):
        raise ValueError("Mismatch in SIC data sources: sicDB.sic_meta and sic_df")

    for meta in sicDB.sic_meta:
        sic_code = SicCode(meta.code)
        sic_node = code_node_dict[sic_code]

        sic_node.sic_meta = _clean_meta(meta)


def _populate_activities(nodes, sic_index_df):
    """Populates activities for SIC nodes.

    Args:
        nodes (list[SicNode]): The list of SIC nodes.
        sic_index_df (pd.DataFrame): The DataFrame containing SIC index data.

    Warning:
        Modifies nodes in place.
    """
    padded_digits_to_sic_codes = {}

    for sic_node in nodes:
        sic_digits = None
        if sic_node.sic_code.n_digits == FOUR_DIGITS:
            sic_digits = sic_node.sic_code.alpha_code[1:5] + "0"
        if sic_node.sic_code.n_digits == FIVE_DIGITS:
            sic_digits = sic_node.sic_code.alpha_code[1:6]

        if sic_digits:
            padded_digits_to_sic_codes[sic_digits] = sic_node

    for sic_digits, activity in sic_index_df[["uk_sic_2007", "activity"]].itertuples(
        index=False, name=None
    ):
        padded_digits_to_sic_codes[sic_digits.strip()].activities.append(activity)


def _clean_text(text):
    """Cleans text by unescaping HTML and removing specific patterns.

    Args:
        text (str): The text to clean.

    Returns:
        str: The cleaned text.
    """
    clean_text = html.unescape(text)

    clean_text = re.sub(SEE_CODE_REGEX, "", clean_text)

    return clean_text


def _clean_meta(meta):
    """Cleans metadata for a SIC node.

    Args:
        meta (object): The metadata object to clean.

    Returns:
        object: The cleaned metadata object.
    """
    clean_detail = _clean_text(meta.detail)
    clean_includes = [_clean_text(text) for text in meta.includes]
    clean_excludes = [_clean_text(text) for text in meta.excludes]

    cleaned_meta = sicDB.ClassificationMeta(
        code=meta.code,
        title=meta.title,
        detail=clean_detail,
        includes=clean_includes,
        excludes=clean_excludes,
    )

    return cleaned_meta


def load_hierarchy(sic_df, sic_index_df):
    """Creates the SIC hierarchy from supporting data.

    Args:
        sic_df (pd.DataFrame): The DataFrame containing SIC structure data.
        sic_index_df (pd.DataFrame): The DataFrame containing SIC index data.

    Returns:
        SIC: An instance of the SIC class providing access to the hierarchy.
    """
    # Codes is unused but we need to unpack it to ensure the correct order
    _codes, nodes, code_node_dict = _define_codes_and_nodes(sic_df)

    _populate_parent_child_relationships(nodes, code_node_dict)

    _populate_sic_meta(nodes, code_node_dict)

    _populate_activities(nodes, sic_index_df)

    lookup = {}

    for node in nodes:
        lookup[str(node.sic_code)] = node
        lookup[node.sic_code.alpha_code] = node
        lookup[node.sic_code.alpha_code.replace("x", "")] = node
        if node.sic_code.n_digits > 1:
            lookup[node.sic_code.alpha_code[1:].replace("x", "")] = node

        if node.sic_code.n_digits == FOUR_DIGITS and not node.children:
            key = node.sic_code.alpha_code[1:5] + "0"
            lookup[key] = node

    return SIC(nodes, lookup)
