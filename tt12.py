import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

# Замените на ваш API токен
API_TOKEN = 'YOUR_API_TOKEN'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Определение состояний конверсации
class Form(StatesGroup):
    choose_souvenir = State()  # Выбор сувенира
    upload_photo = State()    # Загрузка фотографии
    create_stl = State()      # Создание STL-файла
    send_stl = State()        # Отправка STL-файла
    end_conversation = State()  # Завершение разговора

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await Form.choose_souvenir.set()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    item1 = types.KeyboardButton("Table top")
    item2 = types.KeyboardButton("Christmas ball")
    item3 = types.KeyboardButton("Transparent eggs")
    item4 = types.KeyboardButton("Candel holder")
    item5 = types.KeyboardButton("Mug")
    markup.add(item1, item2, item3, item4, item5)
    await message.reply("Hi! I am Amazing STL Creator! Choose a souvenir type:", reply_markup=markup)

# Обработчик выбора сувенира
@dp.message_handler(lambda message: message.text not in ["Table top", "Christmas ball", "Transparent eggs", "Candel holder", "Mug"], state=Form.choose_souvenir)
async def process_choose_souvenir_invalid(message: types.Message):
    return await message.reply("Choose a souvenir type from the keyboard.")

@dp.message_handler(lambda message: message.text in ["Table top", "Christmas ball", "Transparent eggs", "Candel holder", "Mug"], state=Form.choose_souvenir)
async def process_choose_souvenir(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['souvenir_type'] = message.text
    await Form.upload_photo.set()
    await message.reply("Great choice! Now, please send me a photo for your souvenir (or send /skip).")

# Обработчик загрузки фото
@dp.message_handler(content_types=types.ContentType.PHOTO, state=Form.upload_photo)
async def process_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[-1].file_id
    await Form.create_stl.set()
    await message.reply("I have received your photo. Now, I will create an STL file for your souvenir.")

@dp.message_handler(lambda message: message.text.lower() == '/skip', state=Form.upload_photo)
async def process_skip_photo(message: types.Message):
    await Form.create_stl.set()
    await message.reply("You have skipped photo upload. I will proceed to create an STL file.")

# Обработчик создания STL-файла
@dp.message_handler(state=Form.create_stl)
async def process_create_stl(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        souvenir_type = data['souvenir_type']
        photo_file_id = data['photo']
    # В этом месте вы можете выполнить создание STL-файла на основе фото и внешней программы
    # и сохранить STL-файл в переменную, например, data['stl_file'] = 'путь_к_STL_файлу.stl'
    # Здесь вы можете добавить ваш код для создания STL-файла
    await Form.send_stl.set()
    await bot.send_message(message.chat.id, "I have created the STL file. Now, I will send it to you.")

# Обработчик отправки STL-файла
@dp.message_handler(state=Form.send_stl)
async def process_send_stl(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # В этом месте вы можете отправить STL-файл пользователю
        # используя data['stl_file'] (путь к файлу) или отправить его как файл
        await message.reply("Here is your STL file.")
    await Form.end_conversation.set()
    await message.reply("Thank you! I hope you enjoyed creating your souvenir.")

# Обработчик отмены разговора
@dp.message_handler(lambda message: message.text.lower() == '/cancel', state="*")
@dp.message_handler(Text(equals='Cancel', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply('You have canceled the conversation. Bye!', reply_markup=types.ReplyKeyboardRemove())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
