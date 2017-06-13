#sprite classes for ploatform game
import os
import pygame as pg
import random
from time import sleep
from settings import *
vec = pg.math.Vector2

# Player 클래스
class Player(pg.sprite.Sprite):

    def __init__(self, game):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (40, HEIGHT-100)
        self.pos= vec(40, HEIGHT-100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.power = 1


    #시트에 동작별 프레임 단위로 나눠진 이미지 값들을 불러오는 함수
    def load_images(self):
        self.standing_frames = [self.game.stand.get_image(2, 0, 28, 40),
                                self.game.stand.get_image(32, 0, 29, 40),
                                self.game.stand.get_image(62, 0, 28, 40)]
        for frame in self.standing_frames:
            frame.set_colorkey(WHITE)
        self.walk_frame_l = [self.game.move.get_image(0, 0, 30, 40),
                            self.game.move.get_image(30, 0, 30, 40)]
        self.walk_frame_r = []
        for frame in self.walk_frame_l:
            frame.set_colorkey(WHITE)

        for frame in self.walk_frame_l:
            self.walk_frame_r.append(pg.transform.flip(frame, True, False))
        self.jump_frame = self.game.jump.get_image(0, 0, 30, 40)

    def jump(self):
        self.rect.y += 2
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 2
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -PLAYER_JUMP

    #keyup 이벤트 상태일때 player의 y값을 감소 시킴
    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAV)#가속값 -> X는 0이고 Y는 중력이 적용
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        # apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION #X에만 마찰력이 적용됨 (Y는 중력 적용)

        #equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc

        #wrap around the sides of the screen
        if self.pos.x > WIDTH + self.rect.width / 2:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x < 0 - self.rect.width / 2:
            self.pos.x = WIDTH + self.rect.width / 2

        self.rect.midbottom = self.pos

    #이미지 프레임별 애니메이션이 적용되는 함수
    def animate(self):
        now = pg.time.get_ticks() #millisecond 단위로 현재 게임시간을 갖고옴

        #움직임 값(Bollean)에 대한 명세
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        #player가 움직이고 있을 떄(True) 애니메이션
        if self.walking:
            if now - self.last_update > 120: #프레임 속도를 위한 값
                self.last_update = now
                #현재 프레임 값은 계속 1씩 증가하면서 이미지의 프레임 길이만큼 나눠짐
                #즉, 프레임 길이에 따라서 current_frame값이 바뀜
                self.current_frame = (self.current_frame + 1) % len(self.walk_frame_l)
                if self.vel.x > 0: #바뀌는 current_frame 값이 이미지의 프레임을 순회.
                    self.image = self.walk_frame_r[self.current_frame]
                else:
                    self.image = self.walk_frame_l[self.current_frame]

        if self.vel.y != 0:
            self.jumping = True

        #제자리 점프에 대한 애니메이션
        if self.jumping and not self.walking:
            if now - self.last_update > 150:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % 1
                self.image = self.jump_frame
                self.image.set_colorkey(GREEN)

        self.mask = pg.mask.from_surface(self.image) #플레이어 mask

        #가만히 있을때 애니메이션
        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                self.image = self.standing_frames[self.current_frame]

#Menu Slect 클래스
class Select(pg.sprite.Sprite):

    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pg.Surface((120,40))
        self.image.blit(self.game.menu_select, (0, 0))
        self.image.set_alpha(0)
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH - 70, HEIGHT - 340)
        self.select_number = 0

    def update(self):
        self.acc = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            self.select_number -= 1
            if self.select_number < 0:
                self.select_number = 2
            if self.select_number == 0:
                self.rect.center = (WIDTH - 70, HEIGHT - 340)
                sleep(0.14)
            elif self.select_number == 1:
                self.rect.center = (WIDTH - 70, HEIGHT - 290)
                sleep(0.14)
            elif self.select_number == 2:
                self.rect.center = (WIDTH - 70, HEIGHT - 240)
                sleep(0.14)

        if keys[pg.K_DOWN]:
            self.select_number += 1
            if self.select_number > 2:
                self.select_number = 0
            if self.select_number == 0:
                self.rect.center = (WIDTH - 70, HEIGHT - 340)
                sleep(0.14)
            elif self.select_number == 1:
                self.rect.center = (WIDTH - 70, HEIGHT - 290)
                sleep(0.14)
            elif self.select_number == 2:
                self.rect.center = (WIDTH - 70, HEIGHT - 240)
                sleep(0.14)

        if keys[pg.K_z] and self.select_number == 0:
            self.game.openning()

        if keys[pg.K_z] and self.select_number == 1:
            self.game.start_playing = False

        if keys[pg.K_z] and self.select_number == 2:
            pg.quit()
            quit()

#블록 클래스
class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        images = [self.game.block1.get_image(0, 0, 100, 20),
                 self.game.block2.get_image(0, 0, 80, 20),
                 self.game.block3.get_image(0, 0, 50, 20)]
        self.image = random.choice(images)
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if random.randrange(100) < ITEM_SPAWN_PCT:
            Item(self.game, self)
        if random.randrange(100) < HEAD_SPAWN_PCT:
            Rabbithead(self.game, self)

