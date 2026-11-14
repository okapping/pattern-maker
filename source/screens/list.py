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

min_size = 8
max_size = 48

class ListScreen:

    FRAME = [31, 41, 194, 174]
    NEW_BTN = (204, 4, 40, 16)

    COL = 4
    MARGIN = 8
    SIZE = 40

    SCRL_TOP_BTN = [228, 80, 24, 48]
    SCRL_BOTTOM_BTN = [228, 140, 24, 48]

    INIT_X_SIZE_LABEL = [90, 80]
    INIT_X_PLUS_BTN = [130, 80, 32, 32]
    INIT_X_MINUS_BTN = [170, 80, 32, 32]
    INIT_Y_SIZE_LABEL = [90, 130]
    INIT_Y_PLUS_BTN = [130, 130, 32, 32]
    INIT_Y_MINUS_BTN = [170, 130, 32, 32]

    INIT_CANCEL_BTN = [60, 176, 64, 32]
    INIT_CREATE_BTN = [130, 176, 64, 32]

    def __init__(self, app):
        self.app = app
        self.canvases = None

        self.scroll_y = 0

        self.show_init = False
        self.new_canvas_x = 16
        self.new_canvas_y = 16

        self.reset_init()
        self.load_data()
    
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

    def get_canvas(self, id):
        """
        idからキャンバスを取得する
        取得できなかった場合はNoneを返す
        """
        for data in self.canvases:
            if id != data["id"]:
                continue
            
            return data["canvas"]

        return None

    def create_new_canvas(self):
        # キャンバスの初期化
        app = self.app
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

    def reset_init(self):
        self.show_init = False
        self.new_canvas_x = 16
        self.new_canvas_y = 16

    def update(self):
        app = self.app

        # NEWボタンが押されているかによって分岐する
        if self.show_init:
            # X軸＋ボタン
            if click_btnp(*self.INIT_X_PLUS_BTN, long_click=True):
                self.new_canvas_x = min(self.new_canvas_x + 1, max_size)
            # X軸ーボタン
            if click_btnp(*self.INIT_X_MINUS_BTN, long_click=True):
                self.new_canvas_x = max(min_size, self.new_canvas_x - 1)
            # Y軸＋ボタン
            if click_btnp(*self.INIT_Y_PLUS_BTN, long_click=True):
                self.new_canvas_y = min(self.new_canvas_y + 1, max_size)
            # Y軸ーボタン
            if click_btnp(*self.INIT_Y_MINUS_BTN, long_click=True):
                self.new_canvas_y = max(min_size, self.new_canvas_y - 1)
            # 作成ボタン押下
            if click_btnp(*self.INIT_CREATE_BTN):
                self.create_new_canvas()
                self.reset_init()
            # キャンセルボタン押下
            if click_btnp(*self.INIT_CANCEL_BTN):
                self.reset_init()

        else:
            # スクロールボタン押下
            if click_btnp(*self.SCRL_TOP_BTN):
                self.scroll_y = min(self.scroll_y+8, 0)
                return

            if click_btnp(*self.SCRL_BOTTOM_BTN):
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
                
            # if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                # x, y, w, h = self.SCRL_TOP_BTN
                # if (
                #     x <= pyxel.mouse_x < x+w
                #     and y <= pyxel.mouse_y < y+h
                # ):
                #     self.scroll_y = min(self.scroll_y+8, 0)
                #     return

                # x, y, w, h = self.SCRL_BOTTOM_BTN
                # if (
                #     x <= pyxel.mouse_x < x+w
                #     and y <= pyxel.mouse_y < y+h
                # ):
                #     columns = self.COL
                #     margin = self.MARGIN
                #     size = self.SIZE

                #     cnt = len(self.canvases)
                #     cols = pyxel.ceil(cnt/columns)
                #     if (cols*size+cols*margin) < self.FRAME[3]:
                #         return
                #     limit = (cols*size+cols*margin)-self.FRAME[3]+4  # 微調整の「＋４」！！
                #     self.scroll_y = max(self.scroll_y-8, -limit)
                #     return

            # --------------------
            # 「NEW」ボタン押下
            # --------------------

            if click_btnp(*self.NEW_BTN):
                self.show_init = True
                # return            

            # if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            #     x, y, w, h = self.NEW_BTN
            #     if (
            #         x <= pyxel.mouse_x < x+w
            #         and y <= pyxel.mouse_y < y+h
            #     ):
            # --------------------
            # パターンをクリック
            # --------------------
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                columns = self.COL
                margin = self.MARGIN
                size = self.SIZE
                for i in range(len(self.canvases) - 1, -1, -1):
                    loop_index = len(self.canvases)-1-i
                    canvas = self.canvases[i]
                    size_x = len(canvas["canvas"][0])
                    size_y = len(canvas["canvas"])
                    disp_size_x, disp_size_y = self.get_disp_size(size_x, size_y)

                    x = 36+(loop_index % columns) * size + ((loop_index % columns) * margin)
                    y = self.scroll_y+45+(loop_index // columns) * size + ((loop_index // columns) * margin)
                    y += (self.SIZE-disp_size_y)//2
                    x += (self.SIZE-disp_size_x)//2

                    if (
                        x <= pyxel.mouse_x < x+disp_size_x
                        and  y <= pyxel.mouse_y < y+disp_size_y
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
            [0 for _ in range(self.new_canvas_x)]
            for _ in range(self.new_canvas_y)
        ]
        return new_canvas

    def draw(self):
        pyxel.cls(0)
        # 背景
        self.draw_background()
        # ヘッダー
        self.draw_header()
        # 新規ボタン
        self.draw_new_btn()
        # キャンバスたちを表示する枠
        self.draw_frame()
        if self.show_init:
            # 初期設定画面
            self.draw_init()
        else:
            # キャンバス一覧
            self.draw_cavases()
            # スクロールボタン
            self.draw_scroll()
        # pyxel.rectb(
        #     *self.FRAME,
        #     pyxel.rndi(1, 15)
        # )

    def draw_number(self, n, x, y):
        w, h = 16, 32
        s = f"{n:02d}"

        for i in range(2):
            pyxel.blt(
                x+w*i,
                y,
                0,
                int(s[i])*16,
                96,
                w,
                h,
                7
            )

    def draw_init(self):
        def btn(x, y, w, h, is_plus):
            u, v = (128, 16) if is_plus else (144, 16)
            r = 1
            col = 8 if is_plus else 12
            draw_rrect(x,y,w,h,r,10)
            draw_rrectb(x,y,w,h,r,0)
            draw_rrectb(x+1,y+1,w-2,h-2,r-1,0)
            pyxel.blt(
                x+8,
                y+8,
                0,
                u,
                v,
                16,
                16,
                7
            )
        # --------------------
        # サブタイトル
        # 文字を順番に動かす！
        # --------------------
        t = "size select"
        x = pyxel.width//2-self.app.font.text_width(t)//2
        y = 50
        f = pyxel.frame_count//2%(len(t)+12)
        for i, s in enumerate(t):
            draw_text_shadow(
                x,
                y if i != f else y-2,
                s,
                3,
                custom_font=True
            )
            x += self.app.font.text_width(s)

        # --------------------
        # ↔︎
        # --------------------
        pyxel.tri(
            52, 84,
            56, 80,
            56, 88,
            1
        )
        pyxel.tri(
            75, 84,
            71, 80,
            71, 88,
            1
        )
        for i in range(-1, 2):
            pyxel.line(
                56, 84+i,
                71, 84+i,
                1
            )
        x = 52
        y = 92
        for i in range(3):
            for j in range(3):
                pyxel.rect(
                    x+(8*j),
                    y+(8*i),
                    8,
                    8,
                    5 if (i+j)%2==0 else 6
                )

        pyxel.rectb(
            x,
            y,
            24,
            24,
            0
        )
        # --------------------
        # ↕︎
        # --------------------
        pyxel.tri(
            48, 134,
            44, 138,
            52, 138,
            1
        )
        pyxel.tri(
            48, 157,
            44, 153,
            52, 153,
            1
        )
        for i in range(-1, 2):
            pyxel.line(
                48+i, 138,
                48+i, 153,
                1
            )
        x = 58
        y = 134
        for i in range(3):
            for j in range(3):
                pyxel.rect(
                    x+(8*j),
                    y+(8*i),
                    8,
                    8,
                    5 if (i+j)%2==0 else 6
                )

        pyxel.rectb(
            x,
            y,
            24,
            24,
            0
        )

        # --------------------
        # X軸
        # --------------------
        self.draw_number(
            self.new_canvas_x,
            self.INIT_X_SIZE_LABEL[0],
            self.INIT_X_SIZE_LABEL[1]
        )
        plus = (128, 16)
        minus = (144, 16)
        # --------------------
        # ＋ボタン
        btn(*self.INIT_X_PLUS_BTN, True)
        # --------------------
        # ーボタン
        btn(*self.INIT_X_MINUS_BTN, False)
        # --------------------
        # Y軸
        # --------------------
        self.draw_number(
            self.new_canvas_y,
            self.INIT_Y_SIZE_LABEL[0],
            self.INIT_Y_SIZE_LABEL[1]
        )
        # --------------------
        # ＋ボタン
        btn(*self.INIT_Y_PLUS_BTN, True)
        # --------------------
        # ーボタン
        btn(*self.INIT_Y_MINUS_BTN, False)

        # キャンセルボタン
        draw_rrect(
            self.INIT_CANCEL_BTN[0],
            self.INIT_CANCEL_BTN[1],
            self.INIT_CANCEL_BTN[2],
            self.INIT_CANCEL_BTN[3],
            7,
            10
        )
        draw_text_shadow(
            self.INIT_CANCEL_BTN[0]+15,
            self.INIT_CANCEL_BTN[1]+10,
            "BACK",
            8,
            custom_font=True
        )
        # 作成ボタン
        draw_rrect(
            self.INIT_CREATE_BTN[0],
            self.INIT_CREATE_BTN[1],
            self.INIT_CREATE_BTN[2],
            self.INIT_CREATE_BTN[3],
            7,
            10
        )
        draw_text_shadow(
            self.INIT_CREATE_BTN[0]+7,
            self.INIT_CREATE_BTN[1]+10,
            "CREATE",
            5,
            custom_font=True
        )
        # pyxel.rectb(
        #     self.INIT_CREATE_BTN[0],
        #     self.INIT_CREATE_BTN[1],
        #     self.INIT_CREATE_BTN[2],
        #     self.INIT_CREATE_BTN[3],
        #     0
        # )
        
    def draw_background(self):
        pyxel.cls(5)

        if self.show_init:
            return
        # マウスを並ぶパレットにホバーした場合、
        # そのキャンバスを背景に表示する
        hover_canvas = None

        columns = self.COL
        margin = self.MARGIN
        size = self.SIZE
        for i in range(len(self.canvases) - 1, -1, -1):
            loop_index = len(self.canvases)-1-i
            canvas = self.canvases[i]["canvas"]
            size_x = len(canvas[0])
            size_y = len(canvas)
            disp_size_x, disp_size_y = self.get_disp_size(size_x, size_y)

            x = 36+(loop_index % columns) * size + ((loop_index % columns) * margin)
            y = self.scroll_y+45+(loop_index // columns) * size + ((loop_index // columns) * margin)
            x += (self.SIZE-disp_size_x)//2
            y += (self.SIZE-disp_size_y)//2

            if (
                x <= pyxel.mouse_x < x+disp_size_x
                and  y <= pyxel.mouse_y < y+disp_size_y
            ):
                hover_canvas = canvas
        
        if hover_canvas is not None:
            # キャンバスの描画
            size_x = len(hover_canvas[0])
            size_y = len(hover_canvas)

            # 移動分を算出
            move_x = -pyxel.frame_count//2%size_x
            move_y = -pyxel.frame_count//2%size_y

            tile_count_x = (
                pyxel.width // size_x
            )

            tile_count_y = (
                pyxel.height // size_y
            )

            for tile_y in range(-1, tile_count_y):
                for tile_x in range(-1, tile_count_x):
                    tile_left = tile_x * size_x + move_x
                    tile_top = tile_y * size_y + move_y

                    for y in range(size_y):
                        for x in range(size_x):
                            color = hover_canvas[y][x]

                            pyxel.pset(
                                tile_left + x,
                                tile_top + y,
                                color,
                            )

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
            custom_font=True
        )

    def draw_cavases(self):
        # columns = 4  # 4行
        # margin = 8
        # size = 40
        columns = self.COL  # 4行
        margin = self.MARGIN
        size = self.SIZE
        pyxel.clip(*self.FRAME)

        for i in range(len(self.canvases) - 1, -1, -1):
            canvas = self.canvases[i]
            loop_index = len(self.canvases)-1-i

            x = 36+(loop_index % columns) * size + ((loop_index % columns) * margin)
            y = self.scroll_y+45+(loop_index // columns) * size + ((loop_index // columns) * margin)

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
            
    def get_disp_size(self, x, y):
        """
        パターンのサイズをもとに
        実際に表示されるサイズを算出する
        """
        max_size = self.SIZE
        if x < y:
            disp_size_x = int(max_size * (x / y))
            disp_size_y = max_size
        elif x > y:
            disp_size_x = max_size
            disp_size_y = int(max_size * (y / x))
        else:
            disp_size_x = max_size
            disp_size_y = max_size
        return disp_size_x, disp_size_y

    def draw_pattern(self, x, y, canvas):
        """
        パターンの一つを表示する
        """
        # サイズを取得
        size_x = len(canvas[0])
        size_y = len(canvas)

        # サイズに合わせて表示サイズを設定
        disp_size_x, disp_size_y = self.get_disp_size(size_x, size_y)

        # パターンの比率に合わせて表示位置の調整
        x += (self.SIZE-disp_size_x)//2
        y += (self.SIZE-disp_size_y)//2
        
        # 影の描画
        pyxel.rect(
            x+2,
            y+2,
            disp_size_x+2,
            disp_size_y+2,
            1
        )
        # 枠の描画
        pyxel.rect(
            x-1,
            y-1,
            disp_size_x+2,
            disp_size_y+2,
            0
        )

        # パターンの描画
        for dy in range(disp_size_y):
            for dx in range(disp_size_x):
                # 拡大後の座標から、元画像の座標を求める
                src_x = int(dx * size_x / disp_size_x)
                src_y = int(dy * size_y / disp_size_y)

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