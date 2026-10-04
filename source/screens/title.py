import pyxel
import webbrowser

from .list import ListScreen

from utils import *

PTN_SIZE = 16
# webbrowser.open(git_hub_link)
git_hub_link = "https://github.com/okapping/pattern-maker"

PATTERNS = [
    (0, 32),
    (16, 32),
    (32, 32),
    (48, 32),
    (0, 48),
    (16, 48),
    (32, 48),
    (48, 48),
    (0, 64),
    (16, 64),
    (32, 64),
    (48, 64),
]

class TitleScreen:
    def __init__(self, app):
        self.app = app

    def update(self):
        app = self.app
        # git hubアイコンをクリック
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            x = 88
            y = pyxel.height-16-16
            if (
                x <= pyxel.mouse_x < x+16
                and y <= pyxel.mouse_y < y+16
            ):
                webbrowser.open(git_hub_link)
                return
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
        # 文字
        # --------------------
        msg = "Pattern Maker"
        # pyxel.rect(
        #     (pyxel.width // 2) - (app.font.text_width(msg)//2)-2,
        #     20,
        #     app.font.text_width(msg)+4,
        #     11,
        #     1
        # )
        draw_rrect(
            (pyxel.width // 2) - (app.font.text_width(msg)//2)-4,
            20-4,
            app.font.text_width(msg)+8,
            11+8,
            7,
            9
        )
        pyxel.dither(0.5)
        draw_rrect(
            (pyxel.width // 2) - (app.font.text_width(msg)//2)-4,
            20-4,
            app.font.text_width(msg)+8,
            11+8,
            7,
            8
        )
        pyxel.dither(1)
        draw_rrectb(
            (pyxel.width // 2) - (app.font.text_width(msg)//2)-4,
            20-4,
            app.font.text_width(msg)+8,
            11+8,
            7,
            4
        )
        draw_text_shadow(
            (pyxel.width // 2) - (app.font.text_width(msg)//2),
            20,
            msg,
            7,
            custom_font=True
        )

        msg = "Click to START"
        # pyxel.rect(
        #     (pyxel.width // 2) - (app.font.text_width(msg)//2)-2,
        #     180,
        #     app.font.text_width(msg)+4,
        #     11,
        #     1
        # )
        draw_rrect(
            (pyxel.width // 2) - (app.font.text_width(msg)//2)-4,
            180-4,
            app.font.text_width(msg)+8,
            11+8,
            7,
            9
        )
        pyxel.dither(0.5)
        draw_rrect(
            (pyxel.width // 2) - (app.font.text_width(msg)//2)-4,
            180-4,
            app.font.text_width(msg)+8,
            11+8,
            7,
            8
        )
        pyxel.dither(1)
        draw_rrectb(
            (pyxel.width // 2) - (app.font.text_width(msg)//2)-4,
            180-4,
            app.font.text_width(msg)+8,
            11+8,
            7,
            4
        )
        draw_text_shadow(
            (pyxel.width // 2) - (app.font.text_width(msg)//2),
            180,
            msg,
            7,
            custom_font=True
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
        # --------------------
        # Git Hub Icon
        # --------------------
        pyxel.blt(
            88,
            pyxel.height-16-16,
            1,
            0,
            16,
            16,
            16,
            10
        )
