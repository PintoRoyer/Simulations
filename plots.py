"""
Plots
=====

Description
-----------
This module provides to plot maps from netcdf files. Different types of intern organization can be
managed throught a reader class.

Class
-----
Map
"""

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt


class Map:
    """
    This class provides some minimum functions to plot ``contourf``, ``contour`` and ``quiver`` on a
    map.

    Attributes
    ----------
    reader : class
        An instance of a reader class.
    axes : plt.Axes
        The axes to plot the map on.
    """

    def __init__(self, reader):
        """Constructor method."""
        self.reader = reader
        self.axes = None

    def init_axes(
        self,
        axes: plt.axes = None,
        *,
        fig_kw: dict = None,
        axes_kw: dict = None,
        feature_kw: dict = None,
        glines_kw: dict = None
    ):
        """
        Init the axes with geoaxes. If no axes is given, a new figure will be created.

        Parameters
        ----------
        axes : plt.axes, optionnal
            The axes to initialize.
        fig_kw : dict, keyword-only, optionnal
            The kwargs to be given to ``plt.figure``.
        axes_kw : dict, keyword-only, optionnal
            The kwargs to be given to ``plt.axes``.
        feature_kw : dict, keyword-only, optionnal
            The kwargs to be given to ``axes.add_feature``.
        glines_kw : dict, keyword-only, optionnal
            The kwargs to be given to ``axes.gridlines``.

        Returns
        -------
        out : tuple
            A tuple containing three elements: ``(fig, axes, glines)``. If an axes is given,``fig``
            is None. Otherwise, fig is the new figure, axes the geoaxes and glines a gridlines
            object.
        """
        if not fig_kw:
            fig_kw = {}

        if not axes_kw:
            axes_kw = {}

        if not feature_kw:
            feature_kw = {"linewidth": 1, "alpha": 0.5}

        if not glines_kw:
            glines_kw = {"draw_labels": True, "linewidth": 0.5, "alpha": 0.5}

        fig = None
        self.axes = axes
        if not self.axes:
            fig = plt.figure(**fig_kw)
            self.axes = plt.axes(projection=ccrs.PlateCarree(), **axes_kw)

        self.axes.add_feature(cfeature.COASTLINE, **feature_kw)
        self.axes.add_feature(cfeature.BORDERS, **feature_kw)

        glines = self.axes.gridlines(**glines_kw)
        glines.top_labels = glines.right_labels = False

        return fig, self.axes, glines

    def set_title(self, title: str, *, fmt_kw: dict = None, **kwargs):
        """
        Apply a title on the given axes.

        Parameters
        ----------
        title : str
            The title to write. It can contains format.
        fmt_kw : dict, keyword-only, optionnal
            The fields to format ``title``.
        kwargs
            These keyword arguments will be given to ``axes.text``.

        Return
        ------
        title : plt.Text
            The Text instance.

        Example
        -------
        This method can be used as follow:

            my_map.set_title(
                "Title {field1} {field2}",
                fmt_kw={"field1": 42, "field2": "test"},
                color="blue"
            )

        So this set a title "Title 42 test" in blue.
        """
        if "fontsize" not in kwargs:
            kwargs["fontsize"] = plt.rcParams["axes.titlesize"]

        title = self.axes.text(
            0.5, 1.01, title.format(**fmt_kw), ha="center", transform=self.axes.transAxes, **kwargs
        )
        return title

    def plot_contourf(self, *varnames, func: callable = lambda *x: x, **kwargs):
        """
        Add a contourf to the Map axes.

        Parameters
        ----------
        *varnames
            The names of the variables to be given to ``func``.
        func : callable, keyword-only, optionnal
            A function that takes all the variables given in entry and returns a 2D array.
        kwargs
            These keywords arguments will be given to ``axes.contourf``.

        Returns
        ------
        contourf : plt.QuadContourSet
            The added contourf.
        """
        contourf = self.axes.contourf(
            self.reader.longitude,
            self.reader.latitude,
            self.reader.get_var(*varnames, func=func),
            **kwargs
        )

        return contourf

    def plot_contour(self, *varnames, func: callable = lambda *x: x, **kwargs):
        """
        Add a contour to the Map axes.

        Parameters
        ----------
        *varnames
            The names of the variables to be given to ``func``.
        func : callable, keyword-only, optionnal
            A function that takes all the variables given in entry and returns a 2D array.
        kwargs
            These keywords arguments will be given to ``axes.contour``.

        Returns
        ------
        contour : plt.QuadContourSet
            The added contour.
        """
        contour = self.axes.contour(
            self.reader.longitude,
            self.reader.latitude,
            self.reader.get_var(*varnames, func=func),
            **kwargs
        )

        return contour

    def plot_quiver(self, *varnames, mesh: int = None, func: callable = lambda *x: x, **kwargs):
        """
        Add a quiver to the given axes.

        Parameters
        ----------
        *varnames
            The names of the variables to be given to ``func``.
        mesh : int, keyword-only, optionnal
            It corresponds to the arrows to display.
        func : callable, keyword-only, optionnal
            A function that takes all the variables given in entry and returns two 2D arrays.
        kwargs
            These keywords arguments will be given to ``axes.quiver``.

        Returns
        ------
        contourf : plt.Contourf
            The added contourf.
        """
        size = len(self.reader.longitude)

        if not mesh:
            mesh = size // 50

        x_var, y_var = self.reader.get_var(*varnames, func=func)
        quiver = self.axes.quiver(
            self.reader.longitude[::mesh],
            self.reader.latitude[::mesh],
            x_var[::mesh, ::mesh],
            y_var[::mesh, ::mesh],
            **kwargs
        )

        return quiver
