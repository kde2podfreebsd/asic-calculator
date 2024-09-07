from bot.config import *
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot import types
from math import ceil

DEVICES_PER_PAGE = 1

from gsheets import GoogleSheetsAPI
from context import ContextManager

context_manager = ContextManager()

g = GoogleSheetsAPI()
asic_data = g.serialize()

msg_ids = dict()
electricity_prices = {}

class CalculatorStates(StatesGroup):
    choose_algorithm = State()
    choose_blockchain = State()
    choose_manufacturer = State()
    choose_model = State()
    choose_ths = State()
    choose_count = State()
    confirm_additional_device = State()
    choose_price = State()
    finalize_selection = State()
    finish = State()

async def is_user_subscribed(user_id):
    try:
        sub_status = await bot.get_chat_member(CHANNEL_ID, user_id)
        return False if sub_status.status == 'left' else True
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        return False

def get_subscription_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(text='Подписаться!', url="https://t.me/hahehihuha"))
    markup.add(types.InlineKeyboardButton(text='Проверить подписку', callback_data="check_sub"))
    return markup

def get_main_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('📈 Калькулятор доходности'),
        types.KeyboardButton('🛒 Наши устройства')
    )
    return markup

async def send_subscription_message(chat_id):
    markup = get_subscription_markup()
    msg = await bot.send_message(
        chat_id,
        "Пожалуйста, подпишитесь на наш канал, чтобы использовать бота. [Подписаться](https://t.me/hahehihuha)",
        parse_mode='Markdown',
        reply_markup=markup
    )
    msg_ids[chat_id] = msg.id

async def send_main_menu(chat_id):
    markup = get_main_menu_markup()
    msg = await bot.send_message(
        chat_id,
        'ℹ️ Вы можете рассчитать доходность устройства или выбрать и заказать устройства из нашего каталога!',
        reply_markup=markup
    )
    msg_ids[chat_id] = msg.id
    await bot.set_state(chat_id, CalculatorStates.choose_algorithm)

@bot.message_handler(commands=['start', 'menu'])
async def start(message) -> None:
    user_id = message.chat.id

    if await is_user_subscribed(user_id):
        await send_main_menu(message.chat.id)
    else:
        await send_subscription_message(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
async def check_sub(call):
    user_id = call.message.chat.id
    if await is_user_subscribed(user_id):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await send_main_menu(call.message.chat.id)
    else:
        markup = get_subscription_markup()
        await bot.edit_message_text(
            "Вы не подписались:(\nПожалуйста, подпишитесь на наш канал, чтобы использовать бота. [Подписаться](https://t.me/hahehihuha)",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='Markdown'
        )
        await bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
async def back_to_main_menu(call):
    await bot.delete_state(call.from_user.id)
    user_id = call.message.chat.id
    await bot.delete_message(chat_id=user_id, message_id=msg_ids[user_id])
    if await is_user_subscribed(user_id):
        await send_main_menu(call.message.chat.id)
    else:
        await send_subscription_message(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == 'back')
async def back_inline_handler(call):
    current_state = await bot.get_state(user_id=call.from_user.id)

    if current_state == CalculatorStates.choose_blockchain.name:
        await bot.set_state(call.message.chat.id, CalculatorStates.choose_algorithm)
        await choose_algorithm(call.message)

    if current_state == CalculatorStates.choose_manufacturer.name:
        await bot.set_state(call.message.chat.id, CalculatorStates.choose_blockchain)
        await choose_blockchain(call)

    if current_state == CalculatorStates.choose_model.name:
        await bot.set_state(call.message.chat.id, CalculatorStates.choose_manufacturer)
        await choose_manufacturer(call)

    if current_state == CalculatorStates.choose_ths.name:
        await bot.set_state(call.message.chat.id, CalculatorStates.choose_model)
        await choose_model(call)

    if current_state == CalculatorStates.choose_count.name:
        await bot.set_state(call.message.chat.id, CalculatorStates.choose_ths)
        await choose_ths(call)

    if current_state == CalculatorStates.confirm_additional_device.name:
        await bot.set_state(call.message.chat.id, CalculatorStates.choose_count)
        await choose_count(call)

    if current_state == CalculatorStates.choose_algorithm.name:
        print("LOLOLLPLLOLOLOL")
        await bot.set_state(call.message.chat.id, CalculatorStates.choose_count)
        await handle_submit(call)


@bot.message_handler(state=CalculatorStates.choose_algorithm)
async def choose_algorithm(message):
    context_manager.clear(message.chat.id)
    await bot.delete_message(message.chat.id, msg_ids[message.chat.id])
    unique_algorithms = {asic.algorithm for asic in asic_data if isinstance(asic.algorithm, str)}
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=algorithm, callback_data=algorithm) for algorithm in unique_algorithms]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data='main_menu'))
    msg = await bot.send_message(message.chat.id, 'Выберите алгоритм', reply_markup=markup)
    msg_ids[message.chat.id] = msg.id

