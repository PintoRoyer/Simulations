"""A small lib to plot maps from Meso-NH simulat"""

import numpy as np
from netCDF4 import Dataset
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt


def get_limits(files: list, *varnames, func=lambda x: x):
    """
    Search min and max of a given variable.

    Parameters
    ----------
    files : list
        The list that contains all the filenames.
    varnames : str
        The names of the variables.
    function
       	The function to apply to the given variables.

    Returns
    -------
    out : tuple
        A tuple containing two elements: (var_min, var_max).
    """
    var_min = np.inf
    var_max = -np.inf
    for filename in files:
        data = Dataset(filename)

        args = [data.variables[varname][0] for varname in varnames]
        current_min = func(*args).min()
        current_max = func(*args).max()

        if current_min < var_min:
            var_min = current_min

        if current_max > var_max:
            var_max = current_max

    return var_min, var_max


def init_axes(
    axes: plt.axes = None,
    *,
    figsize: tuple = (10, 6),
    feature_kw: dict = None,
    glines_kw: dict = None
):
    """
    Init the axes with geoaxes. If no axes is given, a new figure will be created.

    Parameters
    ----------
    axes : plt.axes, optionnal
        The axes to initialize.
    figsize : tuple, keyword-only, optionnal
        The size of the figure in case of a new figure.
    feature_kw : dict, keyword-only, optionnal
        The kwargs to be given to ``axes.add_feature``.
    glines_kw : dict, keyword-only, optionnal
        The kwargs to be given to gridlines.
    
    Returns
    -------
    out : tuple
	A tuple containing three elements: ``(fig, axes, glines)``. If an axes is given, ``fig`` is
    None. Otherwise, fig is the new figure, axes the geoaxes and glines a gridlines object.
    """
    fig = None
    if not axes:
        fig = plt.figure(figsize=figsize)
        axes = plt.axes(projection=ccrs.PlateCarree())

    if not feature_kw:
        feature_kw = {"linewidth": 1, "alpha": 0.5}

    if not glines_kw:
        glines_kw = {"linewidth": 0.5, "alpha": 0.5}
	
    axes.add_feature(cfeature.COASTLINE, **feature_kw)
    axes.add_feature(cfeature.BORDERS, **feature_kw)

    glines = axes.gridlines(draw_labels=True, **glines_kw)
    glines.top_labels = glines.right_labels = False

    return fig, axes, glines


def set_title(axes: plt.axes, title: str, fmt_kw: dict = None, **kwargs):
    """
    Apply a title on the given axes.

    Parameters
    ----------
    axes : plt.Axes
        The Axes instance on which apply the title.
    title : str
        The title to write. It can contains format.
    fmt_kw : dict
        The field to format ``title``.
    kwargs
        These keyword arguments will be given to ``axes.text``.
    
    Return
    ------
    title : plt.Text
        The Text instance.
    
    Example
    -------
     
    """
    if "fontsize" not in kwargs:
        kwargs["fontsize"] = plt.rcParams["axes.titlesize"]

    title = axes.text(
        0.5,
        1.01,
        title.format(**fmt_kw),
        ha="center",
        transform=axes.transAxes,
        **kwargs
    )
    return title


def plot_contourf(axes: plt.axes, data: Dataset, *varnames, func = lambda x: x, **kwargs):
    """
    Add a contourf to the given axes.
    
    Parameters
    ----------
    axes : plt.Axes
        The Axes instance on which apply the title. 
    data : Dataset
        The Dataset that contains the requested variables.
    varnames
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
    args = [data.variables[varname][0] for varname in varnames]    
    contourf = axes.contourf(
        data.variables["longitude"][0],
        data.variables["latitude"][:, 0],
        func(*args),
        **kwargs
    )
    
    return contourf


def plot_contour(axes: plt.axes, data: Dataset, *varnames, func = lambda x: x, **kwargs):
    """
    Add a contour to the given axes.
    
    Parameters
    ----------
    axes : plt.Axes
        The Axes instance on which apply the title. 
    data : Dataset
        The Dataset that contains the requested variables.
    varnames
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
    args = [data.variables[varname][0] for varname in varnames]    
    contour = axes.contour(
        data.variables["longitude"][0],
        data.variables["latitude"][:, 0],
        func(*args),
        **kwargs
    )
    
    return contour


def plot_quiver(
    axes: plt.axes,
    data: Dataset,
    *varnames,
    mesh = None,
    func = lambda x: x,
    **kwargs
):
    """
    Add a quiver to the given axes.
    
    Parameters
    ----------
    axes : plt.Axes
        The Axes instance on which apply the title. 
    data : Dataset
        The Dataset that contains the requested variables.
    varnames
        The names of the variables to be given to ``func``.
    mesh : int or range
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
    size = len(data.variables["longitude"][0])

    if not mesh:
        mesh = range(0, size, size // 50)
    elif isinstance(mesh, int):    
        mesh = range(0, size, size // mesh)
    
    args = [data.variables[varname][0, mesh, mesh] for varname in varnames]
    x_var, y_var = func(*args)
    quiver = axes.quiver(
        data.variables["longitude"][0, mesh],
        data.variables["latitude"][mesh, 0], 
        x_var,
        y_var,
        **kwargs
    )
    
    return quiver

