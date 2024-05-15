# captest_info_test.py

import pathlib
from typing import Any
import numpy as np
import pandas as pd
import pytest
from .. import io
from .. import sim_study
from .. import captest_info

dta_dir = pathlib.Path(__file__).resolve().parent / 'data'

base_offset = 0.5

run_info_bifi = pd.Series(
    {
        'VCn': 1
        , 'bifi_sim': True
        , 'SystemLabel': 'SAT1'
        , 'SiteLabel': 'Sacramento'
        , 'NearAlbedo': 0.2
        , 'Bifaciality': 0.7
        , 'Height': 2.0
        , 'Notes': 'ran as bifi'
        , 'Csvfile': 'SAT\\Test Bifi SAT_Project_VC1_HourlyRes_0.CSV'
        , 'sep': ','
        , 'dayfirst': False
        , 'date_format': '%m/%d/%y %H:%M'
        , 'StrucShd': 0.05
        , 'BakMismatch': 0.1
        , 'OhmicDC': 1.5
        , 'Uc': 25
        , 'Uv': 1.2
        , 'MQF': -0.8
        , 'MismatchMPP': 1
        , 'MismatchVMPP': 0.15
        , 'LID': 0.5
        , 'SoilingLoss': 0
        , 'IAM': 'FresnelNormal'
        , 'Pitch': 5
        , 'Spc': 0.02
        , 'Tilt': 0
        , 'Azimuth': 0
        , 'ModMfr': 'HT-SAAE'
        , 'ModPAN': 'HT_SAAE_HT78_18X_580_Bifacial.PAN'
        , 'ModNs': 18
        , 'ModNp': 245
        , 'InvMfr': 'SMA'
        , 'InvOND': 'SMA_Central_2200.OND'
        , 'Ninv': 1
        , 'FarAlbedo': 0.2
        , 'Orientation': 'SAT'
        , 'GCR': 0.493
        , 'Latitude': 33.45
        , 'Longitude': -111.983}
    , name = ('Test Bifi SAT_Project.PRJ', 'SAT Az0 (bifi)'))

run_info_mono = pd.Series(
    {
        'VCn': 0
        , 'bifi_sim': False
        , 'SystemLabel': 'SAT1'
        , 'SiteLabel': 'Sacramento'
        , 'NearAlbedo': np.nan
        , 'Bifaciality': 0.0
        , 'Height': np.nan
        , 'Notes': 'Ran as mono'
        , 'Csvfile': 'SAT\\Test Bifi SAT_Project_VC0_HourlyRes_0.CSV'
        , 'sep': ','
        , 'dayfirst': False
        , 'date_format': '%m/%d/%y %H:%M'
        , 'StrucShd': 0.0
        , 'BakMismatch': 0.0
        , 'OhmicDC': 1.5
        , 'Uc': 25
        , 'Uv': 1.2
        , 'MQF': -0.8
        , 'MismatchMPP': 1
        , 'MismatchVMPP': 0.15
        , 'LID': 0.5
        , 'SoilingLoss': 0
        , 'IAM': 'FresnelNormal'
        , 'Pitch': 5
        , 'Spc': 0.02
        , 'Tilt': 0
        , 'Azimuth': 0
        , 'ModMfr': 'HT-SAAE'
        , 'ModPAN': 'HT_SAAE_HT78_18X_580_Bifacial.PAN'
        , 'ModNs': 18
        , 'ModNp': 245
        , 'InvMfr': 'SMA'
        , 'InvOND': 'SMA_Central_2200.OND'
        , 'Ninv': 1
        , 'FarAlbedo': 0.2
        , 'Orientation': 'SAT'
        , 'GCR': 0.493
        , 'Latitude': 33.45
        , 'Longitude': -111.983}
    , name=('Test Bifi SAT_Project.PRJ', 'SAT Az0 (mono)')
)

model_specs_bifi = sim_study.define_sample_captests(
    run_info=run_info_bifi
    , base_offset=0.5)

model_specs_mono = sim_study.define_sample_captests(
    run_info=run_info_mono
    , base_offset=0.5)

