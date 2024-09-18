from bot.config import *
from telebot import types

@bot.callback_query_handler(func=lambda call: call.data in ['calc_income', 'devices_catalog', 'back'], state=CalculatorStates.choose_algorithm)
async def choose_algorithm(call):
    if call.data == 'calc_income' or call.data == 'devices_catalog' or call.data == 'back':
        context_manager.clear(call.message.chat.id)
        await bot.delete_message(call.message.chat.id, msg_ids[call.message.chat.id])
        unique_algorithms = {asic.algorithm for asic in asic_data if isinstance(asic.algorithm, str)}

        markup = types.InlineKeyboardMarkup(row_width=3)
        buttons = [types.InlineKeyboardButton(text=algorithm, callback_data=f'algorithm_{algorithm}') for algorithm in unique_algorithms]
        rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
        for row in rows:
            markup.row(*row)
        markup.row(types.InlineKeyboardButton(text='Назад', callback_data='back'))
        msg = await bot.send_message(call.message.chat.id, 'Выберите алгоритм', reply_markup=markup)
        msg_ids[call.message.chat.id] = msg.id
        await bot.set_state(call.message.chat.id, CalculatorStates.choose_algorithm)
       
