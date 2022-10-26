import json
import os
import aiohttp
import asyncio
import multiprocessing
from itertools import repeat
from aiogram.types import CallbackQuery
from pathlib import Path

data_spread = {
    'Binance' : {},
    'EXMO' : {},
    'Kraken' : {},
    'Gate.io' : {},
    'MEXC Global' : {},
    'FTX Spot' : {},
    'Huobi Global' : {},
    'Kucoin' : {},
    'Bybit Spot' : {},
    'OKX' : {},
    'BitMart' : {},
    'Crypto.com' : {},
    'Cryptology' : {},
    'HitBTC' : {},
    'Poloniex' : {},
    '1inch' : {},
    'Orca' : {},
    'Jupiter' : {},
    'SushiSwap' : {},
    'Uniswap V3' : {},
    'Pancake Swap' : {},
    'Raydium' : {},
}

async def get_page_data(session: aiohttp.ClientSession, exchange):# таск 
    global data_spread
    headers ={
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }
    url = f"https://api.cryptorank.io/v0/exchanges/{exchange}/tickers"

    async with session.get(url=url, headers=headers) as ress:
        datat = await ress.text()#отправляем запрос
        try:
            data = json.loads(datat)#Пробуем загрузить в переменную форматом json, если выходит ошибка, значит мы получили 'блок' на какойто промежуток времени за частые запросы
        except Exception as err:
            pass
        else:
            try:
                coin_pair = [w for w in Path("settings/coin_pair.txt").read_text(encoding="utf-8").replace("\n", " ").split()]
                coin_blacklist = [w for w in Path("settings/coin_blacklist.txt").read_text(encoding="utf-8").replace("\n", " ").split()]
                for d in data:
                    if d['coinKey'] not in coin_blacklist:
                        if d["symbol"].partition("/")[2] in coin_pair:
                            try:
                                data_spread[d["exchangeName"]][d["symbol"]] = [d["usdLast"], d['coinKey'], d['usdVolume']] #Парсим данные, загружаем в переменную
                            except Exception as err:
                                pass
            except Exception as err:
                pass
            
async def gather_data():
    while True:
        async with aiohttp.ClientSession() as session:#Создаем сессию и передаем ее параметром в таск
            tasks = []
            exchanges = [x.strip() for x in open("settings/exch_test.txt").readlines()]
            for exchange in exchanges:
                task = asyncio.create_task(get_page_data(session, exchange))
                tasks.append(task)#Проходимся по монетам и создаем таски
            try:
                await asyncio.gather(*tasks)
            except Exception as err:
                pass
            finally:
                await session.close()
        with open('pkgs/data.json', 'w') as file:
            json.dump(data_spread, file, indent=4)
        await asyncio.sleep(5)

        
async def spread(call: CallbackQuery):
    def sort_col(i):#Функция для сортировки по ключу
        return i[6]

    with open('pkgs/data.json', 'r') as file:
        data = json.load(file)
    pair_data_send = []
    data2 = []
    user_coin_pair = [w for w in Path(f"users/{call.from_user.id}/coin_pair.txt").read_text(encoding="utf-8").replace("\n", " ").split()]
    exchs = [x.strip() for x in open(f"users/{call.from_user.id}/exchanges.txt").readlines()]
    if len(exchs) < 1:
        await call.message.answer('Выберите в настройках минимум 1 биржу')
    else:
        for exch in exchs:
            treading_pairs = data[exch].keys()
            for treading_pair in treading_pairs:
                if treading_pair.partition("/")[2] in user_coin_pair:
                    data_pair = [exch, treading_pair, data[exch][treading_pair]]
                    if data_pair[2][2] > 1000:#Если объем торгов за 24 часа = 0, то мы отбрасываем пару
                        data2.append(data_pair)#Добавляем биржи по фильтрам

        with multiprocessing.Pool() as pool:#Создаем пул процессов, так как на вычесление всех спредов происходит долго
            pair_data_send = pool.starmap(analise_data, zip(data2, repeat(data2)))

        if len(pair_data_send) > int(call.data[4:]):#Ограничение, зависит от нажатой кнопки, если топ10, то ограничение в 10 сообщений
            pair_data_send.sort(key=sort_col)#Сортировка от меньшего спреда к большему
            value_el = len(pair_data_send) - int(call.data[4:])
            del pair_data_send[0:value_el]
        if len(pair_data_send) == 0:
            await call.message.answer('К сожалению мы ничего не нашли')
        else:
            for m in pair_data_send:
                await call.message.answer(f"BUY\nexchange: {m[0]}\n"
                                            f"pair: {m[1]} ({m[2][1]})\n"
                                            f"prise: ${m[2][0]}\n"
                                            f"volume 24: ${round(m[2][2])}\n\n"
                                            f"SELL\nexchange: {m[3]}\n"
                                            f"pair: {m[4]} ({m[5][1]})\n"
                                            f"prise: ${m[5][0]}\n"
                                            f"volume 24: ${round(m[5][2])}\n\n"
                                            f"{round(m[6], 2)}%\n\n"
                                            )

def analise_data(a, data2):#Вычисление спреда, долгая функция, добавляется в пул процессов
    paira = a[1].partition("/")[0]
    for p in data2:
        pairp = p[1].partition("/")[0]
        if paira == pairp and a[2][1] == p[2][1]:
            spr = (a[2][0]/p[2][0]-1)*100
            return [p[0], p[1], p[2], a[0], a[1], a[2], spr]
