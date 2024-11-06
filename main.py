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
from random import randint
from rpg_util import RPG_Util
from rpg import RPG, RPG_Player, RPG_Enemy

ab1 = Pin(5, Pin.IN, Pin.PULL_UP)
ab2 = Pin(4, Pin.IN, Pin.PULL_UP)
db1 = Pin(6, Pin.IN, Pin.PULL_UP) # make this new menu cycle button (up)
db2 = Pin(7, Pin.IN, Pin.PULL_UP)
db3 = Pin(8, Pin.IN, Pin.PULL_UP) # make this new menu cycle button (down)
db4 = Pin(9, Pin.IN, Pin.PULL_UP)


quit_b = Pin(15, Pin.IN, Pin.PULL_UP)

i2c_memory = I2C(0, scl=Pin(1), sda=Pin(0), freq=50000)

SW = 128
SH = 64
FH = 8

f8 = XglcdFont('Wendy7x8.c', 7, FH)
PADDING = 2
store_text_column = f8.measure_text("Select ->") + PADDING
spi = SPI(0, baudrate=10000000, sck=Pin(18), mosi=Pin(19))
d1 = Display(spi, dc=Pin(16), cs=Pin(17), rst=Pin(20))
spi2 = SPI(1, baudrate=10000000, sck=Pin(10), mosi=Pin(11))
d2 = Display(spi2, dc=Pin(12), cs=Pin(13), rst=Pin(2))

eeprom = Eeprom(0x00, i2c_memory)
#read_value = eeprom.eeprom_read()

#save_state_player_data = parse_save_state(read_value)
player = RPG_Player(1)
util = Util()
rpg_u = RPG_Util()

rpg_start = RPG()


# pre load bg ba?
fight_door, shop_door, shop_keep = rpg_start.load_entrences()
bank_door, bank_bg = rpg_start.load_entrences_two()
bg_top, overworld_top, boss_door = rpg_start.load_bg_sprites()

def pressed(b):
    return b.value() == 0

def draw_text(x, y, text, padding=PADDING, clear_first=False, isOne=True, isNotSmall=True):
    text_width = f8.measure_text(text)
    x = x - padding
    if x < text_width:
        x = text_width + padding
    fh = FH if isNotSmall else FHS
    if isOne:
        if clear_first:
            d1.draw_bitmap_array_raw(bytearray([0] * (128 * FH)), 0, y, 128, fh)
        d1.draw_text(x, y, text, f8, False, 180)
    else:
        if clear_first:
            d2.draw_bitmap_array_raw(bytearray([0] * (128 * FH)), 0, y, 128, fh)
        d2.draw_text(x, y, text, f8, False, 180)
    return


# (self, lvl, hp, acc, defense, attack=None, mana=None, max_mana=None, choice=None, speed=None)
def parse_save_state(e):
#    stats_used_so_far = e[:9]
    player = RPG_Player(1, 10, 5, 3)
    return player

#renders screens and sleeps for 30fps average from time passed in
def run_screens(passed_time, clear_one=True, clear_two=True):
    d1.present()
    d2.present()
    time_taken = ticks_ms() - passed_time
    #print(time_taken)
    sleep_amount = 17 - time_taken #60fps is 16.67ms
    if sleep_amount >= 0:
        print("Sleeping for: ", sleep_amount/500)
        sleep(sleep_amount / 500)
    if clear_one:
        d1.clear_buffers()
    if clear_two:
        d2.clear_buffers()
    return

def save_game_data(data):
    print("SAVING GAME")
    eeprom.eeprom_write(data)
    return

