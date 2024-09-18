from bot.config import *
from telebot import types

def create_number_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=str(i), callback_data=f'num_{i}') for i in range(1, 10)]
    buttons.append(types.InlineKeyboardButton(text='Стереть', callback_data='clear'))
    buttons.append(types.InlineKeyboardButton(text='0', callback_data='num_0'))
    buttons.append(types.InlineKeyboardButton(text='Выбрать', callback_data='submit'))

    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data='back'))
    return markup

def format_message_text(context_data, number=None):
    message_text = (f'🟢 Алгоритм: {context_data.get("algorithm")}\n'
                    f'🟢 Монета: {context_data.get("coin")}\n'
                    f'🟢 Производитель: {context_data.get("manufacturer")}\n'
                    f'🟢 Модель: {context_data.get("model")}\n'
                    f'🟢 TH/s: {context_data.get("ths")}')
    if number is not None:
        message_text += f'\n🟢 Количество: {number}'
    return message_text

async def update_message_text(call, message_text, markup):
    await bot.edit_message_text(message_text, call.message.chat.id, msg_ids[call.message.chat.id], parse_mode = 'HTML')
    await bot.edit_message_reply_markup(call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('ths_'), state=CalculatorStates.choose_ths)
async def choose_count(call):
    if call.data == 'back':
        selected_ths = context_manager.current_asic[call.message.chat.id].get('ths')
    else:
        selected_ths = call.data.split('_')[1]

    context_manager.fill_current_asic(call.message.chat.id, ths=selected_ths)

    current_context_data = context_manager.current_asic.get(call.message.chat.id, {})
    message_text = format_message_text(current_context_data)

    markup = create_number_keyboard()
    await update_message_text(call, message_text, markup)
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_count)
    current_state = await bot.get_state(user_id=call.from_user.id)
    print(current_state)

@bot.callback_query_handler(func=lambda call: call.data.startswith('num_'), state=CalculatorStates.choose_count)
async def handle_number(call):
    current_number = context_manager.current_asic[call.message.chat.id].get('number', '')
    number = call.data.split('_')[1]

    if len(current_number) < 6:
        current_number += number
    context_manager.current_asic[call.message.chat.id]['number'] = current_number

    current_context_data = context_manager.current_asic.get(call.message.chat.id, {})
    message_text = format_message_text(current_context_data, current_number)

    markup = create_number_keyboard()
    await update_message_text(call, message_text, markup)

@bot.callback_query_handler(func=lambda call: call.data == 'clear', state=CalculatorStates.choose_count)
async def handle_clear(call):
    context_manager.current_asic[call.message.chat.id]['number'] = ''

    markup = create_number_keyboard()
    message_text = format_message_text(context_manager.current_asic.get(call.message.chat.id, {}), '')
    await update_message_text(call, message_text, markup)
