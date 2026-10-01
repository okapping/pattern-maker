import pyxel


def draw_text_shadow(x, y, text, color=7, custom_font=False):
    """
    文字の右下に黒い影を付ける。
    """
    font = None
    if custom_font:
        # font = pyxel.Font("assets/x10y12pxDonguriDuel.ttf")
        font = pyxel.Font("assets/YokohamaDotsJPN.otf")
        # font = pyxel.Font("assets/x16y32pxGridGazer.ttf")
        # font = pyxel.Font("assets/x12y16pxLineLinker.ttf")
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

def draw_rrect(x, y, w, h, r, col):
    """角丸四角形を描く（塗りつぶし）
    x, y: 左上の座標
    w, h: 幅と高さ
    r: 角の丸さ（半径）
    col: 色
    """
    # 中央の矩形を描く（上下）
    pyxel.rect(x + r, y, w - 2*r, h, col)
    # 中央の矩形を描く（左右）
    pyxel.rect(x, y + r, w, h - 2*r, col)
    
    # 4つの角を円で描く
    pyxel.circ(x + r, y + r, r, col)  # 左上
    pyxel.circ(x + w - r - 1, y + r, r, col)  # 右上
    pyxel.circ(x + r, y + h - r - 1, r, col)  # 左下
    pyxel.circ(x + w - r - 1, y + h - r - 1, r, col)  # 右下

def draw_rrectb(x, y, w, h, r, col):
    """角丸四角形の輪郭を描く（線のみ）
    x, y: 左上の座標
    w, h: 幅と高さ
    r: 角の丸さ（半径）
    col: 色
    """
    # 4つの角の円弧
    # clip(x, y, w, h)
    # 左上
    pyxel.clip(x, y, r, r)
    pyxel.circb(x + r, y + r, r, col)
    # 右上
    pyxel.clip(x + w - r, y, r, r)
    pyxel.circb(x + w - r - 1, y + r, r, col)
    # 左下
    pyxel.clip(x, y + h - r, r, r)
    pyxel.circb(x + r, y + h - r - 1, r, col)
    # 右下
    pyxel.clip(x + w - r, y + h - r, r, r)
    pyxel.circb(x + w - r - 1, y + h - r - 1, r, col)
    # clipの初期化
    pyxel.clip()
    
    # 上下左右の直線
    pyxel.line(x + r, y, x + w - r - 1, y, col)  # 上
    pyxel.line(x + r, y + h - 1, x + w - r - 1, y + h - 1, col)  # 下
    pyxel.line(x, y + r, x, y + h - r - 1, col)  # 左
    pyxel.line(x + w - 1, y + r, x + w - 1, y + h - r - 1, col)  # 右
