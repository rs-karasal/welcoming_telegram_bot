from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from states.welcoming_new_member_states import CommunityMember
from keyboards.simple_row import make_row_keyboard


router = Router()
welcome_url = "https://t.me/+Ax92fc6EFdE3MDcy"


# ШАГ 1: Получение согласия участника на вступление в сообщество
@router.message(StateFilter(None), Command("start"))
async def start_cmd(message: Message, state: FSMContext):
    await message.answer(
        text="Привет! 👋 Я телеграм-бот, и я помогу тебе стать ценным участником нашего сообщества IT-энтузиастов!\n\n"
            "Прежде чем мы начнем, давай убедимся, что мы на одной волне. Пожалуйста, внимательно ознакомься с нашей миссией и ценностями.",
        reply_markup=make_row_keyboard(["Ознакомиться"]))
    await state.set_state(CommunityMember.reading_agreement)


@router.message(
    CommunityMember.reading_agreement,
    F.text.in_(["Ознакомиться"])
)
async def show_member_agreement(message: Message, state: FSMContext):
    await message.answer(
        text="<u><b>Миссия yDecide:</b></u>\n"
            "Мы стремимся создать сообщество, где любой желающий может освоить обязательные навыки совеременности в сфере IT, и достичь успеха в этой области. Независимо от бекграунда. Без скучных лекций и шаблонных курсов.\n\n"
            
            "<u><b>Что будет в сообществе:</b></u>\n"
            "✅Объединение опытных специалистов и новичков. Обмен знаниями и опытом, знакомство и общение в неформальной обстановке.\n"
            "✅Разнообразные мероприятия - вебинары и мастер-классы с опытными наставниками, также совместное решение задач и обсуждение актуальных тем в IT.\n"
            "✅Предоставление поддержки и помощи тем, кто только начинает свой путь. Возможность найти персонального ментора с большим практическим опытом.",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        text="❌Это не очередной телеграм канал с полезностями. Ценность сообщества - сами участники.\n\n"
            
            "<u>Подтверди</u>, что разделяешь наши миссию и готов(-а) активно участвовать в жизни сообщества, помогать другим и не стесняться просить о помощи. Соблюдать общие правила этикета, не оскорблять членов сообщества и с уважением относиться к мнению собеседника.",
        reply_markup=make_row_keyboard(["Подтверждаю", "Не разделяю"])
    )
    await state.set_state(CommunityMember.choosing_member_agreement)


@router.message(CommunityMember.reading_agreement)
async def show_member_agreement_incorrect(message: Message):
    await message.answer(
        text="Я не понимаю.\n\n"
             "Пожалуйста, напиши 'Ознакомиться' или нажми кнопку с соответствующим текстом.",
        reply_markup=make_row_keyboard(["Ознакомиться"])
    )


# ШАГ 2: Получение имени участника
@router.message(
    CommunityMember.choosing_member_agreement,
    F.text.in_(["Подтверждаю", "Не разделяю"])
)
async def member_agreement_chosen(message: Message, state: FSMContext):
    if message.text.lower() == "подтверждаю":
        await state.update_data(chosen_member_agreement=message.text.lower())
        await message.answer(
            text="Отлично! 🙂 Чтобы взаимодействие было эффективным, давай познакомим тебя с комьюнити. Для этого ответь пожалуйста на 5 вопросов о себе.\n\n"
                "Этот этап можно пропустить и начать общение 'анонимно', но рекомендую все же представиться.",
            reply_markup=ReplyKeyboardRemove())
        
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="Пропустить",
            callback_data="skip_hellowing"
        ))

        await message.answer(
            text="1/5. Напиши, как можно к тебе обращаться? (или нажми на кнопку пропустить)",
            reply_markup=builder.as_markup())
    
        await state.set_state(CommunityMember.choosing_member_name)
    else:
        await state.clear()
        await message.answer("К сожалению, я не могу дать доступ к сообществу. 😔 Возможно, в следующий раз.", reply_markup=ReplyKeyboardRemove())


@router.message(CommunityMember.choosing_member_agreement)
async def member_agreement_chosen_incorrectly(message: Message):
    await message.answer(
        text="Я не понимаю.\n\n"
             "Пожалуйста, выберите один из вариантов:",
        reply_markup=make_row_keyboard(["Подтверждаю", "Не разделяю"])
    )

# ШАГ 2.5: вступление в сообщество без сбора инфы
@router.callback_query(F.data == "skip_hellowing")
async def cancel_hellowing(callback: CallbackQuery, state: FSMContext):
    join_community_builder = InlineKeyboardBuilder()
    join_community_builder.add(InlineKeyboardButton(
        text="Вступить в сообщество",
        # callback_data="skip_and_join",
        url=welcome_url
    ))
    await callback.message.answer(
        text="Не буду настаивать. 🙂👌\n\nМожешь вступить в сообщество по кнопке и начать общение.",
        reply_markup=join_community_builder.as_markup()
    )
    await state.set_state()
    await callback.answer()


