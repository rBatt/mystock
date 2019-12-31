
from ..mystock import utils # works ...
from .utils import count_tdays # works ...

def _get_total_shares(x): # TODO where does this belong? Util? Some new data module?
    tot_x = x.sort_values(by=['symbol','date']).groupby('symbol').shares.cumsum()
    tot_x.name = 'total_shares'
    return x.join(tot_x)

def _get_hpr(M_t, flow_t, M_t1):
    return (M_t - flow_t)/M_t1

def _get_twr(x, annualize=False, ann_tday=253): # x is a dataframe or a groupby
    tday_elapsed = x.tday.diff(1).sum()
    twr = x.agg({'hpr':'prod'})
    twr.rename({'hpr':'twr'}, inplace=True) # after agg product, hpr is essentially twr
    if annualize:
        twr['twr'] = (twr.twr**(1/tday_elapsed))**ann_tday

    return twr

def _get_naive_return(x, annualize=False):
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
    # user_txn: dataframe, should have index ['date','symbol']
    #     and column for 'shares' and 'total_shares'
    # stockdata: dataframe, should have same index, plus closing price # TODO change to just 'price'
    # total: if True, will compute statistics for aggregate holdings, else if False will do for each symbol
    # annual: if False, calculates statistics for total time period in user_txn

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

    if total:
        twr = _get_twr(x=df, annualize=annualize)
        naive_return = _get_naive_return(df, annualize=annualize)
    else:
        grouped = df.groupby('symbol')
        twr = grouped.apply(_get_twr, annualize=annualize)
        naive_return = grouped.apply(_get_naive_return, annualize=annualize)

    out = {
        'naive_return': naive_return
        , 'twr': twr.twr
        , 'df': df
    }

    return out




# average return over period (move window around)