def ui_display(player, changed_values, first_draw, in_overworld=False):
    item_string = ', '.join([f'{key}: {value}' for key, value in player.items.items()])
    money_val = int(player.money)
    if money_val >= 1000000000:
        money_val = f"{money_val / 1000000000:.2f}B"
    elif money_val >= 1000000:
        money_val = f"{money_val / 1000000:.2f}M"
    elif money_val >= 1000:
        money_val = f"{money_val / 1000:.2f}K"
    bank_val = int(player.bank_account)
    if bank_val >= 1000000000:
        bank_val = f"{bank_val / 1000000000:.2f}B"
    elif bank_val >= 1000000:
        bank_val = f"{bank_val / 1000000:.2f}M"
    elif bank_val >= 1000:
        bank_val = f"{bank_val / 1000:.2f}K"
    clear = not first_draw
    if first_draw:
        changed_values = ["name", "hp", "mana", "lvl", "exp", "items", "money", "bank"]
    for value in changed_values:
        if value == "name":
            draw_text(128, 52, f"{player.class_type} A:{player.attack} | D:{player.defense}", clear_first=clear, isOne=False)
        if value == "hp":
            draw_text(128, 43, f"Health: {player.hp} / {player.max_hp}", clear_first=clear, isOne=False)
        if value == "mana":
            draw_text(128, 34, f"Mana: {player.mana}/{player.max_mana}", clear_first=clear, isOne=False)
        if value == "lvl":
            draw_text(128, 7, f"Level: {player.lvl}", clear_first=clear, isOne=False)
            if in_overworld:
                draw_text(20, 7, "Use Pot ->", clear_first=clear, isOne=False)
        if value == "exp":
            draw_text(128, 15, f"Exp: {player.exp}/{player.expReq}", clear_first=clear, isOne=False)
        if value == "items":
            draw_text(128, 25, f"Items: {item_string}", clear_first=clear, isOne=False)
        if value == "money":
            draw_text(20, 34, f"$: {money_val}", clear_first=clear, isOne=False)
        if value == "bank":
            draw_text(20, 18, f"Bank: {bank_val}", clear_first=clear, isOne=False)
    
    if in_overworld:
        draw_text(0, 55, "Enter ->", isOne=False)
    d2.draw_rectangle(0, 0, SW, SH)
    return

# this should take in the list defined in the battle test fn so i can order that list and have it reorder the ui
def ui_display_battle(player, b1C):
    item_string = ', '.join([f'{key}: {value}' for key, value in player.items.items()])
    draw_text(128, 50, f"HP: {player.hp} / {player.max_hp}", isOne=False)
    draw_text(128, 40, "Attack", isOne=False)
    draw_text(128, 30, f"Items: {item_string}", isOne=False)
    draw_text(128, 20, f"Magic: {player.mana}/{player.max_mana}", isOne=False) # still does not do anything
    draw_text(128, 10, "Shield", isOne=False)
    draw_text(128, 0, "Run", isOne=False)
    draw_text(0, 10, "Select ->", isOne=False)
    d2.draw_rectangle(store_text_column, b1C*10 - 2, SW-store_text_column, 12)
    d2.draw_rectangle(0, 0, SW, SH)
    return

def ui_shop(money, b1C):
    b1CY = max(b1C, 1)
    draw_text(128, 50, "Potion: 10", isOne=False)
    draw_text(128, 40, "DEF Book: 35", isOne=False)
    draw_text(128, 30, "ATK Book: 35", isOne=False)
    draw_text(128, 20, "SPEED Book: 35", isOne=False)
    draw_text(128, 10, "ACC Book: 35", isOne=False)
    draw_text(0, 28, f"$ {money}", isOne=False)
    draw_text(0, 10, "Select ->", isOne=False)
    draw_text(0, 44, "Leave ->", isOne=False)
    d2.draw_rectangle(store_text_column, b1CY*10 - 2, SW-store_text_column, 12)
    d2.draw_rectangle(0, 0, SW, SH)
    return

def ui_bank(money, rate, lvl, account_value, b1C):
    b1CY = max(b1C, 1)
    cost = 10 * lvl
    rate = rate % 100 #until it is over 100..
    draw_text(128, 50, f"Intrest Rate: {rate}%", isOne=False)
    draw_text(128, 40, f"Bank Lvl: {lvl}", isOne=False)
    draw_text(128, 30, f"Deposit ({money})", isOne=False)
    draw_text(128, 20, f"Withdrawl ({account_value})", isOne=False)
    draw_text(128, 10, f"Upgrade: {cost}", isOne=False)
    draw_text(0, 10, "Select ->", isOne=False)
    draw_text(0, 44, "Leave ->", isOne=False)
    d2.draw_rectangle(store_text_column, b1CY*10 - 2, SW-store_text_column, 12)
    d2.draw_rectangle(0, 0, SW, SH)
    return

def run_rpg_battle_ui(player, b1C, ab1v, can_move_cursor):
    if can_move_cursor:
        if ab1v == 0:
            b1C -= 1
        if b1C < 0:
            b1C = 5
        can_move_cursor = False
    ui_display_battle(player, b1C)
    return b1C, can_move_cursor

def rpg_start_screen():
    screen_ba = rpg_start.load_start_screen()
    d1.draw_bitmap_array_raw(screen_ba, 0, 0, 117, 54)
    d1.present()
    return

