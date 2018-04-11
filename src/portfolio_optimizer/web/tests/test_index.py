def test_make_url():
    url = make_url(base=Index.base,
                   ticker=Index.ticker,
                   start_date=datetime.date(2017, 10, 1),
                   block_position=50)
    assert url == ('http://iss.moex.com/iss/history/engines/stock/markets/index/'
                   'boards/RTSI/securities/MCFTRR.json?start=50&from=2017-10-01')


def test_quotes_none_start_date():
    quotes_gen = Quotes('AKRN', None)
    assert quotes_gen.url == ('https://iss.moex.com/iss/history/engines/stock/markets'
                              '/shares/securities/AKRN.json?start=0')
    assert quotes_gen.df.loc[0, DATE] == pd.Timestamp('2003-02-26')


def test_get_index_history():
    df = get_index_history(datetime.date(2017, 10, 2))
    assert isinstance(df, pd.Series)
    assert df.index.is_monotonic_increasing
    assert df.index.is_unique
    assert df.index[0] == pd.to_datetime('2017-10-02')
    assert df.shape[0] >= 100
    assert df.loc['2018-03-02'] == 3273.16


class TestTotalReturn:
    t = Index(start_date=None)

    def test_data_property_on_init_for_None_start_date(self):
        # lower-level tests of server response
        data = self.t.data
        index = data['history']['columns'].index('TRADEDATE')
        assert data['history']['data'][0][index] == '2003-02-26'

    def test_len_method(self):
        assert len(self.t) == 100

    def test_bool_method(self):
        assert bool(self.t)

    def test_values_property(self):
        assert isinstance(self.t.values, list)
        assert len(self.t.values[0]) == 16

    def test_columns_property(self):
        assert self.t.columns == ['BOARDID',
                                  'SECID',
                                  'TRADEDATE',
                                  'SHORTNAME',
                                  'NAME',
                                  'CLOSE',
                                  'OPEN',
                                  'HIGH',
                                  'LOW',
                                  'VALUE',
                                  'DURATION',
                                  'YIELD',
                                  'DECIMALS',
                                  'CAPITALIZATION',
                                  'CURRENCYID',
                                  'DIVISOR']

    def test_dataframe_property(self):
        assert isinstance(self.t.dataframe, pd.DataFrame)
        assert list(self.t.dataframe.columns) == [CLOSE_PRICE]
        assert self.t.dataframe.loc['2003-02-26', CLOSE_PRICE] == 335.67