sample_case_mono = pd.Series(
    {
        'Description': 'Monofacial'
        , 'Sim. type': 'Monofacial'
        , 'Model': 'ASTM E2848'
        , 'Position': 'N/A'
        , 'QC': 'Default'
        , 'PRJ': 'Test Bifi SAT_Project.PRJ'
        , 'Variant': 'SAT Az0 (mono)'}
    , name=1)

sample_case_bifi0 = pd.Series(
    {
        'Description': 'Bifacial as if it were monofacial'
        , 'Sim. type': 'Bifacial'
        , 'Model': 'ASTM E2848'
        , 'Position': 'N/A'
        , 'QC': 'Default'
        , 'PRJ': 'Test Bifi SAT_Project.PRJ'
        , 'Variant': 'SAT Az0 (bifi)'}
    , name=1)

# (Sim type, Model, Position, QC) : ((PRJ, sim case), model)
ct_cases = pd.DataFrame(
    columns=
        ['Description', 'Sim. type', 'Model', 'Position', 'QC', 'PRJ', 'Variant']
    , data = [
        [
            'Monofacial'
            , 'Monofacial', 'ASTM E2848', 'N/A', 'Default'
            , 'Test Bifi SAT_Project.PRJ', 'SAT Az0 (mono)']
        , [
            'Bifacial as if it was monofacial'
            , 'Bifacial', 'ASTM E2848', 'N/A', 'Default'
            , 'Test Bifi SAT_Project.PRJ', 'SAT Az0 (bifi)'
        ]
        , [
            'Bifacial w/ ref. module'
            , 'Bifacial', 'ASTM E2848', 'Ref. Module', 'Default'
            , 'Test Bifi SAT_Project.PRJ', 'SAT Az0 (bifi)'
        ]
        , [
            'Bifacial with ideal sensor underneath'
            , 'Bifacial', 'ASTM E2848+Erear', 'Under', 'Default'
            , 'Test Bifi SAT_Project.PRJ', 'SAT Az0 (bifi)'
        ]
        , [
            'Bifacial with outboard sensor and default QC'
            , 'Bifacial', 'ASTM E2848+Erear', 'Outboard', 'Default'
            , 'Test Bifi SAT_Project.PRJ', 'SAT Az0 (bifi)'
        ]
        , [
            'Bifacial with outboard sensor and E_rear QC'
            , 'Bifacial', 'ASTM E2848+Erear', 'Outboard', 'E_rear<75'
            , 'Test Bifi SAT_Project.PRJ', 'SAT Az0 (bifi)'
        ]
    ]
    , index=pd.Index(list(range(1, 7)), name='Case No.') 
)

globbakunshd_rcs = {
    pd.Timestamp('1990-01-01 00:00:00'): 26.981518666666666
    , pd.Timestamp('1990-02-01 00:00:00'): 31.652935074626868
    , pd.Timestamp('1990-03-01 00:00:00'): 41.21492821782178
    , pd.Timestamp('1990-04-01 00:00:00'): 39.971012264150936
    , pd.Timestamp('1990-05-01 00:00:00'): 34.837842465753425
    , pd.Timestamp('1990-06-01 00:00:00'): 37.55683647540984
    , pd.Timestamp('1990-07-01 00:00:00'): 39.1290447761194
    , pd.Timestamp('1990-08-01 00:00:00'): 41.96564210526316
    , pd.Timestamp('1990-09-01 00:00:00'): 37.71646654804271
    , pd.Timestamp('1990-10-01 00:00:00'): 34.02840492610837
    , pd.Timestamp('1990-11-01 00:00:00'): 29.145112213740457
    , pd.Timestamp('1990-12-01 00:00:00'): 25.395580882352945}

@pytest.fixture
def hrly_dta_bifi() -> pd.DataFrame:
    return io.read_pvsyst_hourly(
        dta_dir / 'Test Bifi SAT_Project_VC1_HourlyRes_0.CSV'
        , sep=','
        , dayfirst=False
        , date_format='%m/%d/%y %H:%M')

@pytest.fixture
def hrly_dta_bifi_aug(hrly_dta_bifi) -> pd.DataFrame:
    return sim_study.augment_sim_data(
        hrly_dta_bifi
        , run_info=run_info_bifi
        , offset=base_offset)

