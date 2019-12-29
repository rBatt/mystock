import pandas as pd
import pandas_market_calendars as mcal


def count_tdays(x):
    """Convert Dates to Integer Sequence of Trading Days

    Forms a regular time series across trading days. Consecutive trading
    days denoted by consecutive integers, even when there are gaps in
    actual dates due to no NYSE trading on those dates.

    Args:
        x (iterable of str or DateTime): dates to be converted to
            trading day indices

    Returns:
        DataFrame: DataFrame with 'date' index of DateTimes
            ranging from min to max of x, and column 'tday'
            as the corresponding integer trading day
    """
    nyse = mcal.get_calendar('NYSE')
    sched = nyse.schedule(min(x), max(x))
    sched.index.name = 'date'
    idx = sched.index.sort_values() # .schedule() wont return dups
    day_dict = {v:i for i, v in enumerate(idx)} # no dups, count fine
    sched['tday'] = idx.map(day_dict)
    return sched


def get_tdays_per_yr(x):
    """Get Number of Trading Days per Year

    Args:
        x (str, int, iterable): year/s of interest

    Returns:
        dict: key is year (as provided), value is number of trading days
    """
    if isinstance(x, (str, int)):
        x = [x]
    yr_ranges = {i:(f'{i}-01-01', f'{i}-12-31') for i in x}
    n_tday = lambda x: count_tdays(x).tday.max()
    out = {k:n_tday(v) for k,v in yr_ranges.items()}
    return out
