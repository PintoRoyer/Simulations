"""
Readers
=======

Description
-----------
This module provides a number of reader classes for managing different types of time and variables.
These classes are all structured in the same way, so that they can be used in the same way
regardless of the files or variables managed.

It also gives some basic functions to manipulate index and conversion from lon/lat to index and
index to lat/lon.

Create a reader class
---------------------
To create a reader class, you should have the following attributes:

* files: the list of files

* data: the current open file

* longitude: the longitude of the measures

* latitude: the latitude of the measures

and the following methods:

* get_data(file_index: int) to open a file

* get_var(*varnames, func: callable = lambda x: x) to get a variable

* get_limits(*varnames, func: callable = lambda x: x) to get the min and max of a variable

Classes
-------
MesoNH
Antilope
Satellite

Functions
---------
get_mesonh
get_index
index_to_lonlat
lonlat_to_index
"""

import numpy as np
from netCDF4 import Dataset


class MesoNH:
    """
    MesoNH is a reader class that reads Meso-NH files.

    Attributes
    ----------
    files : list
        The list of the Meso-NH files.
    data : Dataset
        The current file open.
    longitude : np.array
        The longitudes.
    latitude : np.array
        The latitudes.
    """

    def __init__(self, files):
        """Constructor method."""
        self.files = files
        self.data = None

        data = Dataset(self.files[0])
        self.longitude = data.variables["longitude"][:, :]
        self.latitude = data.variables["latitude"][:, :]

    def get_data(self, file_index: int):
        """
        Open the file corresponding to the given ``file_index``. The
        ``Dataset`` object is stored into ``MesoNH.data``.

        Parameters
        ----------
        file_index : int
            The index of the the file to open.
        """
        self.data = Dataset(self.files[file_index])

    def get_var(self, *varnames, func: callable = lambda x: x):
        """
        Returns the NumPy array corresponding to result given by ``func`` applied on the given
        variables.

        Parameters
        ----------
        varnames : str
            Variable names to give to ``func``.
        func : callable, keyword-only, optionnal
            The function to apply to the given variables.

        Returns
        -------
        out : np.array
            The result given by ``func``.
        """
        args = []
        for varname in varnames:
            args.append(self.data.variables[varname][0])

        return func(*args)

    def get_mean(
        self,
        index_i: int,
        index_j: int,
        *varnames,
        func: callable = lambda x: x,
        t_range: iter = None,
        size: int = 1,
    ):
        """
        Compute a spatio-temporal average over a group of pixel centered on a given position and
        over a given time range.

        Parameters
        ----------
        index_i : int
            The index on the x-axis.
        index_j : int
            The index on the y-axis
        varnames : str
            Variable names to give to ``func``.
        func : callable, keyword-only, optionnal
            The function to apply to the given variables.
        t_range : iter, keyword-only, optionnal
            The temporal range over wich the average is to be calculated. By default all the
            available time interval will be taken.

            You can give a ``range`` or the list of the index you want.
        size : int, keyword-only, optionnal
            The size of the spatial average in index. By default it's set on ``1``, so the average
            will be calculated of the given case and over the cases around in the four
            directions:

                      size ├───┤
                ───┌───┬───┬───┐ ┬
                j+1│   │   │   │ │ size
                ───├───┼───┼───┤ ┴
                 j │   │i;j│   │
                ───├───┼───┼───┤
                j-1│   │   │   │
                ───└───┴───┴───┘
                   │i-1│ i │i+1│

        Returns
        -------
        out : float
            The computed average.
        """
        if not t_range:
            t_range = range(0, len(self.files))

        mean_per_timestep = []
        for i in t_range:
            data = Dataset(self.files[i])

            args = []
            for varname in varnames:
                args.append(data.variables[varname][0])
            array = func(*args)

            mean_per_timestep.append(
                np.mean(array[index_j - size : index_j + size, index_i - size : index_i + size])
            )
        return np.mean(mean_per_timestep)

    def get_limits(self, *varnames, func: callable = lambda x: x):
        """
        Search min and max of a given variable.

        Parameters
        ----------
        varnames : str
            The names of the variables.
        func : callable, keyword-only, optionnal
            The function to apply to the given variables.

        Returns
        -------
        out : tuple
            A tuple containing two elements: (var_min, var_max).
        """
        var_min = np.inf
        var_max = -np.inf
        for _, file in enumerate(self.files):
            data = Dataset(file)

            args = []
            for varname in varnames:
                args.append(data.variables[varname][0])
            result = func(*args)

            current_min = result.min()
            current_max = result.max()

            if current_min < var_min:
                var_min = current_min

            if current_max > var_max:
                var_max = current_max

        return var_min, var_max


class Antilope:
    """
    Antilope is a reader class that reads ANTILOPE files.

    Attributes
    ----------
    files : list
        The list of the Meso-NH files.
    data : Dataset
        The current file open.
    longitude : np.array
        The longitudes.
    latitude : np.array
        The latitudes.
    day_index : int
        The day to selecte in files.
    """

    def __init__(self, files, day_index: int):
        """Contructor method."""
        self.files = files
        self.day_index = day_index
        self.data = None

        data = Dataset(self.files[0])
        self.longitude = data.variables["lon"][:]
        self.latitude = data.variables["lat"][:]

    def get_data(self, file_index: int):
        """
        Open the file corresponding to the given ``file_index``. The
        ``Dataset`` object is stored into ``Antilope.data``.

        Parameters
        ----------
        file_index : int
            The index of the the file to open.
        """
        self.data = Dataset(self.files[file_index])

    def get_var(self, *varnames, func: callable = lambda x: x):
        """
        Returns the NumPy array corresponding to result given by ``func`` applied on the given
        variables.

        Parameters
        ----------
        varnames : str
            The names of the variables.
        func : callable, keyword-only, optionnal
            The function to apply to the given variables.

        Returns
        -------
        out : np.array
            The result given by ``func``.
        """
        args = []
        for varname in varnames:
            args.append(self.data.variables[varname][self.day_index])

        return func(*args)

    def get_limits(self, *varnames, func: callable = lambda x: x):
        """
        Search min and max of a given variable.

        Parameters
        ----------
        varnames : str
            The names of the variables.
        func : callable, keyword-only, optionnal
            The function to apply to the given variables.

        Returns
        -------
        out : tuple
            A tuple containing two elements: (var_min, var_max).
        """
        var_min = np.inf
        var_max = -np.inf
        for _, file in enumerate(self.files):
            data = Dataset(file)

            args = []
            for varname in varnames:
                args.append(data.variables[varname][self.day_index])
            result = func(*args)

            current_min = result.min()
            current_max = result.max()

            if current_min < var_min:
                var_min = current_min

            if current_max > var_max:
                var_max = current_max

        return var_min, var_max


