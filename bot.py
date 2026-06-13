# bot.py - переработанная версия

import asyncio
import logging
import random
from collections import defaultdict
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, ADMIN_CHAT_ID
from questions import questions as quiz_data
from animals import ZOO_INHABITANTS, AVAILABLE_SPECIES

# Настройка бота
BOT = Bot(token=BOT_TOKEN)
MEMORY_STORAGE = MemoryStorage()
DISPATCHER = Dispatcher(storage=MEMORY_STORAGE)
logging.basicConfig(level=logging.INFO)

# Состояния викторины
class QuizStates(StatesGroup):
    answering = State()
    waiting_for_review = State()

# Хранилища данных пользователей
USER_RESULTS = {}          # user_id -> словарь с баллами
USER_PROGRESS = {}         # user_id -> текущий индекс вопроса

def build_keyboard(answer_variants):
    """Создаёт клавиатуру из вариантов ответов"""
    keyboard_buttons = []
    for idx, variant in enumerate(answer_variants):
        keyboard_buttons.append([InlineKeyboardButton(text=variant["text"], callback_data=f"variant_{idx}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

def get_top_animal(score_dict):
    """Определяет животное с максимальным количеством баллов"""
    if not score_dict:
        return None
    max_score_value = max(score_dict.values())
    top_candidates = [creature for creature, points in score_dict.items() if points == max_score_value]
    return random.choice(top_candidates)

@DISPATCHER.message(Command("start"))
async def welcome_message(message: Message, state: FSMContext):
    person_id = message.from_user.id
    await state.clear()
    USER_RESULTS[person_id] = defaultdict(int)
    USER_PROGRESS[person_id] = 0
    
    welcome_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Запустить викторину 🎯", callback_data="launch_quiz")]
    ])
    
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Я помогу тебе найти твоего духовного покровителя среди обитателей Московского зоопарка.\n"
        "Отвечай на вопросы, и я скажу, кто твоё тотемное животное!\n"
        "Также ты узнаешь, как стать другом зоопарка и помогать животным.\n\n"
        "Готов? Жми на кнопку ниже 👇",
        reply_markup=welcome_buttons
    )

@DISPATCHER.callback_query(F.data == "launch_quiz")
async def launch_quiz(callback: types.CallbackQuery, state: FSMContext):
    person_id = callback.from_user.id
    USER_RESULTS[person_id] = defaultdict(int)
    USER_PROGRESS[person_id] = 0
    await state.set_state(QuizStates.answering)
    await send_next_question(callback.message, person_id)

async def send_next_question(msg: Message, person_id: int):
    """Отправляет следующий вопрос пользователю"""
    current_position = USER_PROGRESS.get(person_id, 0)
    
    if current_position < len(quiz_data):
        current_q = quiz_data[current_position]
        answer_panel = build_keyboard(current_q["options"])
        
        await msg.answer(
            f"📌 Вопрос {current_position + 1} из {len(quiz_data)}:\n\n{current_q['question']}",
            reply_markup=answer_panel
        )
    else:
        # Викторина завершена - показываем итоги
        await display_final_result(msg, person_id)

@DISPATCHER.callback_query(F.data.startswith("variant_"), QuizStates.answering)
async def handle_user_answer(callback: types.CallbackQuery, state: FSMContext):
    person_id = callback.from_user.id
    current_position = USER_PROGRESS.get(person_id, 0)
    
    if current_position >= len(quiz_data):
        await callback.answer("Викторина уже завершена. Для перезапуска введите /start")
        return
    
    current_q = quiz_data[current_position]
    selected_idx = int(callback.data.split("_")[1])
    
    if selected_idx >= len(current_q["options"]):
        await callback.answer("Некорректный выбор")
        return
    
    chosen_variant = current_q["options"][selected_idx]
    
    # Начисляем баллы за ответ
    for creature, weight in chosen_variant["weights"].items():
        USER_RESULTS[person_id][creature] += weight
    
    # Убираем клавиатуру с ответом
    await callback.message.edit_reply_markup(reply_markup=None)
    
    # Переходим к следующему вопросу
    USER_PROGRESS[person_id] += 1
    await send_next_question(callback.message, person_id)
    await callback.answer()

