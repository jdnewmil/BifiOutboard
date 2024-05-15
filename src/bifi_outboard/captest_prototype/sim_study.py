# sim_study.py


from typing import Optional, Iterator, Any, Callable, TypeAlias \
    , TypeVar, Hashable
from dataclasses import dataclass
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from . import captest_info
from . import column_selection
from . import model
from .. import outboard_sat

T = TypeVar('T')  # generator value type

#base_offset = 0.5

def define_sample_captests(
    run_info: pd.Series
    , base_offset: float
) -> tuple[
    captest_info.OLSCapTestInfo
    , captest_info.OLSCapTestInfo]:
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
            , cf_params={})
        }
    # scc1b = {
    #     'E_front': column_selection.SCADAComputedColumn(
    #         computed_function='Linear'
    #         , computed_value_columns={'GlobInc': 1.0}
    #         , cf_params={})
    #     , 'E_rear': column_selection.SCADAComputedColumn(
    #         computed_function='Outboard_PVsyst_SAT_POA'
    #         , computed_value_columns={
    #             'AzSol': 1.0, 'HSol': 1.0, 'PhiAng': 1.0, 'GlobHor': 1.0
    #             , 'GlobGnd': 1.0, 'BkVFLss': 1.0, 'DifSBak': 1.0
    #             , 'BmIncBk': 1.0}
    #         , cf_params={
    #             'height': float(run_info['Height'])
    #             , 'offset': base_offset
    #             , 'GCR': float(run_info['GCR'])
    #             , 'NearAlbedo': float(run_info['NearAlbedo'])})
    #     , 'T_a': column_selection.SCADAComputedColumn(
    #         computed_function='Linear'
    #         , computed_value_columns={'T_Amb': 1.0}
    #         , cf_params={})
    #     , 'v': column_selection.SCADAComputedColumn(
    #         computed_function='Linear'
    #         , computed_value_columns={'WindVel': 1.0}
    #         , cf_params={})
    #     , 'P': column_selection.SCADAComputedColumn(
    #         computed_function='Linear'
    #         , computed_value_columns={'EOutInv': 1.0}
    #         , cf_params={})
    #     }
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
    # qcwsd1b = column_selection.QCComputedSetData(
    #     computed_columns=scc1b
    #     , redundant_data=qcrsd1)
    mrcs1 = captest_info.ModelOLSRCSpec(
        reference_spec=captest_info.FixedReferenceCondition(
            reference_inputs={
                'E': 680, 'T_a': 20.0, 'v': 3.5})
        , conf_level=0.95
        , **captest_info.default_model_info['ASTM_E2848'])
    # mrcs1b = captest_info.ModelOLSRCSpec(
    #     reference_spec=captest_info.FixedReferenceCondition(
    #         reference_inputs={
    #             'E_front': 605, 'E_rear': 107, 'T_a': 20.0, 'v': 3.5})
    #     , conf_level=0.95
    #     , **captest_info.default_model_info['DNV_Bifi_ASTM'])
    ti0 = captest_info.OLSCapTestInfo(
        model_rc_spec=mrcs1
        , computed_set_data=qcwsd0)
    ti1 = captest_info.OLSCapTestInfo(
        model_rc_spec=mrcs1
        , computed_set_data=qcwsd1)
    return ti0, ti1


def mark_qc(df: pd.DataFrame, method='Default') -> pd.Series:
    qc = pd.Series('Ok', index=df.index)
    qc = qc.where(
        df['GlobInc'].ge(400.0)
        , 'Low GlobInc')
    qc = qc.where(
        df['EOutInv'].le(0.995 * df['EOutInv'].max())
        , 'Clipped power')
    qc_cat = ['Low GlobInc', 'Clipped power']
    if 'E_rear<75' == method:
        qc = qc.where(
            df['E_rear_outboard'].gt(75.0)
            , 'Low E_rear')
        qc_cat = qc_cat + ['E_rear<75']
    elif 'Default' != method:
        raise ValueError(f'Unexpected method "{method}" in apply_qc.')
    qc = pd.Categorical(
        qc
        , categories=['Ok'] + qc_cat)
    return pd.Series(qc, index=df.index)


def apply_qc(
    df: pd.DataFrame
    , qc: pd.Series
    , cols: Optional[set[str]] = None
) -> pd.DataFrame:
    if cols is None:
        qcdta = df.loc['Ok' == qc, :]
    else:
        qcdta = df.loc['Ok' == qc, cols] # type: ignore
    return qcdta # type: ignore


