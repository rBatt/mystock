"""Statistics for Your Stock Data"""
from ..mystock import utils # works ...
from .utils import count_tdays # works ...


def _get_total_shares(x): # TODO where does this belong? Util? Some new data module?
    """Helper to Get Total Shares

    Basically calculates a cummulative sum

    Args:
        x (DataFrame): DataFrame with 'symbol' and 'date' index, 'shares' column

    Returns:
        pandas.Series: a series named 'total_shares' that has
            the total shares at a time period
    """
    tot_x = x.sort_values(by=['symbol','date']).groupby('symbol').shares.cumsum()
    tot_x.name = 'total_shares'
    return x.join(tot_x)


def _get_hpr(M_t, flow_t, M_t1):
    """Get Holding Period Return (HPR)

    Formula variable definitions taken from here:
        https://en.wikipedia.org/wiki/Time-weighted_return#Time-weighted_return_compensating_for_external_flows

    Put in separate function basically just for documentation purposes.
    The calculation is simple, but the interpretation needs clarification.

    Args:
        M_t (scalar or Series): Money at time t, immediately after flow_t
            (includes cash flow at time t)
        flow_t (scalar or Series): Cash flow immediately prior to calculating
            M_T, but at time t
        M_t1 (scalar or Series): Money at time t-1

    Returns:
        [type]: [description]
    """
    return (M_t - flow_t)/M_t1


def _get_twr(x, annualize=False, ann_tday=253):
    """Get Time-Weighted Return (TWR)

    https://en.wikipedia.org/wiki/Time-weighted_return#Time-weighted_return_compensating_for_external_flows

    Make sure the DataFrame `x` is sorted by date (ascending; oldest at the top).
        Presumably `x` has 'date' in its index, but this isn't
        strictly necessary (just needs to be sorted).

    Args:
        x (DataFrame): a DataFrame with columns of 'tday' and 'hpr';
            expected as a time series
        annualize (bool, optional): If True, annualizes the TWR. Defaults to False.
        ann_tday (int, optional): Number of (trading) days to use in
            annualization calc. Defaults to 253.

    Returns:
        DataFrame: a pandas DataFrame with a column of 'twr'
    """
    tday_elapsed = x.tday.diff(1).sum()
    twr = x.agg({'hpr':'prod'})
    twr.rename({'hpr':'twr'}, inplace=True) # after agg product, hpr is essentially twr
    if annualize:
        twr['twr'] = (twr.twr**(1/tday_elapsed))**ann_tday

    return twr


def _get_naive_return(x, annualize=False, ann_tday=253):
    """Get Naive Return

    Most basic way of calculating return ... doesn't account holding duration

    Args:
        x (DataFrame): DataFrame with 'date' index, columns for
            'end_value_t' (see M_T in _get_hpr()) and 'txn_value' (shares * price)
        annualize (bool, optional): If True, annualizes output. Defaults to False.
        ann_tday (int, optional): Number of (trading) days to use in
            annualization calc. Defaults to 253.

    Returns:
        [type]: [description]
    """
    get_end_date = lambda x: x.index.get_level_values('date').max()
    end_date = get_end_date(x)
    end_value = x.loc[([end_date]), 'end_value_t'].sum()
    total_txn = x.txn_value.sum()
    naive_return = (end_value-total_txn)/total_txn + 1
    if annualize:
        end_tday = x.loc[([end_date]), 'tday'].unique()[0]
        naive_return = (naive_return**(1/end_tday))**253
    return naive_return


# time-weighted return
def calc_twr(user_txn, stockdata, total=True, annualize=False):
    """Calculate Time-Weighted Return (and other Return Statistics).
    
    Args:
        user_txn (DataFrame): user transaction data with
            'symbol' and 'date' as index, 'shares' as column
        stockdata (DataFrame): StockData() type data, with
            'symbol' and 'date' as index, 'close' as column
        total (bool, optional): Calculate total returns (over all symbols). Defaults to True.
        annualize (bool, optional): If True, annualizes return rate. Defaults to False.
    
    Returns:
        dict:
            'naive_return': scalar indicator basic return rate
            , 'twr': scalar indicating time-weighted return rate
            , 'df': DataFrame with joined inputs and
                    intermediates like Holding Period Return (HPR)
    """

    # join 2 data sets
    df = user_txn.join(stockdata.close)

    # prepare cashflow values at time t, and holding values for times t and t-1
    df.loc[:,'txn_value'] = df.shares * df.close
    df.loc[:,'end_value_t'] = df.total_shares * df.close
    df.loc[:,'end_value_t1'] = df.loc[:,'end_value_t'].groupby('symbol').shift(1, fill_value=0)

    # aggregate if not calculating Returns for each symbol
    if total:
        df.drop(columns=['shares', 'total_shares', 'close'], inplace=True)
        df = df.groupby('date').sum()

    # calculate holding period return
    hpr = _get_hpr(M_t=df.end_value_t, flow_t=df.txn_value, M_t1=df.end_value_t1)

    # calculate trading days
    tdays = utils.count_tdays(hpr.index.get_level_values('date'))
    tdays.drop(columns=['market_open', 'market_close'], inplace=True)
    tdays.index = tdays.index.astype(str)

    # add HPR and TradingDays to the DF
    df['hpr'] = df.index.map(hpr)
    df = df.join(tdays)

    # calculate TWR and naive return
    if total:
        twr = _get_twr(x=df, annualize=annualize)
        naive_return = _get_naive_return(df, annualize=annualize)
    else:
        grouped = df.groupby('symbol')
        twr = grouped.apply(_get_twr, annualize=annualize)
        naive_return = grouped.apply(_get_naive_return, annualize=annualize)

    # format output
    out = {
        'naive_return': naive_return
        , 'twr': twr.twr
        , 'df': df
    }

    return out




# average return over period (move window around)

