# test_outboard_sat.py

import numpy as np
import pandas as pd
import bifi_outboard.outboard_sat as bsat
import pytest

def test_calc_cos_psi():
    ans = bsat.calc_psi(phi_rad=0.0, height=2, offset=1)
    assert np.allclose(0, ans)


@pytest.mark.parametrize(
    "AzSol,HSol,expected"
    , (
        (0, 0, 0)
        , (-90, 45, -45)
        , (90, 45, 45)
        , (30, 30, 40.8933946)
        , (90, -45, 135)))
def test_calc_betasun(AzSol, HSol, expected):
    ans = bsat.calc_betasun(
        np.deg2rad(AzSol)
        , np.deg2rad(HSol))
    assert np.allclose(np.rad2deg(ans), expected)
