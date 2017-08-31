import os
import random
# import pyglet
import pygame as pg
import time
from time import sleep
from settings import *
from sprites import *
from moviepy.editor import VideoFileClip
vec = pg.math.Vector2


class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True #게임 실행 Boolean 값
        self.selecting = True
        self.font_name = pg.font.match_font(FONT_NAME) #FONT_NMAE과 맞는 폰트를 검색
        self.font_dir = os.path.dirname(__file__)
        fnt_dir = os.path.join(self.font_dir, 'font')
        self.brankovic_font = os.path.join(fnt_dir, 'brankovic.ttf')
        self.frame_count = 0
        self.clear = False
        self.start = True
        self.ending = False
        self.load_date()

    def new(self):
        # start a new game
        self.score = 0
        self.head_count = 14
        self.enemy_level = 0
        self.speed_x = 4
        self.speed_y = 5
        self.speed_x_min = -2
        self.speed_y_min = 2
        self.all_sprites = pg.sprite.Group()
        self.explo = pg.sprite.Group()
        self.enemys = pg.sprite.Group() #적 sprite 그룹 생성
        self.bullets = pg.sprite.Group() # 총알 sprite 그룹 생성
        self.platforms = pg.sprite.Group() #platforms(블록) sprites 그룹 생성
        self.player = Player(self) #self.player, Player객체 생성
        self.items = pg.sprite.Group()
        self.heads = pg.sprite.Group()
        self.start_tick = pg.time.get_ticks()
        #PLATFORM_LIST에서 각 value값을 받아와 객체 생성
        for plat in PLATFORM_LIST:
            Platform(self, *plat) #python에서 *은 point가 아닌 리스트 언패킹
        pg.mixer.music.load(os.path.join(self.snd_dir, 'old city theme.mp3')) #배경음 로드
        with open(os.path.join(self.dir, SCORE), 'r') as f:
            try :
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        self.run()

    def run(self):
        #game loop
        pg.mixer.music.play(loops=-1) #배경음 플레이 (loops 값 false = 반복, true = 한번)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500) #배경음이 갑자기 꺼지지 않고 점점 꺼지게 함

    def update(self):
        #game loop - update
        self.all_sprites.update()
        self.second = ((pg.time.get_ticks() - self.start_tick)/1000)
        if self.player.vel.y > 0:
            #hits -> spritecollide 메서드를 이용(x,y, default boolean)충돌 체크
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.x < lowest.rect.right + 15 and \
                   self.player.pos.x > lowest.rect.left - 15:
                    if self.player.pos.y < lowest.rect.bottom:
                        self.player.pos.y = lowest.rect.top+1 #충돌시 player의 Y축 위치값이 충돌한 블록의 TOP값으로
                                                                #즉, 블록위에 있는 것처럼 보이게함
                        self.player.vel.y = 0
                        self.player.jumping = False

       #Game Level 처리, 최대 3번 난이도가 증가.
        if self.score == 1000:
            self.score += 10
            self.level_up.play()
            self.leveup_text()
            sleep(0.4)
            self.enemy_level += 1
            self.levelup(self.enemy_level)
        elif self.score == 2500:
            self.score += 10
            self.level_up.play()
            self.leveup_text()
            sleep(0.4)
            self.levelup(self.enemy_level)
        elif self.score == 4000:
            self.score += 10
            self.level_up.play()
            self.leveup_text()
            sleep(0.4)
            self.levelup(self.enemy_level)

        #게임 클리어 조건
        if self.head_count == 15:
            self.clear_text()
            self.ending = True
            self.playing = False
            self.head_count = 0
            sleep(1)

        #아이템
        item_hits = pg.sprite.spritecollide(self.player, self.items, True)
        for item in item_hits: #아이텥 목록
            if item.type == 'kill': # 현재 생성된 객체들에 한해서 적 객체 제거
                for enemy in self.enemys:
                    self.score += 10
                    self.item_kill.play()
                    enemy.kill()
            if item.type == 'speedup': # 현재 생성된 객체들에 한해서 적 객체 속도 증가
                for enemy in self.enemys:
                    self.item_speedup.play()
                    enemy.speedx = random.randrange(-1, 5)
                    enemy.speedy = random.randrange(3, 7)
            if item.type == 'speeddown': # 현재 생성된 객체들에 한해서 적 객체 속도 감소
                for enemy in self.enemys:
                    self.item_speeddown.play()
                    enemy.speedx = random.randrange(-5, 2)
                    enemy.speedy = random.randrange(0, 3)
            if item.type == 'powerup': # 나가는 총알 개수 증가, 총 3개까지 증가
                self.item_powerup.play()
                if self.player.power <= 3:
                    self.player.power +=1

        #적 생성
        while len(self.enemys) < 8:
            enemy = Enemy(self) #객체 생성
            self.all_sprites.add(enemy) #객체를 all_sprites 그룹에 추가
            self.enemys.add(enemy) # 적 sprite 그룹에 추가

        # player 위치가 1/2(스크린) 이상 왔을 떄len
        if self.player.rect.top <= HEIGHT / 2:
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10
            for ene in self.enemys: #적 객체 또한 plat객체 처럼 '+'시킴
                ene.rect.y += abs(self.player.vel.y)

        #블록 재생성
        while len(self.platforms) < 6:
            random_width = random.randrange(50, 200)
            Platform(self, random.randrange(0, WIDTH-random_width),
                         random.randrange(50, 70))

        #Game over
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 5)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.game_over_sound.play()
            self.playing = False

        #토끼 머리
        get_heads = pg.sprite.spritecollide(self.player, self.heads, True)
        if get_heads:
            self.get_heads.play()
            self.head_count += 1

        #bullet(총알)과 enemy(적) 충돌 체크
        bullet_hits = pg.sprite.groupcollide(self.bullets, self.enemys, True, True)
        if bullet_hits:
            for hit in bullet_hits:
                self.hit_sound.play()
                expl = Explosion(self, hit.rect.center)
                self.score += 10 #점수를 10점 증가시킴

        #player와 enemy 충돌(game over 조건)
        #mask를 씌우면 컬러키를 제외하고 남은 image를 픽셀단위로 체크함
        #collide_mask로 mask끼리의 충돌을 체크하여 좀 더 세밀한 충돌체크가 가능
        hits = pg.sprite.spritecollide(self.player, self.enemys, False, pg.sprite.collide_mask)
        if hits:
            self.playing = False
            self.game_over_sound.play()
            sleep(0.5)

    #Level up 시에 출력될 텍스트
    def leveup_text(self):
        for i in range(5):
            self.draw_text('Speed up !!', 40, BLACK, WIDTH/2, HEIGHT/2-100)
            pg.display.update()
            sleep(0.1)
            self.draw_text('Speed up !!', 40, WHITE, WIDTH/2, HEIGHT/2-100)
            pg.display.update()
            sleep(0.1)

    #Level이 증가함에 따라 적(운석)의 속도를 늘리는 함수 - helper function
    def levelup(self, enemy_level):
        self.speed_x += enemy_level
        self.speed_y += enemy_level
        self.speed_x_min += enemy_level
        self.speed_y_min += enemy_level

    def clear_text(self):
        for i in range(8):
            self.draw_text('CLEAR !! ', 60, GREEN, WIDTH/2, HEIGHT/2-100)
            pg.display.update()
            sleep(0.1)
            self.draw_text('CLEAR !! ', 60, RED, WIDTH/2, HEIGHT/2-100)
            pg.display.update()
            sleep(0.1)

    def events(self):
        #game loop - events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                    self.running = False
                    self.start = False
                self.start = False
            #점프
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_x:
                    self.jump_sound.play()
                    self.player.jump()

            #점프 컷
            if event.type == pg.KEYUP:
                if event.key == pg.K_x:
                    self.player.jump_cut()
            #총 발사
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_z:
                    bullet = Bullet(self, self.player.rect.centerx, self.player.rect.top) #player 객체의 위치정보를 받아 bullet 객체 생성
                    if self.player.power == 1:
                        self.shoot_sound.play()
                        self.all_sprites.add(bullet)
                        self.bullets.add(bullet)
                    if self.player.power == 2:
                        bullet = Bullet(self, self.player.rect.centerx-5, self.player.rect.top) #player 객체의 위치정보를 받아 bullet 객체 생성
                        bullet2 = Bullet(self, self.player.rect.centerx+5, self.player.rect.top) #player 객체의 위치정보를 받아 bullet 객체 생성
                        self.shoot_sound.play()
                        self.all_sprites.add(bullet, bullet2)
                        self.bullets.add(bullet, bullet2)
                    if self.player.power == 3:
                        bullet = Bullet(self, self.player.rect.centerx, self.player.rect.top) #player 객체의 위치정보를 받아 bullet 객체 생성
                        bullet2 = Bullet(self, self.player.rect.centerx+7, self.player.rect.top)
                        bullet3 = Bullet(self, self.player.rect.centerx-7, self.player.rect.top)
                        self.shoot_sound.play()
                        self.all_sprites.add(bullet, bullet2, bullet3)
                        self.bullets.add(bullet, bullet2, bullet3)

    #이미지를 불러오는 함수
    def load_date(self):
        #image, txt
        self.dir = os.path.dirname(__file__)
        self.img_dir = os.path.join(self.dir, 'Image')
        self.stand = Spritesheet(os.path.join(self.img_dir, STAND))
        self.jump = Spritesheet(os.path.join(self.img_dir, JUMP))
        self.move = Spritesheet(os.path.join(self.img_dir, MOVE))
        self.bullet = Spritesheet(os.path.join(self.img_dir, BULLET))
        self.bullet2 = Spritesheet(os.path.join(self.img_dir, BULLET2))
        self.enemy = Spritesheet(os.path.join(self.img_dir, ENEMY))
        self.jump = Spritesheet(os.path.join(self.img_dir, JUMP))
        self.block1 = Spritesheet(os.path.join(self.img_dir, BLOCK1))
        self.block2 = Spritesheet(os.path.join(self.img_dir, BLOCK2))
        self.block3 = Spritesheet(os.path.join(self.img_dir, BLOCK3))
        self.box = Spritesheet(os.path.join(self.img_dir, BOX))
        self.gameImg = pg.image.load(os.path.join(self.img_dir, BACKGROUND))
        self.start_logo = pg.image.load(os.path.join(self.img_dir, START_LOGO))
        self.start_screen = pg.image.load(os.path.join(self.img_dir, START_SCREEND))
        self.menu_select = pg.image.load(os.path.join(self.img_dir, MENU_SELECT))
        self.ending_image = pg.image.load(os.path.join(self.img_dir, ENDING_IMAGE))
        self.head = Spritesheet(os.path.join(self.img_dir, HEAD))
        self.head2 = pg.image.load(os.path.join(self.img_dir, HEAD))
        self.head2.set_colorkey(WHITE)
        self.explosion = Spritesheet(os.path.join(self.img_dir, EXPLOSION))
        self.explosion2 = Spritesheet(os.path.join(self.img_dir, EXPLOSION2))

        #sound(효과음)
        self.snd_dir = os.path.join(self.dir, 'sound')
        self.jump_sound = pg.mixer.Sound(os.path.join(self.snd_dir, 'Jump.wav'))
        self.shoot_sound = pg.mixer.Sound(os.path.join(self.snd_dir, 'Shoot.wav'))
        self.hit_sound = pg.mixer.Sound(os.path.join(self.snd_dir, 'Hit.wav'))
        self.game_over_sound = pg.mixer.Sound(os.path.join(self.snd_dir, 'Gameover.wav'))
        self.item_kill = pg.mixer.Sound(os.path.join(self.snd_dir, 'Item_kill.wav'))
        self.item_speedup = pg.mixer.Sound(os.path.join(self.snd_dir, 'Item_speedup.wav'))
        self.item_speeddown = pg.mixer.Sound(os.path.join(self.snd_dir, 'Item_speeddown.wav'))
        self.item_powerup = pg.mixer.Sound(os.path.join(self.snd_dir, 'Item_powerup.wav'))
        self.get_heads = pg.mixer.Sound(os.path.join(self.snd_dir, 'get_head.wav'))
        self.level_up = pg.mixer.Sound(os.path.join(self.snd_dir, 'level_up.wav'))
        self.intro_effect = pg.mixer.Sound(os.path.join(self.snd_dir, 'intro_effect.wav'))


    def draw(self):
        #game loop - draw
        self.screen.blit(self.gameImg, (0, 0))
        self.screen.blit(self.head2, (5, 5))
        self.all_sprites.draw(self.screen)
        self.draw_text('Score :' +str(self.score), 22, BLACK, WIDTH/2, 15)
        self.draw_text('  X ' +str(self.head_count), 22, BLACK, 50, 15)
        self.draw_text('Level : ' +str(self.enemy_level), 22, WHITE, WIDTH-60, 15)
        pg.display.update()

