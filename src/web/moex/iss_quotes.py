"""Загружает котировки и объемы торгов для тикеров с http://iss.moex.com"""
import json
import ssl
import time
from urllib import request
from urllib.error import URLError

import pandas as pd

from web.labels import CLOSE_PRICE, DATE, VOLUME

# Время ожидания для повторной загрузки при невозможности получить данные
TIMEOUT = 60


class Quotes:
    """Представление ответа сервера по котировкам в виде итератора

    При большом запросе сервер ISS возвращает данные блоками обычно по 100 значений, поэтому класс является итератором
    Если начальная дата не указана, то загружается вся доступная история котировок
    """
    _BASE_URL = 'https://iss.moex.com/iss/history/engines/stock/markets/shares/securities/'

    def __init__(self, ticker: str, start_date):
        self._ticker, self._start_date = ticker, start_date

    def __iter__(self):
        block_position = 0
        while True:
            df = self.get_df(block_position)
            df_len = len(df)
            if df_len == 0:
                break
            block_position += df_len
            yield df

    def url(self, block_position):
        """Создает url для запроса к серверу http://iss.moex.com"""
        url = self._BASE_URL + f'{self._ticker}.json'
        query_args = [f'start={block_position}']
        if self._start_date:
            if not isinstance(self._start_date, pd.Timestamp):
                raise TypeError(self._start_date)
            query_args.append(f"from={self._start_date:%Y-%m-%d}")
        arg_str = '&'.join(query_args)
        return f'{url}?{arg_str}'

    def get_json_data(self, block_position):
        """Загружает и проверяет json с данными"""
        try:
            with request.urlopen(self.url(block_position), context=ssl.SSLContext()) as response:
                json_data = json.load(response)
        except URLError as error:
            if isinstance(error.args[0], TimeoutError):
                print(f'Время ожидания загрузки данных для регистрационного номера {self._ticker} превышено')
                print(f'Новая попытка через {TIMEOUT} секунд')
                time.sleep(TIMEOUT)
                json_data = self.get_json_data(block_position)
            else:
                raise error
        self._validate_response(block_position, json_data)
        return {key: json_data['history'][key] for key in ['data', 'columns']}

    def _validate_response(self, block_position, json_data):
        """Первый запрос должен содержать не нулевое количество строк"""
        if block_position == 0 and len(json_data['history']['data']) == 0:
            raise ValueError(f'Пустой ответ. Проверьте запрос: {self.url(block_position)}')

    def get_df(self, block_position):
        """Формирует DataFrame и выбирает необходимые колонки - даты, цены закрытия и объемы"""
        json_data = self.get_json_data(block_position)
        df = pd.DataFrame(**json_data)
        df[DATE] = pd.to_datetime(df['TRADEDATE'])
        df[CLOSE_PRICE] = pd.to_numeric(df['CLOSE'])
        df[VOLUME] = pd.to_numeric(df['VOLUME'])
        return df[[DATE, CLOSE_PRICE, VOLUME]]


def quotes(ticker, start=None):
    """
    Возвращает историю котировок тикера начиная с даты start_date

    Если дата None, то загружается вся доступная история котировок

    Parameters
    ----------
    ticker : str
        Тикер, например, 'MOEX'

    start : pd.Timestamp or None
        Начальная дата котировок

    Returns
    -------
    pandas.DataFrame
        В строках даты торгов
        В столбцах [CLOSE, VOLUME] цена закрытия и оборот в штуках
    """
    gen = Quotes(ticker, start)
    df = pd.concat(gen, ignore_index=True)
    # Для каждой даты выбирается режим торгов с максимальным оборотом
    df = df.loc[df.groupby(DATE)[VOLUME].idxmax()]
    df = df.set_index(DATE)
    return df


if __name__ == '__main__':
    print(quotes('MSTT'))
