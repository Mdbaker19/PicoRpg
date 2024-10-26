"""x:0, y:0 is generally bottom right"""
from time import ticks_ms, sleep, ticks_diff
from machine import Pin, SPI, ADC, I2C
from xglcd_font import XglcdFont
from ssd1309 import Display
from life import Life
from util import Util
from eeprom import Eeprom
from player import Player
from enemy import Enemy
from projectile import Projectile
from tower import Tower
from test_code import TestCode
from constants import Constants
import json
import math
import random


b1 = Pin(5, Pin.IN, Pin.PULL_UP)
b2 = Pin(4, Pin.IN, Pin.PULL_UP)

db1 = Pin(6, Pin.IN, Pin.PULL_UP)
db2 = Pin(7, Pin.IN, Pin.PULL_UP)
db3 = Pin(8, Pin.IN, Pin.PULL_UP)
db4 = Pin(9, Pin.IN, Pin.PULL_UP)

i2c_memory = I2C(0, scl=Pin(1), sda=Pin(0), freq=50000)

W = 128
H = 64
font_H = 8
'''Create another font, smaller to show enemy lvl values and required kill counts above doors on map?'''
font = XglcdFont('Wendy7x8.c', 7, font_H)

spi = SPI(0, baudrate=10000000, sck=Pin(18), mosi=Pin(19))
d1 = Display(spi, dc=Pin(16), cs=Pin(17), rst=Pin(20))


spi2 = SPI(1, baudrate=10000000, sck=Pin(10), mosi=Pin(11))
d2 = Display(spi2, dc=Pin(12), cs=Pin(13), rst=Pin(2))
util = Util()

#renders screens and sleeps for 30fps average from time passed in
def run_screens(passed_time):
    d1.present()
    d2.present()
    time_taken = ticks_ms() - passed_time
    #print(time_taken)
    sleep_amount = 17 - time_taken #60fps is 16.67ms
    if sleep_amount >= 0:
        sleep(sleep_amount / 500)
    d2.clear_buffers()
    d1.clear_buffers()
    return

'''
MOVE TO xglcdFont
'''
# when x at 0 is right side of screen == text end position at 0
# x: 128 is left side of screen
# does not erase to just draw screen, can overlay an existing bit map
# can take f strings for text
''' Need to return total text height especially for next line wrapping'''
def draw_text(x, y, text, padding=0, clear_first=False, isOne=True):
    text_width = font.measure_text(text)
    x = text_position_X(x, text_width, padding)
    empty_list = [0] * (128 * font_H)
    if isOne:
        if clear_first:
            d1.draw_bitmap_array_raw(bytearray(empty_list), 0, y, 128, font_H)
        d1.draw_text(x, y, text, font, False, 180)
    else:
        if clear_first:
            d1.draw_bitmap_array_raw(bytearray(empty_list), 0, y, 128, font_H)
        d2.draw_text(x, y, text, font, False, 180)

def text_position_X(desiredX, text_w, padding):
    if desiredX < text_w:
        return text_w - desiredX + padding
    else:
        return desiredX - padding
'''
'''


def test_ui(player, changed_values, first_draw=False):
    ui_display(player, changed_values, first_draw)
    d1.present()
    return

'''Get all text width to normalize the position they are drawn at?
Level:    19
Health:   100
Items:    []
(self, lvl, exp, expReq, hp, attack, defense, speed, mana, money)
'''
def ui_display(player, changed_values, first_draw):
    ui_rows = 5
    level = 19
    if first_draw:
        changed_values = ["name", "mana", "hp", "lvl", "stats", "exp"]
    for value in changed_values:
        if value == "name":
            draw_text(128, 52, "Makadee", padding=2, clear_first=not first_draw)
        if value == "mana":
            draw_text(128, 43, f"Mana: {player.mana}", padding=2, clear_first=not first_draw)
        if value == "hp":
            draw_text(128, 34, f"Health: {player.hp}", padding=2, clear_first=not first_draw)
        if value == "lvl":
            draw_text(128, 25, f"Level: {player.lvl}", padding=2, clear_first=not first_draw)
        if value == "stats":
            draw_text(128, 16, f"Stats: A:{player.attack} | K:{player.kills}", padding=2, clear_first=not first_draw)
        if value == "exp":
            draw_text(128, 7, f"Exp: {player.exp}/{player.expReq}", padding=2, clear_first=not first_draw)
    d1.draw_rectangle(0, 0, W, H)
    return



def load_sprites():
    with open('sprites.json', 'r') as file:
        data = json.load(file)
    p = data['player']
    player = {
        "left": bytearray(p['sprite_left']),
        "down": bytearray(p['sprite_front']),
        "right": bytearray(p['sprite_right']),
        "up": bytearray(p['sprite_back'])
    }
    enemy = data['enemy']
    objects = data['objects']

    return (player, enemy, objects)


def test_enemy_and_player_render():
    player, enemy, objects = load_sprites()
    door_open = bytearray(objects['door_open'])
    door = bytearray(objects['door_closed'])
    grave = bytearray(objects['grave'])
    e = bytearray(enemy['sprite'])
    left = bytearray(player['sprite_left'])
    right = bytearray(player['sprite_right'])
    front = bytearray(player['sprite_front'])
    back = bytearray(player['sprite_back'])
    raw_test = [left, right, front, back]


    d2.draw_bitmap_array_raw(front, 30, 30, 16, 20)
    d2.draw_bitmap_array_raw(e, 50, 30, 14, 14)
    d2.draw_bitmap_array_raw(grave, 20, 20, 13, 11)
    d1.draw_bitmap_array_raw(door, 50, 50, 25, 11)
    d1.draw_bitmap_array_raw(door_open, 50, 10, 25, 11)
    d1.present()
    d2.present()
    sleep(10)


    return

def save_game_data(data):
    print("SAVING GAME")
    eeprom.eeprom_write(data)
    return

# (self, lvl, exp, expReq, hp, attack, defense, speed, mana, money): -> e order preserved so all good list unpacking *e
def parse_save_state(e):
    stats_used_so_far = e[:9]
    player = Player(0, 0, *stats_used_so_far)
    return player




def test_arcade_render(ball_count):
    balls = []
    reward = 0
    for i in range(ball_count):
        balls.append(Ball(128, 128, 64))
    for ball in balls:
        if ball.get_dir:
            ball.x -= 5
        else:
            ball.x += 5
        ball.y -= 5
        if ball.y <= 0:
            arcade.get_reward_value(ball.x)
    #d2.present()
    return reward



