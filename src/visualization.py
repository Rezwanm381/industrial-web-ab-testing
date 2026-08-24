"""Compact PNG figures rendered offline with Pillow."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from .statistics import conversion_summary, wilson_interval


WIDTH, HEIGHT = 1400, 800
MARGIN = 120
COLORS = {
    "ink": "#1F2933",
    "muted": "#627181",
    "grid": "#D9E2EC",
    "control": "#425466",
    "treatment": "#007C91",
    "threshold": "#B26A00",
    "white": "#FFFFFF",
}


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    filename = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(filename, size=size)
    except OSError:
        return ImageFont.load_default(size=size)


def _canvas(title: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), COLORS["white"])
    draw = ImageDraw.Draw(image)
    draw.text((MARGIN, 50), title, fill=COLORS["ink"], font=_font(36, bold=True))
    return image, draw


def _save(image: Image.Image, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="PNG", optimize=True)


def plot_conversion_rates(df: pd.DataFrame, output_path: Path, alpha: float = 0.05) -> None:
    summary = conversion_summary(df)
    image, draw = _canvas("Synthetic conversion rates with 95% Wilson intervals")
    plot_left, plot_right = 220, WIDTH - 140
    plot_top, plot_bottom = 160, HEIGHT - 150
    intervals = {
        group: wilson_interval(
            int(summary.loc[group, "conversions"]), int(summary.loc[group, "n"]), alpha
        )
        for group in ("control", "treatment")
    }
    max_rate = max(interval[1] for interval in intervals.values()) * 1.30
    max_rate = max(max_rate, 0.12)

    def y_position(value: float) -> float:
        return plot_bottom - value / max_rate * (plot_bottom - plot_top)

    for tick in range(0, 6):
        value = max_rate * tick / 5
        y = y_position(value)
        draw.line((plot_left, y, plot_right, y), fill=COLORS["grid"], width=2)
        draw.text((70, y - 14), f"{value:.1%}", fill=COLORS["muted"], font=_font(22))
    draw.line((plot_left, plot_top, plot_left, plot_bottom), fill=COLORS["ink"], width=3)
    draw.line((plot_left, plot_bottom, plot_right, plot_bottom), fill=COLORS["ink"], width=3)

    positions = {"control": 520, "treatment": 1_020}
    for group, x in positions.items():
        rate = float(summary.loc[group, "conversion_rate"])
        low, high = intervals[group]
        y, y_low, y_high = y_position(rate), y_position(low), y_position(high)
        color = COLORS[group]
        draw.line((x, y_low, x, y_high), fill=color, width=7)
        draw.line((x - 25, y_low, x + 25, y_low), fill=color, width=7)
        draw.line((x - 25, y_high, x + 25, y_high), fill=color, width=7)
        draw.ellipse((x - 14, y - 14, x + 14, y + 14), fill=color)
        draw.text((x - 65, plot_bottom + 30), group.title(), fill=COLORS["ink"], font=_font(26, bold=True))
        draw.text((x - 50, y - 55), f"{rate:.2%}", fill=color, font=_font(25, bold=True))
    draw.text((35, 320), "Conversion rate", fill=COLORS["ink"], font=_font(24, bold=True))
    draw.text((MARGIN, HEIGHT - 60), "One point per group; whiskers show uncertainty. No truncated bar axis is used.", fill=COLORS["muted"], font=_font(22))
    _save(image, output_path)


def plot_effect_interval(
    difference: float,
    ci_lower: float,
    ci_upper: float,
    practical_threshold: float,
    output_path: Path,
) -> None:
    image, draw = _canvas("A/B effect with 95% Newcombe interval")
    draw.text((MARGIN, 105), "Synthetic demonstration", fill=COLORS["muted"], font=_font(22, bold=True))
    axis_left, axis_right, axis_y = 180, WIDTH - 160, 430
    min_value = min(ci_lower, -0.005) - 0.003
    max_value = max(ci_upper, practical_threshold) + 0.003

    def x_position(value: float) -> float:
        return axis_left + (value - min_value) / (max_value - min_value) * (axis_right - axis_left)

    draw.line((axis_left, axis_y, axis_right, axis_y), fill=COLORS["ink"], width=4)
    for tick in range(7):
        value = min_value + (max_value - min_value) * tick / 6
        x = x_position(value)
        draw.line((x, axis_y - 12, x, axis_y + 12), fill=COLORS["ink"], width=3)
        draw.text((x - 38, axis_y + 28), f"{value * 100:+.1f}", fill=COLORS["muted"], font=_font(20))
    zero_x = x_position(0)
    threshold_x = x_position(practical_threshold)
    draw.line((zero_x, 190, zero_x, 610), fill=COLORS["ink"], width=3)
    draw.line((threshold_x, 190, threshold_x, 610), fill=COLORS["threshold"], width=4)
    draw.text((zero_x - 55, 155), "No effect", fill=COLORS["ink"], font=_font(22, bold=True))
    draw.text((threshold_x - 155, 625), "+1.0-point SCENARIO THRESHOLD", fill=COLORS["threshold"], font=_font(22, bold=True))
    low_x, high_x, estimate_x = x_position(ci_lower), x_position(ci_upper), x_position(difference)
    draw.line((low_x, axis_y, high_x, axis_y), fill=COLORS["treatment"], width=10)
    draw.line((low_x, axis_y - 24, low_x, axis_y + 24), fill=COLORS["treatment"], width=7)
    draw.line((high_x, axis_y - 24, high_x, axis_y + 24), fill=COLORS["treatment"], width=7)
    draw.ellipse((estimate_x - 17, axis_y - 17, estimate_x + 17, axis_y + 17), fill=COLORS["treatment"])
    draw.text((estimate_x - 95, 330), f"Estimate {difference * 100:+.2f} points", fill=COLORS["treatment"], font=_font(24, bold=True))
    draw.text((MARGIN, HEIGHT - 65), "Horizontal scale: treatment minus control conversion difference (percentage points)", fill=COLORS["muted"], font=_font(22))
    _save(image, output_path)


def plot_power_curve(
    curve: pd.DataFrame,
    required_n: int,
    output_path: Path,
    desired_power: float = 0.80,
) -> None:
    """Plot prospective power with readable per-group sample-size ticks."""

    image, draw = _canvas("Synthetic scenario: power for a +1.0 percentage-point effect")
    plot_left, plot_right = 190, WIDTH - 130
    plot_top, plot_bottom = 160, HEIGHT - 150
    x_min, x_max = int(curve["n_per_group"].min()), int(curve["n_per_group"].max())

    def x_position(value: float) -> float:
        return plot_left + (value - x_min) / (x_max - x_min) * (plot_right - plot_left)

    def y_position(value: float) -> float:
        return plot_bottom - value * (plot_bottom - plot_top)

    for tick in range(0, 6):
        value = tick / 5
        y = y_position(value)
        draw.line((plot_left, y, plot_right, y), fill=COLORS["grid"], width=2)
        draw.text((80, y - 14), f"{value:.0%}", fill=COLORS["muted"], font=_font(21))
    draw.line((plot_left, plot_top, plot_left, plot_bottom), fill=COLORS["ink"], width=3)
    draw.line((plot_left, plot_bottom, plot_right, plot_bottom), fill=COLORS["ink"], width=3)
    x_ticks = [
        value
        for value in (1_000, 5_000, 10_000, 15_000, 20_000, 25_000)
        if x_min <= value <= x_max
    ]
    for value in x_ticks:
        x = x_position(value)
        draw.line((x, plot_bottom - 10, x, plot_bottom + 10), fill=COLORS["ink"], width=3)
        label = f"{value // 1_000}k"
        label_box = draw.textbbox((0, 0), label, font=_font(20))
        label_width = label_box[2] - label_box[0]
        draw.text(
            (x - label_width / 2, plot_bottom + 24),
            label,
            fill=COLORS["muted"],
            font=_font(20),
        )
    target_y = y_position(desired_power)
    draw.line((plot_left, target_y, plot_right, target_y), fill=COLORS["threshold"], width=4)
    required_x = x_position(required_n)
    draw.line((required_x, plot_top, required_x, plot_bottom), fill=COLORS["control"], width=4)
    points = [
        (x_position(float(row.n_per_group)), y_position(float(row.power)))
        for row in curve.itertuples(index=False)
    ]
    draw.line(points, fill=COLORS["treatment"], width=7, joint="curve")
    draw.text((plot_right - 190, target_y - 38), "80% target", fill=COLORS["threshold"], font=_font(22, bold=True))
    draw.text((required_x - 120, plot_top + 20), f"Required n = {required_n:,}", fill=COLORS["control"], font=_font(22, bold=True))
    draw.text((MARGIN, HEIGHT - 55), "Sample size per group (two-sided alpha = 0.05; baseline = 10%; scenario effect = +1.0 point)", fill=COLORS["muted"], font=_font(22))
    _save(image, output_path)
