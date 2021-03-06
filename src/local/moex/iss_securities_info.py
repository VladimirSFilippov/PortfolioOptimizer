"""Сохраняет, обновляет и загружает локальную версию информации об акциях"""
from functools import lru_cache

from utils.data_manager import AbstractDataManager
from web import moex
from web.labels import COMPANY_NAME, REG_NUMBER, LOT_SIZE

SECURITIES_INFO_MANE = 'securities_info'


class SecuritiesInfoDataManager(AbstractDataManager):
    """Менеджер локальной информации об акциях

    Вся информация загружается одним запросом для сокращения числа обращений к серверу MOEX
    """
    update_from_scratch = True

    def __init__(self):
        super().__init__(None, SECURITIES_INFO_MANE)

    def download_all(self):
        """Загружает одним запросом информацию о всех тикерах"""
        return moex.securities_info()[[COMPANY_NAME, REG_NUMBER, LOT_SIZE]]

    def download_update(self):
        """Отсутствует возможность частичного обновления данных """
        super().download_update()


def securities_info(tickers: tuple):
    """Возвращает данные по тикерам из списка и при необходимости обновляет локальные данные

    Parameters
    ----------
    tickers
        Кортеж тикеров

    Returns
    -------
    pandas.DataFrame
        В строках тикеры
        В столбцах данные по размеру лота, регистрационному номеру и краткому наименованию
    """
    data = SecuritiesInfoDataManager()
    return data.value.loc[tickers, :]


@lru_cache(maxsize=1)
def lot_size(tickers: tuple):
    """Возвращает размеры лотов для тикеров

    Parameters
    ----------
    tickers
        Кортеж тикеров

    Returns
    -------
    pandas.Series
        В строках тикеры
    """
    return securities_info(tickers)[LOT_SIZE]


def aliases(ticker: str):
    """Возвращает список тикеров аналогов для заданного тикера

    Функция нужна для выгрузки длинной истории котировок с учетом изменения тикера
    Не используется за пределами пакета local

    Parameters
    ----------
    ticker
        Тикер

    Returns
    -------
    tuple
        Тикеры аналоги с таким же регистрационным номером
    """
    reg_number = securities_info((ticker,)).loc[ticker, REG_NUMBER]
    return moex.reg_number_tickers(reg_number)


if __name__ == '__main__':
    print(securities_info(('UPRO',)))
    print(aliases('UPRO'))
