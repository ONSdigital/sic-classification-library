"""SIC data access for packaged ONS UK SIC 2007 workbooks.

Hierarchy and embedding flows (``sic-classification-utils``) load index and structure
from Excel via ``(package_name, filename)`` tuples, matching the previous utils module
behaviour. Lookup flows use ``SICLookup`` with CSV paths separately.
"""

from __future__ import annotations

import logging
from importlib.resources import files

import pandas as pd

from industrial_classification.hierarchy.sic_hierarchy import SIC, load_hierarchy

logger = logging.getLogger(__name__)

SicIndexSource = tuple[str, str]
SicStructureSource = tuple[str, str]


def load_sic_index(resource_ref: SicIndexSource) -> pd.DataFrame:
    """Load the SIC index from an Excel workbook.

    The SIC index provides a list of around 15,000 activities and their
    associated 5-digit SIC codes.

    Args:
        resource_ref: ``(package_name, xlsx_filename)`` for the ONS index workbook.

    Returns:
        DataFrame with ``uk_sic_2007`` and ``activity`` columns.
    """
    pkg, filename = resource_ref
    file_path = files(pkg).joinpath(filename)

    logger.debug("Loading SIC index from %s", file_path)

    sic_index_df = pd.read_excel(
        file_path,
        sheet_name="Alphabetical Index",
        skiprows=2,
        usecols=["UK SIC 2007", "Activity"],
        dtype=str,
    )

    sic_index_df.columns = [
        col.lower().replace(" ", "_") for col in sic_index_df.columns
    ]

    return sic_index_df


def load_sic_structure(resource_ref: SicStructureSource) -> pd.DataFrame:
    """Load the SIC structure from an Excel workbook.

    Args:
        resource_ref: ``(package_name, xlsx_filename)`` for the ONS structure workbook.

    Returns:
        DataFrame with ``description``, ``section``, ``most_disaggregated_level``,
        and ``level_headings`` columns.
    """
    pkg, filename = resource_ref
    file_path = files(pkg).joinpath(filename)

    logger.debug("Loading SIC structure from %s", file_path)

    sic_df = pd.read_excel(
        file_path,
        sheet_name="reworked structure",
        usecols=[
            "Description",
            "SECTION",
            "Most disaggregated level",
            "Level headings",
        ],
        dtype=str,
    )

    sic_df.columns = [col.lower().replace(" ", "_") for col in sic_df.columns]

    for col in sic_df.columns:
        sic_df[col] = sic_df[col].str.strip()

    return sic_df


def load_sic_hierarchy(
    index_ref: SicIndexSource, structure_ref: SicStructureSource
) -> SIC:
    """Load SIC hierarchy from packaged index and structure workbooks."""
    sic_index_df = load_sic_index(index_ref)
    sic_df = load_sic_structure(structure_ref)
    return load_hierarchy(sic_df, sic_index_df)


def load_text_from_config(config_section: tuple[str, str]) -> str:
    """Load UTF-8 text from a packaged resource tuple ``(package_name, filename)``."""
    pkg, filename = config_section
    file_path = files(pkg).joinpath(filename)

    logger.debug("Loading text from %s", file_path)

    with file_path.open(encoding="utf-8") as f:
        return f.read()
