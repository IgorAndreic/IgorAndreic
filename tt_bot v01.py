import asyncio
import logging
import os
import re
import zipfile

from telegram import ReplyKeyboardMarkup,ReplyKeyboardRemove,Update, User
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
size_dict = {
    "Small": 30,
    "Medium": 60,
    "Big": 90,
}

ITEM, IMG, ZIP = range(3)
counter = 1
choice_item = 3
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user What to create."""
    reply_keyboard = [["Table top"],
                      ["Christmas ball"],
                      ["Transparent eggs"],
                      ["Candel holder"],
                      ["Mug"]]
    await update.message.reply_text(
        "Hi! I am Amazing STL Creator! "
        "Send /cancel to stop.\n\n"
        "What do you want to create??",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Choose one option"
        ),
    )
    user = update.message.from_user
    logger.info("Item of %s: %s", user.first_name, update.message.text)

    return ITEM

async def item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected item and asks for a img."""
    user = update.message.from_user
    user_choice = update.message.text  # Получаем текст выбранного пользователем элемента
    choice_item = item_dict.get(user_choice)  # Получаем соответствующее числовое значение из словаря

    logger.info("Item of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "I see! Please send me a image. Images with a dark background are better",
        reply_markup=ReplyKeyboardRemove(),
    )

    return IMG

async def not_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please send me the image as a 'Photo', not as a 'File'")
    
    return IMG

async def ask_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    a = choice_item
    return await image(update, context, choice_item=a)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await image(update, context, choice_item=1)

async def image(update: Update, context: ContextTypes.DEFAULT_TYPE, choice_item) -> int:
    """Stores the image"""
    global counter
    user = update.message.from_user
    img_file_name = fr"C:\Bot\IMG\{counter}_image.jpg"
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive(img_file_name)
    logger.info("Image of %s: %s", user.first_name, img_file_name)
    await update.message.reply_text(
        "Let's create STL! Wait please..."
    )
    stl_file_name = fr"C:\Bot\STL\{counter}_Amazing.stl"
    program_path = "ASC7console.exe"
    args = [str(choice_item), '70', '120', img_file_name, stl_file_name]
    process = await asyncio.create_subprocess_exec(program_path, *args)
    await process.wait()
    logger.info("STL of %s: %s", user.first_name, stl_file_name)
    await update.message.reply_text("STL file is created. Now, I will ZIP for you.")
    
    zip_file_name = fr"C:\Bot\STL\ZIP\{counter}_Amazing.zip"    
    file_name = os.path.basename(stl_file_name)
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(stl_file_name, arcname=file_name)

    await update.message.reply_text("I have created the ZIP arhive. Now, I will send to you.")        
    
    with open(zip_file_name, 'rb') as file:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=file, filename=file.name)

    await update.message.reply_text("Your STL file has been successfully created.")
    counter += 1
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

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Асинхронная функция обработки исключений."""
    try:
        raise context.error
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main() -> None:
    application = Application.builder().token("6861103323:AAF7_2Jo4tw6GTMn8_BN0DmYOzsfkwZGds8").build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), MessageHandler(filters.PHOTO, handle_photo)],
        states={
            ITEM: [MessageHandler(filters.Regex("^(Table top|Christmas ball|Transparent eggs|Candel holder|Mug)$"), item)]
            SIZE: [MessageHandler(filters.Redex("^(Big|Medium|Small)$), size],
            STAND: [MessageHandler(filters.Redex("^(Thick|Normal|Thin)$), stand],                                    
            IMG: [MessageHandler(filters.PHOTO, ask_photo),
                  MessageHandler(filters.ALL, not_image)],
            },            
            fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    application.add_handler(CommandHandler("help", send_instructions))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
   
if __name__ == "__main__":
    main()
