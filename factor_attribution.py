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
        self._load_prices()


    def _load_info(self):
        # use last business days date for info
        path = '{}/info_{}'.format(self.info_dir, self.prev_date_str)
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
            for filename in os.listdir(path):
                if filename.endswith('.csv'):
                    ticker = filename.replace('.csv', '')
                    df = pd.read_csv('{}/{}'.format(path, filename), index_col='Date')
                    data = {
                            "month_ago": self._get_price(df, 'month_ago'),
                            "year_ago": self._get_price(df, 'year_ago'),
                            "yesterday": self._get_price(df, 'yesterday'),
                            "today": self._get_price(df, 'today')
                    }
                    new_df = pd.DataFrame(data, index=[ticker])
                    totals = totals.append(new_df)
            final = pd.merge(info, totals, left_index=True, right_index=True)

        self.info = final
        print(final.head())

    def _get_price(self, df, time_frame):
        counter = 0
        price = 'NOPE'
        while price == 'NOPE' and counter < 2:
            if self._get_date_str(time_frame) in df.index:
                price = df.at[self._get_date_str(time_frame), 'Adj Close']
            else:
                price = 'NOPE'
                self._adjust_date(time_frame)
                counter += 1
        if price == 'NOPE':
            return np.nan
        else:
            return price

    def _get_date_str(self, time_frame):
        if time_frame == 'yesterday':
            return self.prev_date_str
        elif time_frame == 'year_ago':
            return self.one_year_ago_str
        elif time_frame == 'month_ago':
            return self.one_month_ago_str
        elif time_frame == 'today':
            return self.date_str

    def _adjust_date(self, time_frame):
        if time_frame == 'yesterday':
            self.prev_date = self.prev_date - BDay(1)
            self.prev_date_str = self.prev_date.strftime('%Y-%m-%d')
        elif time_frame == 'year_ago':
            self.one_year_ago = self.one_year_ago - BDay(1)
            self.one_year_ago_str = self.one_year_ago.strftime('%Y-%m-%d')
        elif time_frame == 'month_ago':
            self.one_month_ago = self.one_month_ago - BDay(1)
            self.one_month_ago_str = self.one_month_ago.strftime('%Y-%m-%d')



if __name__ == '__main__':
    fa = FactorAttribution()
    fa.run_attribution()
