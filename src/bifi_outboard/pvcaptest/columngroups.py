# pvcaptest_columngroups.pv

import collections
import pandas as pd
import captest as ct


def group_columns_generic(
    data: pd.DataFrame
    , type_defs: collections.OrderedDict = None
) -> ct.columngroups.ColumnGroups:
    """
    Create a dict of raw column names paired to categorical column names.

    Uses a list of type_def formatted dictionaries to determine the type,
    sub-type, and equipment type for data series of a dataframe.  The
    determined types are concatenated to a string used as a dictionary key
    with a list of one or more original column names as the paired value.

    Parameters
    ----------
    data : DataFrame
        Data with columns to group.
    type_defs : collections.OrderedDict
        Column types as keys, lists of substring matches as values.

    Returns
    -------
    ct.columngroups.ColumnGroups
        ColumnGroups object as expected by captest
    """
    if type_defs is None:
        type_defs0 = [
            ct.columngroups.type_defs
            , ct.columngroups.sub_type_defs
            , ct.columngroups.irr_sensors_defs]
    else:
        type_defs0 = type_defs
    # identify column types by multiple categories
    col_types_list = [
        data.apply(ct.columngroups.series_type, args=(t_defs,)).tolist()
        for t_defs in type_defs0]
    # form unified variable names (new_key) for distinct sets of categories
    col_indices = [
        '_'.join(typs)
        for typs in zip(*col_types_list)]
    # list of tuples of new_key, old_key
    names = zip(col_indices, data.columns.tolist())
    # merge old_keys into lists by new_key
    trans = collections.defaultdict(list)
    for new_key, old_key in sorted(names):
        trans[new_key].append(old_key)

    return ct.columngroups.ColumnGroups(sorted(trans.items()))
