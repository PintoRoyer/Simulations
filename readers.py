"""
Readers
=======

Description
-----------
This module provides a number of reader classes for managing different types of time and variables.
These classes are all structured in the same way, so that they can be used in the same way
regardless of the files or variables managed.

Create a reader class
---------------------
To create a reader class, you should have the following attributes:

* files: the list of files

* data: the current open file

* longitude: the longitude of the measures

* latitude: the latitude of the measures

and the following methods:

* get_data(file_index: int) to open a file

* get_var(*varnames, func: callable = lambda *x: x) to get a variable

* get_limits(*varnames, func: callable = lambda *x: x) to get the min and max of a variable

Class
-----
MesoNH
Antilope
Satellite
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
        self.longitude = data.variables["longitude"][0]
        self.latitude = data.variables["latitude"][:, 0]

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

    def get_var(self, *varnames, func: callable = lambda *x: x):
        """
        Returns the NumPy array corresponding to result given by ``func`` applied on the given
        variables.

        Parameters
        ----------
        *varnames : str
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

    def get_limits(self, *varnames, func: callable = lambda *x: x):
        """
        Search min and max of a given variable.

        Parameters
        ----------
        *varnames : str
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
        for file_index in range(len(self.files)):
            self.get_data(file_index)
            result = self.get_var(*varnames, func=func)
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

    def get_var(self, *varnames, func: callable = lambda *x: x):
        """
        Returns the NumPy array corresponding to result given by ``func`` applied on the given
        variables.

        Parameters
        ----------
        *varnames : str
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

    def get_limits(self, *varnames, func: callable = lambda *x: x):
        """
        Search min and max of a given variable.

        Parameters
        ----------
        *varnames : str
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
        for file_index in range(len(self.files)):
            self.get_data(file_index)
            result = self.get_var(*varnames, func=func)
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

    def get_var(self, *varnames, func: callable = lambda *x: x):
        """
        Returns the NumPy array corresponding to result given by ``func`` applied on the given
        variables.

        Parameters
        ----------
        *varnames : str
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

    def get_limits(self, *varnames, func: callable = lambda *x: x):
        """
        Search min and max of a given variable.

        Parameters
        ----------
        *varnames : str
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
        for file_index in range(len(self.files)):
            self.get_data(file_index)
            result = self.get_var(*varnames, func=func)
            current_min = result.min()
            current_max = result.max()

            if current_min < var_min:
                var_min = current_min

            if current_max > var_max:
                var_max = current_max

        return var_min, var_max
