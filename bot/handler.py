from telebot import types
from bot.config import *
from telebot.asyncio_handler_backends import State, StatesGroup
from bitinfo import crypto_full_names
from telebot.asyncio_handler_backends import BaseMiddleware
from telebot import types
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from gsheets import GoogleSheetsAPI

g = GoogleSheetsAPI()
asic_data = g.serialize()

unique_coins = {asic.coin for asic in asic_data if isinstance(asic.coin, str)}

# TODO - добавить чекер подписки

class CalculatorStates(StatesGroup):
    choose_blockchain = State()
    choose_count = State()
    choose_manufacturer = State()
    choose_model = State()
    choose_ths = State()
    choose_algorithm = State()

msg_ids = dict() 
user_data = dict() 
user_access_count = dict() 

user_selected_coin = {}
user_selected_manufacturer = {}
user_selected_model = {}
user_selected_ths = {}
user_selected_algorithm = {}

async def is_user_subscribed(user_id): 
    try: 
        chat_member = await bot.get_chat_member(CHANNEL_ID, user_id) 
        return chat_member.status in ['member', 'administrator', 'creator'] 
    except Exception as e: 
        print(f"Ошибка при проверке подписки: {e}") 
        return False 
 
@bot.message_handler(commands=['start', 'menu']) 
async def start(message) -> None: 
    user_id = message.from_user.id 
    if user_id not in user_access_count: 
        user_access_count[user_id] = 0
 
    if user_access_count[user_id] == 0 or await is_user_subscribed(user_id): 
        user_access_count[user_id] += 1
 
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2) 
        markup.add(
            types.KeyboardButton('📈 Калькулятор доходности'), 
            types.KeyboardButton('🛒 Наши устройства')
        )
        
        msg = await bot.send_message(message.chat.id, 'ℹ️ Вы можете рассчитать доходность устройства или выбрать и заказать устройства из нашего каталога!', reply_markup=markup)
        msg_ids[message.chat.id] = msg.id 
        await bot.set_state(message.chat.id, CalculatorStates.choose_blockchain) 
    else: 
        await bot.send_message(
            message.chat.id, 
            "Пожалуйста, подпишитесь на наш канал, чтобы использовать бота. [Подписаться](https://t.me/hahehihuha)", 
            parse_mode='Markdown'
        )

@bot.message_handler(state=CalculatorStates.choose_blockchain)
async def choose_blockchain(message):
    await bot.delete_message(message.chat.id, msg_ids[message.chat.id])

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=coin, callback_data=coin) for coin in unique_coins]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    
    for row in rows:
        markup.row(*row)
        
    msg = await bot.send_message(message.chat.id, 'ℹ️ Выберите монету', reply_markup=markup)
    msg_ids[message.chat.id] = msg.id

@bot.callback_query_handler(func=lambda call: call.data in unique_coins)
async def choose_manufacturer(call):
    selected_coin = call.data
    user_selected_coin[call.message.chat.id] = selected_coin
    manufacturers = {asic.manufacturer for asic in asic_data if asic.coin == selected_coin}

    if not manufacturers:
        await bot.answer_callback_query(call.id, "Производители не найдены для выбранной монеты.")
        return

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=manufacturer, callback_data=f'manufacturer_{manufacturer}') for manufacturer in manufacturers]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]

    for row in rows:
        markup.row(*row)

    await bot.edit_message_text('ℹ️ Выберите производителя', call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_manufacturer)


@bot.callback_query_handler(func=lambda call: call.data.startswith('manufacturer_'), state=CalculatorStates.choose_manufacturer)
async def choose_model(call):
    selected_manufacturer = call.data.split('manufacturer_')[1]
    user_selected_manufacturer[call.message.chat.id] = selected_manufacturer

    models = {asic.model for asic in asic_data if asic.manufacturer == selected_manufacturer and asic.coin == user_selected_coin[call.message.chat.id]}

    if not models:
        await bot.answer_callback_query(call.id, "Модели не найдены для выбранного производителя.")
        return

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=model, callback_data=f'model_{model}') for model in models]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]

    for row in rows:
        markup.row(*row)

    await bot.edit_message_text('ℹ️ Выберите модель', call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_model)

@bot.callback_query_handler(func=lambda call: call.data.startswith('model_'), state=CalculatorStates.choose_model)
async def choose_ths(call):
    selected_model = call.data.split('model_')[1]
    user_selected_model[call.message.chat.id] = selected_model

    thss = {asic.ths for asic in asic_data if asic.model == selected_model}

    if not thss:
        await bot.answer_callback_query(call.id, "TH не найдены для выбранного производителя.")
        return

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=ths, callback_data=f'ths_{thss}') for ths in thss]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]

    for row in rows:
        markup.row(*row)

    await bot.edit_message_text('ℹ️ Выберите ths', call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_ths)

