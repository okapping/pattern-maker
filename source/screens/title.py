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

PATTERNS = [
    PTN_KATAKUSA,
    PTN_UROKO,
    PTN_ICHIMATSU,
    PTN_KAGOME,
    PTN_KAMADO,
    PTN_KOUSHI,
    PTN_KUSAKI
]

class TitleScreen:
    def __init__(self, app):
        self.app = app

    def update(self):
        app = self.app
        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
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
                    PATTERNS[(pyxel.frame_count // 90) % 7][0],
                    PATTERNS[(pyxel.frame_count // 90) % 7][1],
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
        msg = "PATTERN MAKER"
        pyxel.rect(
            (pyxel.width // 2) - (app.font.text_width(msg)//2)-2,
            20,
            app.font.text_width(msg)+4,
            11,
            5
        )
        draw_text_shadow(
            (pyxel.width // 2) - (app.font.text_width(msg)//2),
            20,
            msg,
            7,
            custom_font=True
        )

        # --------------------
        # Pyxel LOGO
        # --------------------
        msg = "Made with"
        pyxel.rect(
            16,
            pyxel.height-16-16-pyxel.FONT_HEIGHT-1,
            len(msg)*pyxel.FONT_WIDTH,
            pyxel.FONT_HEIGHT,
            5
        )
        draw_text_shadow(
            16,
            pyxel.height-16-16-pyxel.FONT_HEIGHT-1,
            "Made with",
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
        pyxel.text(0, 0, "TITLE", 7)