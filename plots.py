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
import numpy as np
import pandas as pd


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

    def __init__(self, longitude, latitude):
        """Constructor method."""
        self.longitude = longitude
        self.latitude = latitude
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

    def plot_contourf(self, var_array: np.array, **kwargs):
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
            self.longitude,
            self.latitude,
            var_array,
            **kwargs
        )

        return contourf

    def plot_contour(self, var_array: np.array, **kwargs):
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
            self.longitude,
            self.latitude,
            var_array,
            **kwargs
        )

        return contour

    def plot_quiver(self, x_var_array: np.array, y_var_array: np.array, *, x_mesh: int = None, y_mesh: int = None, **kwargs):
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
        x_size = len(x_var_array[0])
        y_size = len(x_var_array[:, 0])
        if not x_mesh:
            x_mesh = x_size // 50
        if not y_mesh:
            y_mesh = y_size // 50


        quiver = self.axes.quiver(
            self.longitude[::y_mesh, ::x_mesh],
            self.latitude[::y_mesh, ::x_mesh],
            x_var_array[::y_mesh, ::x_mesh],
            y_var_array[::y_mesh, ::x_mesh],
            **kwargs
        )

        return quiver


class TemporalProfile:
    def __init__(self, axes: plt.Axes = None, **subplots_kw):
        """Constructor method."""
        self.axes = axes
        if not self.axes:
            self.fig, self.axes = plt.subplots(**subplots_kw)

    def add_profile_from_array(self, time, array, **kwargs):
        self.axes.plot(time, array, **kwargs)

    def add_profile_from_csv(self, filename: str, time: str, variable: str, **kwargs):
        data = pd.read_csv(filename, delimiter=";")
        self.axes.plot(data[time], data[variable], **kwargs)
        self.axes.grid("on")


def get_index(var_array: np.array, value):
    delta = np.abs(value - var_array)
    index = np.array(np.where(delta == delta.min()))
    return index[:,0]


def index_to_latlon(mesonh, i_lim, j_lim):
    lon_min = mesonh.longitude[i_lim[0], j_lim[0]]
    lat_min = mesonh.latitude[i_lim[0], j_lim[0]]
    lon_max = mesonh.longitude[i_lim[1], j_lim[1]]
    lat_max = mesonh.latitude[i_lim[1], j_lim[1]]
    return ((lon_min, lon_max),(lat_min, lat_max))


def latlon_to_index(mesonh, lon_lim, lat_lim):
    j_min = get_index(mesonh.longitude, lon_lim[0])[1]
    j_max = get_index(mesonh.longitude, lon_lim[1])[1]
    i_min = get_index(mesonh.latitude, lat_lim[0])[0]
    i_max = get_index(mesonh.latitude, lat_lim[1])[0]
    return ((i_min, i_max),(j_min, j_max))
