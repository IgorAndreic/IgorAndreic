import asyncio
import json
import logging
import os
import zipfile
import time

from sti001 import stl_to_jpg
from telegram import ReplyKeyboardMarkup,ReplyKeyboardRemove,Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

item_dict = {
    "Table top": 1,
    "Christmas ball": 2,
    "Transparent eggs": 3,
    "Candel holder": 4,
    "Mug": 5,
}
ITEM, ITEM_PHOTO, IMG, REQ_SIZE, SIZE, CREATE_STL, CONTINUE = range(7)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def generate_base_file_name(user_id):
    timestamp = int(time.time())
    return f"{user_id}_{timestamp}"
def load_localization(language_code):
    try:
        with open(fr"C:/Users/Administrator/Downloads/Bot/localization/{language_code}.json", 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        with open(fr"C:/Users/Administrator/Downloads/Bot/localization/en.json", 'r', encoding='utf-8') as file:  # English as default
            return json.load(file)
        
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    base_file_name = generate_base_file_name(user_id)
    context.user_data['base_file_name'] = base_file_name

    user_language_code = update.message.from_user.language_code[:2]  # 'en', 'ru', etc.
    context.user_data['language_code'] = user_language_code  # Сохраняем код языка

    """Starts the conversation and asks the user What to create."""
    user_language_code = context.user_data.get('language_code', 'en')  # Значение по умолчанию - 'en'
    localization = load_localization(user_language_code)
    reply_keyboard = [["Table top"],
                      ["Christmas ball"],
                      ["Transparent eggs"],
                      ["Candel holder"],
                      ["Mug"]]
    await update.message.reply_text(
        localization["welcome_message"],
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder=localization["welcome_options"]
        ),
    )
    user = update.message.from_user
    logger.info("Start Item of %s: %s", user.first_name, update.message.text)

    return ITEM