###-------- start_screen 부분

    def show_start_screen(self):
        #GAME START시에 나타낼 스크린
        pg.mixer.music.load(os.path.join(self.snd_dir, 'Mysterious.ogg'))
        pg.mixer.music.play(loops=-1)
        self.running = True
        self.start_new()
        pg.mixer.music.fadeoRut(500)

    def start_new(self):
        self.start_group = pg.sprite.Group()
        self.select = Select(self)
        self.start_group.add(self.select)
        self.start_run()

    def start_run(self):
        #start loop
        self.start_playing = True
        while self.start_playing:
            self.clock.tick(FPS)
            self.start_events()
            self.start_update()
            self.start_draw()

    def start_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.start_playing:
                    self.start_playing = False
                self.start = False



    def start_update(self):
        self.start_group.update()

    def start_draw(self):
        self.screen.blit(self.start_screen, (0,0))
        self.start_group.draw(self.screen)
        if self.select.select_number == 0:
            self.draw_text("OPENNING", 30, BLACK, WIDTH - 64, HEIGHT - 350)
            self.draw_text("OPENNING", 30, GRAY, WIDTH - 66, HEIGHT - 353)
            self.draw_text("START", 22, BLACK, WIDTH - 52, HEIGHT - 300)
            self.draw_text("START", 22, GRAY, WIDTH - 54, HEIGHT - 303)
            self.draw_text("EXIT", 22, BLACK, WIDTH - 48, HEIGHT - 250)
            self.draw_text("EXIT", 22, GRAY, WIDTH - 50, HEIGHT - 253)
        if self.select.select_number == 1:
            self.draw_text("OPENNING", 22, BLACK, WIDTH - 64, HEIGHT - 350)
            self.draw_text("OPENNING", 22, GRAY, WIDTH - 66, HEIGHT - 353)
            self.draw_text("START", 30, BLACK, WIDTH - 52, HEIGHT - 300)
            self.draw_text("START", 30, GRAY, WIDTH - 54, HEIGHT - 303)
            self.draw_text("EXIT", 22, BLACK, WIDTH - 48, HEIGHT - 250)
            self.draw_text("EXIT", 22, GRAY, WIDTH - 50, HEIGHT - 253)
        if self.select.select_number == 2:
            self.draw_text("OPENNING", 22, BLACK, WIDTH - 64, HEIGHT - 350)
            self.draw_text("OPENNING", 22, GRAY, WIDTH - 66, HEIGHT - 353)
            self.draw_text("START", 22, BLACK, WIDTH - 52, HEIGHT - 300)
            self.draw_text("START", 22, GRAY, WIDTH - 54, HEIGHT - 303)
            self.draw_text("EXIT", 30, BLACK, WIDTH - 48, HEIGHT - 250)
            self.draw_text("EXIT", 30, GRAY, WIDTH - 50, HEIGHT - 253)
        pg.display.update()

