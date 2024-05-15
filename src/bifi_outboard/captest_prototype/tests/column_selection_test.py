# column_selection_test.py

import numpy as np
import pandas as pd
from bifi_outboard.captest_prototype import column_selection
from bifi_outboard.captest_prototype import captest_info
from bifi_outboard.captest_prototype import model_ols

scc = {
    'E': column_selection.SCADAComputedColumn(
        computed_function='Linear'
        , computed_value_columns={'GlobInc': 1.0}
        , cf_params={})
    , 'T_a': column_selection.SCADAComputedColumn(
        computed_function='Linear'
        , computed_value_columns={'T_Amb': 1.0}
        , cf_params={})
    , 'v': column_selection.SCADAComputedColumn(
        computed_function='Linear'
        , computed_value_columns={'WindVel': 1.0}
        , cf_params={})
    , 'P': column_selection.SCADAComputedColumn(
        computed_function='Linear'
        , computed_value_columns={'EOutInv': 1.0}
        , cf_params={})}
src1 = {
    'GlobInc': column_selection.SCADARedundantColumn(
        redundant_function='median'
        , redundant_value_columns=['GlobInc']
        , rf_params={})
    , 'T_Amb': column_selection.SCADARedundantColumn(
        redundant_function='median'
        , redundant_value_columns=['T_Amb']
        , rf_params={})
    , 'WindVel': column_selection.SCADARedundantColumn(
        redundant_function='median'
        , redundant_value_columns=['WindVel']
        , rf_params={})}
qcrsd0 = column_selection.QCRedundantSetData(
    redundant_columns={})
qcwsd0 = column_selection.QCComputedSetData(
    computed_columns=scc
    , redundant_data=qcrsd0)
qcrsd1 = column_selection.QCRedundantSetData(
    redundant_columns=src1)
qcwsd1 = column_selection.QCComputedSetData(
    computed_columns=scc
    , redundant_data=qcrsd1)
mrcs1 = captest_info.ModelOLSRCSpec(
    reference_spec=captest_info.FixedReferenceCondition(
        reference_inputs={
            'E': 680, 'T_a': 20.0, 'v': 3.5})
    , conf_level=0.95
    , **captest_info.default_model_info['ASTM_E2848'])
mrcs1b = captest_info.ModelOLSRCSpec(
    reference_spec=captest_info.FixedReferenceCondition(
        reference_inputs={
            'E_front': 605, 'E_rear': 107, 'T_a': 20.0, 'v': 3.5})
    , conf_level=0.95
    , **captest_info.default_model_info['DNV_Bifi_ASTM'])
ti0 = captest_info.OLSCapTestInfo(
    model_rc_spec=mrcs1
    , computed_set_data=qcwsd0)
ti1 = captest_info.OLSCapTestInfo(
    model_rc_spec=mrcs1
    , computed_set_data=qcwsd1)

dsdta1 = pd.DataFrame(
    {
        'EOutInv': [1, 2, 3, 3.5, 4, 5]
        , 'GlobInc': [10, 20, 30, 34, 40, 50]
        , 'T_Amb': [35, 35, 35, 36, 35, 34]
        , 'WindVel': [3, 3, 3, 3.1, 3, 3.2]})

dsdta1_dates = pd.date_range(start='2024-01-01', periods=2, freq='MS')
dsdta1b = (
    pd.concat(
        [dsdta1, dsdta1]
        , keys=dsdta1_dates
        , names=['date', 'hour'])
    .reset_index()
    .assign(
        dtm=lambda df: df['date'] + pd.to_timedelta(df['hour'], unit='h'))
    .drop(columns=['date', 'hour'])
    .set_index('dtm'))

def test_seq():
    model_cols = (
        set(ti1.model_rc_spec.reference_spec.reference_variables)
        | set([ti1.model_rc_spec.output_col_name]))
    c_cols, c_missing_cols = ti1.computed_set_data.seek_cols(
        missing_cols=model_cols)
    r_cols, r_missing_cols = ti1.computed_set_data.redundant_data.seek_cols(
        missing_cols=c_missing_cols)
    ds_cols, ds_missing_cols = column_selection.seek_dataset_cols(
        set(dsdta1.columns.to_list())
        , missing_cols=r_missing_cols)
    assert not ds_missing_cols
    qcdta_red = ti1.computed_set_data.redundant_data.combine(
        dsdta1
        , list(r_missing_cols - r_cols))
    qcdta_calc = ti1.computed_set_data.compute(
        qcdta_red
        , list(c_missing_cols - r_cols))
    assert isinstance(qcdta_calc, pd.DataFrame)
    assert (6, 5) == qcdta_calc.shape
    rcci = captest_info.RedundantCalcColumnInfo(
        ds_cols=ds_cols
        , r_cols=r_cols
        , r_missing_cols=r_missing_cols
        , c_cols=c_cols
        , c_missing_cols=c_missing_cols
        , model_cols=model_cols)
    ans1 = ti1._apply_model_extractor(
        dta_key=True
        , df=dsdta1
        , qc_fun=lambda dta_key, df: df
        , model_extractor=captest_info.me_fitconf
        , rcci=rcci)
    assert np.allclose(
        np.array([51.3333333, 51.3333333, 51.3333333])
        , ans1.iloc[0, :] # type: ignore
        , rtol=1e-5)
    # more compact approach to make ans1
    ans1b = captest_info.mr_fitconf_combine(
            ti1.model_runner(
                gdf=captest_info.onegroup(dsdta1)
                , gdf_columns=set(dsdta1.columns.to_list())) # type: ignore
            , key_names=['All'])
    assert np.allclose(
        np.array([51.3333333, 51.3333333, 51.3333333])
        , ans1b.iloc[0, :] # type: ignore
        , rtol=1e-5)
    # # more explicit way to make ans1
    # ans1c = {
    #     k:v
    #     for k, v in captest_info.mr_fitconf_combine(
    #         ti1.model_runner(
    #             captest_info.onegroup(dsdta1)
    #             , gdf_columns=set(dsdta1.columns.to_list())) # type: ignore
    #         , key_name='All')} # type: ignore
    # assert isinstance(ans1c[True], pd.DataFrame)
    # assert ['fit', 'lwr', 'upr'] == ans1c[True].columns.to_list()
    # explicit way to do periodic capacity tests
    # ans2a = {
    #     k: v.iloc[0, :]
    #     for k, v in ti1.model_runner(
    #         dsdta1b.resample('MS') # type: ignore
    #         , gdf_columns=set(dsdta1.columns.to_list()))}
    # ans2a_df = pd.concat(
    #     ans2a.values()
    #     , keys=ans2a.keys()
    #     , names=['MonthBegin', 'RC'])
    ans2b = captest_info.mr_fitconf_combine(
        captest_info.PeriodicCaptest(
            period_label='Monthly'
            , test_info=ti1
            , qcdta_iterator=captest_info.onegroup(dsdta1b)
            , qcdta_columns=set(dsdta1b.columns.to_list())
            , model_extractor=captest_info.me_fitconf) # type: ignore
        , key_names=['One', 'MonthBegin']
        , droplevel=True)
    assert 2 == len(ans2b)
    # TODO: remove 0 or replace it with something that makes sense
    assert (pd.Timestamp('2024-02-01 00:00:00'), 0) == ans2b.index[1]
    assert 'MonthBegin' == ans2b.index.names[0]
    

