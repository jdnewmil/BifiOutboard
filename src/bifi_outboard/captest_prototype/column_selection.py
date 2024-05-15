# column_selection.py

from dataclasses import dataclass
#import pathlib
from typing import Any, Callable, ClassVar, Iterable, Set, AnyStr
# from numpy.typing import ArrayLike
import pandas as pd
# import statsmodels.api as sm
# import statsmodels.formula.api as smf
from io import StringIO
from ruamel.yaml import YAML, yaml_object, ScalarNode
from bifi_outboard import outboard_sat


yaml = YAML(typ='safe', pure=True)
yaml.version = (1, 2)  # type: ignore # better quoting, extended


# show null
def my_represent_none(self, data) -> ScalarNode:
    """

    Parameters
    ----------
    data : Any
        This argument is present for compatibility. It will
        be None because this function is only expected to be called
        if the object to be represented has a None type.
    
    Return
    ------
    ScalarNode

    """
    return self.represent_scalar(u'tag:yaml.org,2002:null', u'null')


# register the my_represent_none Callable for handling objects with None value
yaml.representer.add_representer(type(None), my_represent_none)


def object_to_yaml_str(obj, options=None):
    """Convert a python object into a string containing a YAML representation.

    Parameters
    ----------
    obj : Any
        Object to be represented.
    options : dict[Any], optional
        Additional parameters for ruamel.yaml.dump function, by default None

    Returns
    -------
    str
        String representation of obj in YAML format. 
    """
    if options == None: options = {}
    with StringIO() as string_stream:
        yaml.dump(obj, string_stream, **options)
        output_str = string_stream.getvalue()
    return output_str


def cf_linear(
    df: pd.DataFrame
    , computed_value_columns: dict[str, float]
    , cf_params: dict[str, float]
) -> pd.Series:
    if 0 == len(computed_value_columns):
        return pd.Series(pd.NA, index=df.index)
    dta = df[computed_value_columns.keys()]
    coefs = pd.Series(computed_value_columns)
    return dta.mul(coefs, axis=1).sum(axis=1)


def cf_outboard_pvsyst_sat_poa(
    df: pd.DataFrame
    , computed_value_columns: dict[str, float]
    , cf_params: dict[str, float]
) -> pd.Series:
    float_parms = {'height', 'offset', 'GCR', 'NearAlbedo'}
    cv_cols = {
        'AzSol', 'HSol', 'PhiAng', 'GlobHor', 'GlobGnd'
        , 'BkVFLss', 'DifSBak', 'BmIncBk'}
    missing_cols = [
        cvk
        for cvk in computed_value_columns.keys()
        if cvk not in cv_cols]
    if 0 < len(missing_cols):
        raise ValueError(f"argument specification is missing required columns for Outboard_PVsyst_SAT: {missing_cols}")
    missing_parms = [
            cpk
            for cpk in cf_params.keys()
            if cpk not in float_parms]
    if 0 < len(missing_parms):
        raise ValueError(f"argument specification is missing required parameters for Outboard_PVsyst_SAT: {missing_parms}")
    dta_cols = {
        k: df[k]
        for k, v in computed_value_columns.items()}
    return outboard_sat.calc_E_rear(**{
        **dta_cols
        , **cf_params})['E_rear']


@yaml_object(yaml)
@dataclass
class SCADAComputedColumn:
    """Computed column specification.

    This object specifies a set of input columns to be used to compute
    a new output column. The transformation function is specified using
    a label that must be in the default_computed_functions module scope
    dictionary keys with a corresponding Callable.
    Each computed_value_column has an associated floating point number
    (coefficient) to make the simplest case of linear combining of the
    input columns straightforward.
    In addition, the cf_params attribute allows additional float values
    (parameters) to be passed to the corresponding Callable. 
    It is notable that all values at any timestamp must pass QC for
    the result qc to pass QC. If the input values are not redundant,
    this may make obtaining data records that pass all QC more difficult.
    """
    yaml_tag = '!SCADAComputedColumn'
    compute_functions: ClassVar[
        dict[
            str
            , Callable[
                [
                    pd.DataFrame
                    , dict[str, float]
                    , dict[str, float]]
                , pd.Series]]
    ] = {
        'Linear': cf_linear
        , 'Outboard_PVsyst_SAT_POA': cf_outboard_pvsyst_sat_poa}

    computed_function: str
    computed_value_columns: dict[str, float]
    cf_params: dict[str, float]


    def compute(self, df: pd.DataFrame) -> pd.Series:
        def safe_lookup(
            computed_function: str
        ) -> Callable[
            [
                pd.DataFrame
                , dict[str, float]
                , dict[str, float]]
            , pd.Series
        ]:
            if computed_function not in SCADAComputedColumn.compute_functions:
                raise ValueError(
                    f'Computed function {computed_function} not configured '
                    'in SCADAComputedColumn.compute_functions')
            return SCADAComputedColumn.compute_functions[computed_function]
    
        return (
            safe_lookup(computed_function=self.computed_function)(
                df
                , self.computed_value_columns
                , self.cf_params))