@dataclass
class QCResult:
    qcdta: pd.DataFrame
    qc: pd.Series
    dsdta_aug: pd.DataFrame
    run_info: pd.Series
    globbakunshd_rcs: dict[pd.Timestamp, float]
    offset: float


# CaseTuple: TypeAlias = tuple[str, str, str, tuple[str, str]]
# (Model, Position, QC, (PRJ, Variant))
# see ct_cases
# RefConditionDef: TypeAlias = dict[str, float]
# {model_variable: reference_value}


def build_scc_map(model: str, position: str) -> dict[str, str]:
    """Build model variable to redundant variable map.

    To identify reference conditions, specific real-world variable values must
    be used. In the case of field data, values must be redundantly determined.
    In the case of simulated data, there is no redundancy, but the needed
    variables will be identified from the input to the computed variable
    dataset. This function identifies the variables needed from the redundant
    output data set for reference conditions.
    """
    scc_map = {
        'P': 'EOutInv'
        , 'T_a': 'T_Amb'
        , 'v': 'WindVel' }
    if 'ASTM E2848' == model:
        if 'Ref. Module' == position:
            scc_map['E'] = 'GlobCell'
        elif 'N/A' == position:
            scc_map['E'] = 'GlobInc'
        else:
            raise ValueError(f'Unexpected position "{position}" in build_scc_map. for model=ASTM E2848')
    elif 'ASTM E2848+Erear' == model:
        scc_map['E_front'] = 'GlobInc'
        if 'Outboard' == position:
            scc_map['E_rear'] = 'E_rear_outboard'
        elif 'Under' == position:
            scc_map['E_rear'] = 'GlobBakUnshd'
        else:
            raise ValueError(
                f'Unexpected position "{position}" in '
                'build_scc_map for model=ASTM E2848+Erear')
    else:
        raise ValueError(
            f'Unexpected model "{model}" in '
            'build_scc_map')
    return scc_map


e_rear_ts_map = {
    'AzSol': 'AzSol'
    , 'HSol': 'HSol'
    , 'PhiAng': 'PhiAng'
    , 'GlobHor': 'GlobHor'
    , 'GlobGnd': 'GlobGnd'
    , 'BkVFLss': 'BkVFLss'
    , 'DifSBak': 'DifSBak'
    , 'BmIncBk': 'BmIncBk'}


e_rear_info_map = {
    'height': 'Height'
    , 'GCR': 'GCR'
    , 'NearAlbedo': 'NearAlbedo'}


def calc_E_rear_from_info(
    tsdta: pd.DataFrame
    , infodta: pd.Series
    , offset: float
    , tsmap: Optional[dict[str, str]] = None
    , infomap: Optional[dict[str, str]] = None
) -> pd.Series:
    _tsmap = e_rear_ts_map if tsmap is None else tsmap
    _infomap = e_rear_info_map if infomap is None else infomap
    kwargs_ts = {
        k: tsdta[v]
        for k, v in _tsmap.items()}
    kwargs_info = {
        k: infodta[v]
        for k, v in _infomap.items()}
    kwargs = kwargs_ts | kwargs_info
    result = outboard_sat.calc_E_rear(offset=offset, **kwargs)['E_rear'] # type: ignore
    return result


def augment_sim_data(
    er_df: pd.DataFrame
    , run_info: pd.Series
    , offset: float
) -> pd.DataFrame:
    result = er_df.copy()
    result['DiffuseFraction'] = (
        result['DiffHor'] / result['GlobHor'])
    result['Tilt'] = np.abs(result['PhiAng'])
    if run_info['bifi_sim']:
        result['GlobBakUnshd'] = (
            result['GlobBak'] + result['BackShd'])
        result['GlobCell'] = (
            result['GlobInc']
            + run_info['Bifaciality'] * result['GlobBak'])
        if 'SAT' in run_info['SystemLabel']:
            result['E_rear_outboard'] = calc_E_rear_from_info(
                er_df
                , run_info
                , offset=offset)
        elif 'FT' in run_info['SystemLabel']:
            # needs further review
            result['E_rear_outboard'] = result['GlobBakUnshd']
        else:
            raise ValueError(
                'Cannot determine array orientation in '
                'augment_system_data for SystemLabel '
                f'"{run_info["SystemLabel"]}"')
    else:
        result['GlobCell'] = result['GlobEff']
    return result


