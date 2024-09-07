from bot.config import *
from telebot import types
from bot.handlers.menu import start

def get_electricity_markup(price):
    markup = types.InlineKeyboardMarkup(row_width=3)

    markup.add(
        types.InlineKeyboardButton(text='-', callback_data='decrease_price'),
        types.InlineKeyboardButton(text=f'{price:.3f} USD', callback_data='current_price'),
        types.InlineKeyboardButton(text='+', callback_data='increase_price')
    )

    markup.add(
        types.InlineKeyboardButton(text='Выбрать', callback_data='select_price')
    )

    return markup

async def send_price_selection_menu(chat_id):
    if chat_id not in electricity_prices:
        electricity_prices[chat_id] = 0.05

    markup = get_electricity_markup(electricity_prices[chat_id])
    await bot.send_message(
        chat_id,
        f"Выберите цену за электричество: {electricity_prices[chat_id]:.3f} USD",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data in ['tariff', 'decrease_price', 'increase_price', 'current_price', 'go_back', 'select_price'], state=CalculatorStates.confirm_additional_device)
async def handle_price_selection(call):
    chat_id = call.message.chat.id

    if chat_id not in electricity_prices:
        electricity_prices[chat_id] = 0.05

    if call.data == 'decrease_price':
        if electricity_prices[chat_id] > 0.001:
            electricity_prices[chat_id] -= 0.001
    elif call.data == 'increase_price':
        electricity_prices[chat_id] += 0.001
    elif call.data == 'current_price':
        pass
    elif call.data == 'go_back':
        await bot.send_message(call.message.chat.id, "Возврат в предыдущее меню...")
        return
    elif call.data == 'select_price':
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
        await bot.send_message(call.message.chat.id, f'Выбор завершен. \nСпасибо!')
        context_manager.storage[call.message.chat.id].append(float(electricity_prices[chat_id]))
        electricity_prices[chat_id] = 0.05
        print(context_manager.storage[call.message.chat.id])
        await start(call.message)
        return

    markup = get_electricity_markup(electricity_prices[chat_id])
    await bot.edit_message_text(text='Укажите тариф на электроэнергию', chat_id=call.message.chat.id, message_id=call.message.message_id)
    await bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )