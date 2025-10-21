from pgzero.builtins import Actor, Rect, music, sounds, keys
import pgzrun
import pygame
import os
import random

WIDTH = 960
HEIGHT = 640
TITLE = "Fuga do Laboratório"

GRAVITY = 0.6
PLAYER_SPEED = 3.0
JUMP_VELOCITY = -11

MENU, PLAY, GAME_OVER = 'menu', 'play', 'gameover'
state = MENU
music_on = True

PLATFORMS = [
    (0, HEIGHT - 48, WIDTH, 48),
    (120, 460, 200, 20),
    (420, 380, 220, 20),
    (760, 300, 160, 20),
]

# --- Player ---
class Player:
    def __init__(self, pos):
        self.image_idle = 'slime_idle1'
        self.images_walk = ['slime_walk1','slime_walk2']
        self.image_jump = 'slime_jump'
        self.actor = Actor(self.image_idle, pos=pos)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.facing = 1
        self.anim_timer = 0
        self.jump_count = 0
        self.max_jumps = 2
        # input flags
        self.input_left = False
        self.input_right = False

    def update(self):
        # movement from flags
        self.vx = 0
        if self.input_left:
            self.vx = -PLAYER_SPEED
            self.facing = -1
        elif self.input_right:
            self.vx = PLAYER_SPEED
            self.facing = 1

        # physics
        self.vy += GRAVITY
        self.actor.x += self.vx
        self.actor.y += self.vy

        # platform collisions
        self.on_ground = False
        for px,py,pw,ph in PLATFORMS:
            plat = Rect((px,py),(pw,ph))
            if self.actor.colliderect(plat) and self.vy>0 and self.actor.y-self.vy<=py:
                self.actor.y = py
                self.vy = 0
                self.on_ground = True
                self.jump_count = 0

        # clamp
        self.actor.x = max(16, min(WIDTH-16, self.actor.x))

        # animation: only advance frames while moving
        moving = (self.input_left or self.input_right)
        if not self.on_ground:
            self.actor.image = self.image_jump
            # stop walk animation
            self.anim_timer = 0
        elif moving:
            # if just started moving, reset the timer so animation begins cleanly
            if getattr(self, '_was_moving', False) is False:
                self.anim_timer = 0
            self.anim_timer += 1
            idx = (self.anim_timer // 8) % len(self.images_walk)
            self.actor.image = self.images_walk[idx]
        else:
            self.actor.image = self.image_idle
        # record movement flag for next frame
        self._was_moving = moving
        self.actor.flip_h = (self.facing == -1)

    def draw(self):
        self.actor.draw()

    def jump(self):
        if self.jump_count < self.max_jumps:
            self.vy = JUMP_VELOCITY
            try:
                sounds.jump.play()
            except Exception:
                pass
            self.jump_count += 1
            self.on_ground = False

# --- Enemy ---
class Enemy:
    def __init__(self, kind, pos, patrol_range):
        self.kind = kind
        self.images = [f"{kind}1", f"{kind}2"]
        self.actor = Actor(self.images[0], pos=pos)
        self.left_bound = pos[0]-patrol_range
        self.right_bound = pos[0]+patrol_range
        self.vx = 0.6 + random.random()*0.4
        self.anim = 0
        self.paused = False
        self.pause_timer = 0.0
        self.pause_duration = 2.0
        self.next_dir = None

    def update(self):
        # paused state: count down then resume in the next_dir
        if self.paused:
            self.pause_timer -= 1/60.0
            if self.pause_timer <= 0:
                self.paused = False
                # resume moving in the stored direction
                if self.next_dir is not None:
                    self.vx = self.next_dir
                    self.next_dir = None
                else:
                    self.vx = -self.vx
        else:
            # move
            self.actor.x += self.vx
            # reached left bound
            if self.actor.x <= self.left_bound:
                self.actor.x = self.left_bound
                self.paused = True
                self.pause_timer = self.pause_duration
                # store next movement to the right
                self.next_dir = abs(self.vx)
                self.vx = 0
            # reached right bound
            elif self.actor.x >= self.right_bound:
                self.actor.x = self.right_bound
                self.paused = True
                self.pause_timer = self.pause_duration
                # store next movement to the left
                self.next_dir = -abs(self.vx)
                self.vx = 0

        # animate only when not paused
        self.anim += 1
        if not self.paused:
            self.actor.image = self.images[(self.anim // 12) % 2]
        else:
            # show first frame while paused
            self.actor.image = self.images[0]

        # facing according to next movement direction if any
        if getattr(self, 'next_dir', None) is not None:
            self.actor.flip_h = self.next_dir < 0
        else:
            self.actor.flip_h = self.vx < 0

    def draw(self):
        self.actor.draw()

# --- Battery/Door ---
class Battery:
    def __init__(self, pos):
        self.images = ['battery1', 'battery2']
        self.actor = Actor(self.images[0], pos=pos)
        self.anim = random.randint(0, 10)
        self.collected = False

    def update(self):
        if self.collected:
            return

        self.anim += 1
        index = (self.anim // 20) % 2
        self.actor.image = self.images[index]

    def draw(self):
        if not self.collected:
            self.actor.draw()

class Door:
    def __init__(self, pos):
        self.actor = Actor('door_closed', pos=pos)
        self.is_open = False

    def open_door(self):
        self.is_open = True
        self.actor.image = 'door_open'

    def draw(self):
        self.actor.draw()

# --- Setup ---
player = None
enemies = []
batteries = []
door = None
collected_count = 0
total_batteries = 0

def setup_level():
    global player, enemies, batteries, door, collected_count, total_batteries

    player = Player((80, HEIGHT - 120))

    enemies.clear()
    enemies.append(Enemy('spider', (320, 442), 80))
    enemies.append(Enemy('wolf', (600, 360), 120))
    enemies.append(Enemy('globin', (820, 272), 60))

    batteries.clear()
    batteries.append(Battery((160, 420)))
    batteries.append(Battery((520, 340)))

    total_batteries = len(batteries)
    collected_count = 0
    door = Door((920, HEIGHT - 96))

setup_level()

btn_start = Rect((WIDTH//2-120,220),(240,50))
btn_music = Rect((WIDTH//2-120,290),(240,50))
btn_exit = Rect((WIDTH//2-120,360),(240,50))

# --- Music helpers ---
def start_bg_music():
    # try multiple locations for bg_music.mp3
    candidates = []
    try:
        candidates.append(os.path.join(os.path.dirname(__file__), 'sounds', 'bg_music.mp3'))
    except Exception:
        pass
    # current working directory
    candidates.append(os.path.join(os.getcwd(), 'sounds', 'bg_music.mp3'))
    candidates.append(os.path.join(os.getcwd(), 'bg_music.mp3'))

    for path in candidates:
        try:
            if not path or not os.path.exists(path):
                # print(f'bg_music: not found: {path}')
                continue

            print('bg_music: trying', path)

            # try safe pre-init and mixer.music
            try:
                try:
                    pygame.mixer.quit()
                except Exception:
                    pass
                try:
                    pygame.mixer.pre_init(44100, -16, 2, 4096)
                except Exception:
                    pass
                pygame.mixer.init()

                try:
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.set_volume(0.6)
                    pygame.mixer.music.play(-1)
                    print('bg_music: playing via pygame.mixer.music')
                    return True
                except Exception as e_music:
                    print('bg_music: mixer.music.load failed:', repr(e_music))
                    # fallback: try Sound
                    try:
                        snd = pygame.mixer.Sound(path)
                        snd.set_volume(0.6)
                        snd.play(loops=-1)
                        print('bg_music: playing via pygame.mixer.Sound')
                        return True
                    except Exception as e_sound:
                        print('bg_music: mixer.Sound failed:', repr(e_sound))
                        continue

            except Exception as e_init:
                print('bg_music: mixer init failed:', repr(e_init))
                continue
        except Exception:
            continue

    try:
        music.play('bg_music')
        music.set_volume(0.6)
        print('bg_music: playing via pgzero.music')
        return True
    except Exception as e:
        print('bg_music: pgzero.music failed:', repr(e))
        return False


def stop_bg_music():
    try:
        pygame.mixer.music.stop()
    except Exception:
        try:
            music.stop()
        except Exception:
            pass


# start music immediately
if music_on:
    start_bg_music()

# --- Game loop ---
def update():
    global state, collected_count
    if state != PLAY:
        return
    player.update()
    for e in enemies:
        e.update()
        if player.actor.colliderect(e.actor):
            # restart level immediately on death
            try:
                setup_level()
                if music_on:
                    start_bg_music()
            except Exception:
                pass
            return
    for b in batteries:
        b.update()
        if not b.collected and player.actor.colliderect(b.actor):
            b.collected = True
            collected_count += 1
            try:
                sounds.collect.play()
            except Exception:
                pass
            if collected_count >= total_batteries:
                door.open_door()
    if door.is_open and player.actor.colliderect(door.actor):
        setup_level()

# --- Drawing ---
def draw():
    screen.clear()
    if state == MENU:
        draw_menu()
    elif state == PLAY:
        draw_play()
    else:
        draw_game_over()

def draw_menu():
    screen.fill((20, 24, 30))
    screen.draw.text(TITLE, center=(WIDTH // 2, 120), fontsize=56)
    screen.draw.filled_rect(btn_start, (80, 180, 220))
    screen.draw.text('Start', center=btn_start.center, fontsize=28)
    screen.draw.filled_rect(btn_music, (160, 160, 200))
    screen.draw.text(
        f'Music [{"On" if music_on else "Off"}]', center=btn_music.center, fontsize=20
    )
    screen.draw.filled_rect(btn_exit, (200, 80, 120))
    screen.draw.text('Exit', center=btn_exit.center, fontsize=20)

def draw_play():
    screen.fill((30, 40, 60))

    for px, py, pw, ph in PLATFORMS:
        screen.blit('tile', (px, py))

    for b in batteries:
        b.draw()

    door.draw()

    for e in enemies:
        e.draw()

    player.draw()

    screen.draw.text(
        f'Batteries: {collected_count}/{total_batteries}', (10, 10), fontsize=24
    )

def draw_game_over():
    screen.fill((10,12,18))
    screen.draw.text('You Died!', center=(WIDTH//2,200), fontsize=48)
    screen.draw.text('Click to return', center=(WIDTH//2,260), fontsize=24)

def on_mouse_down(pos):
    global state, music_on

    if state == MENU:
        if btn_start.collidepoint(pos):
            state = PLAY

            if music_on:
                try:
                    start_bg_music()
                except Exception:
                    pass

        elif btn_music.collidepoint(pos):
            music_on = not music_on

            try:
                if music_on:
                    start_bg_music()
                else:
                    stop_bg_music()
            except Exception:
                pass

        elif btn_exit.collidepoint(pos):
            quit()

    elif state == GAME_OVER:
        state = MENU

        try:
            start_bg_music()
        except Exception:
            pass

def on_key_down(key):
    global state

    if state == MENU and key == keys.SPACE:
        state = PLAY

    if state == GAME_OVER and key == keys.RETURN:
        state = MENU

    if state == PLAY and (key == keys.UP or key == keys.SPACE):
        try:
            player.jump()
        except Exception:
            pass

    # directional flags
    if state == PLAY and key == keys.LEFT:
        try:
            player.input_left = True
            player.input_right = False
            player.facing = -1
        except Exception:
            pass

    if state == PLAY and key == keys.RIGHT:
        try:
            player.input_right = True
            player.input_left = False
            player.facing = 1
        except Exception:
            pass

def on_key_up(key):
    try:
        if key == keys.LEFT:
            player.input_left = False

        if key == keys.RIGHT:
            player.input_right = False
    except Exception:
        pass

# ensure sounds exist
if not hasattr(sounds, 'jump'):
    sounds.jump = type('S', (), {'play': lambda *a, **k: None})()

if not hasattr(sounds, 'collect'):
    sounds.collect = type('S', (), {'play': lambda *a, **k: None})()

pgzrun.go()
