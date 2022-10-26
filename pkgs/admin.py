import os
import shutil
import asyncio
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from .create_bot import bot, ADMIN, DB
from .state import MailingState, BlackList


admKeyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                     keyboard=[
                                         [
                                             KeyboardButton(text='📊 Статистика')
                                         ],
                                         [
                                             KeyboardButton(text='🗣 Рассылка')
                                         ],
                                         [
                                             KeyboardButton(text='🔽 Скрыть панель')
                                         ]
                                     ])

async def close_panel(message: types.Message):
    if message.from_user.id == ADMIN:
        await message.answer('.', reply_markup=ReplyKeyboardRemove())

async def adm(message: types.Message, state: FSMContext):
    await state.finish()
    if message.from_user.id == ADMIN:

        await message.answer('<b>🤴 Панель администратора</b>', reply_markup=admKeyboard)

async def statistic(message: types.Message):
    if message.from_user.id == ADMIN:
        user_count = len(DB.get_users())
        await message.answer('<b>👥 Статистика по пользователям:</b>\n\n'
                             f'<i>Всего пользователей:</i>  <code>{user_count}</code>\n')


async def copydata(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN:
        await message.answer_document(open('pkgs/cryptorank.db', 'rb'))
        data_file = shutil.make_archive("users", "zip", "users")
        await message.answer_document(open(data_file, 'rb'))
        os.remove(data_file)


async def send_messs(message: types.Message):
    if message.from_user.id == ADMIN:
        mailing_menu = ReplyKeyboardMarkup(resize_keyboard=True,
                                        keyboard=[
                                            [
                                                KeyboardButton(text='Отмена')
                                            ]
                                        ])
        await message.answer('Создайте пост', reply_markup=mailing_menu)
        await MailingState.A1.set()


async def send_mess_1(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await message.answer('<b>🤴 Панель администратора</b>', reply_markup=admKeyboard)
        await state.finish()

    else:
        all_user = DB.get_users()
        count = 0
        count_l = 0

        for i in all_user:
            await asyncio.sleep(0.4)

            try:
                await bot.copy_message(chat_id=i[0], message_id=message.message_id, from_chat_id=message.from_user.id)
                count += 1
            except Exception:
                count_l += 1
                pass

        await message.answer('<b>✅ Успешная рассылка:</b>\n\n'
                             f'<i>Рассылку получили:</i>  <code>{count}</code>\n'
                             f'<i>Заблокировали бота:</i>  <code>{count_l}</code>',
                             reply_markup=admKeyboard)
        await state.finish()



def admin_handl(dp: Dispatcher):
    dp.register_message_handler(close_panel, text='🔽 Скрыть панель', state='*')
    dp.register_message_handler(adm, commands='adm', state='*')
    dp.register_message_handler(statistic, text='📊 Статистика', state='*')
    dp.register_message_handler(send_messs, text='🗣 Рассылка', state='*')
    dp.register_message_handler(send_mess_1, state=MailingState.A1, content_types=types.ContentTypes.ANY)
    dp.register_message_handler(copydata, commands='copydata', state='*')
