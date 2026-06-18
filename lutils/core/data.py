from pathlib import Path
import polars as pl


class FieldData:

    """
    A container for field data loaded from OpenFOAM output files.

    Parameters
    ----------
    file_path : str
        The path to the specific data file.
    field_name : str
        The name identifying this field.
    """

    def __init__(
        self,
        file_path: Path,
        field_name: str
    ) -> None:

        if not file_path.exists():
            raise FileNotFoundError(
                f'File not found at "{file_path}".'
            )

        # Parse data into DataFrame
        internal_field = pl.scan_csv(source=file_path, has_header=True)
        self.name = field_name

        # Filter relevant columns
        keys = ['x', 'y', 'z', self.name]
        self.data = internal_field.select(keys).collect()

    def get_cells(
        self,
        position_axis: str,
        position_value: float,
        data_axis: str,
        tol: float
    ) -> pl.DataFrame:

        """
        Extracts a subset of cells near a specific coordinate and sorts them.

        Parameters
        ----------
        position_axis : str
            The axis name to filter by (e.g., 'x', 'y', or 'z').
        position_value : float
            The target coordinate value along `position_axis`.
        data_axis : str
            The column name to use for sorting the resulting data.
        tol : float
            The tolerance radius around `position_value` for cell selection.

        Returns
        -------
        DataFrame
            A DataFrame containing the filtered cells, sorted by `data_axis`.
        """

        position_value = float(position_value)
        tol = float(tol)
        filtered_and_sorted = self.data.filter(
                ((pl.col(position_axis) - position_value).abs() < tol)
            ).sort(data_axis)

        return filtered_and_sorted


class ResidualData:

    """
    A container for residual data loaded from OpenFOAM output files.

    Parameters
    ----------
    file_path : pathlib.Path
        The path to the residuals file.
    fields : list[str], optional
        A list of specific residual fields to extract. If empty, all fields are loaded.
        Default is an empty list.
    """

    def __init__(
        self,
        file_path: Path
    ) -> None:

        if not file_path.exists():
            raise FileNotFoundError(
                f'File not found at "{file_path}".'
            )

        self.data = pl.read_csv(source=file_path, has_header=True, skip_rows=1)


class InterpolationData:

    """
    Placeholder
    """

    def __init__(
        self,
        file_path: Path
    ) -> None:

        if not file_path.exists():
            raise FileNotFoundError(
                f'File not found at "{file_path}".'
            )

        self.data = pl.read_csv(source=file_path, has_header=True)

    def scope_data(
        self,
        lower_corner: list[float],
        upper_corner: list[float]
    ) -> pl.DataFrame:

        """
        Placeholder
        """

        # Make sure values are floats
        lower_corner = list(map(float, lower_corner))
        upper_corner = list(map(float, upper_corner))

        # Only get data in the specified scope. Sphagetti filtering for now
        scoped = self.data.filter(
                pl.col("intPoint0_x") >= lower_corner[0],
                pl.col("intPoint0_x") <= upper_corner[0],
                pl.col("intPoint0_y") >= lower_corner[1],
                pl.col("intPoint0_y") <= upper_corner[1],
                pl.col("intPoint0_z") >= lower_corner[2],
                pl.col("intPoint0_z") <= upper_corner[2],
                )

        return scoped.clone()


class GeometryData:
    pass