def distance(p1, p2):
    return (p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2
def is_point_in_range(tower, target):
    dis = distance(tower, target)
    #print(f"Is {dis} less than {tower.distance}")
    return dis <= tower.distance


# maybe do a half screen partition depending on how i set tower ranges
# need bullet ba for projectile here
def test_tower_sets(player, player_ba_list, towers, enemies, objects):
    test_ui(player)
    ammo_ba = bytearray(objects['tower_ammo'])
    towerW = 10
    towerH = 16
    rta = 0
    iterations = 100
    for i in range(iterations):
        loop_time = ticks_ms()
        # establish tower targets and shoot at them
        curr_time = ticks_ms()
        enemies_dict = {}
        for enemy in enemies:
            d2.draw_bitmap_array_raw(enemy.ba, enemy.x, enemy.y, enemy.size, enemy.size)
            enemies_dict[enemy.ide] = enemy
            enemy.change_value('x', random.randint(-4, 5))
            enemy.change_value('y', random.randint(-4, 5))

        for tower in towers:
            d2.draw_bitmap_array_raw(tower.ba, tower.x, tower.y, towerW, towerH)
            if ticks_diff(curr_time, tower.last_shoot_time) >= tower.shoot_time:
                tower.last_shoot_time = curr_time
                for enemy in enemies:
                    if is_point_in_range(tower, enemy):
                        #print(f"tower at {tower.x} / {tower.y} has a target at {enemy.x} / {enemy.y}")
                        id_set = set(tower.targets)
                        if enemy.ide not in id_set:
                            tower.targets.append(enemy.ide) # add if not present
                        tower.projectiles.append(Projectile(tower.x + towerW/2, tower.y + towerH/2, random.randint(-9999, 9999), 2, 2, ba=ammo_ba, path=util.get_direction_vector(tower, enemy), speed=1.8)) # will be tower shoot speed later


            tower.projectiles = [p for p in tower.projectiles if util.is_on_screen(p)]
            for projectile in tower.projectiles:
                (x_path, y_path) = projectile.path
                #print(x_path, y_path) # slope calc is f'd, may need slope path accumulator stored in projectile as property
                projectile.increment_x(x_path)
                projectile.increment_y(y_path)
                d2.draw_bitmap_array_raw(projectile.ba, int(projectile.x), int(projectile.y), projectile.w, projectile.h)

            # seems to need big hitbox.. which is fine honestly
                for e in tower.targets:
                    en = enemies_dict.get(e)
                    if en and util.check_for_collision(en.x, en.y, en.size, en.size, projectile.x, projectile.y, projectile.w, projectile.h, hit_box_mult=80):
                        en.change_value('hp', -tower.damage)
                        projectile.increment_x(200)
                        #print(f"contact made at {en.x} {en.y}")

                    # if enemy dead, remove from tower targets and target ide and enemy list...
        enemies = [ehp for ehp in enemies if ehp.hp >= 0]
# does not seem necessary
#tower.targets = [e for e in tower.targets if e.hp >= 0]


        run_screens(loop_time)

        time_taken = ticks_ms() - loop_time
        rta += time_taken
    print(rta / iterations)
    return

'''
This returns a list of len 255 of ints ranging from 0-255 themselves
255 should be ignored as that is considered empty space
'''
eeprom = Eeprom(0x00, i2c_memory)
#read_value = eeprom.eeprom_read()
#print(f"Read from eeprom: {read_value}")

#save_state_player_data = parse_save_state(read_value)

# testing, dont need to keep reading
save_state_player_data = Player(0, 0, 1, 0, 1, 100, 4, 2, 4, 10, 99)
# (self, x, y, lvl, exp, expReq, hp, attack, defense, speed, mana, money): -> e order preserved so all good list unpacking *e
'''
Needs font, load sprites, draw text...
test_code = TestCode()
test_code.test_life()
test_code.test_movement()
'''
#test_ui(save_state_player_data)
#test_enemy_and_player_render()


# TODO: need to figure out what to do after enemy is killed first time
#test_enemies_present_snowball_kill(save_state_player_data)



#_, x, y, distance, damage, projectiles, shoot_time, ba, target
player_ba_list, eba, objects = load_sprites()
enemy_sprite = bytearray(eba['sprite'])
tower_sprite = bytearray(objects['tower_defense_1'])
t1 = Tower(100, 40, 5050, 1, [], 1000, tower_sprite, [])
t2 = Tower(38, 30, 1250, 1, [], 1030, tower_sprite, [])
t3 = Tower(65, 36, 300, 1, [], 50, tower_sprite, [])
my_towers = [t1, t3]

#_, lvl, x, y, ba, size, ide
enemy_targets = [
    Enemy(1, 40,20, enemy_sprite, 14, random.randint(-9999, 9999)),
    Enemy(1, 40, 47, enemy_sprite, 14, random.randint(-9999, 9999)),
    Enemy(1, 0, 8, enemy_sprite, 14, random.randint(-9999, 9999)),
    Enemy(1, 100, 47, enemy_sprite, 14, random.randint(-9999, 9999)),
    Enemy(1, 65, 27, enemy_sprite, 14, random.randint(-9999, 9999)),
    Enemy(1, 18, 40, enemy_sprite, 14, random.randint(-9999, 9999)),
    Enemy(1, 88, 47, enemy_sprite, 14, random.randint(-9999, 9999)),
    Enemy(1, 110, 20, enemy_sprite, 14, random.randint(-9999, 9999))
]


# jeez this runs slow when many enemies on screen up to 50 ms per frame ;_;
# at 10 mana, a tower will spawn, mana will increment to 10
def test_enemy_waves(player, player_bas, e_sprite, objects):
    right_profile = bytearray(player_bas['sprite_right'])
    tower_sprite = bytearray(objects['tower_defense_1'])
    t_ammo = bytearray(objects['tower_ammo'])
    snowball_ba = bytearray(objects['snowball'])
    test_ui(player, [], first_draw=True)
#    iterations = 500
    player.x = W - player.w
    player_snowballs = []
    snowball_interval = 500
    max_snow = 10
    prev_time = ticks_ms()
    player_values_changed = False
    towers = []
    towerW = 10
    towerH = 16
    mana_req = 10
    prev_e_spawn = ticks_ms()
    curr_e_level = 1
    current_kills = 0
    wall_pos = 108
    esize = 14
    enemies_alive = []
    while player.hp >= 0 and current_kills < 50:
        changed_values = []
#    for i in range(iterations):
        enemies_dict = {}
        kill_req = 5 * curr_e_level
        e_spawn_time = 3000 / curr_e_level
        loop_time = ticks_ms()
        curr_time = ticks_ms()
        if ticks_diff(curr_time, prev_e_spawn) >= e_spawn_time:
            prev_e_spawn = curr_time
            ey = random.randint(0, Constants.max_y(14))
            enemies_alive.append(Enemy(curr_e_level, -5, ey, e_sprite, esize, random.randint(-99999, 99999)))
        for e in enemies_alive:
            enemies_dict[e.ide] = e
            d2.draw_bitmap_array_raw(e.ba, e.x, e.y, e.size, e.size)
            if e.x < wall_pos - e.size:
                #e.change_value('x', random.randint(0, 1))
                e.x += random.randint(0, 1)
            else:
                if ticks_diff(curr_time, e.last_at_time) >= e.at_int:
                    e.last_at_time = curr_time
                    player.hp -= e.lvl
                    #player.change_value("hp", -e.lvl)
                    player_values_changed = True
                    changed_values.append("hp")

        # handle player attacks
        if ticks_diff(curr_time, prev_time) >= snowball_interval:
            prev_time = curr_time
            player.mana += 1 # for now
            changed_values.append("mana")
            player_values_changed = True
            if len(player_snowballs) < max_snow:
                sy = int(player.y + (player.h / 3))
                new_snow = Projectile(player.x, sy, random.randint(-9999, 9999), 5, 4, snowball_ba)
                player_snowballs.append(new_snow)

        # handle bullet travel
        player_snowballs = [s for s in player_snowballs if s.x >= 0]
        for s in player_snowballs:
            s.increment_x(-2)
            d2.draw_bitmap_array_raw(s.ba, s.x, s.y, s.w, s.h)
            # get enemies in coord based on relative pos from snowball x and e.x and snowball y within 10 of e.y
            possible_enemies = [e for e in enemies_alive if e.x <= s.x and (e.y + e.size >= s.y and e.y <= s.y + s.h)]
            for enemy in possible_enemies:
                if util.check_for_collision(enemy.x, enemy.y, enemy.size, enemy.size, s.x, s.y, s.w, s.h, hit_box_mult=2):
                    #enemy.change_value("hp", -player.attack)
                    enemy.hp -= player.attack
                    s.increment_x(-130)
                    if enemy.hp <= 0:
                        #player.change_value("exp", 6)
                        changed_values.append("exp")
                        changed_values.append("stats")
                        player.exp += 6 * curr_e_level
                        if player.exp >= player.expReq:
                            player.level_up()
                            changed_values.append("lvl")
                            changed_values.append("hp")
                        player_values_changed = True
                        current_kills += 1
                        player.kills += 1

        for tower in towers:
            d2.draw_bitmap_array_raw(tower.ba, tower.x, tower.y, towerW, towerH)
            if ticks_diff(curr_time, tower.last_shoot_time) >= tower.shoot_time:
                tower.last_shoot_time = curr_time
                for enemy in enemies_alive:
                    if is_point_in_range(tower, enemy):
                        #print(f"tower at {tower.x} / {tower.y} has a target at {enemy.x} / {enemy.y}")
                        id_set = set(tower.targets)
                        if enemy.ide not in id_set:
                            tower.targets.append(enemy.ide) # add if not present
                        tower.projectiles.append(Projectile(tower.x + towerW/2, tower.y + towerH/2, random.randint(-9999, 9999), 2, 2, ba=t_ammo, path=util.get_direction_vector(tower, enemy), speed=2.2)) # will be tower shoot speed later


            tower.projectiles = [p for p in tower.projectiles if util.is_on_screen(p)]
            for projectile in tower.projectiles:
                (x_path, y_path) = projectile.path
                #print(x_path, y_path) # slope calc is f'd, may need slope path accumulator stored in projectile as property
                projectile.increment_x(x_path)
                projectile.increment_y(y_path)
                d2.draw_bitmap_array_raw(projectile.ba, int(projectile.x), int(projectile.y), projectile.w, projectile.h)

            # seems to need big hitbox.. which is fine honestly
                for e in tower.targets:
                    en = enemies_dict.get(e)
                    if en and util.check_for_collision(en.x, en.y, en.size, en.size, projectile.x, projectile.y, projectile.w, projectile.h, hit_box_mult=100):
                        en.change_value('hp', -tower.damage)
                        projectile.increment_x(200)
                        if enemy.hp <= 0:
                            changed_values.append("exp")
                            changed_values.append("stats")
                            player.exp += 6 * curr_e_level
                            if player.exp >= player.expReq:
                                player.level_up()
                                changed_values.append("lvl")
                                changed_values.append("hp")
                            player_values_changed = True
                            current_kills += 1
                            player.kills += 1

        enemies_alive = [ehp for ehp in enemies_alive if ehp.hp >= 0]
        going_up = b1.value() == 1
        going_down = b2.value() == 1

        if going_up:
            player.y -= player.speed
        elif going_down:
            player.y += player.speed

        # refactor to return full constrained value between max_y and 0
        if player.y >= Constants.max_y(player.h):
            player.y = Constants.max_y(player.h)
        if player.y <= 0:
            player.y = 0

        if player.mana >= mana_req and len(towers) < 7:
            player.mana -= mana_req
            mana_req += 8
            changed_values.append("mana")
            player_values_changed = True
            towers.append(Tower(random.randint(20, 100),random.randint(0, 48),random.randint(200, 2800),random.randint(1, 5),[],random.randint(400, 1200),tower_sprite,[]))

        d2.draw_bitmap_array_raw(right_profile, player.x, player.y, player.w, player.h)
        d2.draw_vline(wall_pos, 0, H-1)

        if current_kills >= kill_req:
            curr_e_level += 1

        if player_values_changed:
            test_ui(player, changed_values)
            player_values_changed = False
        run_screens(loop_time)
    return


def test_full_movement(player, player_ba_list):
    iterations = 200
    crossed_screens = False
    on_top_screen = False
    for i in range(iterations):
        loop_time = ticks_ms()
        db1v = db1.value()
        db2v = db2.value()
        db3v = db3.value()
        db4v = db4.value()
        profile, crossed_screens, on_top_screen = player.handle_movement(player_ba_list, db1v, db2v, db3v, db4v, crossed_screens, on_top_screen)
        
        if on_top_screen:
            d1.draw_bitmap_array_raw(profile, player.x, player.y, player.w, player.h)
        else:
            d2.draw_bitmap_array_raw(profile, player.x, player.y, player.w, player.h)
        run_screens(loop_time)
    return
#test_tower_sets(save_state_player_data, player_ba_list, my_towers, enemy_targets, objects)
#test_enemy_waves(save_state_player_data, player_ba_list, enemy_sprite, objects)

#test_full_movement(save_state_player_data, player_ba_list)

def double_check_collision():
    x = 60
    y = 38
    m = 1
    ex = 60
    ey = 39
    for i in range(100):
        loop_time = ticks_ms()
        
        db1v = db1.value()
        db2v = db2.value()
        db3v = db3.value()
        db4v = db4.value()
        
        going_down = db1v == 1
        going_right = db2v == 1
        going_up = db3v == 1
        going_left = db4v == 1
        
        if going_down:
            y += m
        if going_right:
            x -= m
        if going_up:
            y -= m
        if going_left:
            x += m
        
        
        d1.draw_bitmap_array_raw(bytearray([255]), ex, ey, 1, 1)
        d1.draw_bitmap_array_raw(bytearray([255, 0, 0, 255]), x, y, 2, 2)
        if util.check_for_collision(x, y, 2, 2, ex, ey, 1, 1):
            print("collision")
        else:
            print("None")
            
        
        run_screens(loop_time)
    return

double_check_collision()

sleep(.25)
d1.cleanup()
d2.cleanup()


print('Done.')


'''

get collision detection figured out √
get the UI figured out √
load different levels
kill something √
enemy attack me √ and health decrement √
create a parse function and list of readable inventory for save state loading
Load a list of save state data and populate UI elements - player level, inventory √


'''


