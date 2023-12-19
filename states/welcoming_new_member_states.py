from aiogram.fsm.state import StatesGroup, State


class CommunityMember(StatesGroup):
    reading_agreement = State()
    choosing_member_agreement = State()
    choosing_member_name = State()
    choosing_member_location = State()
    choosing_member_exp = State()
    choosing_member_bio = State()
    choosing_member_goal = State()
    finish_state = State()