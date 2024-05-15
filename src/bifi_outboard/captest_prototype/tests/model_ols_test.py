# model_ols_test.py
"""Testing ols_model"""

import pathlib
import numpy as np
import pandas as pd
import pytest
from ..io import read_pvsyst_hourly
from ..model_ols import Model, ModelFit


@pytest.fixture(name='sample_pvsyst_hourly')
def sample_pvsyst_hourly_fixture() -> pd.DataFrame:
    """Figure for sample system data."""
    dta_dir = pathlib.Path(__file__).parent / 'data'
    samplefile = dta_dir / 'Test Bifi SAT_Project_VC0_HourlyRes_0.CSV'
    return read_pvsyst_hourly(
        samplefile
        , sep=','
        , date_format='%m/%d/%y %H:%M')


@pytest.fixture(name='sample_pvsyst_hourly_qc')
def sample_pvsyst_hourly_qc_fixture(sample_pvsyst_hourly) -> pd.DataFrame:
    """Fixture for sample qc system data."""
    testdtaqc = sample_pvsyst_hourly.copy()
    testdtaqc = (
        testdtaqc
        .loc[
            testdtaqc['GlobInc'].ge(400)
            & testdtaqc['EOutInv'].lt(0.995 * testdtaqc['EOutInv'].max())
            , ['GlobInc', 'T_Amb', 'WindVel', 'EOutInv']]
        .rename(
            columns={
                'EOutInv': 'P'
                , 'T_Amb' : 'T_a'
                , 'GlobInc': 'E'
                , 'WindVel': 'v'}))
    return testdtaqc


def test_model(sample_pvsyst_hourly_qc):
    """Test Model class."""
    mod1 = Model(sample_pvsyst_hourly_qc)
    assert isinstance(mod1, Model)
    fit1 = mod1.fit()
    assert isinstance(fit1, ModelFit)
    ans1 = fit1.predict()
    assert isinstance(ans1, pd.DataFrame)
    assert (len(sample_pvsyst_hourly_qc), 3) == ans1.shape
    ref_cond = pd.DataFrame(
        {
            'E': 650.0
            , 'T_a': 25.0
            , 'v': 3.5}
        , index=['arbitrary_rc']
    )
    ans2 = fit1.predict(ref_cond, conf_level=0.9)
    assert isinstance(ans2, pd.DataFrame)
    assert (1, 3) == ans2.shape
    assert 'arbitrary_rc' == ans2.index[0]
    assert np.allclose(
        ans2.iloc[0, :]
        , np.array([1460548.0, 1430605.0, 1490491.0])
        , rtol=1e-6)
