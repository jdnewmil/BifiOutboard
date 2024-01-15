# pvcaptest_io.py

import pathlib
import pandas as pd


def load_pvsyst_df(
    path
    , renames_list: list[dict] = None
    , **kwargs
):
    """
    Load data from a PVsyst energy production model.

    Will load day first or month first dates. Expects files that use a comma as a
    separator rather than a semicolon.

    Parameters
    ----------
    path : str
        Path to file to import.
    renames_list : list[dict], default None
        List of dictionaries defining columns that need renaming. If None, the default
        value will be set to [{"T Amb": "T_Amb"}, {"TAmb": "T_Amb"}]. If you want no
        translations, pass an empty list [].
    **kwargs
        Use to pass additional kwargs to pandas read_csv. Pass sep=';' to load files
        that use semicolons instead of commas as the separator.

    Returns
    -------
    CapData

    Notes
    -----
    Standardizes the ambient temperature column name to T_Amb. v6.63 of PVsyst
    used "T Amb", v.6.87 uses "T_Amb", and v7.2 uses "T_Amb". Will change 'T Amb'
    or 'TAmb' to 'T_Amb' if found in the column names.

    """
    if renames_list is None:
        renames_list0 = [{"T Amb": "T_Amb"}, {"TAmb": "T_Amb"}]
    else:
        renames_list0 = renames_list

    dirName = pathlib.Path(path)

    encodings = ["utf-8", "latin1", "iso-8859-1", "cp1252"]
    for encoding in encodings:
        try:
            # there is a pandas bug prior to pandas v1.3.0 that causes the blank
            # line between the headers and data to be skipped
            # after v.1.3.0, the blank line will be loaded
            # loading headers and data separately and then combining them to avoid
            # issues with pandas versions before and after the fix
            pvraw_headers = pd.read_csv(
                dirName, skiprows=10, encoding=encoding, header=[0, 1], **kwargs
            ).columns
            pvraw_data = pd.read_csv(
                dirName, skiprows=12, encoding=encoding, header=None, **kwargs
            ).dropna(axis=0, how="all")
            pvraw = pvraw_data.copy()
            pvraw.columns = pvraw_headers
        except UnicodeDecodeError:
            continue
        else:
            break

    pvraw.columns = pvraw.columns.droplevel(1)
    try:
        dates = pvraw.loc[:, "date"]
    except KeyError:
        warnings.warn(
            "No 'date' column found in the PVsyst data. This may be due to "
            "the separator being a semicolon ';' rather than a comma ','. "
            "If this is the case, try passing sep=';' when calling load_pvsyst. "
            "Otherwise the date column may actually be missing. Exception:"
        )
        raise
    # PVsyst creates dates like '01/01/90 00:00' i.e. January 1st, 1990.
    # Opening the PVsyst output in excel will likely result in the dates modified to
    # 1/1/1990 0:00. The strftime format specified won't load the excel modified dates
    # so these are caught by checking for consistent length and reformatted
    if not all(dates.str.len() == 14):
        date_parts = dates.str.split(' ').str[0].str.split('/')
        time_parts = dates.str.split(' ').str[1].str.split(':')
        dates = (
            date_parts.str[0].str.zfill(2) + '/' +
            date_parts.str[1].str.zfill(2) + '/' +
            '90 ' +
            time_parts.str[0].str.zfill(2) + ':' +
            time_parts.str[1]
        )
    try:
        # mm/dd/yy hh:mm, lower case y gives
        # Year without century as a zero-padded decimal number. e.g. 00, 01, …, 99
        dt_index = pd.to_datetime(dates, format="%m/%d/%y %H:%M")
    except ValueError:
        warnings.warn(
            'Dates are not in month/day/year format. '
            'Trying day/month/year format.'
        )
        dt_index = pd.to_datetime(dates, format="%d/%m/%y %H:%M")
    pvraw.index = dt_index
    pvraw.drop("date", axis=1, inplace=True)
    for d in renames_list0:
        pvraw = pvraw.rename(columns=d, )
    pvraw.index.name = "Timestamp"

    return pvraw
