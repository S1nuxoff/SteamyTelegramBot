import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
import app.database.requests as rq
from app.utils.compare_prices import compare_price
from app.keyboards import chart_period, back
from app.utils.price_chart import price_chart
from app.utils.check_liquidity import check_liquidity
from app.localization import localization, get_text

tools_router = Router()

@tools_router.callback_query(F.data.startswith("compare_prices"))
async def compare_prices_handler(callback: CallbackQuery, state: FSMContext):
    user_data = await rq.get_state(callback.from_user.id)
    sel_game_data = user_data.get("sel_game_data")
    inspected_item = user_data.get("inspected_item")
    currency = user_data.get("currency")
    currency_name = user_data.get("currency_name")
    user_language = user_data.get('language')

    data = await compare_price(sel_game_data, inspected_item, currency, currency_name)

    if data["success"]:
        text_template = get_text(user_language, 'compare_prices.MARKET_PRICES')
        steam_data = data.get("steam_data", {})
        dmarket_data = data.get("dmarket_data", {})

        text = text_template.format(
            item=inspected_item,
            steam_min_price=steam_data.get("min_price", "N/A"),
            steam_average_price=steam_data.get("average_price", "N/A"),
            steam_offers=steam_data.get("offers", "N/A"),
            dmarket_converted_min_price=dmarket_data.get("converted_min_price", "N/A"),
            dmarket_converted_average_price=dmarket_data.get("converted_average_price", "N/A"),
            dmarket_offers=dmarket_data.get("offers", "N/A"),
            currency_name=currency_name,
            dmarket_converted_ratio=dmarket_data.get("converted_ratio", "N/A"),
            dmarket_exchange_time=dmarket_data.get("exchange_time", "N/A")
        )

        keyboard = await back("inspect_menu", user_language)

    else:
        text = get_text(user_language, 'errors.DATA_ERROR')
        keyboard = await back("start_menu", user_language)

    await callback.message.edit_text(
        text=text, parse_mode="HTML", reply_markup=keyboard
    )

    await callback.answer()



@tools_router.callback_query(F.data.startswith("price_chart"))
async def view_chart(callback: CallbackQuery):
    user_data = await rq.get_state(callback.from_user.id)
    user_language = user_data.get('language')

    await callback.message.edit_text(
        text=get_text(user_language, 'price_chart.PRICE_CHART_PERIOD_TEXT'),
        parse_mode="HTML",
        reply_markup=await chart_period(user_language),
    )


@tools_router.callback_query(F.data.startswith("chart_period_"))
async def handle_chart_period(callback: CallbackQuery, state: FSMContext):
    user_data = await rq.get_state(callback.from_user.id)
    sel_game_data = user_data.get("sel_game_data")
    inspected_item = user_data.get("inspected_item")
    currency = user_data.get("currency")
    currency_name = user_data.get("currency_name")
    user_language = user_data.get('language')

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
        text_template = get_text(user_language, 'price_chart.PRICE_CHART_REPORT')

        text = text_template.format(
            inspected_item=inspected_item,
            period=period,
            converted_max_price=data.get('converted_max_price'),
            currency_name=currency_name,
            max_price=data.get('max_price', 'N/A'),
            sales_at_max_price=data.get('sales_at_max_price', 'N/A'),
            converted_min_price=data.get("converted_min_price"),
            min_price=data.get('min_price', 'N/A'),
            sales_at_min_price=data.get('sales_at_min_price', 'N/A'),
            converted_avg_price=data.get("converted_avg_price"),
            avg_price=data.get('avg_price', 'N/A'),
            sales_at_avg_price=data.get('sales_at_avg_price', 'N/A'),
            total_sales=data.get('total_sales', 'N/A'),
            converted_ratio=data.get("converted_ratio"),
            exchange_time=data.get("exchange_time")
        )

        await callback.message.answer(
            text=text,
            reply_markup=await back("inspect_menu", user_language),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

        await state.update_data(photo_message_id=sent_message.message_id)
        os.remove(chart_path)

    else:
        await callback.message.answer(
            text=get_text(user_language, 'price_chart.FAIL_GENERATE_CHART'),
            reply_markup=await back("inspect_menu", user_language)
        )
        await state.clear()


@tools_router.callback_query(F.data.startswith("check_liquidity"))
async def check_liquidity_handler(callback: CallbackQuery, state: FSMContext):
    user_data = await rq.get_state(callback.from_user.id)
    sel_game_data = user_data.get("sel_game_data")
    inspected_item = user_data.get("inspected_item")
    currency = user_data.get("currency")
    user_language = user_data.get('language')
    keyboard = await back("inspect_menu", user_language)

    data = await check_liquidity(
        sel_game_data.get("steam_id"), inspected_item, currency
    )

    text_template = get_text(user_language, 'check_liquidity.LIQUIDITY_REPORT')

    text = text_template.format(
        highest_buy_order=data.get('highest_buy_order', 'N/A'),
        lowest_sell_order=data.get('lowest_sell_order', 'N/A'),
        highest_sell_order_no_fee=data.get('highest_sell_order_no_fee'),
        margin_status=data.get('margin_status', 'N/A'),
        margin_value=data.get('margin_value', 'N/A'),
        margin=data.get('margin', 'N/A')
    )


    await callback.message.edit_text(
        text=text, parse_mode="HTML", reply_markup=keyboard
    )

    await callback.answer()
