import matplotlib.pyplot as plt
import matplotlib.figure as fgr
from pathlib import Path
from typing import cast

from lutils.core.data import FoamCase
from lutils.utils.misc import check_dir
from lutils.io.parser import parse_yaml_config


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

    def __init__(self,
                 plot_dir: str = './plots/') -> None:
        self._plot_dir = Path(plot_dir)
        self._plot_data = {}

        if not self._plot_dir.exists():
            self._plot_dir.mkdir()

    def _get_plot_config(self,
                         label_path: str
                         #style: str
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
        """
        # Set style
        #plt.style.use(style)

        # Return dict with labels
        return parse_yaml_config(label_path)

    def add_data(self,
                 case: FoamCase,
                 field_name: str,
                 label: str) -> None:
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

    def del_data(self,
                 label: str) -> None:
        """
        Removes a specific dataset from the plotting queue.

        Parameters
        ----------
        label : str
            The label of the dataset to remove.
        """
        try:
            del self._plot_data[label]
        except KeyError:
            print(f'Plot data with label "{label}" not found.')

    def plot_profile(self,
                     output_file: str,
                     field: str,
                     data_axis: str,
                     position_axis: str,
                     position_value: float,
                     position_tol: float,
                     labels: str = 'velocity',
                     #style: str = 'lutils.plt_cfg.lutils',
                     figure_id: str | int | None = None,
                     out_csv: bool = True) -> None:
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
        config = self._get_plot_config(labels)

        # Retrieve figure
        fig, ax = self._get_figure_ax(figure_id)

        # Set labels
        ax.set_title(config['title'])
        ax.set_xlabel(config['xlabel'])
        ax.set_ylabel(config['ylabel'])

        # Plot all plot data entries
        for key, value in self._plot_data.items():
            trimmed = value.get_cells(
                position_axis, position_value, data_axis, position_tol)
            ax.scatter(trimmed[data_axis],
                       trimmed[field], label=key)
            if out_csv:
                trimmed.to_csv(self._plot_dir / str(key+'.csv'))

        fig.legend()

        fig.savefig(self._plot_dir / output_file)

    def _get_figure_ax(self,
                       figure_id: str | int | None) -> tuple[fgr.Figure, fgr.Axes]:
        """
        Retrieves an existing figure or creates a new one.

        Parameters
        ----------
        figure_id : str or int or None
            The unique identifier for the figure.

        Returns
        -------
        matplotlib.figure.Figure
            The active matplotlib figure object.
        """
        if figure_id:
            fig = cast(fgr.Figure, plt.figure(figure_id))
            ax = fig.gca()
        else:
            raw_fig, ax = plt.subplots()
            fig = cast(fgr.Figure, raw_fig)

        return fig, ax
