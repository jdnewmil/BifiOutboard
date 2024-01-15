# captest.py

import pandas as pd
import captest as ct
from . import columngroups


def make_pvsyst_captest(
    df: pd.DataFrame
    , name: str ="pvsyst"
    , egrid_unit_adj_factor: float = None
    , set_regression_columns: bool =True
    , column_groups: ct.columngroups.ColumnGroups = None
) -> ct.capdata.CapData:
    """
    Construct a CapData object given a PVsyst simulation data frame.

    Will load day first or month first dates. Expects files that use a comma as a
    separator rather than a semicolon.

    Parameters
    ----------
    df : pd.DataFrame
        Data frame to initialize the CapData object with.
    name : str, default pvsyst
        Name to assign to returned CapData object.
    egrid_unit_adj_factor : numeric, default None
        E_Grid will be divided by the value passed.
    set_regression_columns : bool, default True
        By default sets power to E_Grid, poa to GlobInc, t_amb to T Amb, and w_vel to
        WindVel. Set to False to not set regression columns on load.
    column_groups : ct.columngroups.ColumnGroups, optional
        Column groups to use with df. If None then a default list of
        type_defs will be used to create a default grouping. Default None.

    Returns
    -------
    CapData
    """
    cd = ct.capdata.CapData(name)
    cd.data = df.copy()
    cd.data['index'] = (
        cd
        .data
        .index
        .to_series()
        .apply(
            lambda x: x.strftime('%m/%d/%Y %H %M')))
    if egrid_unit_adj_factor is not None:
        cd.data["E_Grid"] = cd.data["E_Grid"] / egrid_unit_adj_factor
    cd.data_filtered = cd.data.copy()
    if column_groups is None:
        cd.column_groups = columngroups.group_columns(cd.data)
    else:
        cd.column_groups = column_groups
    cd.trans_keys = list(cd.column_groups.keys())
    if set_regression_columns:
        cd.set_regression_cols(
            power="E_Grid", poa="GlobInc", t_amb="T_Amb", w_vel="WindVel")
    return cd