def pick_character_type():
    choice_made = False
    cba, fire, daggers, sword = rpg_start.load_obj_sprites()
    (w, r, k) = rpg_start.psprites
    ww, wh = rpg_start.wizard_s
    rw, rh = rpg_start.rouge_s
    kw, kh = rpg_start.knight_s
    cx = 70
    cy = 42
    choice = None
    while not choice_made:
        loop_time = ticks_ms()
        if pressed(quit_b):
            print("ending early!")
            break

        x, y = util.get_button_dir(db1, db2, db3, db4, 2)
        ab1v = ab1.value()
        selection_made = ab1v == 0

        if selection_made:
            if cx < 24:
                choice = (w, 'w')
                atk_ba = fire
            elif cx < 66 and cx > 40:
                choice = (r, 'r')
                atk_ba = daggers
            elif cx < 114 and cx > 80:
                choice = (k, 'k')
                atk_ba = sword
            if not choice is None:
                choice_made = True

        cx += x
        cy += y

        cy = Constants.constrained_between(cy, 0, SH-14)
        cx = Constants.constrained_between(cx, 0, SW-14)

        d1.draw_bitmap_array_raw(w, 6, 0, ww, wh)
        d1.draw_bitmap_array_raw(r, 0 + ww + 20, 0, rw, rh)
        d1.draw_bitmap_array_raw(k, 0 + ww + rw + 38, 0, kw, kh)
        d1.draw_bitmap_array_raw(cba, cx, cy, 14, 14)
        draw_text(128, 48, "Choose class", padding=4, clear_first=False, isOne=False, isNotSmall=True)
        draw_text(118, 28, "Knight", padding=4, clear_first=False, isOne=False, isNotSmall=True)
        draw_text(74, 28, "Rouge", padding=4, clear_first=False, isOne=False, isNotSmall=True)
        draw_text(38, 28, "Wizard", padding=4, clear_first=False, isOne=False, isNotSmall=True)
        draw_text(0, 10, "-->", isOne=False)
        run_screens(loop_time)
    return choice, atk_ba


# is everything really needed here along with b1C? or can i clean and trim up
def check_input(b1C, can_move_cursor, player, ab1v):
    b1C, can_move_cursor = run_rpg_battle_ui(player, b1C, ab1v, can_move_cursor)
    selections = ['Run', 'Items', 'Magic', 'Shield', 'Attack']
    selection = None
    if ab2v == 0:
        selection = selections[b1C-1]
    return selection


def is_in(v1, v2, value):
    return value >= v1 and value <= v2

def rpg_world(player):
    show_fight_door = True
    d_sx = 12 # door start x and below end x's
    sd_ex = 70
    fd_ex = 79
    bd_ex = 63
    bs_ex = 114
    d_values = [fd_ex, sd_ex, bd_ex, bs_ex]
    d_check_value = 0
    ui_display(player, [], True, True)
    door_words = ["Battle", "Store", "Bank", "Boss"]
    curr_door = door_words[d_check_value]
    while True:
        loop_time = ticks_ms()

        if pressed(quit_b):
            print("ending early!")
            break

        x, y = util.get_button_dir(db1, db2, db3, db4, 5)
        
        if pressed(ab1):
            # use items menu
            print("I want to use items")
            if player.use_item("Potion"):
                ui_display(player, ["hp", "items"], False, True)
                sleep(.5)
        
        
        player.x += x
        if player.x >= 95:
            player.x = 0
            d_check_value += 1
            d_check_value %= len(door_words)
            curr_door = door_words[d_check_value]
        player.x = Constants.constrained_between(player.x, 0, SW - player.w)

        if curr_door == "Battle":
            d1.draw_bitmap_array_raw(fight_door, d_sx, 0, 67, 51)
        elif curr_door == "Store":
            d1.draw_bitmap_array_raw(shop_door, d_sx, 0, 58, 54)
        elif curr_door == "Bank":
            d1.draw_bitmap_array_raw(bank_door, d_sx, 0, 51, 63)
        elif curr_door == "Boss":
            d1.draw_bitmap_array_raw(boss_door, d_sx, 0, 51, 63)    
        next_door = door_words[(d_check_value + 1) % 3]
        draw_text(128, 50, f"<- {next_door}", padding=2, isOne=True)


        d1.draw_bitmap_array_raw(overworld_top, 0, SH-5, 128, 5) #overworld_top is 5 high
        d1.draw_bitmap_array_raw(player.choice, player.x, 0, player.w, player.h)
        if pressed(ab2):
            if is_in(d_sx, d_values[d_check_value], player.x):
                return curr_door

        # Not good for later im sure, need to preserve d2 UI... save time
        run_screens(loop_time, True, False)
    return


