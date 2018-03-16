import pytest
import numpy as np
import numpy.testing as npt

from neuroglia import interpolator


# values from justin kiggins
TIME_PRECISE = np.arange(0, 0.2, 0.001)
TIME_TARGET = TIME_PRECISE[::10]  # real time
TIME_OBSERVED = TIME_TARGET + 0.002 * np.random.randn(*TIME_TARGET.shape)  # unevenly sampled time
make_neuron = lambda t: np.sin(100 * t)


@pytest.mark.parametrize("x, y, u, expected", [
    (
        np.linspace(-np.pi, np.pi, 201),
        np.sin(np.linspace(-np.pi, np.pi, 201)),
        np.linspace(-np.pi, np.pi, 201),
        np.sin(np.linspace(-np.pi, np.pi, 201)),
    ),
    (
        np.linspace(0, 5, 100),
        np.linspace(0, 5, 100),
        np.linspace(0, 5, 100),
        np.linspace(0, 5, 100),
    ),
    (
        TIME_OBSERVED,
        make_neuron(TIME_OBSERVED),
        TIME_OBSERVED,
        make_neuron(TIME_OBSERVED),
    ),
])
def test_kriging_interpolator_factory(x, y, u, expected):
    """Bad test...
    """
    npt.assert_allclose(
        interpolator.kriging_interpolator_factory(x, y)(u),
        expected,
        atol=0.05
    )


@pytest.mark.parametrize("x, y, u, expected", [
    (
        np.linspace(-np.pi, np.pi, 201),
        np.sin(np.linspace(-np.pi, np.pi, 201)),
        np.linspace(-np.pi, np.pi, 201),
        np.sin(np.linspace(-np.pi, np.pi, 201)),
    ),
    (
        np.linspace(0, 5, 100),
        np.linspace(0, 5, 100),
        np.linspace(0, 5, 100),
        np.linspace(0, 5, 100),
    ),
])
def test_sinc_interpolator_factory(x, y, u, expected):
    npt.assert_allclose(
        interpolator.sinc_interpolator_factory(x, y)(u),
        expected,
        atol=0.05
    )
