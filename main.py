from aiogram import types
from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher import filters
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from conf import BOT_TOKEN, channels, button_text, button_url
from states import States
from tasks import prepare_video


bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


watch_channels = set([i[0] for i in channels])

button_for_posts = types.InlineKeyboardMarkup(1, [
        [types.InlineKeyboardButton(button_text, url=button_url)]
    ])


@dp.message_handler(filters.Regexp("^(http|https):\/\/[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(\/\S*)?$"))
async def url(message: types.Message, state: FSMContext):
    await States.choose_chanel.set()
    await state.update_data(url=message.text)
    markup = types.InlineKeyboardMarkup(1, [
        [types.InlineKeyboardButton(el[-1],
                              callback_data=f"{idx}")] for idx, el in enumerate(channels)
    ])

    await message.answer('Выберете канал для отправки', reply_markup=markup)
    
    
@dp.callback_query_handler(state=States.choose_chanel)
async def chanel(callback: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    prepare_video.delay(state_data['url'], channels[int(callback.data)])
    await callback.message.delete()
    await callback.message.answer('Добавлено в очередь')
    await state.finish()
    await callback.answer()


@dp.channel_post_handler(content_types=types.ContentType.VIDEO)
async def handle_video_post(message: types.Message):
    if message.chat.id not in watch_channels:
        return
    try:
        await message.edit_reply_markup(button_for_posts)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)