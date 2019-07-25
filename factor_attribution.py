import datetime as dt
import numpy as np
import os
import pandas as pd
from pandas.tseries.offsets import BDay
from scipy.stats import zscore


class FactorAttribution:

    def __init__(self, date_str=dt.date.today().strftime('%Y-%m-%d'), prices_dir='prices', info_dir='info'):
        self.date_str = date_str
        self.date = dt.datetime.strptime(date_str, '%Y-%m-%d')
        self.prev_date = self.date - BDay(1)
        self.prev_date_str = self.prev_date.strftime('%Y-%m-%d')
        self.one_year_ago = self.date - BDay(252)
        self.one_year_ago_str = self.one_year_ago.strftime('%Y-%m-%d')
        self.one_month_ago = self.date - BDay(22)
        self.one_month_ago_str = self.one_month_ago.strftime('%Y-%m-%d')
        self.prices_dir = prices_dir
        self.info_dir = info_dir

    def run_attribution(self):
        self._load_info()
        self._load_one_year_return()
        self._load_one_month_return()


    def _load_info(self):
        # use last business days date for info
        path = '{}/info_{}'.format(self.info_dir, self.prev_date_str)
        if os.path.exists(path):
            for filename in os.listdir(path):
                if filename.endswith('.csv'):
                    print('here we go')
                    df = pd.read_csv('{}/{}'.format(path, filename))
                    df.columns = ['ticker', 'mkt_cap', 'cur_price', 'prev_price', 'beta', 'book_value', 'sector', 'eps']
                    print(df.head())
                    exit()

    def _load_one_year_return(self):
        pass

    def _load_one_month_return(self):
        pass


if __name__ == '__main__':
    fa = FactorAttribution()
    fa.run_attribution()
