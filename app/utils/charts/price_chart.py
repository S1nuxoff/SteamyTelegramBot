import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from scipy.interpolate import make_interp_spline
import matplotlib.image as mpimg
from matplotlib.colors import LinearSegmentedColormap
import random


def create_custom_cmap():
    fixed_color_rgba_start = (0.988, 0.835, 0.208, 0.0)
    fixed_color_rgba_end = (0.988, 0.835, 0.208, 0.2)

    custom_cmap = LinearSegmentedColormap.from_list(
        "custom_cmap", [fixed_color_rgba_start, fixed_color_rgba_end], N=256
    )
    return custom_cmap


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
        color="#0B0E11",
    )


def _customize_plot(ax, fig, min_price, max_price, y_start):
    ax.set_facecolor("#181A20")
    fig.patch.set_facecolor("#181A20")
    ax.tick_params(colors="#5E6673")
    ax.grid(
        color="#5E6673", linestyle="-", linewidth=0.1, axis="both", which="both"
    )
    ax.set_ylim(y_start, max_price + (max_price - min_price) * 0.1)

    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.xticks(rotation=0, fontsize=6, color="#5E6673")
    plt.yticks(fontsize=6, color="#5E6673")
    ax.locator_params(axis="y", nbins=10)
    plt.tight_layout(pad=0)


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
        )
        ax_watermark.axis("off")
    else:
        print(f"Водяной знак не найден по пути: {watermark_path}")


def _save_chart_image(fig, item_name, period):
    temp_dir = "temp"

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    random_number = random.randint(1000, 9999)
    safe_item_name = item_name.replace(" ", "_").replace("|", "")
    filename = f"{safe_item_name}_{period}_{random_number}.png"

    image_path = os.path.join(temp_dir, filename)

    fig.savefig(image_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    return image_path


def _gradient_fill(ax, dates, prices, y_start, y_max, cmap):
    verts = np.column_stack([dates, prices])
    verts = np.vstack(
        [[dates[0], y_start], verts, [dates[-1], y_start], [dates[0], y_start]]
    )
    codes = [Path.MOVETO] + [Path.LINETO] * (len(dates)) + [Path.LINETO, Path.CLOSEPOLY]
    path = Path(verts, codes)

    patch = PathPatch(
        path, facecolor="none", edgecolor="none"
    )

    ax.add_patch(patch)

    gradient = np.linspace(0, 1, 256).reshape(-1, 1)
    gradient = np.flipud(gradient)

    extent = (dates[0], dates[-1], y_start, y_max + (y_max - y_start) * 0.1)

    ax.imshow(
        gradient,
        extent=extent,
        aspect="auto",
        cmap=cmap,
        alpha=1.0,
        clip_path=patch,
        clip_on=True,
    )


async def create_price_chart(dates, prices, item_name, period, currency_symbol):
    if len(dates) < 2:
        return None

    dates_num = matplotlib.dates.date2num(dates)
    sorted_indices = np.argsort(dates_num)
    dates = np.array(dates)[sorted_indices]
    prices = np.array(prices)[sorted_indices]
    x_vals = np.arange(len(dates))

    if len(dates) > 3:
        x_new = np.linspace(x_vals.min(), x_vals.max(), 300)
        spline = make_interp_spline(x_vals, prices, k=1)
        prices_smooth = spline(x_new)
        dates_smooth = np.interp(x_new, x_vals, matplotlib.dates.date2num(dates))
    else:
        prices_smooth = prices
        dates_smooth = matplotlib.dates.date2num(dates)

    min_price = prices.min()
    max_price = prices.max()
    min_index = np.argmin(prices)
    max_index = np.argmax(prices)
    min_time, max_time = dates[min_index], dates[max_index]

    y_start = max(min_price - 1, min_price * 0.9)

    fig, ax = plt.subplots(figsize=(6, 2), dpi=300)

    ax.plot(
        matplotlib.dates.num2date(dates_smooth),
        prices_smooth,
        color="#FCD535",
        lw=0.7,
        marker="o",
        markerfacecolor="#FCD535",
        markevery=[-1],
        solid_capstyle="round",
        alpha=0.9,
    )

    custom_cmap = create_custom_cmap()
    _gradient_fill(ax, dates_smooth, prices_smooth, y_start, max_price, custom_cmap)

    _annotate_price(ax, min_time, min_price, currency_symbol, "#F6465D", offset=-24)
    _annotate_price(ax, max_time, max_price, currency_symbol, "#0ECB81", offset=16)

    last_price = prices[-1]
    last_time = dates[-1]
    _annotate_price(ax, last_time, last_price, currency_symbol, "#FFC700", offset=16)

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

    _customize_plot(ax, fig, min_price, max_price, y_start)

    _add_watermark(fig)

    image_path = _save_chart_image(fig, item_name, period)

    return image_path
