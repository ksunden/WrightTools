"""Kent Meyer."""


# --- import --------------------------------------------------------------------------------------


import os

import collections

import numpy as np

from scipy.interpolate import griddata

from ._data import Data
from .. import kit as wt_kit


# --- define --------------------------------------------------------------------------------------


__all__ = ['from_KENT']


# --- from function -------------------------------------------------------------------------------


def from_KENT(filepaths, name=None, ignore=['wm'], delay_tolerance=0.1, frequency_tolerance=0.5,
              parent=None, verbose=True):
    """Create data object from KENT file(s).

    Parameters
    ----------
    filepaths : string or list of strings
        Filepath(s).
    name : string (optional)
        Unique dataset identifier. If None (default), autogenerated.
    ignore : list of strings (optional)
        Columns to ignore. Default is ['wm'].
    delay_tolerance : float (optional)
        Tolerance below-which to ignore delay changes (in picoseconds).
        Default is 0.1.
    frequency_tolerance : float (optional)
        Tolerance below-which to ignore frequency changes (in wavenumbers).
        Default is 0.5.
    parent : WrightTools.Collection (optional)
        Collection to place new data object within. Default is None.
    verbose : bool (optional)
        Toggle talkback. Default is True.

    Returns
    -------
    WrightTools.Data
        Data from KENT.
    """
    # define columns ------------------------------------------------------------------------------
    # axes
    axes = collections.OrderedDict()
    axes['w1'] = {'units': 'wn', 'idx': 0, 'label': '1'}
    axes['w2'] = {'units': 'wn', 'idx': 1, 'label': '2'}
    axes['wm'] = {'units': 'wn', 'idx': 2, 'label': 'm'}
    axes['d1'] = {'units': 'ps', 'idx': 3, 'label': '1'}
    axes['d2'] = {'units': 'ps', 'idx': 4, 'label': '2'}
    for key in axes.keys():
        if 'w' in key:
            axes[key]['tolerance'] = frequency_tolerance
        elif 'd' in key:
            axes[key]['tolerance'] = delay_tolerance
    # channels
    channels = collections.OrderedDict()
    channels['signal'] = {'idx': 5}
    channels['OPA1'] = {'idx': 6}
    channels['OPA2'] = {'idx': 7}
    # do we have a list of files or just one file? ------------------------------------------------
    if isinstance(filepaths, list):
        file_example = filepaths[0]
    else:
        file_example = filepaths
        filepaths = [filepaths]
    # import full array ---------------------------------------------------------------------------
    arr = np.concatenate([np.genfromtxt(f).T for f in filepaths], axis=1)
    # recognize dimensionality of data ------------------------------------------------------------
    axes_discover = axes.copy()
    for key in ignore:
        if key in axes_discover:
            axes_discover.pop(key)  # remove dimensions that mess up discovery
    scanned = wt_kit.discover_dimensions(arr, axes_discover)
    # create data object --------------------------------------------------------------------------
    if name is None:
        name = wt_kit.string2identifier(os.path.basename(filepaths[0]))
    kwargs = {'name': name, 'kind': 'KENT', 'source': filepaths}
    if parent is not None:
        data = parent.create_data(**kwargs)
    else:
        data = Data(**kwargs)
    # grid and fill data --------------------------------------------------------------------------
    # variables
    ndim = len(scanned)
    for i, key in enumerate(scanned.keys()):
        for name in key.split('='):
            shape = [1] * ndim
            a = scanned[key]
            shape[i] = a.size
            a.shape = tuple(shape)
            units = axes[name]['units']
            data.create_variable(name=name, values=a, units=units)
    for key, dic in axes.items():
        if key not in data.variable_names:
            c = np.mean(arr[dic['idx']])
            if not np.isnan(c):
                shape = [1] * ndim
                a = np.array([c])
                a.shape = tuple(shape)
                units = dic['units']
                data.create_variable(name=key, values=a, units=units)
    # channels
    if len(scanned) == 1:  # 1D data
        for key in channels.keys():
            channel = channels[key]
            zi = arr[channel['idx']]
            data.create_channel(name=key, values=zi)
    else:  # all other dimensionalities
        # channels
        points = tuple(arr[axes[key.split('=')[0]]['idx']] for key in scanned.keys())
        xi = tuple(np.meshgrid(*scanned.values(), indexing='ij'))
        for key in channels.keys():
            channel = channels[key]
            zi = arr[channel['idx']]
            fill_value = min(zi)
            grid_i = griddata(points, zi, xi, method='linear', fill_value=fill_value)
            data.create_channel(name=key, values=grid_i)
    # axes
    data.transform(*scanned.keys())
    # return --------------------------------------------------------------------------------------
    if verbose:
        print('data created at {0}'.format(data.fullpath))
        print('  axes: {0}'.format(data.axis_names))
        print('  shape: {0}'.format(data.shape))
    return data
