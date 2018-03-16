import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor


def _sinc_interpolator(x, s, u):
    """sinc interpolator

    from:
    https://gist.github.com/endolith/1297227

    Parameters
    ----------
    x : `np.ndarray`
        sampled values
    s : `np.ndarray`
        sampled points
    u : `np.ndarray`
        unsampled points

    Returns
    -------
    np.ndarray
        interpolated values

    Notes
    -----
    - `x` is typically the dependent variable and `s` is typically the
    independent variable
    """
    if len(x) != len(s):
        raise ValueError('x and s must be the same length')

    # Find the period
    T = s[1] - s[0]

    sincM = np.tile(u, (len(s), 1)) - np.tile(s[:, np.newaxis], (1, len(u)))

    return np.dot(x, np.sinc(sincM / T))


def kriging_interpolator_factory(x, y, **kwargs):
    """1-dimensional kriging

    from:
    https://stackoverflow.com/questions/24978052/interpolation-over-regular-grid-in-python

    Parameters
    ----------
    x : `np.ndarray`
        independent variable used to generate interpolator
    y : `np.ndarray`
        dependent variable used to generator interpolator
    **kwargs
        keyword arguments supplied to `GaussianProcessRegressor`

    Returns
    -------
    function
        interpolator function

    Notes
    -----
    - assumes `x` and `y` are of shape: (n, ), with an equal number of elements
    """
    process = GaussianProcessRegressor(**kwargs)
    process.fit(x.reshape(1, -1), y.reshape(1, -1))

    return lambda u: process.predict(u.reshape(1, -1)).reshape(-1)


def sinc_interpolator_factory(x, y):
    """sinc interpolator factory

    Parameters
    ----------
    x : `np.ndarray`
        independent variable used to generate interpolator
    y : `np.ndarray`
        dependent variable used to generator interpolator

    Returns
    -------
    function
        interpolator function
    """
    return lambda u: _sinc_interpolator(y, x, u)