###---------------end

    def show_over_screen(self):
        # Game Over시에 나타낼 스크린
        self.screen.blit(self.gameImg, (1,1))
        self.draw_text("GAVE OVER", 48, BLACK, WIDTH/2, HEIGHT/4)
        self.draw_text("Score : "+ str(self.score), 22, BLACK, WIDTH/2, HEIGHT/2)
        self.draw_text("Press a 'Z' key to play again, 'ESC' to 'QUIT'", 22, BLACK, WIDTH/2, HEIGHT*3/4)
        self.draw_text("Time : " +str(self.second), 22, BLACK, WIDTH/2, HEIGHT*3/4+50)
        pg.display.update()
        sleep(1.5)
        self.wait_for_key()

    #게임 클리어시 나타낼 화면
    def ending_screen(self):
        self.screen.blit(self.ending_image, (1,1))
        pg.mixer.music.load(os.path.join(self.snd_dir, 'Ending.mp3'))
        pg.mixer.music.play(loops=-1)
        self.draw_text("GAME OVER", 48, WHITE, WIDTH/2, HEIGHT - 400)
        self.draw_text("YOUR SCORE : "+ str(self.score), 20, WHITE, WIDTH/2, HEIGHT - 300)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE! : "+ str(self.score), 20, WHITE, WIDTH/2, HEIGHT - 250)
            with open(os.path.join(self.dir, SCORE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("HIGH SCORE : "+ str(self.highscore), 20, WHITE, WIDTH/2, HEIGHT - 250)
        self.draw_text("ClEAR TIME : "+ str(self.second), 20, WHITE, WIDTH/2, HEIGHT - 200)
        self.draw_text("Press 'ESC' -> Menu", 20, WHITE, WIDTH/2, HEIGHT - 80)
        pg.display.update()
        self.wait_for_key2()

    #START와 OVER스크린에서 화면대기 및 진행을 위한 메서드
    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                    self.start = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False
                        waiting = False
                    if event.key == pg.K_z:
                        self.start = True
                        waiting = False

    def wait_for_key2(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                    self.start = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        waiting = False
                        self.running = False

    #화면에 텍스트 처리를 위한 메서드
    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.brankovic_font, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)
        #render(text, antialias, color, background=None) -> Surface

    #밑줄 그어진 텍스트 처리
    def draw_text2(self, text, size, color, x, y):
        font = pg.font.Font(self.brankovic_font, size).set_underline(True)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    #Intro 영상 재생
    def intro_movie(self):
        clip = VideoFileClip('intro.mpeg')
        clip.preview()
        self.intro_effect.play()
        self.draw_text("17.8", 40, WHITE, WIDTH/2, HEIGHT-100)
        pg.display.update()
        sleep(2)

    def openning(self):
        clip = VideoFileClip('open.mp4')
        clip.preview()
        sleep(2)
        self.show_start_screen()

g = Game()
g.intro_movie()
while g.start:
    g.show_start_screen()
    while g.running:
        g.new()
        if g.ending == True:
            g.ending_screen()
        else:
            g.show_over_screen()
pg.quit()