def rpg_battle_test(player, enemy_level, isBoss=False):
    b1C = 4
    selections = ['Run', 'Shield', 'Mana', 'Items', 'Attack']
    selection = None

    e_ba = None
    e_sizes = None
    name = None
    e_has_attacked = False
    turn_count = 1
    is_hard = False
    
    if isBoss:
        eatkbaw = 20
        eatkbah = 18
        e_ba, e_sizes, name, e_atk_ba = rpg_start.gen_ran_boss()
    else:
        eatkbaw = 9
        eatkbah = 10

        if enemy_level % 3 == 0:
            e_ba, e_sizes, name, e_atk_ba = rpg_start.gen_ran_enemy_h() #atk ba is 13x10
            eatkbaw = 13
            is_hard = True
        else:
            e_ba, e_sizes, name, e_atk_ba = rpg_start.gen_ran_enemy_e() #atk ba is 9x10

    e_projectiles = []

    ew, eh = e_sizes
    e_atk_move = 5
    ex = SW-ew-e_atk_move # little room for not off screen
    current_enemy = RPG_Enemy(enemy_level, ew, eh, name, is_hard, isBoss)
    # p_waiting, attack_made, enemy_attack_made, end? exit : go again
    battle_state = 1

    p_atk_miss_text_time = 600
    p_atk_missed = False
    p_atk_text = f"{current_enemy.hp:.2f}"
    prev_p_atk_time = ticks_ms()
    while True:
        if pressed(quit_b):
            print("ending early!")
            return False
        lt = ticks_ms()
        
        if isBoss and turn_count > 9:
            player.hp = 1
            print("out of time!")
            return False
    
        if p_atk_missed:
            if ticks_diff(lt, prev_p_atk_time) >= p_atk_miss_text_time:
                prev_p_atk_time = lt
                p_atk_text = f"{current_enemy.hp:.2f}"

        x, _ = util.get_button_dir(db1, db2, db3, db4, 3)
        player.x += x
        player.x = Constants.constrained_between(player.x, 0, SW - player.w - (ew - 3)) # cant walk on enemy
        player_blocked = False

        '''Waiting for player input'''
        if battle_state == 1:
            if pressed(db1):
                b1C += 1
                b1C %= 5
            elif pressed(db3):
                b1C -= 1
                b1C = max(0, b1C)

            if pressed(ab1):
                selection = selections[b1C]
                battle_state += 1
                print(f"Battle choice: {selection}")

        ''''''

        '''Handle Player Turn'''
        # for now to wait till bad ass art attack is done showing
        if len(e_projectiles) == 0:
            if battle_state == 2:
                if selection == 'Attack':
                    player.attack_list.append(Projectile(player.x, player.y + int(player.h *.4), randint(-99999, 99999), player.atk_w, player.atk_h, ba=player.atk_ba, speed=max(player.speed, 20)))
                    p_atk_turn = rpg_u.attack_calc(player, current_enemy, 1.15, 1, False, False, True, player.items)
                    battle_state += 1
                    current_enemy.hp -= p_atk_turn
                    #print(f"Player Atk made: {p_atk_turn}")
                    if p_atk_turn <= 0:
                        p_atk_text = 'Miss'
                        p_atk_missed = True
                    else:
                        p_atk_missed = False
                        p_atk_text = f"{current_enemy.hp:.2f}"
                    prev_p_atk_time = lt
                    #print(f"E health left: {current_enemy.hp}")
                elif selection == 'Shield':
                    player_blocked = True
                    battle_state += 1
                elif selection == 'Run':
                    return False
                elif selection == 'Items':
                    if player.use_item("Potion"):
                        battle_state += 1
                    else:
                        print("You had nothing, go again")
                        battle_state = 1
                else: # for now testing input - Need items and magic
                    player_blocked = True
                    battle_state += 1
                    
        ''''''

        # for now to wait till bad ass art attack is done showing
        if len(player.attack_list) == 0:
            '''Handle E Turn'''
            if battle_state == 3:
                battle_state = 4
                if current_enemy.hp > 0:
                    e_has_attacked = True
                    e_projectiles.append(Projectile(int(SW - ew + 3), int(eh * .6), randint(-99999, 99999), eatkbaw, eatkbah, ba=e_atk_ba, speed=int(max(max(current_enemy.speed, 8), 20))))
                    ex -= e_atk_move
                    e_atk_turn = rpg_u.attack_calc(current_enemy, player, 1.15, 1, False, player_blocked, False)
                    #print(f"Enemy Atk made: {e_atk_turn}")
                    player.hp -= e_atk_turn
                    #print(f"P health left: {player.hp}")
                else:
                    print("You win! looting")
                    loot = current_enemy.loot_table()
                    player.loot_victory(loot, current_enemy.lvl)
            ''''''

            '''Handle If Death'''
            if battle_state == 4:
                turn_count += 1
                if player.hp < 0 or current_enemy.hp < 0:
                    print("Done!")
                    battle_state = 0
                else:
                    battle_state = 1
            ''''''

        ui_display_battle(player, b1C)
        d1.draw_bitmap_array_raw(bg_top, 0, 0, 128, 14)
        d1.draw_bitmap_array_raw(e_ba, ex, 0, ew, eh)
        if e_has_attacked:
            e_has_attacked = False
            ex += e_atk_move
        draw_text(SW, 50, f"{p_atk_text}", isOne=True)    
        d1.draw_bitmap_array_raw(player.choice, player.x, player.y, player.w, player.h)

        player.attack_list = [p for p in player.attack_list if p.x < SW]
        for projectile in player.attack_list:
            d1.draw_bitmap_array_raw(projectile.ba, projectile.x, projectile.y, projectile.w, projectile.h)
            projectile.x += int(projectile.shot_speed_mult * 2) # for now

        e_projectiles = [p for p in e_projectiles if p.x > 0]
        for projectile in e_projectiles:
            d1.draw_bitmap_array_raw(projectile.ba, projectile.x, projectile.y, projectile.w, projectile.h)
            projectile.x -= int(projectile.shot_speed_mult) # ^

        run_screens(lt)

        if battle_state == 0:
            break
    return True

