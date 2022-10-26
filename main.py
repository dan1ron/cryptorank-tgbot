import asyncio
import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from pkgs.create_bot import dp, bot, DB
from pkgs.parser import spread, gather_data
from pathlib import Path
from pkgs.state import Pair, Exchang
from pkgs import admin
import os

logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    if len(DB.get_user(message.from_user.id)) != 1: 
        DB.add_user(message.from_user.id)
        os.mkdir(f'users/{message.from_user.id}')
        with open(f'users/{message.from_user.id}/coin_pair.txt', 'w+') as file:
            file.write('USDT\n')
        with open(f'users/{message.from_user.id}/exchanges.txt', 'w+') as file:
            file.write('Binance\n')
    await bot.send_message(message.from_user.id, 'Добро пожаловать!\nДля начала настройте фильтры "Монеты котировки" и "Биржи"')
    await dp.bot.set_my_commands([
        types.BotCommand('pairs', 'Монеты котировки'),
        types.BotCommand('exchanges', 'Биржи')
    ])


@dp.message_handler(commands=['pairs'])
async def pair(message: types.Message, state: FSMContext):
    mess = await message.answer('.', reply_markup=ReplyKeyboardRemove())
    await message.delete()
    await bot.delete_message(message.from_user.id, mess.message_id)
    coin_pair = [w for w in Path("settings/coin_pair.txt").read_text(encoding="utf-8").replace("\n", " ").split()]
    user_coin_pair = [w for w in Path(f"users/{message.from_user.id}/coin_pair.txt").read_text(encoding="utf-8").replace("\n", " ").split()]
    inline_keyboard = InlineKeyboardMarkup()
    for c in coin_pair:
        if c in user_coin_pair:
            inline_keyboard.add(InlineKeyboardButton(text=f'✓{c}', callback_data=f'chngpair_{c}_1'))
        else:
            inline_keyboard.add(InlineKeyboardButton(text=f'+{c}', callback_data=f'chngpair_{c}_0'))
    inline_keyboard.add(InlineKeyboardButton(text='☑️Сохранить', callback_data='exit'))
    await message.answer('Выберите монеты за которые хотите совершать сделки', reply_markup=inline_keyboard)
    await Pair.A1.set()
    await state.update_data(pairs=user_coin_pair)


@dp.callback_query_handler(state=Pair.A1)
async def qweqefd(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'exit':
        data = await state.get_data()
        key = data.get('pairs')
        with open(f"users/{call.from_user.id}/coin_pair.txt", 'w+') as file:
            for  line in key:
                file.write(line + '\n')
        await call.message.delete()
        await state.finish()
        await call.message.answer('Настройки сохранены', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Search')))
    else:
        coin = call.data.partition('_')[2].partition('_')[0]
        have = int(call.data[-1])
        data = await state.get_data()
        key = data.get('pairs')
        if have == 1:
            key.remove(coin)
        elif have == 0:
            key.append(coin)
        await state.update_data(pairs=key)
        coin_pair = [w for w in Path("settings/coin_pair.txt").read_text(encoding="utf-8").replace("\n", " ").split()]
        markup = InlineKeyboardMarkup()
        for c in coin_pair:
            if c in key:
                markup.add(InlineKeyboardButton(text=f'✓{c}', callback_data=f'chngpair_{c}_1'))
            else:
                markup.add(InlineKeyboardButton(text=f'+{c}', callback_data=f'chngpair_{c}_0'))
        markup.add(InlineKeyboardButton(text='☑️Сохранить', callback_data='exit'))
        await call.message.edit_reply_markup(reply_markup=markup)


@dp.message_handler(commands=['exchanges'])
async def pair(message: types.Message, state: FSMContext):
    mess = await message.answer('.', reply_markup=ReplyKeyboardRemove())
    await message.delete()
    await bot.delete_message(message.from_user.id, mess.message_id)
    exchanges = [x.strip() for x in open("settings/exchanges.txt").readlines()]
    user_exchanges = [x.strip() for x in open(f"users/{message.from_user.id}/exchanges.txt").readlines()]
    inline_keyboard = InlineKeyboardMarkup()
    for c in exchanges:
        if c in user_exchanges:
            inline_keyboard.add(InlineKeyboardButton(text=f'✓ {c}', callback_data=f'chngexch_{c}_1'))
        else:
            inline_keyboard.add(InlineKeyboardButton(text=f'+ {c}', callback_data=f'chngexch_{c}_0'))
    inline_keyboard.add(InlineKeyboardButton(text='☑️Сохранить', callback_data='exit'))
    await message.answer('Выберите биржи на которых вы хотите совершать сделки', reply_markup=inline_keyboard)
    await Exchang.A1.set()
    await state.update_data(uexchanges=user_exchanges)
    await state.update_data(exchanges=exchanges)


@dp.callback_query_handler(state=Exchang.A1)
async def qweqefd(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'exit':
        data = await state.get_data()
        key = data.get('uexchanges')
        with open(f"users/{call.from_user.id}/exchanges.txt", 'w+') as file:
            for  line in key:
                file.write(line + '\n')
        await call.message.delete()
        await state.finish()
        await call.message.answer('Настройки сохранены', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Search')))
    else:
        exchange = call.data.partition('_')[2].partition('_')[0]
        have = int(call.data[-1])
        data = await state.get_data()
        key = data.get('uexchanges')
        if have == 1:
            key.remove(exchange)
        elif have == 0:
            key.append(exchange)
        await state.update_data(uexchanges=key)
        exchanges = data.get('exchanges')

        markup = InlineKeyboardMarkup()
        for c in exchanges:
            if c in key:
                markup.add(InlineKeyboardButton(text=f'✓ {c}', callback_data=f'chngexch_{c}_1'))
            else:
                markup.add(InlineKeyboardButton(text=f'+ {c}', callback_data=f'chngexch_{c}_0'))
        markup.add(InlineKeyboardButton(text='☑️Сохранить', callback_data='exit'))
        await call.message.edit_reply_markup(reply_markup=markup)

@dp.message_handler(text='Search')
async def mainMenu(message: types.Message, state: FSMContext):
    top_keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Топ 10', callback_data='top_10'),
                                                InlineKeyboardButton('Топ 20', callback_data='top_20'),
                                                InlineKeyboardButton('Топ 30', callback_data='top_30'),
                                                InlineKeyboardButton('Топ 40', callback_data='top_40'))

    await message.answer('<b>Выберите топ лучших спредов</b>\n'
                        'Данные обновляются каждые 5 секунд\n\n'
                        'Disclaimer:\n'
                        'Разработчик не несет ответственнности за работоспособность связок.\n'
                        'Все риски вы берете на себя',
                        reply_markup=top_keyboard)

        
@dp.callback_query_handler(lambda call: call.data.startswith('top_'))
async def mainMenu(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text('Поиск')
    await call.message.edit_text('Поиск.')
    await call.message.edit_text('Поиск..')
    await call.message.edit_text('Поиск...')
    await call.message.edit_text('Поиск....')
    await call.message.edit_text('Поиск.....')
    await call.message.edit_text('Поиск......')
    await call.message.edit_text('Поиск.......')
    await call.message.delete()
    await spread(call)

admin.admin_handl(dp)
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(gather_data())
    executor.start_polling(dp, skip_updates=True)
