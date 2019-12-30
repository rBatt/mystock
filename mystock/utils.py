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
    start = f"{str(min(x))}-01-01"
    end = f"{str(max(x))}-12-31"
    days = count_tdays(x=(start, end))
    days['year'] = days.index.year
    cnts = days.loc[:,['year']].groupby('year').size()
    cnts_yrs = cnts.index.map(type(x[0])) # change type to match input (if input was str)
    return {k:v for k, v, in zip(cnts_yrs, cnts.values)}