@pytest.fixture
def hrly_bifi_qc(hrly_dta_bifi_aug) -> pd.Series:
    return sim_study.mark_qc(hrly_dta_bifi_aug)

@pytest.fixture
def hrly_bifi_qcdta(hrly_dta_bifi_aug, hrly_bifi_qc) -> pd.DataFrame:
    return sim_study.apply_qc(df=hrly_dta_bifi_aug, qc=hrly_bifi_qc)


@pytest.fixture
def hrly_dta_mono() -> pd.DataFrame:
    return io.read_pvsyst_hourly(
        dta_dir / 'Test Bifi SAT_Project_VC0_HourlyRes_0.CSV'
        , sep=','
        , dayfirst=False
        , date_format='%m/%d/%y %H:%M')

@pytest.fixture
def hrly_dta_mono_aug(hrly_dta_mono) -> pd.DataFrame:
    return sim_study.augment_sim_data(
        hrly_dta_mono
        , run_info=run_info_mono
        , offset=base_offset)

@pytest.fixture
def hrly_mono_qc(hrly_dta_mono_aug) -> pd.Series:
    return sim_study.mark_qc(hrly_dta_mono_aug)


@pytest.fixture
def hrly_mono_qcdta(hrly_dta_mono_aug, hrly_mono_qc) -> pd.DataFrame:
    return sim_study.apply_qc(df=hrly_dta_mono_aug, qc=hrly_mono_qc)

@pytest.fixture
def run_infos() -> pd.DataFrame:
    return pd.concat([run_info_bifi, run_info_mono], axis=1).T # type: ignore


def test_ref_calculation_agg():
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 1.0, 0.0])
    ans1 = sim_study.ref_calculation_agg(rca=10, s=s)
    assert 10 == ans1
    ans2 = sim_study.ref_calculation_agg(rca='mean', s=s)
    assert np.allclose(1.83333, ans2)
    ans3 = sim_study.ref_calculation_agg(rca='median', s=s)
    assert np.allclose(1.5, ans3)
    ans4 = sim_study.ref_calculation_agg(rca='p60', s=s)
    assert np.allclose(2.0, ans4)
    

