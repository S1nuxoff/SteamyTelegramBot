import os
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from scipy.interpolate import make_interp_spline
import matplotlib.image as mpimg
from matplotlib.colors import LinearSegmentedColormap

from datetime import datetime
import app.database.requests as rq
from app.api.steam import get_item_html

# from app.utils.currency_exchanger import convert_prices

import random


def create_custom_cmap():
    fixed_color_rgba_start = (0.988, 0.835, 0.208, 0.0)
    fixed_color_rgba_end = (0.988, 0.835, 0.208, 0.2)

    custom_cmap = LinearSegmentedColormap.from_list(
        "custom_cmap", [fixed_color_rgba_start, fixed_color_rgba_end], N=256
    )
    return custom_cmap


async def create_price_chart(dates, prices, item_name, period, currency_symbol):
    if len(dates) < 2:
        return None  # Недостаточно данных для графика

    # Сортировка дат и цен по дате
    dates_num = matplotlib.dates.date2num(dates)
    sorted_indices = np.argsort(dates_num)
    dates = np.array(dates)[sorted_indices]
    prices = np.array(prices)[sorted_indices]
    x_vals = np.arange(len(dates))

    # Сглаживание цен, если точек больше 3
    if len(dates) > 3:
        x_new = np.linspace(x_vals.min(), x_vals.max(), 300)
        spline = make_interp_spline(x_vals, prices, k=1)
        prices_smooth = spline(x_new)
        dates_smooth = np.interp(x_new, x_vals, matplotlib.dates.date2num(dates))
    else:
        prices_smooth = prices
        dates_smooth = matplotlib.dates.date2num(dates)

    # Определение мин/макс цен и соответствующих дат
    min_price = prices.min()
    max_price = prices.max()
    min_index = np.argmin(prices)
    max_index = np.argmax(prices)
    min_time, max_time = dates[min_index], dates[max_index]

    # Установка начала y-оси на основе минимальной цены
    y_start = max(min_price - 1, min_price * 0.9)

    # Создание фигуры и оси
    fig, ax = plt.subplots(figsize=(6, 2), dpi=300)

    # Построение сглаженной линии цены
    ax.plot(
        matplotlib.dates.num2date(dates_smooth),
        prices_smooth,
        color="#FCD535",  # Цвет линии
        lw=0.7,
        marker="o",
        markerfacecolor="#FCD535",  # Цвет маркеров
        markevery=[-1],
        solid_capstyle="round",
        alpha=0.9,  # Установка прозрачности линии
    )

    # Создание градиентной заливки под кривой с кастомной cmap
    custom_cmap = create_custom_cmap()
    _gradient_fill(ax, dates_smooth, prices_smooth, y_start, max_price, custom_cmap)

    # Рассеивание и аннотация мин/макс цен
    _annotate_price(ax, min_time, min_price, currency_symbol, "#F6465D", offset=-24)
    _annotate_price(ax, max_time, max_price, currency_symbol, "#0ECB81", offset=16)

    # Аннотация последней цены
    last_price = prices[-1]
    last_time = dates[-1]
    _annotate_price(ax, last_time, last_price, currency_symbol, "#FFC700", offset=16)

    # Добавление названия предмета под графиком
    fig.text(
        0.45,
        0.00,
        item_name,
        fontsize=4,
        color="#5E6673",
        weight="regular",
        ha="left",
        va="top",
        transform=fig.transFigure,
    )

    # Настройка внешнего вида графика
    _customize_plot(ax, fig, min_price, max_price, y_start)

    # Добавление водяного знака, если файл существует
    _add_watermark(fig)

    # Генерация уникального имени файла и сохранение изображения
    image_path = _save_chart_image(fig, item_name, period)

    return image_path


# Функция для аннотации цен
def _annotate_price(ax, time, price, currency_symbol, color, offset):
    ax.scatter([time], [price], color=color, s=20, zorder=5)
    ax.annotate(
        f"{price:.2f} {currency_symbol}",
        (time, price),
        textcoords="offset points",
        xytext=(0, offset),
        ha="center",
        fontsize=6,
        bbox=dict(facecolor=color, pad=5, boxstyle="round,pad=0.5", edgecolor="none"),
        color="#0B0E11",  # Цвет текста
    )


# Функция для настройки внешнего вида графика
def _customize_plot(ax, fig, min_price, max_price, y_start):
    ax.set_facecolor("#181A20")  # Цвет фона оси
    fig.patch.set_facecolor("#181A20")  # Цвет фона фигуры
    ax.tick_params(colors="#5E6673")  # Цвет меток осей
    ax.grid(
        color="#5E6673", linestyle="-", linewidth=0.1, axis="both", which="both"
    )  # Цвет и стиль сетки
    ax.set_ylim(y_start, max_price + (max_price - min_price) * 0.1)

    # Удаление спайн (рамок)
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.xticks(rotation=0, fontsize=6, color="#5E6673")  # Цвет меток по оси X
    plt.yticks(fontsize=6, color="#5E6673")  # Цвет меток по оси Y
    ax.locator_params(axis="y", nbins=10)
    plt.tight_layout(pad=0)


