from pygame import *
from random import randint
from pygame import draw as py_draw
'''Необходимые классы'''

#класс-родитель для спрайтов 
class GameSprite(sprite.Sprite):
    #конструктор класса
    def __init__(self, player_image, player_x, player_y, player_speed, w, h):
        super().__init__()
 
        # каждый спрайт должен хранить свойство image - изображение
        self.image = transform.scale(image.load(player_image).convert_alpha(), (w, h))
        self.speed = player_speed
 
        # каждый спрайт должен хранить свойство rect - прямоугольник, в который он вписан
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def draw(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

#класс-наследник для спрайта-игрока (управляется стрелками)
class Player(GameSprite):

   reload = 20
   health = 100
   points = 0

   def update(self):
      self.reload += 1
      keys = key.get_pressed()
      if keys[K_LEFT] and self.rect.x > 5:
         self.rect.x -= self.speed
      if keys[K_RIGHT] and self.rect.x < win_width - 80:
         self.rect.x += self.speed
      if keys[K_UP] and self.rect.y > 5:
         self.rect.y -= self.speed
      if keys[K_DOWN] and self.rect.y < win_height - 80:
         self.rect.y += self.speed
      if keys[K_SPACE]:
         self.fire()

   def fire(self):
      if self.reload >= 20:
         bullet = Bullet('fireball.png', self.rect.x, self.rect.y,
                        5, 15, 30)
         bullets.add(bullet)
         self.reload = 0
         fire_snd.play()
   def draw(self):
      super().draw()
      rect1= Rect(self.rect.x, self.rect.bottom, self.rect.w*self.health/100, 5)
      rect2= Rect(self.rect.x, self.rect.bottom, self.rect.w, 5)
      color = (255 - int(255*self.health/100),int(255*self.health/100), 0)
      py_draw.rect(window, color, rect1)
      py_draw.rect(window, color, rect2, 2)
      

class Star(GameSprite):
   def update(self):
      self.rect.y += self.speed
      if self.rect.y > win_height:
         stars.remove(self)

class Bullet(GameSprite):
   def update(self):
      self.rect.y -= self.speed
      if self.rect.y < -50:
         self.kill()

class Ufo(GameSprite):
   def update(self):
      self.rect.y += self.speed
      if self.rect.y > win_height:
         self.kill()
         global ufo_missed
         ufo_missed += 1


class Boom(sprite.Sprite):
    def __init__(self, ufo_center, boom_sprites, booms) -> None:
        super().__init__() 
        #global booms, boom_sprites              
        self.frames = boom_sprites        
        self.frame_rate = 1   
        self.frame_num = 0
        self.image = boom_sprites[0]
        self.rect = self.image.get_rect()
        self.rect.center = ufo_center
        self.add(booms)
    
    def next_frame(self):
        self.image = self.frames[self.frame_num]
        self.frame_num += 1
        
    
    def update(self):
        self.next_frame()
        if self.frame_num == len(self.frames)-1:
            self.kill()
#класс-наследник для спрайта-врага (перемещается сам)

def sprites_load(folder, file_name, size, colorkey):    
    sprites = []
    load = True
    num = 1
    while load:
        try:
            spr = image.load(f'{folder}\\{file_name}{num}.png')
            spr = transform.scale(spr,size)
            if colorkey: spr.set_colorkey((0,0,0))
            sprites.append(spr)
            num += 1
        except:
            load = False
    return sprites


def set_text(text,color, x, y):
    window.blit(font1.render(text, True , color), (x,y))


#Игровая сцена:
win_width = 700
win_height = 500
window = display.set_mode((win_width, win_height))
display.set_caption("GALAXY")
background = transform.scale(image.load("space.jpg"), (win_width, win_height))
ufo_missed = 0
#Персонажи игры:

player = Player('rocket.png', 5, win_height - 80, 4, 65,65)
boom_sprites = sprites_load('boom4', 'boom', (70, 70), (0,0,0))

font.init()
font1 = font.Font(None, 36)
font2 = font.Font(None, 20)

game = True
finish = False
win = False
stars = []
ufos = sprite.Group()
bullets = sprite.Group()
booms = sprite.Group()

ticks = 0

clock = time.Clock()
FPS = 60

#музыка
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_snd = mixer.Sound('fire.ogg')




while game:
    display.set_caption("GALAXY (fps-" + \
                    str(int(clock.get_fps())) + ")")
    for e in event.get():
        if e.type == QUIT:
            game = False
    
    if not finish:        
        
        if ticks % 5 == 0: 
            size = randint(10, 30)           
            star = Star('star2.png', randint(0, win_width), -10, randint(1, 10), size, size)
            stars.append(star)

        if ticks % 60 == 0: 
            size = randint(70, 80)           
            ufo = Ufo('nlo.png', randint(0, win_width), -100,
                randint(2, 2), size, size)
            ufos.add(ufo)
        
        
        window.blit(background,(0, 0))     

        for star in stars:
            star.update()
            star.draw()

        ufos.update()
        bullets.update()
        player.update()
        booms.update()
        
        collides = sprite.groupcollide(ufos, bullets, True, True)        
        if collides:
            player.points += 1
            if player.points >=20:
                finish= True
                win = True
            for ufo, bullet in collides.items():
                ufo_center = ufo.rect.center
                Boom(ufo_center, boom_sprites, booms)

        if sprite.spritecollide(player, ufos, False):
            player.health -= 1
            if player.health <= 0:
               finish = True


        player.draw()
        ufos.draw(window)
        bullets.draw(window)
        booms.draw(window)

        set_text(f'Очки - {player.points}', (255, 255, 200), 10, 10)
        set_text(f'Пропущенные - {ufo_missed}', (255, 255, 200), 450, 10)
        
    else:
        if win:
            go = GameSprite('youwin.png.png', 0,0, 0, 700, 500)
            go.draw()
        else:
            # если конец игры
            go = GameSprite('youlose.png.jpg', 0,0, 0, 700, 500)
            go.draw()

    display.update()
    clock.tick(FPS)
    ticks += 1