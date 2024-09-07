from bot.config import *
from telebot import types
from math import ceil

@bot.callback_query_handler(func=lambda call: call.data.startswith('submit'), state=CalculatorStates.choose_count)
async def handle_submit(call):
    user_id = call.message.chat.id
    current_context = context_manager.current_asic.get(user_id, {})
    if call.data != 'submit$':
        if 'number' not in current_context or not current_context['number']:
            return
    await display_devices_with_pagination(call, page=1, is_slider=False)

async def display_devices_with_pagination(call, page: int = 1, is_slider: bool = False):
    user_id = call.message.chat.id

    if not is_slider:
        context_manager.append(user_id=user_id)

    storage = context_manager.storage[user_id]

    if not storage:
        await bot.send_message(user_id, 'Вы еще не выбрали устройства.')
        return

    amount_of_pages = ceil(len(storage) / DEVICES_PER_PAGE)
    chunks = [storage[i:i + DEVICES_PER_PAGE] for i in range(0, len(storage), DEVICES_PER_PAGE)]
    data_to_display = chunks[page - 1] if page <= len(chunks) else []

    devices_text = '\n'.join([
        f'🟢 Алгоритм: {d["algorithm"]}\n'
        f'🟢 Монета: {d["coin"]}\n'
        f'🟢 Производитель: {d["manufacturer"]}\n' 
        f'🟢 Модель: {d["model"]}\n'
        f'🟢 TH/s: {d["ths"]}\n'
        f'🟢 Количество: {d["number"]}\n' for d in data_to_display
    ])

    message_text = (f'Вы выбрали следующие устройства:\n{devices_text}\n'
                    'Хотите добавить еще устройства или закончить выбор?')

    markup = types.InlineKeyboardMarkup(row_width=3)
    if amount_of_pages > 1:
        back = types.InlineKeyboardButton(
            text="<", callback_data=f"submit#{page - 1 if page - 1 >= 1 else 1}"
        )
        page_cntr = types.InlineKeyboardButton(
            text=f"{page}/{amount_of_pages}", callback_data="nullified"
        )
        forward = types.InlineKeyboardButton(
            text=">", callback_data=f"submit#{page + 1 if page + 1 <= amount_of_pages else amount_of_pages}"
        )
        markup.add(back, page_cntr, forward)

    markup.add(
        types.InlineKeyboardButton(text='Добавить еще устройства', callback_data='add_more'),
    )

    markup.add(
        types.InlineKeyboardButton(text='Тариф электроэнергии', callback_data='tariff')
    )

    if user_id in msg_ids:
        await bot.edit_message_text(message_text, user_id, msg_ids[user_id], reply_markup=markup)
    else:
        msg = await bot.send_message(user_id, message_text, reply_markup=markup)
        msg_ids[user_id] = msg.message_id

    await bot.set_state(user_id, CalculatorStates.confirm_additional_device)

@bot.callback_query_handler(func=lambda call: call.data.startswith('submit#'))
async def handle_pagination(call):
    data = call.data.split('#')
    page = int(data[1]) if len(data) > 1 else 1
    await display_devices_with_pagination(call, page=page, is_slider=True)