# Функция для добавления водяного знака
def _add_watermark(fig):
    watermark_path = os.path.join("images", "watermark.png")
    if os.path.exists(watermark_path):
        watermark_img = mpimg.imread(watermark_path)
        watermark_width = 0.1
        watermark_height = watermark_width * (
            watermark_img.shape[0] / watermark_img.shape[1]
        )

        ax_watermark = fig.add_axes(
            [1 - watermark_width - 0.01, 0.01, watermark_width, watermark_height],
            anchor="SE",
            zorder=10,
        )
        ax_watermark.imshow(
            watermark_img, alpha=0.5
        )  # Установка прозрачности водяного знака
        ax_watermark.axis("off")
    else:
        print(f"Водяной знак не найден по пути: {watermark_path}")


# Функция для сохранения изображения графика
def _save_chart_image(fig, item_name, period):
    random_number = random.randint(1000, 9999)
    safe_item_name = item_name.replace(" ", "_").replace("|", "")
    image_path = f"{safe_item_name}_{period}_{random_number}.png"
    fig.savefig(image_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return image_path


# Функция для градиентной заливки под кривой с кастомной cmap
def _gradient_fill(ax, dates, prices, y_start, y_max, cmap):
    """
    Создает вертикальную градиентную заливку под кривой.

    Параметры:
    - ax: matplotlib ось для рисования.
    - dates: Массив значений дат (числовой формат).
    - prices: Массив значений цен, соответствующих датам.
    - y_start: Начальное y-значение для градиента.
    - y_max: Максимальное y-значение для градиента.
    - cmap: Кастомная цветовая карта.
    """
    # Создание пути для заливки
    verts = np.column_stack([dates, prices])
    verts = np.vstack(
        [[dates[0], y_start], verts, [dates[-1], y_start], [dates[0], y_start]]
    )
    codes = [Path.MOVETO] + [Path.LINETO] * (len(dates)) + [Path.LINETO, Path.CLOSEPOLY]
    path = Path(verts, codes)

    # Создание PathPatch без границы
    patch = PathPatch(
        path, facecolor="none", edgecolor="none"
    )  # Установка edgecolor='none'

    # Добавление патча на оси
    ax.add_patch(patch)

    # Создание градиентного изображения
    gradient = np.linspace(0, 1, 256).reshape(-1, 1)  # Вертикальный градиент
    gradient = np.flipud(gradient)  # Инвертировать для градиента сверху вниз

    # Определение границ градиента
    extent = (dates[0], dates[-1], y_start, y_max + (y_max - y_start) * 0.1)

    # Отображение градиентного изображения с отсечением по пути
    ax.imshow(
        gradient,
        extent=extent,
        aspect="auto",
        cmap=cmap,  # Использование кастомной цветовой карты
        alpha=1.0,  # Альфа-канал imshow устанавливается в 1, так как прозрачность уже задана в cmap
        clip_path=patch,
        clip_on=True,
    )


async def price_chart(appid, inspected_item, period, currency_id, currency_name):
    data = await get_item_html(appid, inspected_item, period, currency_id)

    symbol = "$"
    dates = data.get("dates")
    prices = data.get("prices")  # Список цен для графика
    period = data.get("period")

    # Формируем словарь для передачи в функцию convert_prices
    price_dict = {
        "max_price": data.get("max_price"),
        "min_price": data.get("min_price"),
        "avg_price": data.get("avg_price"),
    }

    chart_path = await create_price_chart(dates, prices, inspected_item, period, symbol)

    exchange_ratio = await rq.get_currency_ratio(currency_id)

    ratio = exchange_ratio.get("ratio")
    exchange_time = datetime.fromisoformat(exchange_ratio.get("time")).strftime(
        "%d %B %Y, %H:%M"
    )
    converted_max_price = round(data.get("max_price") * ratio, 2)
    converted_min_price = round(data.get("min_price") * ratio, 2)
    converted_avg_price = round(data.get("avg_price") * ratio, 2)
    converted_ratio = round(ratio, 2)

    # Формируем текст отчета о ценах
    price_report = (
        f"💬 <b>{inspected_item} {period} prices</b>\n\n"
        f"🟢 <b>Max Price:</b>\n"
        f"• <b>{converted_max_price} {currency_name}</b> / {data.get('max_price', 'N/A')} USD\n"
        f"• Sold: {data.get('sales_at_max_price')} units\n\n"
        f"🔴 <b>Min Price:</b>\n"
        f"• <b>{converted_min_price} {currency_name}</b> / <b>{data.get('min_price', 'N/A')} USD</b>\n"
        f"• Sold: <b>{data.get('sales_at_min_price')} units</b>\n\n"
        f"🟡 <b>Avg Price:</b>\n"
        f"• <b>{converted_avg_price} {currency_name}</b> / <b>{data.get('avg_price', 'N/A')} USD</b>\n"
        f"• Sold: <b>{data.get('sales_at_avg_price')} units</b>\n\n"
        f"<b>Total Sold:</b> {data.get('total_sales', 'N/A')} units\n\n"
        f"<b>Rate:</b> 1 USD = <b>{converted_ratio} {currency_name}</b>\n"
        f"<b>Updated</b> {exchange_time}"
    )

    return {
        "message": price_report,
        "chart_path": chart_path,
        "max_price_usd": data.get("max_price"),
        "sales_at_max_price": data.get("sales_at_max_price"),
        "min_price_usd": data.get("min_price"),
        "sales_at_min_price": data.get("sales_at_min_price"),
        "avg_price_usd": data.get("avg_price"),
        "total_sales": data.get("total_sales"),
        "converted_max_price": converted_max_price,
        "converted_min_price": converted_min_price,
        "converted_avg_price": converted_avg_price,
        "converted_ratio": converted_ratio,
        "exchange_time": exchange_time,
    }