def ref_calculation_agg(
    rca: str | float | int
    , s: pd.Series
) -> float:
    if isinstance(rca, float) or isinstance(rca, int):
        return rca
    else:
        if 'median' == rca:
            return s.median()
        elif 'p60' == rca:
            return s.quantile(0.6)
        elif 'mean' == rca:
            return s.mean()
        else:
            raise ValueError(
                f'Unexpected aggregation label "{rca}" '
                'in ref_calculation_agg')


def calc_y_x(df: pd.DataFrame, y: str, x: str, ref_x: float) -> float:
    fit_yx = smf.ols(formula=f'{y} ~ {x}', data=df).fit()
    return fit_yx.predict({x: ref_x})[0]


@dataclass
class EquivalentPositionReferenceCondition:
    """Implement a comparable reference condition.

    Instance of ReferenceCondition Protocol.

    Parameters
    ==========
    default_rc : dict[str, str | float | int]
        Dictionary of reference condition computation specs.
        Only needs to specify T_a and v.
    e_cell_rc : str | float | int
        Reference condition for GlobCell. Any other positions
        will be derived as corresponding to this reference condition.
    e_cell_colname : str
        Redundant variable name for GlobCell (reference module
        irradiance).
    model : str
        Label indicating which regression model to assume. One
        of 'ASTM E2848' or 'ASTM E2848+Erear'.
    bifi_position : str
        Label indicating which rear or combined sensor position
        to assume. For model=ASTM E2848, values of "N/A" and
        "Ref. Module" are supported. For model=ASTM E2848+Erear,
        values of "Under" and "Outboard" are supported.
    override_rc : Optional[dict[Hashable, dict[str, float | int]]], default None
        Dictionary of capacity test cases for which pre-defined
        reference conditions should be used. Special case handling
        for handling varying datasets for which computed rcs would
        not be comparable.
    """
    default_rc: dict[str, str | float | int]
    e_cell_rc: str | float | int
    e_cell_colname: str
    e_globbakunshd_rc: Optional[str | float | int]
    e_globbakunshd_rcs: Optional[dict[Hashable, str | float | int]]
    e_globbakunshd_colname: str
    bifaciality: float
    model: str
    bifi_position: str
    override_rcs: Optional[dict[Hashable, dict[str, float | int]]] = None

    @property
    def reference_variables(self) -> list[str]:
        """Retrieve list of reference variables.

        Returns
        -------
        list[str]
            list of variables in the keys of the dictionary
            returned by get_reference_condition.
        """
        var_db = {
            'ASTM E2848': ['E', 'T_a', 'v', 'GlobCell']
            , 'ASTM E2848+Erear': [
                'E_front', 'E_rear', 'T_a', 'v', 'GlobCell'
                , 'GlobEff', 'GlobBak', 'GlobBakUnshd'
                , 'E_rear_outboard']}
        if self.model not in var_db.keys():
            raise ValueError(
                f'Unknown model "{self.model}" in '
                , 'EquivalentPositionReferenceCondition.reference_variables')
        return var_db[self.model].copy()


    def get_reference_condition(
        self
        , dta_key: Hashable
        , qcdta_redundant: pd.DataFrame
    ) -> dict[str, float]:
        """Retrieve comparable reference condition.

        This class implements an algorithmic method of determining
        a reference set of floating point values
        appropriate to specific boundaries but all corresponding
        to the same reference irradiance at the cell level.

        Parameters
        ----------
        dta_key : Hashable
            Key indicating which of a stream of dataframes supplied by
            generators this one is. Is in this case used to help
            retrieve GlobBakUnshd values to use.
        qcdta_redundant : pd.DataFrame
            Quality-checked data with all redundancies merged
            used as input to the model.

        Returns
        -------
        dict[str, float]
            Dictionary of floating point values, keyed by the names of the
            input variables required by the model.
        """
        if self.override_rcs is not None:
            if dta_key in self.override_rcs:
                return self.override_rcs[dta_key]
        scc_map = build_scc_map(self.model, self.bifi_position)
        e_cell_ref = ref_calculation_agg(
            rca=self.e_cell_rc
            , s=qcdta_redundant[self.e_cell_colname])
        if 'E' in scc_map:
            if 'N/A' == self.bifi_position:
                e_ref = calc_y_x(
                    df=qcdta_redundant
                    , y=scc_map['E']
                    , x=self.e_cell_colname
                    , ref_x=e_cell_ref
                )
            elif 'Ref. Module' == self.bifi_position:
                e_ref = e_cell_ref
            else:
                raise ValueError(
                    f'unexpected bifi_position "{self.bifi_position}"')
            result = {
                'E': e_ref
            }
        elif 'E_front' in scc_map:
            if self.bifi_position not in ['Under', 'Outboard']:
                raise ValueError(
                    f'unexpected bifi_position "{self.bifi_position}"')
            if self.e_globbakunshd_rcs is not None \
                and dta_key in self.e_globbakunshd_rcs:
                if isinstance(self.e_globbakunshd_rcs[dta_key], float) \
                    or isinstance(self.e_globbakunshd_rcs[dta_key], int):
                    e_globbakunshd_ref = self.e_globbakunshd_rcs[dta_key]
                else:
                    raise ValueError(
                        f'Non-numeric value in e_globbakunshd_rcs["{dta_key}"]')
            else:
                if self.e_globbakunshd_rc is not None:
                    e_globbakunshd_ref = ref_calculation_agg(
                        rca=self.e_globbakunshd_rc
                        , s=qcdta_redundant[self.e_globbakunshd_colname])
                else:
                    raise ValueError(
                        'At least one of e_globbakunshd_rc and'
                        f'e_globbakunshd_rcs["{dta_key}"] must not be None')
            e_globbak_ref = calc_y_x(
                df=qcdta_redundant
                , y='GlobBak'
                , x=self.e_globbakunshd_colname
                , ref_x=e_globbakunshd_ref) # type: ignore
            e_globeff_ref = e_cell_ref - self.bifaciality * e_globbak_ref
            e_front_ref = calc_y_x(  # GlobInc
                df=qcdta_redundant
                , y=scc_map['E_front']  # GlobInc
                , x='GlobEff'
                , ref_x=e_globeff_ref)
            if self.e_globbakunshd_colname == scc_map['E_rear']:
                e_rear_ref = e_globbakunshd_ref
            elif 'E_rear_outboard' == scc_map['E_rear']:
                e_rear_ref = calc_y_x(
                    df=qcdta_redundant
                    , y='E_rear_outboard'
                    , x=self.e_globbakunshd_colname
                    , ref_x=e_globbakunshd_ref) # type: ignore
            result = {
                'E_front': e_front_ref
                , 'E_rear': e_rear_ref}
        # apply aggregation rules to remaining variables
        for model_var, model_rc in self.default_rc.items():
            if model_var not in ['E', 'E_front', 'E_rear']:
                result[model_var] = ref_calculation_agg(
                    model_rc
                    , s=qcdta_redundant[scc_map[model_var]])
        return result


