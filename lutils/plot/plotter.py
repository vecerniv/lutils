import matplotlib.pyplot as plt
import matplotlib.figure as fgr
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection
import yaml
from pathlib import Path
from typing import cast
import polars as pl
import numpy as np

from lutils.core.case import FoamCase
from lutils.plot.labels import Labels


class FoamPlot:

    """
    Base class for plotting OpenFOAM post-processing data.

    This class manages the configuration, storage, and rendering of plots
    derived from OpenFOAM cases. It handles data aggregation from multiple
    cases and output directory management.

    Parameters
    ----------
    plot_dir : str, optional
        The directory path where generated plots and CSV data will be saved.
        Default is './plots/'.
    """

    def __init__(
        self,
        plot_dir: str = './plots/'
    ) -> None:

        self._plot_data = {}
        self._interpolation_data = {}
        self._residual_data = {}

        self._plot_dir = Path(plot_dir)
        if not self._plot_dir.exists():
            self._plot_dir.mkdir()

    def _get_plot_config(
        self,
        label_path: str,
        style: str
    ) -> dict[str, str]:

        """
        Configures the matplotlib style and plot labels from a config file.

        Parameters
        ----------
        label_path : str
            The path to a YAML configuration file containing 'title',
            'xlabel', and 'ylabel' keys, or a preset name.
        style : str
            The valid matplotlib style sheet name to apply.

        Returns
        -------
        dict : [str, str]
            The dictionary with labels.

        Raises
        ------
        FileNotFoundError
            If `label_path` does not match a preset and the provided path does not exist.
        """

        # Set style
        plt.style.use(style)

        # Check if input matches any preset labels
        labels = Labels()
        match label_path:
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
        path = Path(label_path)
        if not path.exists():
            raise FileNotFoundError(f'Config file not found at path: {path}')

        with path.open() as f:
            config = yaml.safe_load(f)

        # Return dict with labels
        return config

    def field_add(
        self,
        case: FoamCase,
        field_name: str,
        label: str
    ) -> None:

        """
        Registers field data from a specific OpenFOAM case for plotting.

        Parameters
        ----------
        case : FoamCase
            The OpenFOAM case object containing the data.
        field_name : str
            The name of the field variable to extract (e.g., 'U', 'p').
        label : str
            The legend label to assign to this dataset in the plot.
        """

        self._plot_data[label] = case.fields[field_name]

    def field_delete(
        self,
        label: str
    ) -> None:

        """
        Removes specific field data from the plotting queue.

        Parameters
        ----------
        label : str
            The label of the dataset to remove.
        """

        try:
            del self._plot_data[label]
        except KeyError:
            print(f'Plot data with label "{label}" not found.')

    def interpolation_add(
        self,
        case: FoamCase,
        lower_corner: list[float],
        upper_corner: list[float]
    ) -> None:

        """
        Placeholder
        """

        int_data = case.get_interpolation()

        if not int_data:
            print(f'No interpolation data is loaded in case "{case.label}".')
            return

        scoped_data = int_data.scope_data(lower_corner, upper_corner)

        if scoped_data.is_empty():
            print('No points found in the ' +
                  f'"{lower_corner} - {upper_corner}" domain.')
            return

        self._interpolation_data[case.label] = scoped_data

    def interpolation_delete(
        self,
        case: FoamCase
    ) -> None:

        """
        Placeholder
        """

        try:
            del self._interpolation_data[case.label]
        except KeyError:
            print(f'Interpolation data for case "{case.label}" is not loaded.')

    def plot_interpolation(
        self
    ) -> None:

        """
        Placeholder
        """

        for key, value in self._interpolation_data.items():
            output_file = self._plot_dir / f'interpolation_{key}.png'
            self._plot_2D_interpolation(output_file, value, key)

    def _plot_2D_interpolation(
        self,
        output_file: Path,
        int_data: pl.DataFrame,
        label: str
    ) -> None:

        """
        Placeholder
        """

        # Un-normalize the surface normals get a clean look
        magnitude_x = abs(
            max(
                int_data['intPoint0_x']
                - int_data['intPoint2_x']
            )
        )
        magnitude_y = abs(
            max(
                int_data['intPoint0_y']
                - int_data['intPoint2_y']
            )
        )

        # Times 1.1 so points don't overlap
        surfNorm_x = (
            int_data['intPoint0_x']
            + magnitude_x*int_data['surfNorm_x']*1.1
        )
        surfNorm_y = (
            int_data['intPoint0_y']
            + magnitude_y*int_data['surfNorm_y']*1.1
        )

        # Reshape to fit LineCollection structure
        segments = np.column_stack((
            int_data['intPoint0_x'],
            int_data['intPoint0_y'],
            surfNorm_x,
            surfNorm_y
        )).reshape(-1, 2, 2)

        lines = LineCollection(
            segments,
            colors='black',
            label='surfNorm'
        )

        # Declare ax nad fig, because hinting for mpl is sus
        ax: Axes
        fig: fgr.Figure

        fig, ax = plt.subplots()

        ax.set_title(f'IBM interpolation - {label}')
        ax.set_xlabel('x')
        ax.set_ylabel('y')

        # Scaled surface normals
        ax.add_collection(lines)
        ax.autoscale()

        # First interpolation points - wall
        ax.scatter(
            x=int_data['intPoint0_x'],
            y=int_data['intPoint0_y'],
            marker='s',
            color='orange',
            label='intPoint0'
        )

        # Second interpolation points - first in-stream
        ax.scatter(
            x=int_data['intPoint1_x'],
            y=int_data['intPoint1_y'],
            marker='s',
            color='blue',
            label='intPoint1'
        )

        # Third interpolation points - second in-stream
        ax.scatter(
            x=int_data['intPoint2_x'],
            y=int_data['intPoint2_y'],
            marker='s',
            color='green',
            label='intPoint2'
        )

        fig.legend()
        fig.savefig(output_file)
        plt.close(fig)

    def plot_profile(
        self,
        output_file: str,
        field: str,
        data_axis: str,
        position_axis: str,
        position_value: float,
        position_tol: float,
        labels: str = 'velocity',
        style: str = 'lutils.profile',
        figure_id: str | int | None = None,
        out_csv: bool = True
    ) -> None:

        """
        Generates a profile plot by extracting data along a geometric slice.

        This method filters 3D field data to find cells close to a specific
        coordinate ('position_value') along a 'position_axis', effectively
        creating a line plot through the domain.

        Parameters
        ----------
        output_file : str
            The filename for the saved plot (e.g., 'profile.png').
        field : str
            The specific scalar component of the field to plot.
        data_axis : str
            The axis to plot against (usually the independent variable axis).
        position_axis : str
            The axis used to slice the domain (the fixed coordinate axis).
        position_value : float
            The coordinate value along `position_axis` where the slice is taken.
        position_tol : float
            The tolerance width around `position_value` to include cells.
        labels : str, optional
            The label configuration preset or path. Default is 'velocity'.
        style : str, optional
            The matplotlib style sheet to use. Default is 'lutils.plt_cfg.lutils'.
        figure_id : str or int or None, optional
            The unique identifier for the figure. If None, a new figure is created.
        out_csv : bool, optional
            If True, exports the sliced data to CSV files in the plot directory.
            Default is True.
        """

        # Get label and style
        config = self._get_plot_config(labels, style)

        # Retrieve figure
        fig, ax = self._get_figure_ax(figure_id)

        # Set labels
        ax.set_title(config['title'])
        ax.set_xlabel(config['xlabel'])
        ax.set_ylabel(config['ylabel'])

        # Plot all plot data entries
        for key, value in self._plot_data.items():
            trimmed = value.get_cells(
                position_axis,
                position_value,
                data_axis,
                position_tol
            )
            ax.scatter(
                trimmed[data_axis],
                trimmed[field],
                label=key
            )
            if out_csv:
                trimmed.write_csv(file=self._plot_dir / str(key+'.csv'))

        fig.legend()

        fig.savefig(self._plot_dir / output_file)

    def _get_figure_ax(
        self,
        figure_id: str | int | None
    ) -> tuple[fgr.Figure, fgr.Axes]:

        """
        Retrieves an existing figure or creates a new one.

        Parameters
        ----------
        figure_id : str or int or None
            A unique identifier for the figure.

        Returns
        -------
        matplotlib.figure.Figure
            An active matplotlib figure object.
        """

        if figure_id:
            fig = cast(
                fgr.Figure,
                plt.figure(figure_id)
            )
            ax = fig.gca()
        else:
            raw_fig, ax = plt.subplots()
            fig = cast(fgr.Figure, raw_fig)

        return fig, ax
