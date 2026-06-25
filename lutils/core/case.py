from pathlib import Path
import subprocess
import polars as pl

from lutils.core.data import FieldData, InterpolationData, ResidualData
from lutils.core.utils import get_latest_time


class FoamCase:

    """
    A base class representing an OpenFOAM case.

    This class manages the case directory structure, handles script execution,
    and facilitates the loading and storage of post-processing data.

    Parameters
    ----------
    case_path : str

    label : str
        A unique label or identifier for the case.
    of_distribution : str, optional
        The specific OpenFOAM distribution used.
        Default is org.

    Attributes
    ----------
    case_path : Path
        The file path to the OpenFOAM case directory.
    label : str
        A unique indentifier for the case.
    fields : dict[str, FieldData]
        A dictionary of {field_name: FieldData} values.
    of_distribution : str
        The type of OpenFOAM distribution ('com' for ESI/OpenCFD, 'org' for Foundation).
    """

    def __init__(
        self,
        case_path: str,
        label: str,
        of_distribution: str = 'org'
    ) -> None:

        if not Path(case_path).is_dir():
            raise FileNotFoundError(
                    f'Case not found at {case_path}.'
                )

        self.case_path = Path(case_path)
        self.label = label
        self.of_distribution = of_distribution
        self.fields = {}
        self.residuals = None
        self.interpolation = None

    def run_script(
        self,
        file_name: str
    ) -> None:

        """
        Executes an arbitrary script within the context of the OpenFOAM case.

        Parameters
        ----------
        file_name : str
            The path to the script file. If a relative path is provided, it is
            resolved relative to the case directory. Absolute paths are used as-is.

        Raises
        ------
        FileNotFoundError
            If the script file does not exist at the resolved path.
        RuntimeError
            If the script execution fails (returns a non-zero exit code) or if an
            unexpected error occurs during execution.
        """

        script_path = Path(file_name)

        # Check if script_path is absolute, else run relative to dir case
        if script_path.is_absolute():
            command = str(script_path)

            if not script_path.exists():
                raise FileNotFoundError(
                    f'Script file not found at absolute path: {script_path}'
                )
        else:
            full_script_path = self.case_path / script_path

            if not full_script_path.exists():
                raise FileNotFoundError(
                    'Script file not found inside case directory: ' +
                    f'{full_script_path}'
                )

            command = f'./{file_name}'

        try:
            # Run script inside case directory
            subprocess.run(command, cwd=self.case_path, check=True)
        except subprocess.CalledProcessError as e:
            err_msg = (
                f'Script execution failed for case "{self.label}" ' +
                f'at path: {self.case_path}.'
            )
            raise RuntimeError(err_msg) from e
        except Exception as e:
            raise RuntimeError(
                'An unexpected error occured while trying to run script ' +
                f'"{file_name}" for case "{self.label}": {e}'
            )

    def field_add(
        self,
        file_path: str,
        field_name: str
    ) -> None:

        """
        Loads field data from a file and registers it to the case.

        Parameters
        ----------
        file_path : str
            The path to the data file, relative to the case directory.
        field_name : str
            The unique name (key) to assign to this field data.
        """

        path = self.case_path / file_path

        self.fields[field_name] = FieldData(
            path, field_name
        )

    def field_delete(
        self,
        field_name: str
    ) -> None:

        """
        Removes a specified field from the case.

        Parameters
        ----------
        field_name : str
            The name of the field to delete.
        """

        try:
            del self.fields[field_name]
        except ValueError:
            print(
                f'Field "{field_name}" is not in "{self.label}" fields.'
            )

    def residuals_add(
        self,
        file_path: str
    ) -> None:

        """
        Loads residual data from a specified file.

        Parameters
        ----------
        file_path : str
            The path to the residuals file, relative to the case directory.
        fields : list[str], optional
            A list of specific residual fields to load. If empty, all available
            fields are loaded. Default is an empty list.
        """

        path = self.case_path / file_path

        self.residuals = ResidualData(path)

    def get_residuals(
        self
    ) -> ResidualData | None:

        """
        Placeholder
        """

        return self.residuals

    def interpolation_add(
        self,
        file_path: str
    ) -> None:

        """
        Placeholder
        """

        path = self.case_path / file_path

        self.interpolation = InterpolationData(path)

    def get_interpolation(
        self
    ) -> InterpolationData | None:

        """
        Placeholder
        """

        return self.interpolation

    def get_yplus(
        self
    ) -> None:

        """
        Placeholder
        """

        dir = get_latest_time(self.case_path)
        if dir <= 0:
            print(f'No simulation time was found for case "{self.label}"')
            return

        dir = str(dir)
        file = self.case_path / dir / 'yOrthoi'

        if not file.exists():
            print(f'"yOtrhoi" not found in directory "{dir}"' +
                  f' for case "{self.label}".')
            return

        data = []
        in_brackets = False
        with file.open() as f:
            for line in f:
                clean_line = line.strip()
                if clean_line == '(':
                     in_brackets = True
                     continue

                if clean_line == ')':
                    in_brackets = False
                    continue

                if in_brackets:
                    value = float(line)
                    if value <= 0:
                        continue
                    data.append(value)

        df = pl.DataFrame(data)

        print(f'y+ for case: {self.label}')
        print(f'    mean: {df.mean().item()}')
        print(f'    min:  {df.min().item()}')
        print(f'    max:  {df.max().item()}')