def build_pvsyst_olscti(
    mrcspec: captest_info.ModelOLSRCSpec
    , model: str
    , position: str
) -> captest_info.OLSCapTestInfo:
    scc_map = build_scc_map(model=model, position=position)
    # Assumes that E_rear or GlobCell have already been added to qc data
    # rather than being computed on the fly in the computed columns
    scc = {
        model_var: column_selection.SCADAComputedColumn(
            computed_function='Linear'
            , computed_value_columns={data_var: 1.0}
            , cf_params={})
        for model_var, data_var in scc_map.items()}
    # in a simulation, there is no need to use data redundancy
    qcwsd = column_selection.QCComputedSetData(
        computed_columns=scc
        , redundant_data=column_selection.QCRedundantSetData(
            redundant_columns={}))
    return captest_info.OLSCapTestInfo(
        model_rc_spec=mrcspec
        , computed_set_data=qcwsd)


# def make_case_tuple(sample_case: pd.Series) -> CaseTuple:
#     sample_key = (
#         sample_case['Model']
#         , sample_case['Position']
#         , sample_case['QC']
#         , tuple(sample_case.loc[['PRJ', 'Variant']].values))
#     return sample_key

def make_case_run_info_key(sample_case: pd.Series) -> tuple[str, str]:
    return tuple(sample_case.loc[['PRJ', 'Variant']].to_list())