def test_EquivalentPositionReferenceCondition(hrly_mono_qcdta, hrly_bifi_qcdta):
    one_globbakunshd_rcs = {True: 110}
    eprc_mono = sim_study.EquivalentPositionReferenceCondition(
        default_rc={'E': 500, 'T_a': 20, 'v': 4}
        , e_cell_rc=480
        , e_cell_colname='GlobCell'
        , e_globbakunshd_rc=100
        , e_globbakunshd_rcs=one_globbakunshd_rcs # type: ignore
        , e_globbakunshd_colname='GlobBakUnshd'
        , bifaciality=0.7
        , model='ASTM E2848'
        , bifi_position='N/A')
    ans1a = eprc_mono.get_reference_condition(
        dta_key=True
        , qcdta_redundant=hrly_mono_qcdta)
    # monofacial simulation, GlobInc corresponding to GlobCell (=GlobEff) is higher
    assert np.allclose(503.226093, ans1a['E'], rtol=1e-6)
    ans1b = eprc_mono.get_reference_condition(
        dta_key=True
        , qcdta_redundant=hrly_bifi_qcdta)
    # bifacial simulation, GlobInc corresponding to GlobCell is lower
    # because of contribution from rear side displacing front-side
    # irradiance
    assert np.allclose(466.040345, ans1b['E'], rtol=1e-6)

    eprc_refmod = sim_study.EquivalentPositionReferenceCondition(
        default_rc={'E': 500, 'T_a': 20, 'v': 4}
        , e_cell_rc=480
        , e_cell_colname='GlobCell'
        , e_globbakunshd_rc=None
        , e_globbakunshd_rcs=one_globbakunshd_rcs # type: ignore
        , e_globbakunshd_colname='GlobBakUnshd'
        , bifaciality=0.7
        , model='ASTM E2848'
        , bifi_position='Ref. Module')
    ans2a = eprc_refmod.get_reference_condition(
        dta_key=True
        , qcdta_redundant=hrly_bifi_qcdta)
    # bifacial simulation, direct GlobCell reference
    assert np.allclose(480.0, ans2a['E'], rtol=1e-6)

    eprc_bifi_under = sim_study.EquivalentPositionReferenceCondition(
        default_rc={'E': 500, 'T_a': 'p60', 'v': 'median'}
        , e_cell_rc=480
        , e_cell_colname='GlobCell'
        , e_globbakunshd_rc=None
        , e_globbakunshd_rcs=one_globbakunshd_rcs # type: ignore
        , e_globbakunshd_colname='GlobBakUnshd'
        , bifaciality=0.7
        , model='ASTM E2848+Erear'
        , bifi_position='Under')
    ans2b = eprc_bifi_under.get_reference_condition(
        dta_key=True
        , qcdta_redundant=hrly_bifi_qcdta)
    assert np.allclose(429.624596, ans2b['E_front'], rtol=1e-6)
    assert np.allclose(110.0, ans2b['E_rear'], rtol=1e-6)
    assert np.allclose(24.67, ans2b['T_a'], rtol=1e-6)
    assert np.allclose(2.1999, ans2b['v'], rtol=1e-6)

    eprc_bifi_outboard = sim_study.EquivalentPositionReferenceCondition(
        default_rc={'E_front': 500, 'E_rear': 90, 'T_a': 'mean', 'v': 'p60'}
        , e_cell_rc=480
        , e_cell_colname='GlobCell'
        , e_globbakunshd_rc=None
        , e_globbakunshd_rcs=one_globbakunshd_rcs # type: ignore
        , e_globbakunshd_colname='GlobBakUnshd'
        , bifaciality=0.7
        , model='ASTM E2848+Erear'
        , bifi_position='Outboard'
        , override_rcs={
            True: {
                'E_front': 500.0
                , 'E_rear': 111.0
                , 'T_a': 3
                , 'v': 2.1}})
    ans2c = eprc_bifi_outboard.get_reference_condition(
        dta_key=True
        , qcdta_redundant=hrly_bifi_qcdta)
    assert np.allclose(500.0, ans2c['E_front'], rtol=1e-6)
    assert np.allclose(111.0, ans2c['E_rear'], rtol=1e-6)
    assert np.allclose(3.0, ans2c['T_a'], rtol=1e-6)
    assert np.allclose(2.1, ans2c['v'], rtol=1e-6)

# def test_periodiccaptest(hrly_dta):
    # all_fits_eq_rc = (
    #     pd.concat(
    #         [
    #             sim_study.calc_case_periodic_cts(
    #                 sample_case=sample_case
    #                 , qc_results=qc_results
    #                 , period_label='Monthly'
    #                 , ct_case_rcs=ct_case_rcs)
    #             for k, sample_case in ct_cases.iterrows()]
    #         , keys=ct_cases['Description']))



def test_calc_case_periodic_models(hrly_dta_bifi_aug, run_infos):
    sample_case = sample_case_bifi0.copy()
    run_info1 = (
        run_infos
        .loc[sim_study.make_case_run_info_key(sample_case=sample_case)])
    mspec1 = sim_study.model_spec_per_sample_case(
        sample_case # type: ignore
        , rc_calc='mean'
        , run_info=run_info1
        , globbakunshd_rc=None
        , globbakunshd_rcs=globbakunshd_rcs # type: ignore
        , conf_level=0.95)
    qc_result = sim_study.get_qcresult(
        run_info=run_info1
        , dsdta=hrly_dta_bifi_aug
        , qc_method=sample_case['QC']
        , globbakunshd_rcs=globbakunshd_rcs
        , offset=base_offset)
    ans1 = sim_study.calc_case_periodic_models(
        sample_case=sample_case
        , qc_result=qc_result
        , period_label='Monthly'
        , model_spec=mspec1)
    assert 12 == len(ans1)  # type: ignore
    assert isinstance(
        ans1[(True, pd.Timestamp('1990-01-01 00:00:00'))]  # type: ignore
        , captest_info.OLSFullModel)

