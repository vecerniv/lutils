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

        with file_path.open() as f:
            f.readline()
            line = f.readline()
            col_names = line.strip('#').split()

        data = pl.read_csv(
            source=file_path,
            skip_rows=3,
            separator='\t',
            new_columns=col_names
        )

        stripped_time = data.select(
            pl.col('Time').str.strip_chars()
        ).to_series(0).str.to_integer()

        data = data.replace_column(0, stripped_time)

        self.data = data

    def get_columns(
        self
    ) -> list[pl.Series]:

        """
        Placeholder
        """

        out = []

        for col in self.data:
            out.append(col)

        return out


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
                pl.col("bCell_x") >= lower_corner[0],
                pl.col("bCell_x") <= upper_corner[0],
                pl.col("bCell_y") >= lower_corner[1],
                pl.col("bCell_y") <= upper_corner[1],
                pl.col("bCell_z") >= lower_corner[2],
                pl.col("bCell_z") <= upper_corner[2],
                )

        return scoped.clone()


class GeometryData:
    pass