@bot.callback_query_handler(func=lambda call: call.data.startswith('ths_'), state=CalculatorStates.choose_ths)
async def choose_algorithm(call):
    selected_ths = call.data.split('ths_')[1]
    user_selected_ths[call.message.chat.id] = selected_ths

    algorithms = {asic.algorithm for asic in asic_data if asic.ths == selected_ths}

    if not algorithms:
        await bot.answer_callback_query(call.id, "Алгоритмы не найдены для выбранного производителя.")
        return

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=algorithm, callback_data=f'algorithm_{algorithms}') for algorithm in algorithms]
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]

    for row in rows:
        markup.row(*row)

    await bot.edit_message_text('ℹ️ Выберите algorithm', call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_algorithm)

@bot.callback_query_handler(func=lambda call: call.data.startswith('asic_'))
async def choose_count(call):
    user_data[call.from_user.id] = {'number': ''}
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=str(i), callback_data=f'num_{i}') for i in range(1, 10)]
    buttons.append(types.InlineKeyboardButton(text='Стереть', callback_data='clear'))
    buttons.append(types.InlineKeyboardButton(text='0', callback_data='num_0'))
    buttons.append(types.InlineKeyboardButton(text='Выбрать', callback_data='submit'))
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    await bot.edit_message_text('ℹ️ Выберите количество', call.message.chat.id, msg_ids[call.message.chat.id])
    await bot.edit_message_reply_markup(call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)
    await bot.set_state(call.message.chat.id, CalculatorStates.choose_count)

@bot.callback_query_handler(func=lambda call: call.data.startswith('num_'))
async def handle_number(call):
    user_id = call.from_user.id
    current_number = user_data.get(user_id, {}).get('number', '')
    number = call.data.split('_')[1]
    
    if len(current_number) < 6:
        current_number += number
    user_data[user_id]['number'] = current_number

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=str(i), callback_data=f'num_{i}') for i in range(1, 10)]
    buttons.append(types.InlineKeyboardButton(text='Стереть', callback_data='clear'))
    buttons.append(types.InlineKeyboardButton(text='0', callback_data='num_0'))
    buttons.append(types.InlineKeyboardButton(text='Выбрать', callback_data='submit'))
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    
    number_display = f'Кол-во: {current_number}'
    await bot.edit_message_text(number_display, call.message.chat.id, msg_ids[call.message.chat.id])
    await bot.edit_message_reply_markup(call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'clear')
async def handle_clear(call):
    user_id = call.from_user.id
    user_data[user_id]['number'] = ''
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=str(i), callback_data=f'num_{i}') for i in range(1, 10)]
    buttons.append(types.InlineKeyboardButton(text='0', callback_data='num_0'))
    buttons.append(types.InlineKeyboardButton(text='Стереть', callback_data='clear'))
    buttons.append(types.InlineKeyboardButton(text='Выбрать', callback_data='submit'))
    rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in rows:
        markup.row(*row)
    
    await bot.edit_message_text('Кол-во: ', call.message.chat.id, msg_ids[call.message.chat.id])
    await bot.edit_message_reply_markup(call.message.chat.id, msg_ids[call.message.chat.id], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'submit')
async def handle_submit(call):
    user_id = call.from_user.id
    quantity = user_data.get(user_id, {}).get("number", "не указано")

    # Создание PDF файла
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Регистрация шрифта
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/DejaVuSans.ttf'))
    c.setFont('DejaVuSans', 12)

    # Добавляем текст в PDF
    c.drawString(100, height - 100, f'Вы выбрали количество: {quantity}')
    c.drawString(100, height - 130, 'Цена: 640 USD')

    # Сохраняем PDF
    c.save()

    # Переносим содержимое PDF из буфера в файл
    buffer.seek(0)
    pdf_file_path = '/tmp/user_invoice.pdf'
    try:
        with open(pdf_file_path, 'wb') as f:
            f.write(buffer.read())
        print(f"PDF файл создан: {pdf_file_path}")
    except Exception as e:
        print(f"Ошибка при сохранении PDF файла: {e}")
        await bot.send_message(call.message.chat.id, "Не удалось создать PDF файл. Попробуйте снова.")
        return

    try:
        # Отправка PDF пользователю
        with open(pdf_file_path, 'rb') as f:
            await bot.send_document(call.message.chat.id, f, caption="Ваш расчет")
        print("PDF файл отправлен пользователю")
    except Exception as e:
        print(f"Ошибка при отправке PDF: {e}")
        await bot.send_message(call.message.chat.id, "Произошла ошибка при отправке PDF. Попробуйте снова.")
    finally:
        # Удаление временного файла
        if os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)
            print(f"Временный файл удален: {pdf_file_path}")