class Satellite:
    """
    Satellite is a reader class that reads satellite files.

    Attributes
    ----------
    files : list
        The list of the Meso-NH files.
    data : Dataset
        The current file open.
    longitude : np.array
        The longitudes.
    latitude : np.array
        The latitudes.
    time_step : int
        The temporal step inside the files.
    """

    def __init__(self, files, time_step: int):
        """Contructor method."""
        self.files = files
        self.time_step = time_step
        self.data = None

        data = Dataset(self.files[0])
        self.longitude = data.variables["lon"][:]
        self.latitude = data.variables["lat"][:]

    def get_data(self, file_index: int):
        """
        Open the file corresponding to the given ``file_index``. The
        ``Dataset`` object is stored into ``Satellite.data``.

        Parameters
        ----------
        file_index : int
            The index of the the file to open.
        """
        self.data = Dataset(self.files[file_index])

    def get_var(self, *varnames, func: callable = lambda x: x):
        """
        Returns the NumPy array corresponding to result given by ``func`` applied on the given
        variables.

        Parameters
        ----------
        varnames : str
            The names of the variables.
        func : callable, keyword-only, optionnal
            The function to apply to the given variables.

        Returns
        -------
        out : np.array
            The result given by ``func``.
        """
        args = []
        for varname in varnames:
            args.append(self.data.variables[varname][self.time_step])

        return func(*args)

    def get_limits(self, *varnames, func: callable = lambda x: x):
        """
        Search min and max of a given variable.

        Parameters
        ----------
        varnames : str
            The names of the variables.
        func : callable, keyword-only, optionnal
            The function to apply to the given variables.

        Returns
        -------
        out : tuple
            A tuple containing two elements: (var_min, var_max).
        """
        var_min = np.inf
        var_max = -np.inf
        for _, file in enumerate(self.files):
            data = Dataset(file)

            args = []
            for varname in varnames:
                args.append(data.variables[varname][self.time_step])
            result = func(*args)

            current_min = result.min()
            current_max = result.max()

            if current_min < var_min:
                var_min = current_min

            if current_max > var_max:
                var_max = current_max

        return var_min, var_max


def get_mesonh(resolution_dx: int, path: str = "../Donnees/"):
    """
    Returns a Meso-NH reader for the given resolution and path.

    Parameters
    ----------
    resolution_dx : int
        The wanted resolution.
    path : str, optionnal
        The path of the netCDF files. By default it's set on ``../Donnees/``.

    Returns
    -------
    out : MesoNH
        The Meso-NH reader.
    """
    files = [
        f"{path}DX{resolution_dx}/CORSE.1.SEG01.OUT.{str(t).zfill(3)}.nc" for t in range(1, 361)
    ]
    return MesoNH(files)


def get_index(array: np.array, target):
    """
    Search and return the index of the value closest to ``target`` in the given array. This function
    can handle n-dimensionnal arrays.

    Parameters
    ----------
    array : np.array
        The array in which to search.
    target
        The value to search in ``array``.

    Returns
    -------
    out : np.array
        The index of the value closest to ``target`` in ``array``. If seraval indexes matche, it
        only returns the first one.
    """
    delta = np.abs(target - array)
    index = np.array(np.where(delta == delta.min()))
    return index[:, 0]


def get_index_from_vect(x_array, y_array, value):
    norms = np.sqrt((x_array - value[0])**2 + (y_array - value[1])**2)
    index = np.array(np.where(norms == norms.min()))
    return index[:, 0]


def index_to_lonlat(reader, i: int, j: int):
    """
    Get the longitudes and latitudes from given limits indexes.

    Parameters
    ----------
    reader
        An instance of reader.
    i_lim : tuple
        The limit indexes on x-axis.
    j_lim : tuple
        The limit indexes on y-axis.

    Returns
    -------
    out : tuple
        A tuple that contains two tuples: ``(longitude_min, longitude_max)`` and
        ``(latitude_min, latitude_max)``.
    """
    lon = reader.longitude[j, i]
    lat = reader.latitude[j, i]
    return (lon, lat)


def lonlat_to_index(reader, lon: float, lat: float):
    """
    Get the indexes from given limit longitudes and latitudes.

    .. warning::
        Due to projection, the returned indexes may not match perfectly match the given lon/lat.

    Parameters
    ----------
    reader
        An instance of reader.
    lon_lim : tuple
        The limit indexes on longitude.
    lat_lim : tuple
        The limit indexes on latitude.

    Returns
    -------
    out : tuple
        A tuple that contains two tuples: ``(i_min, i_max)`` and ``(j_min, j_max)``.
    """
    j, i =  get_index_from_vect(reader.longitude, reader.latitude, (lon, lat))
    return i, j
