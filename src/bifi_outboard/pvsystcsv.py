# pvsystcsv.py

import pandas as pd


def read_pvsyst_csv(full_fname: str, sep=";", dayfirst=False, encoding="ISO8859"):
    """Simple PVsyst simulation data reader.

    To get at the simulation results in a PVsyst hourly output file,
    numerous header lines must be skipped.

    Parameters
    ----------
    full_fname : str or pathlib.Path
        Filename with extension and relative or absolut path.
    sep : str, optional
        Data and column name separator symbol, by default ";"
    dayfirst : bool, optional
        Whether to assume DMY (or if False then MDY), by default False
    encoding : str, optional
        Encoding to assume for the data file text, by default "ISO8859".

    Returns
    -------
    dta : pd.DataFrame
        8760 hourly rows of simulation results. Consult PVsyst documentation
        for names of simulation outputs that can be specified in that program.
        `date` column in the file is parsed and set as the index of the
        data frame.
    """
    hdr_rows = list(range(10))
    units_row = 11
    blank_row = 12
    dta = pd.read_csv(
        full_fname
        , sep=sep
        , skiprows=hdr_rows + [units_row] + [blank_row]
        , dayfirst=dayfirst
        , index_col='date'
        , parse_dates=[0]
        , encoding=encoding)
    return dta