# ШАГ 3: получение локации участника
@router.message(CommunityMember.choosing_member_name)
async def member_name_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_member_name=message.text.title())
    await message.answer(
        text=f"Рад знакомству, <b>{message.text.title()}</b>.\n\n2/5. В каком городе сейчас проживаешь?"
        )
    await state.set_state(CommunityMember.choosing_member_location)


# ШАГ 4: получение интересующей сферы IT и опыта работы
@router.message(CommunityMember.choosing_member_location)
async def member_location_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_member_location=message.text.title())
    await message.answer(
        text=f"Когда-нибудь побываю в <b>{message.text.title()}</b>, когда ИИ захватит мир и у меня появится физическая оболочка, хе-хе...\n\n"
            "3/5. А теперь расскажи про направление IT, которое тебе интересно и текущий опыт в этой сфере.",
    )
    await state.set_state(CommunityMember.choosing_member_exp)


# ШАГ 5: получение информации об участнкие в свободной форме
@router.message(CommunityMember.choosing_member_exp)
async def member_exp_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_member_exp=message.text)
    await message.answer(
        text="Понял.\n\n4/5. Напиши о себе немного в свободной форме (образование, увлечение, хобби, цели в АйТи и т.д.)."
    )
    await state.set_state(CommunityMember.choosing_member_bio)


# ШАГ 6: получение информации об участнкие в свободной форме
@router.message(CommunityMember.choosing_member_bio)
async def member_bio_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_member_bio=message.text)
    await message.answer(
        text="5/5. Наконец, опиши пожалуйста, какие ожидания от сообщества единомышленников (активности, контент и т.д.)."
    )
    await state.set_state(CommunityMember.choosing_member_goal)


# ШАГ7: вся инфа получена, отправка данных в группу yDecide
@router.message(CommunityMember.choosing_member_goal)
async def member_goal_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_member_goal=message.text)
    data = await state.get_data()
    await message.answer(
        text="<b>Участникам сообщества yDecide будет отправлено сообщение:</b>\n\n"
            f"Всем привет! ✋🙂 Меня зовут <b>{data['chosen_member_name']}</b>!\n"
            f"Проживаю в <b>{data['chosen_member_location']}</b>.\n"
            f"Интересующая сфера IT и опыт: <b>{data['chosen_member_exp']}</b>.\n"
            f"Немного о себе: <b>{data['chosen_member_bio']}</b>.\n"
            f"Ожидания от коммьюнити: <b>{data['chosen_member_goal']}</b>.\n\n"
            f"Телеграм: @{message.from_user.username}",
            reply_markup=make_row_keyboard(["Отправить сообщение и вступить в сообщество"])
            )
    await state.set_state(CommunityMember.finish_state)


@router.message(CommunityMember.finish_state, F.text.in_(["Отправить сообщение и вступить в сообщество"]))
async def send_message_and_join(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    await bot.send_message(
        chat_id=-1002104440872,
        text="#обомне\n\n"
            f"Всем привет! ✋🙂 Меня зовут <b>{data['chosen_member_name']}</b>!\n"
            f"Проживаю в <b>{data['chosen_member_location']}</b>.\n"
            f"Интересующая сфера IT и опыт: <b>{data['chosen_member_exp']}</b>.\n"
            f"Немного о себе: <b>{data['chosen_member_bio']}</b>.\n"
            f"Ожидания от коммьюнити: <b>{data['chosen_member_goal']}</b>.\n\n"
            f"Телеграм: @{message.from_user.username}",
        message_thread_id=2
        )
    await bot.send_message(
        chat_id=-1002104440872,
        text="#обомне\n\n"
            f"Всем привет! ✋🙂 Меня зовут <b>{data['chosen_member_name']}</b>!\n"
            f"Проживаю в <b>{data['chosen_member_location']}</b>.\n"
            f"Интересующая сфера IT и опыт: <b>{data['chosen_member_exp']}</b>.\n"
            f"Немного о себе: <b>{data['chosen_member_bio']}</b>.\n"
            f"Ожидания от коммьюнити: <b>{data['chosen_member_goal']}</b>.\n\n"
            f"Телеграм: @{message.from_user.username}",
        message_thread_id=63
        )
    await message.answer(
        text="Добро пожаловать! 👐\n"
            f"{welcome_url}",
        reply_markup=ReplyKeyboardRemove()
        )
    await state.clear()