class Labels:
    """
    A container for preset plot label configurations.

    This class provides a set of standard dictionaries for common OpenFOAM
    field variables (Velocity, k, nut, epsilon, omega), containing
    pre-formatted LaTeX strings for titles and axis labels.
    """
    def __init__(
        self
    ) -> None:

        self._velocity = {
            'title': 'Velocity profile',
            'xlabel': '$y$ / $-$',
            'ylabel': '$U_x$ / $m \\cdot s^{-1}$'
        }
        self._k = {
            'title': 'Turbulence kinetic energy profile',
            'xlabel': '$y$ / $-$',
            'ylabel': '$k$ / $m^{2} \\cdot s^{-2}$'
        }
        self._nut = {
            'title': 'Turbulence viscosity profile',
            'xlabel': '$y$ / $-$',
            'ylabel': '$\\nu_t$ / $m^{2} \\cdot s^{-1}$'
        }
        self._epsilon = {
            'title': 'Average dissipation of turbulence kinetic ' +
            'energy profile',
            'xlabel': '$y$ / $-$',
            'ylabel': '$\\varepsilon$ / $m^{2} \\cdot s^{-3}$'
        }
        self._omega = {
            'title': 'Specific dissipation rate of turbulence kinetic ' +
            'energy profile',
            'xlabel': '$y$ / $-$',
            'ylabel': '$\\omega$ / s^{-1}$'
        }

    @property
    def velocity(
        self
    ) -> dict[str, str]:

        """dict[str, str]: Configuration for velocity plots."""

        return self._velocity

    @property
    def k(
        self
    ) -> dict[str, str]:

        """dict[str, str]: Configuration for turbulence kinetic energy ($k$) plots."""

        return self._k

    @property
    def nut(
        self
    ) -> dict[str, str]:

        """dict[str, str]: Configuration for turbulence viscosity ($\\nu_t$) plots."""

        return self._nut

    @property
    def epsilon(
        self
    ) -> dict[str, str]:

        """dict[str, str]: Configuration for average dissipation of $k$ ($\\varepsilon$) plots."""

        return self._epsilon

    @property
    def omega(
        self
    ) -> dict[str, str]:

        """dict[str, str]: Configuration for specific dissipation rate of $k$ ($\\omega$) plots."""

        return self._omega
