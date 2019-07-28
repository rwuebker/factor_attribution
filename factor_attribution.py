import datetime as dt
import numpy as np
import os
import pandas as pd
from pandas.tseries.offsets import BDay
from scipy.stats import zscore
from tqdm import tqdm


class FactorAttribution:

    def __init__(self, date_str=dt.date.today().strftime('%Y-%m-%d'), prices_dir='prices', info_dir='info', periods=1):
        # prev date is decision date, trade date is the price we get
        self.date_str = date_str
        self.date = dt.datetime.strptime(date_str, '%Y-%m-%d')
        self.analysis_date = self.date - BDay(2)
        self.analysis_date_str = self.analysis_date.strftime('%Y-%m-%d')
        self.prev_date = self.analysis_date - BDay(periods)
        self.prev_date_str = self.prev_date.strftime('%Y-%m-%d')
        self.trade_date = self.analysis_date + BDay(1)
        self.trade_date_str = self.trade_date.strftime('%Y-%m-%d')
        self.year_ago = self.analysis_date - BDay(252)
        self.year_ago_str = self.year_ago.strftime('%Y-%m-%d')
        self.month_ago = self.analysis_date - BDay(22)
        self.month_ago_str = self.month_ago.strftime('%Y-%m-%d')
        self.prices_dir = prices_dir
        self.info_dir = info_dir
        self.date_sets = {}

    def run_attribution(self):
        self._load_info()
        self._load_prices()


    def _load_info(self):
        # use last business days date for info
        path = '{}/info_{}'.format(self.info_dir, self.analysis_date_str)
        totals = pd.DataFrame()
        if os.path.exists(path):
            for filename in os.listdir(path):
                if filename.endswith('.csv'):
                    df = pd.read_csv('{}/{}'.format(path, filename))
                    df.columns = ['ticker', 'mkt_cap', 'cur_price', 'prev_price', 'beta', 'book_value', 'sector', 'eps']
                    df.set_index('ticker', inplace=True)
                    totals = totals.append(df)

        self.info = totals

    def _load_prices(self):
        path = '{}/prices_{}'.format(self.prices_dir, self.date_str)
        info = self.info
        totals = pd.DataFrame()
        if os.path.exists(path):
            for filename in tqdm(os.listdir(path)):
                if filename.endswith('.csv'):
                    ticker = filename.replace('.csv', '')
                    self._initialize_date_set(ticker)
                    full_file_name = '{}/{}'.format(path, filename)
                    print('this is full_file_name: ', full_file_name)
                    df = pd.read_csv(full_file_name, index_col='Date')
                    data = {
                            "month_ago": self._get_value(ticker, df, 'month_ago', 'Adj Close'),
                            "year_ago": self._get_value(ticker, df, 'year_ago', 'Adj Close'),
                            "prev_date": self._get_value(ticker, df, 'prev_date', 'Adj Close'),
                            "analysis_date": self._get_value(ticker, df, 'analysis_date', 'Adj Close'),
                            "trade_date": self._get_value(ticker, df, 'trade_date', 'Adj Close'),
                            "today": self._get_value(ticker, df, 'date', 'Adj Close'),
                            "volume": self._get_value(ticker, df, 'analysis_date', 'Volume')
                    }
                    new_df = pd.DataFrame(data, index=[ticker])
                    totals = totals.append(new_df)
            final = pd.merge(info, totals, left_index=True, right_index=True)

        self.info = final
        print(final.head())

    def _initialize_date_set(self, ticker):
        date_set = {
            'date': self.date,
            'date_str': self.date_str,
            'prev_date': self.prev_date,
            'prev_date_str': self.prev_date_str,
            'analysis_date': self.analysis_date,
            'analysis_date_str': self.analysis_date_str,
            'trade_date': self.trade_date,
            'trade_date_str': self.trade_date_str,
            'year_ago': self.year_ago,
            'year_ago_str': self.year_ago_str,
            'month_ago': self.month_ago,
            'month_ago_str': self.month_ago_str
        }
        self.date_sets[ticker] = date_set


    def _get_value(self, ticker, df, time_frame, value_name):
        counter = 0
        value = 'NOPE'
        while value == 'NOPE' and counter < 2:
            date_str = self.date_sets[ticker]['{}_str'.format(time_frame)]
            if date_str in df.index:
                value = df.at[date_str, value_name]
            else:
                value = 'NOPE'
                if time_frame == 'trade_date':
                    return np.nan
                self._adjust_date(ticker, time_frame)
                counter += 1
        if value == 'NOPE':
            return np.nan
        else:
            return value

    def _adjust_date(self, ticker, time_frame):
        if time_frame == 'trade_date':
            return False
        print('adjusting data for ticker: {} and this time frame: {}'.format(ticker, time_frame))
        self.date_sets[ticker][time_frame] = self.date_sets[ticker][time_frame] - BDay(1)
        self.date_sets[ticker]['{}_str'.format(time_frame)] = self.date_sets[ticker][time_frame].strftime('%Y-%m-%d')
        return True


if __name__ == '__main__':
    fa = FactorAttribution(date_str='2019-07-26')
    fa.run_attribution()