#게임 내 아이템 클래스
class Item(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.type = random.choice(['powerup', 'kill', 'speeddown', 'speedup'])
        self.image = self.game.box.get_image(0, 0, 20, 20)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.plat.rect.topleft
        self.rect.bottom = self.plat.rect.top+1

    def update(self):
        self.rect.bottom = self.plat.rect.top+1
        if not self.game.platforms.has(self.plat): #아이템 중복검사
            self.kill()

#토끼 머리 클래스
class Rabbithead(pg.sprite.Sprite):
    def __init__(self, game, plat):
        self.groups = game.all_sprites, game.heads
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.plat = plat
        self.image = self.game.head.get_image(0, 0, 30, 30)
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom = self.plat.rect.top+1

    def update(self):
        self.rect.bottom = self.plat.rect.top+1
        if not self.game.platforms.has(self.plat): #아이템 중복검사
            self.kill()

#적 클래스
class Enemy(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.current_frame = 0
        self.last_update = 0
        self.load_date()
        self.max_speed_x = self.game.speed_x
        self.max_speed_y = self.game.speed_y
        self.min_speed_x = self.game.speed_x_min
        self.min_speed_y = self.game.speed_y_min
        self.image = self.meteo_frames[0]
        self.rect = self.image.get_rect()
        #Enemy 객체가 생성되는 x,y 값은 랜덤하게 생성됨
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        #Enemy의 각 객체별로 상이한 속도를 갖고 있음.
        self.speedx = random.randrange(self.min_speed_x, self.max_speed_x)
        self.speedy = random.randrange(self.min_speed_y, self.max_speed_y)

    def load_date(self):
        self.meteo_frames = [self.game.enemy.get_image(0, 0, 30, 40),
                             self.game.enemy.get_image(30, 0, 30, 40),
                             self.game.enemy.get_image(60, 0, 30, 40),
                             self.game.enemy.get_image(90, 0, 30, 40)]
        for frames in self.meteo_frames:
            frames.set_colorkey(BLACK)

    def update(self):
        self.animate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        #객체가 바닥을 지나거나, 왼쪽 또는 오른쪽 화면을 넘어 갔을시
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedx = random.randrange(-3, 3)
            self.speedy = random.randrange(1, 5)
        self.mask = pg.mask.from_surface(self.image) #적 mask

    def animate(self):
        now = pg.time.get_ticks() #millisecond 단위로 현재 게임시간을 갖고옴

        if now - self.last_update > 120: #프레임 속도를 위한 값
            self.last_update = now
            #현재 프레임 값은 계속 1씩 증가하면서 이미지의 프레임 길이만큼 나눠짐
            #즉, 프레임 길이에 따라서 current_frame값이 바뀜
            self.current_frame = (self.current_frame + 1) % len(self.meteo_frames)
            self.image = self.meteo_frames[self.current_frame]

#폭발 클래스
class Explosion(pg.sprite.Sprite):
    def __init__(self, game, center):
        self.groups = game.all_sprites, game.explo
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.load_date()
        self.image = self.explosion_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.current_frame = 0
        self.last_update = 0

    def load_date(self):
        self.explosion_frames = [self.game.explosion2.get_image(2, 0, 46, 50),
                                 self.game.explosion2.get_image(52, 0, 47, 50),
                                 self.game.explosion2.get_image(102, 0, 47, 50),
                                 self.game.explosion2.get_image(152, 0, 47, 50),
                                 self.game.explosion2.get_image(202, 0, 47, 50)]
        for frames in self.explosion_frames:
            frames.set_colorkey(BROWN)

    def update(self):
        now = pg.time.get_ticks() #millisecond 단위로 현재 게임시간을 갖고옴

        if now - self.last_update > 120: #프레임 속도를 위한 값
            self.last_update = now
            #현재 프레임 값은 계속 1씩 증가하면서 이미지의 프레임 길이만큼 나눠짐
            #즉, 프레임 길이에 따라서 current_frame값이 바뀜
            self.current_frame = (self.current_frame + 1) % len(self.explosion_frames)
            self.image = self.explosion_frames[self.current_frame]
            if self.current_frame == 4:
                self.kill()

#총알 클래스
class Bullet(pg.sprite.Sprite):
    def __init__(self, game, x , y):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = self.game.bullet.get_image(0, 0, 11, 20)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        #총알 객체는 현재 player객체의 위치를 기준으로 생성 됨,
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

#이미지 sheet 및 이미지 로드를 위한 클래스
class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

        """The returned Surface will contain the same color format,
        colorkey and alpha transparency as the file it came from.
        You will often want to call Surface.convert() with no arguments,
        to create a copy that will draw more quickly on the screen."""

    #불러온 이미지(self.spritesheet)를  (0,0)에 불러오며, 이미지의(x,y)부터 (width, height)까지 자르겠다.
    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0,0), (x, y, width, height))
        return image