async def item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected item and asks for a img."""
    
    user_choice = update.message.text  # Получаем текст выбранного пользователем элемента
    choice_item = item_dict.get(user_choice)  # Получаем соответствующее числовое значение из словаря
    context.user_data['choice_item'] = choice_item
    user_language_code = context.user_data.get('language_code', 'en')  # Значение по умолчанию - 'en'
    localization = load_localization(user_language_code)

    user = update.message.from_user
    logger.info("Item of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        localization["prompt_image"],
        reply_markup=ReplyKeyboardRemove(),
    )

    return IMG

async def not_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_language_code = context.user_data.get('language_code', 'en')  # Значение по умолчанию - 'en'
    localization = load_localization(user_language_code)
    await update.message.reply_text(localization["error_not_image"])
    
    return IMG

async def save_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_language_code = context.user_data.get('language_code', 'en')  # Значение по умолчанию - 'en'
    localization = load_localization(user_language_code)
    base_file_name = context.user_data.get('base_file_name')
    img_file_name = fr"E:\Bot\IMG\{base_file_name}.jpg"
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive(img_file_name)
    user = update.message.from_user
    logger.info("Save photo of %s: %s", user.first_name, img_file_name)
    await update.message.reply_text(
        localization["enter_height"]
    )
    return CREATE_STL

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    user_id = update.message.from_user.id
    base_file_name = generate_base_file_name(user_id)
    context.user_data['base_file_name'] = base_file_name

    user_language_code = update.message.from_user.language_code[:2]  # 'en', 'ru', etc.
    context.user_data['language_code'] = user_language_code  # Сохраняем код языка
    user_language_code = context.user_data.get('language_code', 'en')  # Значение по умолчанию - 'en'
    localization = load_localization(user_language_code)


    img_file_name = fr"E:\Bot\IMG\{base_file_name}.jpg"
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive(img_file_name)
    user = update.message.from_user
    logger.info("Handler photo  of %s: %s", user.first_name, img_file_name)
    reply_keyboard = [["Table top"],
                      ["Christmas ball"],
                      ["Transparent eggs"],
                      ["Candel holder"],
                      ["Mug"]]
    await update.message.reply_text(
        localization["welcome_short"],
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder=localization["welcome_options"]
        ),
    )
    logger.info("Model of handler photo %s: %s", user.first_name, update.message.text)    
    
    return REQ_SIZE

async def req_size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_choice = update.message.text  # Получаем текст выбранного пользователем элемента
    choice_item = item_dict.get(user_choice)  # Получаем соответствующее числовое значение из словаря
    context.user_data['choice_item'] = choice_item
    user_language_code = context.user_data.get('language_code', 'en')  # Значение по умолчанию - 'en'
    localization = load_localization(user_language_code)

    user = update.message.from_user
    logger.info("Item of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        localization["enter_height"],
    )
    return CREATE_STL


async def handle_size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice_size = update.message.text  # Получаем текст выбранного пользователем элемента
    context.user_data['choice_size'] = choice_size
    user = update.message.from_user
    logger.info("Handler Size of %s: %s", user.first_name, update.message.text)
    return CREATE_STL

async def not_size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_language_code = context.user_data.get('language_code', 'en')  # Значение по умолчанию - 'en'
    localization = load_localization(user_language_code)
    await update.message.reply_text("Enter numbers until 999, please,\n\n"
                                    "or send /cancel to stop.")
    
    return SIZE

async def create_stl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_language_code = context.user_data.get('language_code', 'en')  # Значение по умолчанию - 'en'
    localization = load_localization(user_language_code)
    choice_size = update.message.text  # Получаем текст выбранного пользователем элемента
    # Проверка, что choice_size можно преобразовать в число
    try:
        choice_size = int(choice_size)
    except ValueError:
        await update.message.reply_text(localization["error_invalid_number"])
        return CREATE_STL  # Вернуться к состоянию для повторного ввода

    base_file_name = context.user_data.get('base_file_name')
    img_file_name = fr"E:\Bot\IMG\{base_file_name}.jpg"
    stl_file_name = fr"E:\Bot\STL\{base_file_name}_Amazing.stl"
    program_path = "ASC7console.exe"
    choice_item = context.user_data.get('choice_item')
    args = [str(choice_item), str(choice_size), '120', img_file_name, stl_file_name]
    user = update.message.from_user
    logger.info("%s: %s", user.first_name, args)
    process = await asyncio.create_subprocess_exec(program_path, *args)
    await process.wait()
    user = update.message.from_user
    logger.info("STL of %s: %s", user.first_name, stl_file_name)
    await update.message.reply_text(localization["stl_created"])

    jpg_file_name = fr"E:\Bot\IMG\{base_file_name}_output.jpg"

    # Вызов функции stl_to_jpg для создания изображения
    stl_to_jpg(stl_file_name, jpg_file_name)

    # Отправка изображения пользователю
    with open(jpg_file_name, 'rb') as file:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=file)
    # Отправка клавиатуры с вопросом
    reply_keyboard = [['Download'], ['Cancel']]

    logger.info("Answer Download of %s: %s", user.first_name, stl_file_name)
    await update.message.reply_text(
        localization["buy_query"],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return CONTINUE

async def continue_zip (update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_language_code = context.user_data.get('language_code', 'en')  # Значение по умолчанию - 'en'
    localization = load_localization(user_language_code)
    base_file_name = context.user_data.get('base_file_name')
    stl_file_name = fr"E:\Bot\STL\{base_file_name}_Amazing.stl"
    zip_file_name = fr"E:\Bot\STL\ZIP\{base_file_name}_Amazing.zip"    
    file_name = os.path.basename(stl_file_name)
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(stl_file_name, arcname=file_name)
    user = update.message.from_user
    logger.info("ZIP of %s: %s", user.first_name, zip_file_name)
    await update.message.reply_text(localization["zip_created"],
                                     reply_markup=ReplyKeyboardRemove()
                                    )        
    
    with open(zip_file_name, 'rb') as file:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=file, filename=file.name)
    logger.info("END of %s: %s", user.first_name, stl_file_name)
    await update.message.reply_text(localization["stl_success"], 
                                    reply_markup=ReplyKeyboardRemove()
                                    )
    return ConversationHandler.END

async def send_instructions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    instructions = """
    *How to Use the STL Creation Bot* 🤖

    Welcome to our Telegram bot, designed to create STL files for 3D printing using the Amazing STL Creator 7 software. Follow these simple steps to create your own STL files:

    1. *Start by Selecting a Model*: 📐
       - Begin a chat with the bot and choose the model you want to create. The bot offers several options such as "Table top", "Christmas ball", "Transparent eggs", "Candel holder", and "Mug".

    2. *Upload Your Image*: 🖼️
       - After selecting a model, upload an image that you want to use for your STL file. Images with a dark background are better. 
       - *Important*: Please upload the image as a photo, not as a file attachment.

    3. *Wait for the STL File to be Created*: ⏳
       - Once you've uploaded your image, the bot will process it using Amazing STL Creator 7.
       - This process may take some time, so please be patient.

    4. *Receive and Download Your STL File*: 📥
       - After processing, you'll receive a ZIP archive containing your STL file.
       - Download the ZIP file to your device.

    5. *Unzip and Print*: 🖨️
       - Extract the STL file from the ZIP archive to any directory.
       - The STL file is now ready to be sent for 3D printing.

    Enjoy creating custom 3D models with ease and convenience, right from your Telegram!
    """
    await update.message.reply_text(instructions, parse_mode='Markdown')

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Асинхронная функция обработки исключений."""
    try:
        raise context.error
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_language_code = context.user_data.get('language_code', 'en')  # Значение по умолчанию - 'en'
    localization = load_localization(user_language_code)
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        localization["cancel_message"], reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main() -> None:
    application = Application.builder().token("6861103323:AAF7_2Jo4tw6GTMn8_BN0DmYOzsfkwZGds8").build()
    conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start), MessageHandler(filters.PHOTO, handle_photo)],
    states={
        ITEM: [MessageHandler(filters.Regex("^(Table top|Christmas ball|Transparent eggs|Candel holder|Mug)$"), item)],
        ITEM_PHOTO: [
            MessageHandler(filters.PHOTO, save_photo),
            MessageHandler(filters.ALL, not_image),
            CommandHandler("cancel", cancel)
        ],
        IMG: [
            MessageHandler(filters.PHOTO, save_photo),
            MessageHandler(filters.ALL, not_image),
            CommandHandler("cancel", cancel)
        ],
        REQ_SIZE: [
            MessageHandler(filters.Regex("^(Table top|Christmas ball|Transparent eggs|Candel holder|Mug)$"), req_size),
            CommandHandler("cancel", cancel)
        ],
        SIZE: [
            MessageHandler(filters.Regex(r"^\d{1,3}$"), handle_size),
            MessageHandler(filters.ALL, not_size),
            CommandHandler("cancel", cancel)
        ],
        CREATE_STL: [
            MessageHandler(filters.ALL, create_stl)
        ],
        CONTINUE: [
            MessageHandler(filters.Regex('^Download$'), continue_zip),
            MessageHandler(filters.Regex('^Cancel$'), cancel)
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    application.add_handler(CommandHandler("help", send_instructions))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
   
if __name__ == "__main__":
    main()
