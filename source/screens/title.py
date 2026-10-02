import pyxel
from .list import ListScreen

from utils import *

PTN_SIZE = 16
PTN_KATAKUSA = (0, 32)
PTN_UROKO = (16, 32)
PTN_ICHIMATSU = (32, 32)
PTN_KAGOME = (48, 32)
PTN_KAMADO = (0, 48)
PTN_KOUSHI = (16, 48)
PTN_KUSAKI = (32, 48)
PTN_KUSAKI = (48, 48)

PATTERNS = [
    (0, 32),
    (16, 32),
    (32, 32),
    (48, 32),
    (0, 48),
    (32, 64),
    (16, 48),
    (32, 48),
    (48, 48),
    (0, 64),
    (16, 64),
]

class TitleScreen:
    def __init__(self, app):
        self.app = app

    def update(self):
        app = self.app
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            app.screens[app.SCREEN_LIST] = ListScreen(app)
            app.change_screen(app.SCREEN_LIST)
    
    def draw(self):
        pyxel.cls(0)

        app = self.app
        
        for i in range((pyxel.width // PTN_SIZE) + 1):
            for j in range((pyxel.height // PTN_SIZE) + 1):
                pyxel.blt(
                    i * PTN_SIZE,
                    j * PTN_SIZE,
                    0,
                    PATTERNS[(pyxel.frame_count // 90) % len(PATTERNS)][0],
                    PATTERNS[(pyxel.frame_count // 90) % len(PATTERNS)][1],
                    PTN_SIZE,
                    PTN_SIZE
                )
        # --------------------
        # タイトル
        # --------------------
        w, h, = 200, 120
        pyxel.blt(
            (pyxel.width // 2) - (w // 2),
            30,
            2,
            0,
            0,
            w,
            h,
            7

        )
        # --------------------
        # 文字
        # --------------------
        msg = "Pattern Maker"
        pyxel.rect(
            (pyxel.width // 2) - (app.font.text_width(msg)//2)-2,
            20,
            app.font.text_width(msg)+4,
            11,
            1
        )
        draw_text_shadow(
            (pyxel.width // 2) - (app.font.text_width(msg)//2),
            20,
            msg,
            7,
            custom_font=True
        )

        msg = "Click to START"
        pyxel.rect(
            (pyxel.width // 2) - (app.font.text_width(msg)//2)-2,
            180,
            app.font.text_width(msg)+4,
            11,
            1
        )
        draw_text_shadow(
            (pyxel.width // 2) - (app.font.text_width(msg)//2),
            180,
            msg,
            7,
            custom_font=True
        )

        # --------------------
        # Pyxel LOGO
        # --------------------
        s = "Powered by"
        pyxel.rect(
            16-1,
            pyxel.height-16-16-pyxel.FONT_HEIGHT-2,
            len(s)*pyxel.FONT_WIDTH+2,
            pyxel.FONT_HEIGHT+2,
            1
        )
        draw_text_shadow(
            16,
            pyxel.height-16-16-pyxel.FONT_HEIGHT-1,
            s,
            7,
            # custom_font=True
        )
        pyxel.blt(
            16,
            pyxel.height-16-16,
            1,
            0,
            0,
            38,
            16,
            0
        )
