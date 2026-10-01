import pyxel
import json
import uuid

from js import window
from copy import deepcopy

from .editor import EditorScreen
from utils import *

""" sample data
data_list = [
    {
        "id": 12345,
        "name": "hogehoge",　　# 未実装
        "canvas": []
    },
    {
        "id": 67890,
        "name": "fugafuga",　　# 未実装
        "canvas": [
            [0, 1, 2],
            [3, 4, 5]
        ]
    }
]
"""

class ListScreen:

    NEW_BTN = (204, 4, 40, 16)

    def __init__(self, app):
        self.app = app
        self.canvases = None


        self.load_data()

    def save_data(self):
        json_data = json.dumps(self.canvases)
        window.localStorage.setItem("canvases", json_data)

    def load_data(self):
        # ↓ローカルストレージの削除処理
        # window.localStorage.removeItem("canvases")
        json_data = window.localStorage.getItem("canvases")
        print(f"json_ata: {json_data}")
        if json_data is None or str(json_data) == "jsnull":
            self.canvases = []
            self.save_data()
            return

        self.canvases = json.loads(str(json_data))

    def save_canvas(self, id, canvas):
        """
        エディター画面から更新用のidとキャンバスを受け取り、
        該当のキャンバスの内容を修正する。

        戻り値として、ステータスを返す。
        成功時＝"SAVED"
        失敗時時＝"FAILED"
        """
        for data in self.canvases:
            if id != data["id"]:
                continue
            data["canvas"] = deepcopy(canvas)
            self.save_data()
            return "SAVED"
        return "ERROR!"
    def update(self):
        app = self.app

        # --------------------
        # 「NEW」ボタン押下
        # --------------------

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            x, y, w, h = self.NEW_BTN
            if (
                x <= pyxel.mouse_x < x+w
                and y <= pyxel.mouse_y < y+h
            ):
                # キャンバスの初期化
                new_canvas = self.create_canvas()
                new_id = str(uuid.uuid4())
                new_data = {
                    "id": new_id,
                    "canvas": new_canvas
                }
                # コピをキャンバスへ渡し、勝手に同期しないようにする
                self.canvases.append(deepcopy(new_data))
                app.screens[app.SCREEN_EDITOR] = EditorScreen(
                    app,
                    self,
                    new_data["id"],
                    new_data["canvas"]
                )
                app.change_screen(app.SCREEN_EDITOR)
    
    def create_canvas(self):
        """
        キャンバスを黒で初期化する。
        """

        size = 16

        new_canvas = [
            [0 for _ in range(size)]
            for _ in range(size)
        ]
        return new_canvas

    def draw(self):
        pyxel.cls(5)
        pyxel.text(0, 0, f"canvases_cnt: {len(self.canvases)}",7)
        # ヘッダー
        self.draw_header()
        # 新規ボタン
        self.draw_new_btn()
        # キャンバスたちを表示する枠
        self.draw_frame()
        # キャンバス一覧
        self.draw_cavases()
        
        # columns = 4  # 4行
        # for i, canvas in enumerate(self.canvases):
        #     x = 100 + (i % columns) * 16
        #     y = 100 + (i // columns) * 16
        #     self.draw_canvas(x, y, canvas["canvas"])

    def draw_header(self):
        """
        ヘッダー
        """
        s = "Pattarn Maker"
        draw_text_shadow(
            (pyxel.width // 2) - (self.app.font.text_width(s) // 2),
            8,
            s,
            7,
            custom_font=True
        )
        # pyxel.text(
        # )
    def draw_frame(self):
        """
        キャンバス一覧を表示する額縁を描く
        """

        cols = [4, 9, 10, 7]
        w, h, = 220, 200
        r = 10
        for i in range(4):
            # draw_rrect(
            #     (pyxel.width//2)-(w//2),
            #     (pyxel.height//2)-(h//2),
            #     w,
            #     h,
            #     r,
            #     cols[i]
            # )
            # draw_rrectb(
            #     (pyxel.width//2)-(w//2),
            #     (pyxel.height//2)-(h//2),
            #     w,
            #     h,
            #     r,
            #     1
            # )
            pyxel.rect(
                (pyxel.width//2)-(w//2),
                (pyxel.height//2)-(h//2),
                w,
                h,
                cols[i]
            )
            pyxel.rectb(
                (pyxel.width//2)-(w//2),
                (pyxel.height//2)-(h//2),
                w,
                h,
                1
            )
            w -= 8
            h -= 8
            r -= 3

    def draw_new_btn(self):

        pyxel.rect(
            self.NEW_BTN[0],
            self.NEW_BTN[1],
            self.NEW_BTN[2],
            self.NEW_BTN[3],
            3
        )
        s = "NEW"
        draw_text_shadow(
            self.NEW_BTN[0]+4,
            self.NEW_BTN[1]+3,
            s,
            7,
            self.app.font
        )

    def draw_cavases(self):
        columns = 4  # 4行
        margin = 8
        size = 40
        for i, canvas in enumerate(self.canvases):
            x = 36+(i % columns) * size + ((i % columns) * margin)
            y = 45+(i // columns) * size + ((i // columns) * margin)
            pyxel.rect(
                x+3,
                y+3,
                size,
                size,
                1
            )
            self.draw_canvas(x, y, canvas["canvas"])
            
    
    def draw_canvas(self, x, y, canvas):
        src_height = len(canvas)
        src_width = len(canvas[0])
        # 拡大後の40×40ピクセルを1ピクセルずつ描画
        display_size = 40
        for dy in range(display_size):
            for dx in range(display_size):
                # 拡大後の座標から、元画像の座標を求める
                src_x = int(dx * src_width / display_size)
                src_y = int(dy * src_height / display_size)

                color = canvas[src_y][src_x]
                pyxel.pset(x + dx, y + dy, color)
