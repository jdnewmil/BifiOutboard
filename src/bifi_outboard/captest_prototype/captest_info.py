# captest_info.py

from dataclasses import dataclass
from typing import Callable, Any, TypeVar, TypeAlias, Optional, ClassVar, Iterator
from collections.abc import Hashable, Iterator
import numpy as np
import pandas as pd
import pandas.core.groupby.generic as pdgeneric
import pandas.api.typing as pdtyping
import matplotlib.figure as mfig
import matplotlib.pyplot as plt
import plotnine as p9
from ruamel.yaml import YAML, yaml_object
from bifi_outboard.captest_prototype import column_selection
from bifi_outboard.captest_prototype import model_ols
from .model import ReferenceCondition  # model prototypes

K = TypeVar('K')  # hashable key
T = TypeVar('T')  # iterator value type

DataframeDictIterator: TypeAlias = Iterator[tuple[K, pd.DataFrame]]
RCBuilder: TypeAlias = Callable[[str, dict[str, Any]], ReferenceCondition]

def onegroup(
    df: pd.DataFrame
) -> DataframeDictIterator:
    return (tup for tup in df.groupby(lambda x: True))


# @yaml_object(column_selection.yaml)
# @dataclass
# class ComputedRCSpec:
#     yaml_tag = '!ComputedRCSpec'
#     method: str
#     default_rc: dict[str, Any]

#     instantiation_map: ClassVar[dict[str, RCBuilder]]

#     def build(self, **kwargs) -> ReferenceCondition:
#         if self.method not in ComputedRCSpec.instantiation_map.keys():
#             raise ValueError(f'Unrecognized ComputedRCSpec.method "{self.method}"')
#         return ComputedRCSpec.instantiation_map[self.method](
#             self.method
#             , self.default_rc
#             , **kwargs)


@yaml_object(column_selection.yaml)
@dataclass
class ModelOLSRCSpec:
    yaml_tag = '!ModelRCSpec'
    model_type: str
    reference_spec: ReferenceCondition
    output_col_name: str
    formula: str
    coef_names: list[str]
    conf_level: float

    def build_reference_inputs(
        self
        , dta_key: Hashable
        , qcdta_redundant: pd.DataFrame
    ) -> dict[str, float]:
        return self.reference_spec.get_reference_condition(
            dta_key=dta_key
            , qcdta_redundant=qcdta_redundant)
        

    def build_model(
        self
        , df: pd.DataFrame
        , reference_inputs: dict[str, float]
    ) -> model_ols.Model:
        return model_ols.Model(
            data=df
            , formula=self.formula
            , input_names=tuple(reference_inputs.keys())
            , output_name=self.output_col_name
            , coef_labels=self.coef_names)


default_model_info = {
    'ASTM_E2848': {
        'model_type': 'ASTM_E2848'
        , 'formula': 'P ~ E + I(E * E) + I(E * T_a) + I(E * v) -1' 
        , 'coef_names' : ['a1', 'a2', 'a3', 'a4']
        , 'output_col_name': 'P'}
    , 'DNV_Bifi_ASTM': {
        'model_type': 'DNV_Bifi_ASTM'
        , 'formula': (
            'P ~ '
            'I(E_front + E_rear) '
            '+ I(I(E_front+E_rear) * E_front) '
            '+ I(I(E_front+E_rear) * E_rear) '
            '+ I(I(E_front+E_rear) * T_a) '
            '+ I(I(E_front+E_rear) * v) '
            '-1')
        , 'coef_names' : ['a1', 'a2a', 'a2b', 'a3', 'a4']
        , 'output_col_name': 'P'}}


@dataclass
class RedundantCalcColumnInfo:
    ds_cols: set[str]
    r_cols: set[str]
    r_missing_cols: set[str]
    c_cols: set[str]
    c_missing_cols: set[str]
    model_cols: set[str]


@dataclass
class RedundantCalcData:
    dta_key: Hashable
    qcdta_redundant: pd.DataFrame
    qcdta_computed: pd.DataFrame


