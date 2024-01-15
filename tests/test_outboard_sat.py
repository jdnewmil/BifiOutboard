# test_outboard_sat.py

import numpy as np
import pandas as pd
import bifi_outboard.outboard_sat as bsat


def test_calc_cos_psi():
    ans = bsat.calc_psi(phi=0.0, height=2, offset=1)
    assert np.allclose(0, ans)
