import pandas as pd

from ..loader_securities import  make_url, get_raw_json, get_securities_info

def test_make_url():
    assert make_url('AKRN') == make_url(['AKRN'])
    assert make_url(['AKRN', 'GAZP', 'LKOH', 'SBER']).endswith('SBER') 
    
def test_make_raw_json():    
    d = get_raw_json(['AKRN', 'GAZP', 'LKOH', 'SBER'])
    assert isinstance(d, dict)
    assert list(d.keys()) == ['securities', 'marketdata', 'dataversion']  
    
def test_get_securities_info():    
    df = get_securities_info(['AKRN','GAZP'])
    assert isinstance(df, pd.DataFrame)
    assert df.loc['AKRN', 'SHORTNAME'] == 'Акрон'
    assert df.loc['GAZP', 'SHORTNAME'] == 'ГАЗПРОМ ао'
