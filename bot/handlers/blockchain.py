from bot.config import *
from telebot import types

@bot.callback_query_handler(func=lambda call: True, state=CalculatorStates.choose_algorithm)
async def choose_blockchain(call):
    if call.data == 'back':
        selected_algorithm = context_manager.current_asic[call.message.chat.id]['algorithm']
    else:
        selected_algorithm = call.data
    context_manager.fill_current_asic(call.message.chat.id, algorithm=selected_algorithm)
    coins = {asic.coin for asic in asic_data if selected_algorithm == asic.algorithm}

    message_text = (f'🟢 Алгоритм: {selected_algorithm}\n'
                    '...Выберите монету')

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=coin, callback_data=coin) for coin in coins]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data='back'))
    await bot.edit_message_text(message_text, call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_blockchain)