def me_fitconf(
    model_rc_spec: ModelOLSRCSpec
    , rccd: RedundantCalcData
    , rcci: RedundantCalcColumnInfo
) -> pd.Series:
    """Model/fit/predict confidence intervals.

    Parameters
    ----------
    model_rc_spec : ModelOLSRCSpec
        Captest model object for a single data set.
    rccd : RedundantCalcData
        Redundantly-combined dataset, and computed dataset. Model
        is assumed to rely on the computed dataset.
    rcci : RedundantCalcColumnInfo
        Variables being extracted from data. Ignored
        in this function, parameter is suppled for
        custom results reviews.

    Returns
    -------
    pd.DataFrame
        _description_
    """
    reference_inputs = (
        model_rc_spec
        .build_reference_inputs(dta_key=rccd.dta_key, qcdta_redundant=rccd.qcdta_computed))
    model_obj = (
        model_rc_spec
        .build_model(
            rccd.qcdta_computed
            , reference_inputs=reference_inputs))
    fit = model_obj.fit()
    result = fit.predict(
        new_data=pd.DataFrame(reference_inputs, index=[0])
        , conf_level=model_rc_spec.conf_level)
    return result # .loc[0, :] # type: ignore


@yaml_object(column_selection.yaml)
@dataclass
class OLSCapTestInfo:
    yaml_tag = '!OLSCapTestInfo'
    model_rc_spec: ModelOLSRCSpec
    computed_set_data: column_selection.QCComputedSetData

    def model_runner(
        self
        , gdf: Iterator[tuple[K, pd.DataFrame]]
        , qc_fun: Optional[Callable[[Hashable, pd.DataFrame], pd.DataFrame]] = None
        , model_extractor: Callable[
            [ModelOLSRCSpec, RedundantCalcData, RedundantCalcColumnInfo], T] = me_fitconf
        , gdf_columns: Optional[set[str]] | Optional[list[str]] = None
    ) -> Iterator[tuple[K, T]]:
        # handle DataFrame like it is a grouped dataframe
        _gdf: DataframeDictIterator = (
            onegroup(gdf)
            if isinstance(gdf, pd.DataFrame)
            else gdf)
        # if not grouped, group all rows together
        if isinstance(gdf, pd.DataFrame) and gdf_columns is None:
            gdf_columns = set(gdf.columns)
        else:
            if gdf_columns is None:
                raise ValueError(
                    "When passing a grouped/resampled dataframe to "
                    "OLSCapTestInfo.model_runner, you must"
                    "also supply the column names in gdf_columns.")
            elif not isinstance(gdf_columns, set):
                gdf_columns = set(gdf_columns)
        # retrieve the input and output columns from the model
        model_cols = (
            set(
                self
                .model_rc_spec
                .reference_spec
                .reference_variables)
            | set(self.model_rc_spec.output_col_name))
        c_cols, c_missing_cols = (
            self
            .computed_set_data
            .seek_cols(missing_cols=model_cols))
        r_cols, r_missing_cols = (
            self
            .computed_set_data
            .redundant_data
            .seek_cols(missing_cols=c_missing_cols))
        ds_cols, ds_missing_cols = column_selection.seek_dataset_cols(
            gdf_columns
            , missing_cols=r_missing_cols)
        if ds_missing_cols:
            raise ValueError(
                "Required column names not found in CapTestInfo.models "
                f"input data: {ds_missing_cols}")
        rcci = RedundantCalcColumnInfo(
            ds_cols=ds_cols
            , r_cols=r_cols
            , r_missing_cols=r_missing_cols
            , c_cols=c_cols
            , c_missing_cols=c_missing_cols
            , model_cols=model_cols)
        if qc_fun is None:
            _qc_fun = lambda dta_key, df: df
        else:
            _qc_fun = qc_fun
        return (
            (k, self._apply_model_extractor(
                dta_key=k
                , df=df
                , qc_fun=_qc_fun
                , model_extractor=model_extractor
                , rcci=rcci))
            for k, df in _gdf)

    def _apply_model_extractor(
        self
        , dta_key: Hashable
        , df: pd.DataFrame
        , qc_fun: Callable[[Hashable, pd.DataFrame], pd.DataFrame]
        , model_extractor: Callable[
            [ModelOLSRCSpec, RedundantCalcData, RedundantCalcColumnInfo], T]
        , rcci: RedundantCalcColumnInfo
    ) -> T:
        # separate out redundant values
        qcdta_redundant = self.computed_set_data.redundant_data.combine(
            qc_fun(dta_key, df)
            , list(rcci.r_missing_cols - rcci.r_cols))
        # apply computations to redundant values
        qcdta_computed = self.computed_set_data.compute(
            qcdta_redundant
            , list(rcci.c_missing_cols - rcci.r_cols))
        return model_extractor(
            self.model_rc_spec
            , RedundantCalcData(                
                dta_key=dta_key
                , qcdta_redundant=qcdta_redundant
                , qcdta_computed=qcdta_computed)
            , rcci)