async def display_final_result(msg: Message, person_id: int):
    """Показывает пользователю его тотемное животное"""
    scores_data = USER_RESULTS.get(person_id, {})
    
    if not scores_data:
        await msg.answer("Что-то пошло не так. Попробуй начать заново через /start")
        return
    
    winner_creature = get_top_animal(scores_data)
    
    if not winner_creature:
        await msg.answer("Не удалось определить тотем. Пожалуйста, перезапусти викторину командой /start")
        return
    
    creature_data = ZOO_INHABITANTS[winner_creature]
    
    # Формируем информационное сообщение
    result_message = (
        f"✨ <b>Твой духовный наставник — {creature_data['title']}!</b> ✨\n\n"
        f"📖 <i>{creature_data['bio']}</i>\n\n"
        f"🤝 {creature_data['sponsor_link']}"
    )
    
    # Отправляем фото с подписью
    try:
        animal_photo = FSInputFile(f"images/{creature_data['photo']}")
        await msg.answer_photo(animal_photo, caption=result_message, parse_mode="HTML")
    except Exception:
        await msg.answer(result_message + "\n\n(картинка пока не загрузилась, но суть не меняется 😊)", parse_mode="HTML")
    
    # Получаем имя бота для шеринга
    bot_info = await BOT.get_me()
    bot_nickname = bot_info.username
    
    # Финальная панель действий
    action_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💚 Как стать опекуном?", callback_data="guardian_info")],
        [InlineKeyboardButton(text="📢 Поделиться результатом",
                              switch_inline_query=f"Мой тотем — {creature_data['title']}! А кто твой? Узнай у @{bot_nickname}")],
        [InlineKeyboardButton(text="📞 Связаться с зоопарком", callback_data="ask_contact")],
        [InlineKeyboardButton(text="💬 Оставить отзыв", callback_data="give_review")],
        [InlineKeyboardButton(text="🔄 Пройти викторину заново", callback_data="launch_quiz")]
    ])
    
    await msg.answer("Что желаешь сделать дальше?", reply_markup=action_buttons)

@DISPATCHER.callback_query(F.data == "guardian_info")
async def show_guardian_info(callback: types.CallbackQuery):
    info_text = (
        "🌸 <b>Программа «Клуб друзей зоопарка»</b> 🌸\n\n"
        "Стать опекуном животного — значит внести свой вклад в его благополучие.\n"
        "Собранные средства идут на:\n"
        "• качественное питание 🍎\n"
        "• обустройство вольеров 🏠\n"
        "• ветеринарный уход 🩺\n\n"
        "Опекуном может стать кто угодно — частное лицо или целая компания.\n\n"
        "Все детали на официальном сайте:\n"
        "https://moscowzoo.ru/about/guardianship\n\n"
        "Спасибо, что помогаете нашим подопечным! 🐾"
    )
    await callback.message.answer(info_text, parse_mode="HTML", disable_web_page_preview=True)
    await callback.answer()

@DISPATCHER.callback_query(F.data == "ask_contact")
async def request_contact(callback: types.CallbackQuery):
    person_id = callback.from_user.id
    scores_data = USER_RESULTS.get(person_id, {})
    
    if scores_data:
        winner_creature = get_top_animal(scores_data)
        if winner_creature:
            creature_title = ZOO_INHABITANTS[winner_creature]["title"]
            user_score_value = scores_data[winner_creature]
            contact_report = (
                f"🔔 Запрос связи от @{callback.from_user.username} (ID: {person_id})\n"
                f"Результат викторины: {creature_title}\n"
                f"Набрано баллов: {user_score_value}"
            )
        else:
            contact_report = f"🔔 Запрос связи от @{callback.from_user.username} (ID: {person_id})\nРезультат не определён"
    else:
        contact_report = f"🔔 Запрос связи от @{callback.from_user.username} (ID: {person_id})\nВикторина ещё не пройдена"
    
    try:
        await BOT.send_message(ADMIN_CHAT_ID, contact_report)
        await callback.message.answer(
            "📞 Сотрудник зоопарка свяжется с тобой в ближайшее время.\n"
            "А пока можешь написать на почту: zoofriends@moscowzoo.ru"
        )
    except Exception as error:
        await callback.message.answer(
            "⚠️ Не удалось отправить запрос. Пожалуйста, напиши напрямую на почту zoofriends@moscowzoo.ru"
        )
    await callback.answer()

@DISPATCHER.callback_query(F.data == "give_review")
async def request_review(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(QuizStates.waiting_for_review)
    await callback.message.answer(
        "📝 Будем рады услышать твоё мнение!\n"
        "Напиши свой отзыв или пожелания одним сообщением. Всё передадим сотрудникам зоопарка."
    )
    await callback.answer()

@DISPATCHER.message(QuizStates.waiting_for_review)
async def save_user_review(message: Message, state: FSMContext):
    person_id = message.from_user.id
    review_content = message.text
    
    with open("feedback.txt", "a", encoding="utf-8") as file:
        file.write(f"Отзыв от {person_id}: {review_content}\n")
    
    await message.answer(
        "🌿 Спасибо за обратную связь! Каждый отзыв делает зоопарк лучше.\n"
        "Желаем хорошего дня! 🦊"
    )
    await state.clear()

async def launch_bot():
    await DISPATCHER.start_polling(BOT)

if __name__ == "__main__":
    asyncio.run(launch_bot())