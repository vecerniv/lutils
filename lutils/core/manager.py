from lutils.core.case import FoamCase


class CaseManager:

    """
    A manager class for controlling multiple OpenFOAM cases.

    This class acts as a registry for FoamCase objects, allowing for batch
    execution of scripts and management of case instances via unique labels.

    Parameters
    ----------
    case_paths : list[str]
        A list of file paths to the OpenFOAM case directories.
    case_labels : list[str]
        A list of unique labels corresponding to each case path.

    Attributes
    ----------
    cases : dict[str, FoamCase]
        A dictionary mapping unique case labels to their corresponding
        FoamCase objects.
    """

    def __init__(
        self,
        case_paths: list[str],
        case_labels: list[str]
    ) -> None:

        self.cases = {}
        # Load each case into dict
        for path, label in zip(case_paths, case_labels):
            self.add_case_by_path(path, label)

    def run_script(
        self,
        file_name: str,
        case_labels: list[str] | None = None
    ) -> None:

        """
        Executes an arbitrary script across selected OpenFOAM cases.

        Parameters
        ----------
        file_name : str
            The name or path of the script to execute. Relative paths are
            assumed to be relative to the specific case directory.
        case_labels : list[str], optional
            A list of specific case labels to run the script on. If None,
            the script is executed on all managed cases. Default is None.

        Raises
        ------
        KeyError
            If a label provided in `case_labels` does not exist in the manager.
        """

        # Select cases based on input
        if not case_labels:
            cases = list(self.cases.values())
        else:
            cases = [self.cases[label] for label in case_labels]
        # Run script inside case directories
        for case in cases:
            case.run_script(file_name)

    def add_case_by_path(
        self,
        path: str,
        case_label: str
    ) -> None:

        """
        Instantiates a FoamCase and registers it to the manager.

        Parameters
        ----------
        path : str
            The file path to the OpenFOAM case directory.
        case_label : str
            The unique identifier for this case.

        Raises
        ------
        ValueError
            If the case path is invalid, if FoamCase initialization fails,
            or if the 'case_label' already exists in the manager.
        """

        try:
            case = FoamCase(path, case_label)

        except (FileNotFoundError, OSError, ValueError) as e:
            raise ValueError(
                'Error adding case to manager. Invalid path or internal ' +
                'FoamCase creation failed.'
                f'Check path: {path}.'
            ) from e

        if case_label in self.cases:
            raise ValueError(
                f'Unique Label Error: A case with label "{case_label}" ' +
                'already in the manager!')

        self.cases[case.label] = case

    def get_cases(
        self
    ) -> list:

        """
        Placeholder description
        """

        return list(self.cases.values())