def rpg_shop_test(player):
    print("Shop")
    b1C = 0
    selection = None
    selections = ["Acc", "Speed", "Atk", "Def", "Potion"]
    shop_k_y = 0
    shop_k_x = 30
    bought = True
    
    show_text_time = 800
    buy_attempt = False
    shop_text = "please buy.. im hungry"
    prev_shop_buy = ticks_ms()
    active_bounce_delay = False
    shop_buy_bounce_delay = 120
    prev_active_bounce = ticks_ms()
    
    while True:
        if pressed(quit_b):
            print("ending early!")
            break
        
        lt = ticks_ms()
        if buy_attempt:
            if ticks_diff(lt, prev_shop_buy) >= show_text_time:
                prev_shop_buy = lt
                buy_attempt = False
        else:
            shop_text = "please buy.. im hungry"
            
        if active_bounce_delay:
            if not ticks_diff(lt, prev_active_bounce) >= shop_buy_bounce_delay:
                continue
            else:
                prev_active_bounce = lt

        if pressed(ab2):
            print("leaving shop")
            return 'leave'
        if pressed(db1):
            b1C += 1
            b1C %= 5
        elif pressed(db3):
            b1C -= 1
            b1C = max(0, b1C)
        ui_shop(player.money, b1C+1) # re use so need to add 1?
        #print(f"B1C: {b1C}")
        if pressed(ab1):
            selection = selections[b1C]
        if selection != None:
            buy_attempt = True
            cost = 35
            if selection == "Potion":
                cost = 10
            bought = handle_shop_choice(selection, player, cost)
            if not bought:
                shop_text = "nothing for me or you.."
            else:
                shop_text = "Yay you Buy'd '_' "
            selection = None
            active_bounce_delay = True
            prev_shop_buy = lt #...hmmmm
            prev_active_bounce = lt
        d1.draw_bitmap_array_raw(shop_keep, shop_k_x, shop_k_y, 63, 47)
        draw_text(max(min(shop_k_x + 63, SW), 0), max(shop_k_y - 5, 0), f"{shop_text}", isOne=True)
        shop_k_y += randint(-2, 2)
        shop_k_x += randint(-5, 5)
        shop_k_x = Constants.constrained_between(shop_k_x, 0, SW - 63)
        shop_k_y = Constants.constrained_between(shop_k_y, 0, SH - 47)
        run_screens(lt)
    
    return

def handle_shop_choice(selection, player, cost):
    money = player.money
    if money >= cost:
        player.get_item(selection)
        player.money -= cost
        return True
    return False

