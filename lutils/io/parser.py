from pathlib import Path
import numpy as np
import yaml

from lutils.core.types import DataFrame
from lutils.plot.labels import Labels


def parse_internal_field(path: Path) -> DataFrame:
    """
    Parses a CSV-style internal field file into a DataFrame.

    This function expects a comma-separated format where the first line contains
    headers and subsequent lines contain numerical data.

    Parameters
    ----------
    path : Path
        The file path to the CSV data file.

    Returns
    -------
    DataFrame
        A DataFrame instance containing the parsed numerical data.
    """
    if not path.exists():
        raise FileNotFoundError(f'Internal field file not found at: {path}')
    # Open and parse file
    with path.open() as f:
        lines = f.readlines()
        # Separate header
        header = lines[0].strip().split(',')
        data = []
        for line in lines[1:]:
            # Skip empty lines
            if not line.strip():
                continue
            values = line.strip().split(',')
            # Convert to float, convert to np.nan for empty cells
            row = [float(x) if x else np.nan for x in values]
            data.append(row)
    # Convert the list into np.ndarray
    arr = np.array(data)

    return DataFrame(header, arr)


def parse_residuals(path: Path) -> DataFrame:
    """
    Parses an OpenFOAM residuals file into a DataFrame.

    This function specifically handles OpenFOAM formatted logs where the header
    is located on the second line (prefixed with '#') and fields are whitespace-separated.

    Parameters
    ----------
    path : Path
        The file path to the residuals file.

    Returns
    -------
    DataFrame
        A DataFrame containing the residuals data. Values are converted to floats
        where possible; otherwise, they are kept as strings or NaN.
    """
    # Check if file exists
    if not path.exists():
        raise FileNotFoundError(f'Residuals file not found at: {path}')
    # Open and parse file
    with path.open() as f:
        lines = f.readlines()
        # Separate header
        header = lines[1].strip('#').split()
        data = []
        for line in lines[2:]:
            # Skip empty lines
            if not line.strip():
                continue
            values = line.strip().split()
            # Convert to float, if non convertable leave as is, covnert to np.nan for empty cells
            row = []
            for x in values:
                if x:
                    try:
                        row.append(float(x))
                    except:
                        row.append(x)
                else:
                    row.append(np.nan)
            data.append(row)
    # Convert the list into np.ndarray
    arr = np.array(data)

    return DataFrame(header, arr)


def parse_yaml_config(cfg_path: str) -> dict[str, str]:
    """
    Retrieves configuration labels from a preset or a YAML file.

    Parameters
    ----------
    cfg_path : str
        The configuration source. This can be a preset name
        ('velocity', 'k', 'nut', 'epsilon', 'omega') or a valid file path
        to a YAML configuration file.

    Returns
    -------
    dict[str, str]
        A dictionary mapping configuration keys to labels.

    Raises
    ------
    FileNotFoundError
        If `cfg_path` does not match a preset and the provided path does not exist.
    """
    # Check if input matches any preset labels
    labels = Labels()
    match cfg_path:
        case 'velocity':
            return labels.velocity
        case 'k':
            return labels.k
        case 'nut':
            return labels.nut
        case 'epsilon':
            return labels.epsilon
        case 'omega':
            return labels.omega
        case _:
            pass

    # Otherwise load labels from file
    path = Path(cfg_path)
    if not path.exists():
        raise FileNotFoundError(f'Config file not found at path: {path}')

    with path.open() as f:
        config = yaml.safe_load(f)

    return config