def mr_fitconf_combine(
    mr_out: Iterator[tuple[Any, pd.DataFrame]]
    , key_names: list[str]
    , droplevel: bool = False
) -> pd.DataFrame:
    d = {
        k: v
        for k, v in mr_out}
    result = pd.concat(d.values(), keys=d.keys(), names=key_names)
    if droplevel:
        result = result.droplevel(0)
    return result


ct_periods = {
    'Monthly': {'offset_alias': 'MS', 'column_name': 'MonthBegin'}
    , 'Weekly': {'offset_alias': 'W-MON', 'column_name': 'WeekBegin'}
}


@dataclass
class OLSFullModel:
    model_rc_spec: ModelOLSRCSpec
    rcci: RedundantCalcColumnInfo
    rccd: RedundantCalcData
    reference_inputs: dict[str, float]
    model_obj: model_ols.Model
    fit: model_ols.ModelFit

    def plot(self, method: Optional[str] = None, **kwargs) -> mfig.Figure:
        """Generate matplotlib-compatible plots.

        Parameters
        ----------
        method : str, optional
            specify which plot is desired, by default None.
            - 'partregress_grid': partial regression, grid
                including result vs each input.
            - 'influence_plot': plot of standardized residuals
                versus influence, selected points labeled using the most
                influential dataframe index values.

        Returns
        -------
        mfig.Figure
            Matplotlib Figure object.

        Raises
        ------
        ValueError
            _description_
        """
        if method is None or 'partregress_grid' == method:
            return self.fit.plot(method='partregress_grid')
        elif 'influence_plot' == method:
            return self.fit.plot(method='influence_plot')
        raise ValueError(f'Unknown method "{method}" in OLSFullModel.autoplot')
        
    def autoplot(
        self
        , method: Optional[str] =None
        , nrow: Optional[int] = None
        , ylim: Optional[tuple[float, float]] = None
        ,  **kwargs
    ) -> p9.ggplot:
        """Generate plotnine-compatible plot objects.

        Parameters
        ----------
        method : str, optional
            Label string indicating which plot is desired, by default None
            Supported methods:
            - 'partial_model': plot of results vs each of the regression
                inputs, with guide lines.
        nrow : Optional[int], optional
            Number of rows in facet_wrap, by default None
        ylim : Optional[tuple[float, float]], optional
            Range into which to restrict output axis, by default None

        Returns
        -------
        p9.ggplot
            A ggplot object that can be modified with further
            plotnine functions.

        Raises
        ------
        ValueError
            If method is not one of the supported values, this exception
            will be raised.
        """
        if 'partial_model' == method:
            refdf = pd.DataFrame(
                self.reference_inputs
                , index=['value'])
            target = self.fit.predict(new_data=refdf)
            target['neg'] = -np.Inf
            target['pos'] = np.Inf
            return (
                p9.ggplot(
                    self.vdta().reset_index()
                    , p9.aes(x='x', y='y'))
                + p9.geom_rect(
                    data=target
                    , mapping=p9.aes(
                        ymin='lwr'
                        , ymax='upr'
                        , xmin='neg'
                        , xmax='pos')
                    , fill='green'
                    , alpha=0.1
                    , inherit_aes=False)
                + p9.geom_point(size=1, alpha=0.2)
                + p9.geom_vline(
                    data=refdf.T.rename_axis('spec_var').reset_index()
                    , mapping=p9.aes(xintercept='value', group='spec_var')
                    , color='blue')
                + p9.geom_hline(
                    data=target
                    , mapping=p9.aes(yintercept='fit')
                    , color='green')
                + p9.facet_wrap(
                    '~ spec_var'
                    , nrow=nrow
                    , scales='free_x')
                + p9.labs(
                    x='Value'
                    , y=self.model_rc_spec.output_col_name)
                + p9.coord_cartesian(
                    ylim=ylim
                ))
        else:
            raise ValueError(f'Unknown method "{method}" in OLSFullModel.autoplot')

    def marginal_df(self, spec_var: str) -> pd.DataFrame:
        f = self.fit.fit
        rcdf = pd.DataFrame(
            self.reference_inputs
            , index=f.resid.index)
        rcdf[spec_var] = self.rccd.qcdta_computed[spec_var]
        rcdf[self.model_obj.output_name] = f.predict(rcdf) + f.resid
        return pd.DataFrame(
            {
                'x': rcdf[spec_var]
                , 'y': rcdf[self.model_obj.output_name]})

    def vdta(self) -> pd.DataFrame:
        return pd.concat(
            [
                self.marginal_df(spec_var=spec_var)
                for spec_var in self.model_obj.input_names]
            , keys=[
                spec_var
                for spec_var in self.model_obj.input_names]
            , names=['spec_var'])