def bank_deposit_withdrawl_ui(player):
    print("Loading bank deposit UI")
    b1C = 0
    total = 0
    d1.draw_bitmap_array_raw(bank_bg, 0, 0, 113, 64)
    bank_move_rate = max(int(player.bank_account * .05), 10)
    while True:
        lt = ticks_ms()
        if pressed(quit_b):
            print("ending early!")
            break
        b1CY = max(b1C, 1)
        if pressed(db3):
            b1C += 1
            b1C %= 3
            sleep(.1)
        if pressed(db1):
            b1C -= 1
            b1C = max(0, b1C)
            sleep(.1)
        if pressed(ab2):
            break

        if pressed(ab1):
            # check if player has enough money (done on action)
            total += bank_move_rate
        draw_text(128, 20, f"+{bank_move_rate}", isOne=False)
        draw_text(128, 40, f"-{bank_move_rate}", isOne=False)
        draw_text(0, 44, "OK", isOne=False)
        draw_text(0, 10, "Select ->", isOne=False)
        d2.draw_rectangle(0, b1CY*20 - 2, SW, 12)
        d2.draw_rectangle(0, 0, SW, SH)

        draw_text(128, 50, f"{total}", isOne=False)
        run_screens(lt, clear_one=False)
    return total

def handle_bank_choice(choice, player):
    val = None
    if choice == 'u':
        cost = player.bank_level * 33
        if player.money >= cost:
            player.bank_level += 1
            player.bank_intrest += 1
            player.money -= cost
            # TODO: need to modify UI changed value to reflect new bank_level, intrest rate and upgrade cost....
        #check player money is enough for curr_player_bank_cost <- base it on curr bank level?
    elif choice == 'd':
        # get some kind of amount *_;
        val = bank_deposit_withdrawl_ui(player)
        deposited_amount = min(player.money, val)
        player.money -= deposited_amount
        player.bank_account += deposited_amount
        # add to player bank amount, decrement player money
    elif choice == 'w':
        val = bank_deposit_withdrawl_ui(player)
        withdrawl_amount = min(player.bank_account, val)
        player.bank_account -= withdrawl_amount
        player.money += withdrawl_amount
        # another UI.... with some amount to enter ;_*
        # inverse above
    return val

def rpg_bank(player):
    b1C = 0
    # TODO: upon loading bank, handle days past and accrue interest
    options = ["u", "w", "d"]
    while True:
        lt = ticks_ms()
        if pressed(ab2):
            print("Leaving shop")
            return 'leave'
        if pressed(quit_b):
            print("ending early!")
            break
        if pressed(db1):
            b1C += 1
            b1C %= 3
        elif pressed(db3):
            b1C -= 1
            b1C = max(0, b1C)
        elif pressed(ab1):
            print("Bank action")
            choice = options[b1C] # why is it named b1C? wakademasen
            print(choice)
            money_change = handle_bank_choice(choice, player)
            if money_change != None:
                print(f"Deposit or withdrawl: {money_change}")
                # preform modify on player money +- to money and bank_account
            else:
                print("upgrade done!")
        ui_bank(player.money, player.bank_intrest, player.bank_level, player.bank_account, b1C+1) # re use so need to add 1?
        d1.draw_bitmap_array_raw(bank_bg, 0, 0, 113, 64)
        run_screens(lt)
    return

def run_the_sequence():
    enemy_level = 1
    boss_rank = 1
    while True:
        if pressed(quit_b):
            print("ending early!")
            break
        choice = rpg_world(player)
        sleep(.5)
        if choice == "Battle":
            val = rpg_battle_test(player, enemy_level)
            if val:
                enemy_level += 1
                print("Enemy level up: ", enemy_level)
                player.handle_money_intrest()
            else:
                print("you ran..")
        if choice == "Boss":
            val = rpg_battle_test(player, enemy_level, isBoss=True)
            if val:
                boss_rank += 1
                print("Boss rank up: ", boss_rank)
                player.handle_money_intrest()
            else:
                print("you ran..")
        elif choice == "Store":
            val = rpg_shop_test(player)
            if val == 'leave':
                choice = ''
                sleep(.5)
            player.apply_items_bought()
        elif choice == "Bank":
            val = rpg_bank(player)
            if val == 'leave':
                choice = ''
                sleep(.5)
        else:
            print("Hmm how did you do this?")
    return

rpg_start_screen()
sleep(1)
rpg_choice, atk_ba = pick_character_type()
choice, letter = rpg_choice

d2.clear_buffers()
d1.clear_buffers()
player.be_born(choice, letter, atk_ba)
sleep(.35)
run_the_sequence()
d1.cleanup()
d2.cleanup()


print('Done.')