def get_qcresult(
    run_info: pd.Series
    , dsdta: pd.DataFrame
    , qc_method: str
    , globbakunshd_rcs: dict[pd.Timestamp, float]
    , offset: float
) -> QCResult:
    dsdta_aug = augment_sim_data(
        dsdta
        , run_info=run_info
        , offset=offset)
    qc = mark_qc(df=dsdta_aug, method=qc_method)
    qcdta = apply_qc(df=dsdta_aug, qc=qc)
    return QCResult(
        qcdta=qcdta
        , qc=qc
        , dsdta_aug=dsdta_aug
        , run_info=run_info
        , globbakunshd_rcs=globbakunshd_rcs
        , offset=offset)


def calc_case_periodic_ct_gen(
    sample_case: pd.Series
    , qc_result: QCResult
    , period_label: str
    , model_spec: captest_info.ModelOLSRCSpec
    , model_extractor: Callable[
        [
            captest_info.ModelOLSRCSpec
            , captest_info.RedundantCalcData
            , captest_info.RedundantCalcColumnInfo]
        , Any] = captest_info.full_model_extractor
) -> Iterator[tuple[Any, Any]]:
    olscti = build_pvsyst_olscti(
        mrcspec=model_spec
        , model=sample_case['Model']
        , position=sample_case['Position'])
    periodic_fit_gen = captest_info.PeriodicCaptest(
        period_label=period_label
        , test_info=olscti
        , qcdta_iterator=captest_info.onegroup(qc_result.qcdta)
        , qcdta_columns=set(qc_result.qcdta.columns.to_list())
        , model_extractor=model_extractor)
    return periodic_fit_gen


def calc_case_periodic_cts(
    sample_case: pd.Series
    , qc_result: QCResult
    , period_label: str
    , model_spec: captest_info.ModelOLSRCSpec
) -> pd.DataFrame:
    periodic_fit_gen = calc_case_periodic_ct_gen(
        sample_case=sample_case
        , qc_result=qc_result
        , period_label=period_label
        , model_spec=model_spec
        , model_extractor=captest_info.me_fitconf)
    return captest_info.mr_fitconf_combine(
        periodic_fit_gen
        , key_names=[
            'All'
            , captest_info.ct_periods[period_label]["column_name"]
            , 'Ref. Number']
        , droplevel=True)


def calc_case_periodic_models(
    sample_case: pd.Series
    , qc_result: QCResult
    , period_label: str
    , model_spec: captest_info.ModelOLSRCSpec
) -> captest_info.OLSFullModel:
    periodic_fit_gen = calc_case_periodic_ct_gen(
        sample_case=sample_case
        , qc_result=qc_result
        , period_label=period_label
        , model_spec=model_spec
        , model_extractor=captest_info.full_model_extractor)
    return {
        k: mdl
        for k, mdl in periodic_fit_gen} # type: ignore


def model_spec_per_sample_case(
    sample_case: pd.Series
    , rc_calc: str
    , run_info: pd.Series
    , globbakunshd_rc: Optional[str | float | int]
    , globbakunshd_rcs: Optional[dict[Hashable, str | float | int]]
    , conf_level: float = 0.95
    , override_rcs: Optional[dict[Hashable, dict[str, float | int]]] = None
) -> captest_info.ModelOLSRCSpec:
    # run_info_key = tuple(sample_case[['PRJ', 'Variant']].to_list())
    # run_info = run_infos.loc[run_info_key, :] # type: ignore
    model_translation = {
        'ASTM E2848': 'ASTM_E2848'
        , 'ASTM E2848+Erear': 'DNV_Bifi_ASTM'
    }
    if 'ASTM E2848' == sample_case['Model']:
        default_rc = {'E': rc_calc}
    else:
        default_rc = {'E_front': rc_calc, 'E_rear': rc_calc}
    default_rc = default_rc | {'T_a': rc_calc, 'v':rc_calc}
    return captest_info.ModelOLSRCSpec(
        reference_spec=EquivalentPositionReferenceCondition(
            default_rc=default_rc # type: ignore
            , e_cell_rc=rc_calc
            , e_cell_colname='GlobCell'
            , e_globbakunshd_colname='GlobBakUnshd'
            , e_globbakunshd_rc=globbakunshd_rc
            , e_globbakunshd_rcs=globbakunshd_rcs
            , bifaciality=run_info['Bifaciality'] # type: ignore
            , model=sample_case['Model'] # type: ignore
            , bifi_position=sample_case['Position'] # type: ignore
            , override_rcs=override_rcs)
        , conf_level=conf_level
        , **captest_info.default_model_info[
            model_translation[sample_case['Model']]]) # type: ignore
