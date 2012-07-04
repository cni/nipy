""" Testing brain segmentation module
"""

import numpy as np

from nose.tools import assert_equal

from ..segmentation import Segmentation
from ..brain_segmentation import BrainT1Segmentation

from ....io.files import load as load_image
from ....testing import anatfile

anat_img = load_image(anatfile)
anat_mask = anat_img.get_data() > 0


def _check_dims(x, ndim, shape):
    if isinstance(shape, int):
        shape = (shape, )
    for i in range(ndim):
        assert_equal(x.shape[i], shape[i])


def _test_brain_seg(model, niters=3, beta=0, ngb_size=6, init_params=None,
                    convert=True):
    S = BrainT1Segmentation(anat_img.get_data(), mask=anat_mask,
                            model=model, niters=niters, beta=beta,
                            ngb_size=ngb_size, convert=convert)
    shape = anat_img.shape
    if convert:
        nclasses = 3
    else:
        nclasses = S.mixmat.shape[0]
    _check_dims(S.ppm, 4, list(shape) + [nclasses])
    _check_dims(S.label, 3, shape)
    _check_dims(S.mu, 1, S.mixmat.shape[0])
    _check_dims(S.sigma, 1, S.mixmat.shape[0])


def test_brain_seg1():
    _test_brain_seg('3k', niters=3, beta=0.0, ngb_size=6)


def test_brain_seg2():
    _test_brain_seg('3k', niters=3, beta=0.5, ngb_size=6)


def test_brain_seg3():
    _test_brain_seg('4k', niters=3, beta=0.5, ngb_size=6)


def test_brain_seg4():
    _test_brain_seg('4k', niters=3, beta=0.5, ngb_size=26)


def test_brain_seg5():
    _test_brain_seg(np.array([[1., 0., 0.],
                              [1., 0., 0.],
                              [0., 1., 0.],
                              [0., 1., 0.],
                              [0., 0., 1.]]),
                    niters=3, beta=0.5, ngb_size=6)


def test_brain_seg6():
    _test_brain_seg('3k', niters=3, beta=0.5, ngb_size=6,
                    convert=False)


def test_brain_seg7():
    mu = np.array([0, 50, 100])
    sigma = np.array([1000, 2000, 3000])
    _test_brain_seg('3k', niters=3, beta=0.5, ngb_size=6,
                    init_params=(mu, sigma))


def _test_segmentation(S, nchannels=1):
    assert_equal(S.nchannels, nchannels)
    S.run(niters=5)
    label = S.map()
    assert_equal(label.ndim, 3)
    assert_equal(label.dtype, 'uint8')
    assert isinstance(S.free_energy(), float)


def test_segmentation_3d():
    data = np.random.rand(21, 22, 23)
    _test_segmentation(Segmentation(data, mu=[0.25, 0.75], sigma=[1, 1]))


def test_segmentation_3d_with_MRF():
    data = np.random.rand(21, 22, 23)
    _test_segmentation(Segmentation(data, mu=[0.25, 0.75],
                                    sigma=[1, 1], beta=.2))


def test_segmentation_3d_with_mask():
    data = np.random.rand(21, 22, 23)
    mask = data > .1
    if mask[0].size < 1:
        return
    _test_segmentation(Segmentation(data, mu=[0.25, 0.75],
                                    sigma=[1, 1], mask=mask))


def test_segmentation_3d_multichannel():
    data = np.random.rand(21, 22, 23, 2)
    mask = data[..., 0] > .1
    if mask[0].size < 1:
        return
    _test_segmentation(Segmentation(data,
                                    mu=[[0.25, 0.25], [0.75, 0.75]],
                                    sigma=[np.eye(2), np.eye(2)],
                                    mask=mask),
                       nchannels=2)
