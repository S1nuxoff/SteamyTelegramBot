from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
import app.database.requests as rq
from app.utils.compare_prices import compare_price
from app.keyboards import chart_period, back
from app.utils.price_chart import price_chart
from app.utils.check_liquidity import check_liquidity
import os

tools_router = Router()


@tools_router.callback_query(F.data.startswith("compare_prices"))
async def compare_prices_handler(callback: CallbackQuery, state: FSMContext):
    user_data = await rq.get_state(callback.from_user.id)
    sel_game_data = user_data.get("sel_game_data")
    inspected_item = user_data.get("inspected_item")
    currency = user_data.get("currency")
    currency_name = user_data.get("currency_name")

    # Получение текста из функции compare_price
    compare_result = await compare_price(
        sel_game_data, inspected_item, currency, currency_name
    )

    if compare_result["success"]:
        text = compare_result["text"]
        keyboard = await back("inspect_menu")
    else:
        text = compare_result["text"]
        keyboard = await back(
            "start_menu"
        )  # Или другой соответствующий клавиатурный макет

    await callback.message.edit_text(
        text=text, parse_mode="HTML", reply_markup=keyboard
    )

    await callback.answer()


@tools_router.callback_query(F.data.startswith("price_chart"))
async def view_chart(callback: CallbackQuery):
    await callback.message.edit_text(
        text="📊 <b>Select Price Chart Period</b>\n"
        "Please choose a time period to generate the price chart for the selected item:",
        parse_mode="HTML",
        reply_markup=await chart_period(),
    )


@tools_router.callback_query(F.data.startswith("chart_period_"))
async def handle_chart_period(callback: CallbackQuery, state: FSMContext):

    user_data = await rq.get_state(callback.from_user.id)
    sel_game_data = user_data.get("sel_game_data")
    inspected_item = user_data.get("inspected_item")
    currency = user_data.get("currency")
    currency_name = user_data.get("currency_name")

    period = callback.data.split("_")[-1]

    data = await price_chart(
        sel_game_data.get("steam_id"),
        inspected_item,
        period,
        currency,
        currency_name,
    )

    chart_path = data.get("chart_path")

    if chart_path and os.path.exists(chart_path):

        # Удаление предыдущего сообщения
        await callback.message.delete()

        # Отправляем фото и сохраняем message_id
        sent_message = await callback.message.answer_photo(
            photo=FSInputFile(chart_path), parse_mode="Markdown"
        )

        await callback.message.answer(
            text=data.get("message"),
            reply_markup=await back("inspect_menu"),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

        await state.update_data(photo_message_id=sent_message.message_id)
        os.remove(chart_path)

    else:
        await callback.message.answer(
            "❌ Failed to generate the chart.", reply_markup=await back("inspect_menu")
        )
        await state.clear()


@tools_router.callback_query(F.data.startswith("check_liquidity"))
async def check_liquidity_handler(callback: CallbackQuery, state: FSMContext):
    user_data = await rq.get_state(callback.from_user.id)
    sel_game_data = user_data.get("sel_game_data")
    inspected_item = user_data.get("inspected_item")
    currency = user_data.get("currency")
    keyboard = await back("inspect_menu")

    data = await check_liquidity(
        sel_game_data.get("steam_id"), inspected_item, currency
    )

    text = (
        f"💧 <b>Liquidity Check</b>\n\n"
        f"🏆 <b>Highest Buy Request:</b> {data.get('highest_buy_order', 'N/A')} or lower\n"
        f"🏷️ <b>Lowest Sell Offer:</b> {data.get('lowest_sell_order', 'N/A')} "
        f"(after fees: {data.get('highest_sell_order_no_fee')})\n\n"
        f"⚖️ <b>Margin Status:</b> {data.get('margin_status', 'N/A')}\n"
        f"💼 <b>Margin Value:</b> {data.get('margin_value', 'N/A')} "
        f"({data.get('margin', 'N/A')}%)\n\n"
        f"📈 Make smart trading decisions with these insights!"
    )

    await callback.message.edit_text(
        text=text, parse_mode="HTML", reply_markup=keyboard
    )

    await callback.answer()