@bot.callback_query_handler(func=lambda call: True, state=CalculatorStates.choose_algorithm)
async def choose_blockchain(call):
    if call.data == 'back':
        selected_algorithm = context_manager.current_asic[call.message.chat.id]['algorithm']
    else:
        selected_algorithm = call.data
    context_manager.fill_current_asic(call.message.chat.id, algorithm=selected_algorithm)
    coins = {asic.coin for asic in asic_data if selected_algorithm == asic.algorithm}

    message_text = (f'🟢 Алгоритм: <b>{selected_algorithm}</b>\n'
                    '...Выберите монету')
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=coin, callback_data=coin) for coin in coins]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data='back'))
    await bot.edit_message_text(message_text, call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup, parse_mode='HTML')
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_blockchain)

@bot.callback_query_handler(func=lambda call: True, state=CalculatorStates.choose_blockchain)
async def choose_manufacturer(call):
    if call.data == 'back':
        selected_coin = context_manager.current_asic[call.message.chat.id]['coin']
    else:
        selected_coin = call.data

    context_manager.fill_current_asic(call.message.chat.id, coin=selected_coin)

    manufacturers = {asic.manufacturer for asic in asic_data if asic.coin == selected_coin}

    message_text = (f'🟢 Алгоритм: {context_manager.current_asic.get(call.message.chat.id, {}).get("algorithm")}\n'
                    f'🟢 Монета: {selected_coin}\n'
                    '...Выберите производителя')

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=manufacturer, callback_data=f'manufacturer_{manufacturer}') for manufacturer in manufacturers]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data='back'))
    await bot.edit_message_text(message_text, call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_manufacturer)

@bot.callback_query_handler(func=lambda call: call.data.startswith('manufacturer_'), state=CalculatorStates.choose_manufacturer)
async def choose_model(call):
    if call.data == 'back':
        selected_manufacturer = context_manager.current_asic[call.message.chat.id]['manufacturer']
    else:
        selected_manufacturer = call.data.split('_')[1]

    context_manager.fill_current_asic(call.message.chat.id, manufacturer=selected_manufacturer)

    models = {asic.model for asic in asic_data if asic.manufacturer == selected_manufacturer and asic.coin == context_manager.current_asic[call.message.chat.id]['coin']}
    
    current_context_data = context_manager.current_asic.get(call.message.chat.id, {})
    message_text = (f'🟢 Алгоритм: {current_context_data.get("algorithm")}\n'
                    f'🟢 Монета: {current_context_data.get("coin")}\n'
                    f'🟢 Производитель: {selected_manufacturer}\n'
                    '...Выберите модель')

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=model, callback_data=f'model_{model}') for model in models]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data='back'))
    await bot.edit_message_text(message_text, call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_model)

@bot.callback_query_handler(func=lambda call: call.data.startswith('model_'), state=CalculatorStates.choose_model)
async def choose_ths(call):
    if call.data == 'back':
        selected_model = context_manager.current_asic[call.message.chat.id]['model']
        context_manager.current_asic[call.message.chat.id]['number'] = ''
    else:
        selected_model = call.data.split('_')[1]

    context_manager.fill_current_asic(call.message.chat.id, model=selected_model)

    thss = {asic.ths for asic in asic_data if asic.model == selected_model}

    current_context_data = context_manager.current_asic.get(call.message.chat.id, {})
    message_text = (f'🟢 Алгоритм: {current_context_data.get("algorithm")}\n'
                    f'🟢 Монета: {current_context_data.get("coin")}\n'
                    f'🟢 Производитель: {current_context_data.get("manufacturer")}\n'
                    f'🟢 Модель: {selected_model}\n'
                    '...Выберите TH/s')

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=ths, callback_data=f'ths_{ths}') for ths in thss]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data='back'))
    await bot.edit_message_text(message_text, call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)    
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_ths)

