# test_ct_captest.py

import pathlib
import bifi_outboard as bob
import captest as ct


dtadir = pathlib.Path('data')

def test_make_pvsyst_captest():
    fname0 = dtadir / 'FT' / 'Test Bifi Sheds_Project_VC0_HourlyRes_0.CSV'
    df = bob.pvcaptest.io.load_pvsyst_df(fname0)
    cg = bob.pvcaptest.columngroups.group_columns_generic(df)
    ans = bob.pvcaptest.captest.make_pvsyst_captest(
        df
        , "pvsyst"
        , set_regression_columns=False
        , column_groups=cg)
    assert isinstance(ans, ct.capdata.CapData)
    