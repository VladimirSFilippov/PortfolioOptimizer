import pathlib

import numpy as np
import pandas as pd
import pytest

import settings
from local import moex
from local.moex.iss_quotes_t2 import QuotesT2DataManager, t2_shift, log_returns_with_div
from web.labels import CLOSE_PRICE, VOLUME


def test_quotes_t2_manager(tmpdir, monkeypatch):
    data_dir = pathlib.Path(tmpdir.mkdir("test_quotes_t2"))
    monkeypatch.setattr(settings, 'DATA_PATH', data_dir)
    manager = QuotesT2DataManager('UPRO')
    assert isinstance(manager.value, pd.DataFrame)
    assert len(manager.value.columns) == 2
    assert manager.value.index.is_monotonic_increasing
    assert manager.value.index.is_unique
    assert manager.value.index[0] == pd.to_datetime('2014-06-09')
    assert manager.value.iloc[1, 0] == pytest.approx(2.9281)
    assert manager.value.iloc[2, 1] == 44868000
    assert manager.value.shape[0] > 1000
    assert manager.value.loc['2018-09-07', CLOSE_PRICE] == pytest.approx(2.633)
    assert manager.value.loc['2018-09-10', VOLUME] == 9303000


def test_quotes_t2_manager_update():
    manager = QuotesT2DataManager('MTSS')
    last_row = manager.value.iloc[-1:, :]
    df = manager.download_update()
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (1, 2)
    assert np.allclose(df, last_row)


def test_quotes_t2():
    df = moex.quotes_t2('BANEP')
    assert isinstance(df, pd.DataFrame)
    assert len(df.columns) == 2
    assert df.index.is_monotonic_increasing
    assert df.index.is_unique
    assert df.index[0] == pd.to_datetime('2014-06-09')
    assert df.iloc[1, 0] == pytest.approx(1833.0)
    assert df.iloc[2, 1] == 23164
    assert df.shape[0] > 1000
    assert df.loc['2018-09-07', CLOSE_PRICE] == pytest.approx(1721.5)
    assert df.loc['2018-09-10', VOLUME] == 35287


def test_prices_t2():
    df = moex.prices_t2(('MSTT', 'SBERP'))
    assert isinstance(df, pd.DataFrame)
    assert len(df.columns) == 2
    assert df.index.is_monotonic_increasing
    assert df.index.is_unique
    assert df.index[0] == pd.to_datetime('2013-03-25')
    assert df.loc['2013-03-26', 'SBERP'] == pytest.approx(72.30)
    assert np.isnan(df.loc['2013-03-27', 'MSTT'])
    assert df.loc['2014-06-09', 'MSTT'] == pytest.approx(110.48)
    assert df.shape[0] > 1000
    assert df.loc['2018-09-07', 'MSTT'] == pytest.approx(92.0)
    assert df.loc['2018-09-10', 'SBERP'] == pytest.approx(148.36)


def test_volumes_t2():
    df = moex.volumes_t2(('GMKN', 'AKRN'))
    assert isinstance(df, pd.DataFrame)
    assert len(df.columns) == 2
    assert df.index.is_monotonic_increasing
    assert df.index.is_unique
    assert df.index[0] == pd.to_datetime('2014-06-09')
    assert df.loc['2014-06-09', 'GMKN'] == 212826
    assert df.loc['2014-06-10', 'AKRN'] == 16888
    assert df.shape[0] > 1000
    assert df.loc['2018-09-07', 'GMKN'] == 100714
    assert df.loc['2018-09-10', 'AKRN'] == 4631


def test_t2_shift():
    index = moex.prices_t2(('NLMK',)).loc[:pd.Timestamp('2018-10-08')].index
    assert pd.Timestamp('2018-05-14') == t2_shift(pd.Timestamp('2018-05-15'), index)
    assert pd.Timestamp('2018-07-05') == t2_shift(pd.Timestamp('2018-07-08'), index)
    assert pd.Timestamp('2018-09-28') == t2_shift(pd.Timestamp('2018-10-01'), index)
    assert pd.Timestamp('2018-10-09') == t2_shift(pd.Timestamp('2018-10-10'), index)
    assert pd.Timestamp('2018-10-11') == t2_shift(pd.Timestamp('2018-10-12'), index)
    assert pd.Timestamp('2018-10-11') == t2_shift(pd.Timestamp('2018-10-13'), index)
    assert pd.Timestamp('2018-10-11') == t2_shift(pd.Timestamp('2018-10-14'), index)
    assert pd.Timestamp('2018-10-12') == t2_shift(pd.Timestamp('2018-10-15'), index)
    assert pd.Timestamp('2018-10-17') == t2_shift(pd.Timestamp('2018-10-18'), index)


def test_log_returns_with_div():
    data = log_returns_with_div(('GMKN', 'RTKMP', 'MTSS'), pd.Timestamp('2018-10-06'))
    assert isinstance(data, pd.DataFrame)
    assert list(data.columns) == ['GMKN', 'RTKMP', 'MTSS']
    assert data.index[-13] == pd.Timestamp('2017-10-06')
    assert data.index[-1] == pd.Timestamp('2018-10-06')

    assert data.loc['2018-10-06', 'MTSS'] == pytest.approx(np.log(((275.1 + 0) / 256.1)))
    assert data.loc['2018-10-06', 'GMKN'] == pytest.approx(np.log(((11292 + 776.02) / 11206)))
    assert data.loc['2018-08-06', 'RTKMP'] == pytest.approx(np.log(((61.81 + 0) / 62)))
    assert data.loc['2018-07-06', 'RTKMP'] == pytest.approx(np.log(((62 + 5.045825249373) / 64)))

    data = log_returns_with_div(('GMKN', 'RTKMP', 'MTSS'), pd.Timestamp('2018-10-07'))
    assert data.loc['2018-10-07', 'MTSS'] == pytest.approx(np.log(((275.1 + 0) / 256)))

    data = log_returns_with_div(('GMKN', 'RTKMP', 'MTSS'), pd.Timestamp('2018-10-08'))
    assert data.loc['2018-10-08', 'MTSS'] == pytest.approx(np.log(((269.9 + 2.6) / 256)))