@bot.callback_query_handler(func=lambda call: call.data.startswith('ths_'), state=CalculatorStates.choose_ths)
async def choose_count(call):
    if call.data == 'back':
        selected_ths = context_manager.current_asic[call.message.chat.id].get('ths')
    else:
        selected_ths = call.data.split('_')[1]

    context_manager.fill_current_asic(call.message.chat.id, ths=selected_ths)
    
    current_context_data = context_manager.current_asic.get(call.message.chat.id, {})
    message_text = (f'🟢 Алгоритм: {current_context_data.get("algorithm")}\n'
                    f'🟢 Монета: {current_context_data.get("coin")}\n'
                    f'🟢 Производитель: {current_context_data.get("manufacturer")}\n'
                    f'🟢 Модель: {current_context_data.get("model")}\n'
                    f'🟢 TH/s: {selected_ths}\n'
                    '...Выберите количество')
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=str(i), callback_data=f'num_{i}') for i in range(1, 10)]
    buttons.append(types.InlineKeyboardButton(text='Стереть', callback_data='clear'))
    buttons.append(types.InlineKeyboardButton(text='0', callback_data='num_0'))
    buttons.append(types.InlineKeyboardButton(text='Выбрать', callback_data='submit'))
    
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data='back'))
    await bot.edit_message_text(message_text, call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)   
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_count)

@bot.callback_query_handler(func=lambda call: call.data.startswith('num_'), state=CalculatorStates.choose_count)
async def handle_number(call):
    current_number = context_manager.current_asic[call.message.chat.id].get('number', '')
    number = call.data.split('_')[1]
    
    if len(current_number) < 6:
        current_number += number
    context_manager.current_asic[call.message.chat.id]['number'] = current_number

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=str(i), callback_data=f'num_{i}') for i in range(1, 10)]
    buttons.append(types.InlineKeyboardButton(text='Стереть', callback_data='clear'))
    buttons.append(types.InlineKeyboardButton(text='0', callback_data='num_0'))
    buttons.append(types.InlineKeyboardButton(text='Выбрать', callback_data='submit'))
    
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data='back'))
    current_context_data = context_manager.current_asic.get(call.message.chat.id, {})
    number_display = (f'🟢 Алгоритм: {current_context_data.get("algorithm")}\n'
                        f'🟢 Монета: {current_context_data.get("coin")}\n'
                        f'🟢 Производитель: {current_context_data.get("manufacturer")}\n'
                        f'🟢 Модель: {current_context_data.get("model")}\n'
                        f'🟢 TH/s: {current_context_data.get("ths")}\n'
                        f'🟢 Количество: {current_number}')

    await bot.edit_message_text(number_display, call.message.chat.id, msg_ids[call.message.chat.id])
    await bot.edit_message_reply_markup(call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'clear', state=CalculatorStates.choose_count)
async def handle_clear(call):
    context_manager.current_asic[call.message.chat.id]['number'] = ''
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=str(i), callback_data=f'num_{i}') for i in range(1, 10)]
    buttons.append(types.InlineKeyboardButton(text='Стереть', callback_data='clear'))
    buttons.append(types.InlineKeyboardButton(text='0', callback_data='num_0'))
    buttons.append(types.InlineKeyboardButton(text='Выбрать', callback_data='submit'))
    
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data='back'))
    await bot.edit_message_text('Кол-во: ', call.message.chat.id, msg_ids[call.message.chat.id])
    await bot.edit_message_reply_markup(call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)

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

@bot.callback_query_handler(func=lambda call: call.data == 'add_more', state=CalculatorStates.confirm_additional_device)
async def add_more_device(call):
    await bot.delete_message(call.message.chat.id, msg_ids[call.message.chat.id])
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_algorithm)
    markup = types.InlineKeyboardMarkup(row_width=3)
    unique_algorithms = {asic.algorithm for asic in asic_data if isinstance(asic.algorithm, str)}
    buttons = [types.InlineKeyboardButton(text=algorithm, callback_data=algorithm) for algorithm in unique_algorithms]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    msg = await bot.send_message(call.message.chat.id, 'Выберите алгоритм', reply_markup=markup)
    msg_ids[call.message.chat.id] = msg.id

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