def rf_median(
    df: pd.DataFrame
    , redundant_value_columns: list[str]
    , rf_params: dict[str, Any]
) -> pd.Series:
    if 0 == len(redundant_value_columns):
        return pd.Series(pd.NA, index=df.index)
    dta = df[redundant_value_columns]
    return dta.median(axis=1)


@yaml_object(yaml)
@dataclass
class SCADARedundantColumn:
    """(TODO) Filters columns according to qc and aggregates to one column. 

    This object specifies a set of input value columns to be used to compute a
    new output column. The assumption is that all of the input columns
    are interchangeable, and the goal is to eliminate outlier values
    in each row of the columns before aggregating the remaining values
    in that row to obtain a single result that passes QC.
    It is notable that as few as one valid value per row can allow
    that row to pass QC, making it easier to obtain more valid records
    for modeling.
    """
    yaml_tag = '!SCADARedundantColumn'
    redundant_functions: ClassVar[
        dict[
            str
            , Callable[
                [
                    pd.DataFrame
                    , list[str]
                    , dict[str, Any]]
                , pd.Series]]
    ] = {
        'median': rf_median}

    redundant_function: str
    redundant_value_columns: list[str]
    rf_params: dict[str, Any]

    def combine(self, df: pd.DataFrame) -> pd.Series:
        def safe_lookup(redundant_function: str) -> Callable:
            if redundant_function not in SCADARedundantColumn.redundant_functions:
                raise ValueError(
                    f'Redundant function {redundant_function} not configured '
                    'in SCADARedundantColumn.redundant_functions')
            return SCADARedundantColumn.redundant_functions[redundant_function]
        return safe_lookup(self.redundant_function)(
            df
            , self.redundant_value_columns
            , self.rf_params)


@yaml_object(yaml)
@dataclass
class QCRedundantSetData:
    """Contain a map of result column names to SCADARedundantColumn objects.

    (TODO) May in the future also contain a specification for quality
    control (marking of rows) of input data.
    """
    yaml_tag = '!QCRedundantSetData'
    redundant_columns: dict[str, SCADARedundantColumn]

    def seek_cols(
        self
        , missing_cols: set[str]
    ) -> tuple[set[str], set[str]]:
        rcs = self.redundant_columns
        # identify subset of computed columns that are actually needed
        r_cols = missing_cols.intersection(set(rcs.keys()))
        # identify union of all input columns needed to compute c_cols
        rv_cols = (
            set()
            .union(*[
                set(v.redundant_value_columns)
                for v in rcs.values()]))
        return r_cols, (missing_cols - r_cols) | rv_cols
    
    def combine(self, df: pd.DataFrame, extra_cols: list[str]) -> pd.DataFrame:
        # TODO enhance to deal with merging quality flags on input columns
        # to create an appropriate quality marking for the output columns
        return pd.concat(
            [
                pd.DataFrame(
                    {
                        k: v.combine(df)
                        for k, v in self.redundant_columns.items()})
                , df[extra_cols]]
            , axis=1)


@yaml_object(yaml)
@dataclass
class QCComputedSetData:
    """Contain a map of column names and a link to a redundant data spec.
    """
    yaml_tag = '!QCComputedSetData'

    redundant_data: QCRedundantSetData
    computed_columns: dict[str, SCADAComputedColumn]

    def seek_cols(self, missing_cols: set[str]) -> tuple[set[str], set[str]]:
        """Seek columns needed for analysis.

        The computed column definitions may satisfy some or all of the
        input needs for modeling. Assuming the modeled columns have not
        yet been found (missing_cols), this method returns a set of
        column names representing the computations needed for the
        model (keys of the computed column map) and a second set
        representing all column names needed for the needed computations)
        along with any remaining column names from the input missing_cols
        parameter.

        Parameters
        ----------
        missing_cols : set[str]
            Column names that have not yet been found (presumably all
            of the column names referenced in the model.)

        Returns
        -------
        tuple[set[str], set[str]]
            Two sets of column names: computed columns present in the
            missing_cols parameter, and a second set including all
            input columns needed to compute the columns listed in the
            first returned set, along with any of the missing_cols that
            were not listed in the first set.

        """
        ccs = self.computed_columns
        # identify subset of computed columns that are actually needed
        c_cols = missing_cols.intersection(set(ccs.keys()))
        # identify union of all input columns needed to compute c_cols
        cv_cols = (
            set()
            .union(*[
                set(v.computed_value_columns.keys())
                for v in self.computed_columns.values()]))
        return c_cols, (missing_cols - c_cols) | cv_cols

    def compute(self, df: pd.DataFrame, extra_cols: list[str]) -> pd.DataFrame:
        ccdta = pd.DataFrame(
            {
                dest_computed_col: scc.compute(df)
                for dest_computed_col, scc in self.computed_columns.items()})
        missing_cols = list(set(extra_cols) - set(ccdta.columns.to_list()))
        return pd.concat(
            [ccdta, df[missing_cols]]
            , axis=1)


def seek_dataset_cols(
    ds_columns: Set[AnyStr]
    , missing_cols: Set[AnyStr]
) -> tuple[Set[AnyStr], Set[AnyStr]]:
    ds_cols = missing_cols.intersection(set(ds_columns))
    return ds_cols, (missing_cols - ds_cols)
