from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, Text
import re

from data import RequestData
from config import VK_API_TOKEN
from state import State
import api


bot = Bot(token=VK_API_TOKEN)

MENU_KEYBOARD = (
    Keyboard(one_time=True, inline=False)
    .add(Text('Составить заявку'))
    .get_json()
)


# Начало работы с ботом
@bot.on.message(text='Начать')
async def start_handler(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    await message.answer('Здравствуйте, {}.'.format(users_info[0].first_name), keyboard=MENU_KEYBOARD)
    await bot.state_dispenser.set(message.from_id, state=State.MENU_SELECTION)


# Список категорий
@bot.on.message(text='Составить заявку', state=State.MENU_SELECTION)
async def new_request_handler(message: Message):
    users_info = await bot.api.users.get(message.from_id)

    categories_keyboard = Keyboard(one_time=False, inline=True)
    try:
        categories_json = api.get_categories()
    except:
        return
    categories = []
    for category in categories_json['data']:
        categories.append([category['id'], category['title']])
        categories_keyboard.add(Text(category['title']))
    categories_keyboard.get_json()

    await message.answer('Выберите категорию заявки:'.format(users_info[0].first_name), keyboard=categories_keyboard)
    await bot.state_dispenser.set(message.from_id, state=State.CATEGORY_SELECTION, categories=categories)


# Выбор категории
@bot.on.message(state=State.CATEGORY_SELECTION)
async def select_category_handler(message: Message): 
    for category in message.state_peer.payload['categories']:
        if category[1] == message.text:
            id = category[0]
    
    if id is None:
        await message.answer('Введенная категория не существует')
        return
    
    RequestData.data[message.from_id] = {}
    RequestData.data[message.from_id]['problemCategories'] = [id]
    
    await bot.state_dispenser.set(message.from_id, state=State.FULL_NAME_INPUT)
    await message.answer('Введите ФИО')


# Ввод ФИО
@bot.on.message(state=State.FULL_NAME_INPUT)
async def full_name_input_handler(message: Message):
    full_name = message.text

    try:
        if len(full_name.split()) != 3:
            raise
        if not full_name.replace(' ', '').isalpha():
            raise
    except:
        await message.answer('Введите корректное ФИО')
        return
    
    RequestData.data[message.from_id]['fio'] = message.text

    await bot.state_dispenser.set(message.from_id, state=State.PHONE_NUMBER_INPUT)
    await message.answer('Введите номер телефона (071XXXXXXX)')
      

# Ввод номера телефона
@bot.on.message(state=State.PHONE_NUMBER_INPUT)
async def phone_number_input_handler(message: Message):
    phone_number = message.text

    if re.match(r'^071\d{7}$', phone_number) is None:
        await message.answer('Введите корректный номер телефона')
        return
    
    RequestData.data[message.from_id]['phone'] = message.text

    await bot.state_dispenser.set(message.from_id, state=State.IMAGE_SELECTION)
    await message.answer('Отправьте фотографии')


# Выбор фотографии
@bot.on.message(state=State.IMAGE_SELECTION)
async def image_selection_handler(message: Message):
    photo_urls = []

    if len(message.attachments) == 0:
        await message.answer('Отправьте фотографии')
        return

    for attachment in message.attachments:
        if attachment.photo:
            url = attachment.photo.sizes[-1].url
            photo_urls.append(url)
    
    RequestData.data[message.from_id]['content'] = [{'type': 0, 'url': i} for i in photo_urls]

    await bot.state_dispenser.set(message.from_id, state=State.ADDRESS_INPUT)
    await message.answer('Введите адрес')


# Ввод адреса
@bot.on.message(state=State.ADDRESS_INPUT)
async def address_input_handler(message: Message):
    RequestData.data[message.from_id]['address'] = message.text

    await bot.state_dispenser.set(message.from_id, state=State.DESCRIPTION_INPUT)
    await message.answer('Введите описание')


# Ввод описания
@bot.on.message(state=State.DESCRIPTION_INPUT)
async def description_input_handler(message: Message):
    RequestData.data[message.from_id]['description'] = message.text

    await bot.state_dispenser.set(message.from_id, state=State.MENU_SELECTION)

    try:
        api.send_request(message.from_id)
        await message.answer('Заявка отправлена', keyboard=MENU_KEYBOARD)
    except:
        return


bot.run_forever()