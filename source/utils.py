import pyxel


def draw_text_shadow(x, y, text, color=7, custom_font=False):
    """
    文字の右下に黒い影を付ける。
    """
    font = None
    if custom_font:
        # font = pyxel.Font("assets/x8y12pxDenkiChip.ttf")
        font = pyxel.Font("assets/x10y12pxDonguriDuel.ttf")
    pyxel.text(
        x + 1,
        y + 1,
        text,
        0,
        font,
    )

    pyxel.text(
        x,
        y,
        text,
        color,
        font,
    )