def full_model_extractor(
    model_rc_spec: ModelOLSRCSpec
    , rccd: RedundantCalcData
    , rcci: RedundantCalcColumnInfo
) -> OLSFullModel:
    reference_inputs = (
        model_rc_spec
        .build_reference_inputs(dta_key=rccd.dta_key, qcdta_redundant=rccd.qcdta_computed))
    model_obj = (
        model_rc_spec
        .build_model(
            rccd.qcdta_computed
            , reference_inputs=reference_inputs))
    return OLSFullModel(
        model_rc_spec=model_rc_spec
        , rcci=rcci
        , rccd=rccd
        , reference_inputs=reference_inputs
        , model_obj=model_obj
        , fit=model_obj.fit())


@dataclass
class PeriodicCaptest():
    """Divide dataframes by periods.

    Parameters
    ----------
    period_label : str
    test_info : OLSCapTestInfo
    qcdta_iterator : Iterator[tuple[Hashable, pd.DataFrame]]
    
    """
    period_label: str
    olsfullmodels: Iterator[tuple[Any, OLSFullModel]]

    def __init__(
        self
        , period_label: str
        , test_info: OLSCapTestInfo
        , qcdta_iterator: Iterator[tuple[Hashable, pd.DataFrame]]
        , qcdta_columns: set[str]
        , model_extractor: Callable[
            [ModelOLSRCSpec, RedundantCalcData, RedundantCalcColumnInfo]
            , OLSFullModel]
        , min_len: Optional[int] = None
    ):
        """Initialize the periodic data iterator for capacity tests.

        Parameters
        ----------
        period_label : str
            One of the values in the dictionary "ct_periods", e.g.
            "Monthly" and "Weekly".
        test_info : OLSCapTestInfo
            Object encapsulating the core capacity test configuration
            to be applied to the data.
        qcdta_iterator : Iterator[tuple[Hashable, pd.DataFrame]]
            Dataframe iterator. Each dataframe is expected to have
            a non-MultiIndex Timestamp index, and have columns named
            with strings including at least the column names indicated
            in the qcdta_columns parameter.
        qcdta_columns : set[str]
            Minimal set of column names that can be expected to
            be in the dataframes processed in the iterator pipeline.
        model_extractor : Callable[ [ModelOLSRCSpec, RedundantCalcData, RedundantCalcColumnInfo] , OLSFullModel]
            Function to extract relevant results from the raw
            capacity test results.
        min_len : Optional[int], optional
            Minimum number of rows that must be in the dataframe
            to perform the capacity test, by default None (which means
            to estimate using the number of variables used in
            the model). If any of the intervals has insufficient
            rows, then it will be omitted from the iterator pipeline
            entirely. This does mean that it is possible that zero
            results might get returned in the entire pipeline when
            there is too little data in all periods. 
        """
        if min_len is None:
            _min_len = len(
                test_info
                .model_rc_spec
                .reference_spec
                .reference_variables) + 2
        else:
            _min_len = min_len
        self.period_label = period_label
        self.olsfullmodels = (
            test_info.model_runner(
                gdf=(
                    ((k, tm), interval_dsdta_aug)
                    for k, qcdta in qcdta_iterator
                    for tm, interval_dsdta_aug in (
                        qcdta.resample(
                            ct_periods[period_label]['offset_alias']))
                    if _min_len <= len(interval_dsdta_aug))
                , gdf_columns=set(qcdta_columns)
                , model_extractor=model_extractor))

    def __iter__(self):
        return iter(self.olsfullmodels)

    def __next__(self):
        return next(self.olsfullmodels)


@yaml_object(column_selection.yaml)
@dataclass
class FixedReferenceCondition:
    """Predefined reference conditions class.
    """
    reference_inputs: dict[str, float]

    @property
    def reference_variables(self) -> list[str]:
        """Retrieve list of reference variables.

        Returns
        -------
        list[str]
            list of variables in the keys of the dictionary
            returned by get_reference_condition.
        """
        return list(self.reference_inputs.keys())


    def get_reference_condition(
        self
        , dta_key: Hashable
        , qcdta_redundant: pd.DataFrame
    ) -> dict[str, float]: # type: ignore
        return self.reference_inputs.copy()


