import math
import random
import sys
import time

import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 2  # 爆弾の数


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとん，または，爆弾SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        img0 = pg.transform.rotozoom(pg.image.load(f"ex03/fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
        self.imgs = {  # 0度から反時計回りに定義
            (+5, 0): img,  # 右
            (+5, -5): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -5): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-5, -5): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-5, 0): img0,  # 左
            (-5, +5): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +5): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+5, +5): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.img = self.imgs[(+5, 0)]
        self.rct = self.img.get_rect()
        self.rct.center = xy

        self.dire = [+5, 0]

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"ex03/fig/{num}.png"), 0, 2.0)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = self.imgs[tuple(sum_mv)]

        if sum_mv != [0, 0]:
            self.dire = [sum_mv[0], sum_mv[1]]

        screen.blit(self.img, self.rct)


class Beam:
    def __init__(self, bird: Bird):
        """
        ビームSurfaceを生成する
        引数1 xy：こうかとんのインスタンス
        """
        img = pg.image.load(f"ex03/fig/beam.png")
        self.vx, self.vy = bird.dire[0], bird.dire[1]
        theta = math.atan2(-self.vy, self.vx)
        angle = math.degrees(theta)
        self.img = pg.transform.rotozoom(img, angle, 1.0)
        self.rct = self.img.get_rect()

        self.rct.centerx = bird.rct.centerx + bird.rct.width*self.vx/5
        self.rct.centery = bird.rct.centery + bird.rct.height*self.vy/5

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self):
        """
        ランダムなサイズ・位置・色の爆弾円Surfaceを生成する
        """
        colors = [(r, g, b) for r in [0, 255] for g in [0, 255] for b in [0, 255]]
        directions = [-5, +5]

        rad = random.randint(10, 50)
        color = random.choice(colors)
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx = random.choice(directions)
        self.vy = random.choice(directions)

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("ex03/fig/pg_bg.jpg")
    bird = Bird(3, (900, 400))
    bombs = [Bomb() for _ in range(NUM_OF_BOMBS)]
    beams: [Beam] = []
    explosions: [Explosion] = []
    score = Score()

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.append(Beam(bird))

        screen.blit(bg_img, [0, 0])

        for i, bomb in enumerate(bombs):
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(1)
                return

            for j, beam in enumerate (beams):
                if beam.rct.colliderect(bomb.rct):
                    # beamとbombを消す
                    bombs[i] = None
                    beams[j] = None

                    # explosionを生成
                    explosions.append(Explosion(bomb))

                    # こうかとん画像を喜ぶ画像に切り替える
                    bird.change_img(6, screen)
                    pg.display.update()

                    # 1点獲得
                    score.gain_points(100)

                elif beam.rct.right > screen.get_width():
                    beams[j] = None

            beams = [beam for beam in beams if beam is not None]

        bombs = [bomb for bomb in bombs if bomb is not None]
        explosions = [explosion for explosion in explosions if explosion is not None]

        key_lst = pg.key.get_pressed()

        bird.update(key_lst, screen)

        for bomb in bombs:
            bomb.update(screen)

        for beam in beams:
            beam.update(screen)

        for i, explosion in enumerate(explosions):
            explosion.update(screen)
            if explosion.life <= 0:
                explosions[i] = None

        score.update(screen)

        pg.display.update()
        tmr += 1
        clock.tick(50)


class Explosion:
    def __init__(self, bomb: Bomb):
        explosion_img = pg.image.load("ex03/fig/explosion.gif")

        self._img_list = [
            pg.transform.flip(explosion_img, False, False),
            pg.transform.flip(explosion_img, False, True),
            pg.transform.flip(explosion_img, True, False),
            pg.transform.flip(explosion_img, True, True)
        ]

        self._img_index = 0
        self.img = self._get_img()

        self.rct = self.img.get_rect()
        self.rct.center = bomb.rct.center

        self._change_img_interval = 10
        self.life = len(self._img_list) * self._change_img_interval

    def update(self, screen: pg.Surface):
        self.life -= 1
        if self.life % self._change_img_interval == 0:
            self._next_img()

        screen.blit(self.img, self.rct)

    def _next_img(self):
        """
        画像を切り替える
        """
        self._img_index += 1
        img_list_last_index = len(self._img_list) - 1
        if (self._img_index > img_list_last_index):
            self._img_index = img_list_last_index
        self.img = self._get_img()

    def _get_img(self) -> pg.Surface:
        """
        現在の画像を返す
        """
        return self._img_list[self._img_index]


class Score:
    def __init__(self):
        self._score = 0

        self.font = pg.font.SysFont("hgp創英角ポップ体", 30)
        self._font_color = (0, 0, 255)
        self.img = self.font.render(f"Score: {self._score}", 0, self._font_color)
        self.rct = self.img.get_rect()
        display_bottom = pg.display.get_surface().get_height()
        self.rct.center = 100, display_bottom - 50

    def gain_points(self, points: int):
        self._score += points

    def update(self, screen: pg.Surface):
        self.img = self.font.render(f"Score: {self._score}", 0, self._font_color)
        self.rct = self.img.get_rect()
        screen.blit(self.img, self.rct)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
