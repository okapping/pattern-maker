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

    FRAME = [31, 41, 194, 174]
    NEW_BTN = (204, 4, 40, 16)

    COL = 4
    MARGIN = 8
    SIZE = 40

    SCRL_TOP_BTN = [228, 80, 24, 48]
    SCRL_BOTTOM_BTN = [228, 140, 24, 48]

    def __init__(self, app):
        self.app = app
        self.canvases = None

        self.scroll_y = 0

        self.load_data()
        # self.debug()
    
    def debug(self):
        for i in range(20):
            new_canvas = self.create_canvas()
            new_id = str(uuid.uuid4())
            new_data = {
                "id": new_id,
                "canvas": new_canvas
            }
            self.canvases.append(deepcopy(new_data))


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
        """

        for data in self.canvases:
            if id != data["id"]:
                continue
            data["canvas"] = deepcopy(canvas)
            self.save_data()
            return
        
        # idが存在しない場合は新規保存する
        new_pattern = {
            "id": id,
            "canvas": deepcopy(canvas)
        }
        self.canvases.append(new_pattern)
        self.save_data()
        
        return

    def update(self):
        app = self.app

        # スクロールボタン押下
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            x, y, w, h = self.SCRL_TOP_BTN
            if (
                x <= pyxel.mouse_x < x+w
                and y <= pyxel.mouse_y < y+h
            ):
                self.scroll_y = min(self.scroll_y+8, 0)
                return

            x, y, w, h = self.SCRL_BOTTOM_BTN
            if (
                x <= pyxel.mouse_x < x+w
                and y <= pyxel.mouse_y < y+h
            ):
                columns = self.COL
                margin = self.MARGIN
                size = self.SIZE

                cnt = len(self.canvases)
                cols = pyxel.ceil(cnt/columns)
                if (cols*size+cols*margin) < self.FRAME[3]:
                    return
                limit = (cols*size+cols*margin)-self.FRAME[3]+4  # 微調整の「＋４」！！
                self.scroll_y = max(self.scroll_y-8, -limit)
                return

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
                # self.canvases.append(deepcopy(new_data))
                app.screens[app.SCREEN_EDITOR] = EditorScreen(
                    app,
                    self,
                    new_data["id"],
                    new_data["canvas"]
                )
                app.change_screen(app.SCREEN_EDITOR)
                return
        
        # --------------------
        # パターンをクリック
        # --------------------
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            columns = self.COL
            margin = self.MARGIN
            size = self.SIZE
            # for i, canvas in enumerate(self.canvases.copy()):
            for i in range(len(self.canvases) - 1, -1, -1):
                canvas = self.canvases[i]
                loop_index = len(self.canvases)-1-i
                x = 36+(loop_index % columns) * size + ((loop_index % columns) * margin)
                y = self.scroll_y+45+(loop_index // columns) * size + ((loop_index // columns) * margin)
                if (
                    x <= pyxel.mouse_x < x+size
                    and  y <= pyxel.mouse_y < y+size
                ):
                    if pyxel.btn(pyxel.KEY_CTRL):
                        self.canvases.remove(canvas)
                        self.save_data()
                        return
                    else:
                        # 編集画面へは、コピーを渡す
                        copy_canvas = deepcopy(canvas)
                        app.screens[app.SCREEN_EDITOR] = EditorScreen(
                            app,
                            self,
                            copy_canvas["id"],
                            copy_canvas["canvas"]
                        )
                        app.change_screen(app.SCREEN_EDITOR)
                        return



    
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
        # ヘッダー
        self.draw_header()
        # 新規ボタン
        self.draw_new_btn()
        # キャンバスたちを表示する枠
        self.draw_frame()
        # キャンバス一覧
        self.draw_cavases()
        # pyxel.rectb(
        #     *self.FRAME,
        #     pyxel.rndi(1, 15)
        # )

        # スクロールボタン
        self.draw_scroll()
        
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

    def draw_frame(self):
        """
        キャンバス一覧を表示する額縁を描く
        """

        cols = [4, 9, 10, 7]
        w, h, = 220, 200
        r = 10
        for i in range(4):
            draw_rrect(
                (pyxel.width//2)-(w//2),
                (pyxel.height//2)-(h//2),
                w,
                h,
                r,
                cols[i]
            )
            draw_rrectb(
                (pyxel.width//2)-(w//2),
                (pyxel.height//2)-(h//2),
                w,
                h,
                r,
                1
            )
            # pyxel.rect(
            #     (pyxel.width//2)-(w//2),
            #     (pyxel.height//2)-(h//2),
            #     w,
            #     h,
            #     cols[i]
            # )
            # pyxel.rectb(
            #     (pyxel.width//2)-(w//2),
            #     (pyxel.height//2)-(h//2),
            #     w,
            #     h,
            #     1
            # )
            w -= 6+i*2
            h -= 6+i*2
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
        # columns = 4  # 4行
        # margin = 8
        # size = 40
        columns = self.COL  # 4行
        margin = self.MARGIN
        size = self.SIZE
        pyxel.clip(*self.FRAME)

        # for i, canvas in enumerate(self.canvases):
        for i in range(len(self.canvases) - 1, -1, -1):
            canvas = self.canvases[i]
            loop_index = len(self.canvases)-1-i

            x = 36+(loop_index % columns) * size + ((loop_index % columns) * margin)
            y = self.scroll_y+45+(loop_index // columns) * size + ((loop_index // columns) * margin)
            pyxel.rect(
                x+2,
                y+2,
                size+2,
                size+2,
                1
            )
            pyxel.rect(
                x-1,
                y-1,
                42,
                42,
                0
            )
            self.draw_pattern(x, y, canvas["canvas"])
            if pyxel.btn(pyxel.KEY_CTRL):
                pyxel.circ(
                    x+20,
                    y+20,
                    13,
                    0,
                )
                pyxel.circb(
                    x+20,
                    y+20,
                    13,
                    7,
                )
                pyxel.blt(
                    x+13,
                    y+13,
                    0,
                    96,
                    16,
                    15,
                    16,
                    0
                )

        pyxel.clip()
            
    
    def draw_pattern(self, x, y, canvas):
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

    def draw_scroll(self):
        # 上向のボタン
        pyxel.rect(
            self.SCRL_TOP_BTN[0],
            self.SCRL_TOP_BTN[1],
            self.SCRL_TOP_BTN[2],
            self.SCRL_TOP_BTN[3],
            3,
        )
        pyxel.rectb(
            self.SCRL_TOP_BTN[0],
            self.SCRL_TOP_BTN[1],
            self.SCRL_TOP_BTN[2],
            self.SCRL_TOP_BTN[3],
            0,
        )
        pyxel.blt(
            self.SCRL_TOP_BTN[0]+4,
            self.SCRL_TOP_BTN[1]+16,
            0,
            112,
            16,
            16,
            16,
            0
        )

        # 下向のボタン
        pyxel.rect(
            self.SCRL_BOTTOM_BTN[0],
            self.SCRL_BOTTOM_BTN[1],
            self.SCRL_BOTTOM_BTN[2],
            self.SCRL_BOTTOM_BTN[3],
            3,
        )
        pyxel.rectb(
            self.SCRL_BOTTOM_BTN[0],
            self.SCRL_BOTTOM_BTN[1],
            self.SCRL_BOTTOM_BTN[2],
            self.SCRL_BOTTOM_BTN[3],
            0,
        )
        pyxel.blt(
            self.SCRL_BOTTOM_BTN[0]+4,
            self.SCRL_BOTTOM_BTN[1]+16,
            0,
            112,
            16,
            16,
            16,
            0,
            rotate=180
        )