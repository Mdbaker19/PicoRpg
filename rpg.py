import random
import math
import json
class RPG:
    def __init__(self):
        self.esprites = self.load_esprites()
        self.besprites = self.load_basic_esprites()
        self.psprites = self.load_psprites()
        self.wizard_s = (27,64)
        self.rouge_s = (28,49)
        self.knight_s = (28,62)
    def load_psprites(self):
        pdata = None
        with open('rpg_players.json', 'r') as file:
            pdata = json.load(file)
        w = bytearray(pdata['wizard'])
        r = bytearray(pdata['rouge'])
        k = bytearray(pdata['knight'])
        return (w, r, k)
    def load_esprites(self):
        edata = None
        with open('rpg_sprites.json', 'r') as file:
            edata = json.load(file)
        al = bytearray(edata['alien'])
        sb = bytearray(edata['sqrew_bot'])
        jar = bytearray(edata['jar'])

        return [al, sb, jar]
    
    def load_basic_esprites(self):
        edata = None
        with open('rpg_e_one_sprites.json', 'r') as file:
            edata = json.load(file)
        sl = bytearray(edata['slime'])
        sn = bytearray(edata['snail'])
        ft = bytearray(edata['fat'])
        k_deformed = bytearray(edata['k_deformed'])

        return [sl, sn, ft, k_deformed]
    
    # load attacks and assign the sizes to the player and maybe the ba to the player too
    def load_obj_sprites(self):
        odata = None
        with open('rpg_objects.json', 'r') as file:
            odata = json.load(file)
        cursor = bytearray(odata['cursor'])
        fireball = bytearray(odata['fireball'])
        dagger = bytearray(odata['dagger'])
        sword = bytearray(odata['sword'])
        return cursor, fireball, dagger, sword
    
    def load_bg_sprites(self):
        d = None
        with open('background.json', 'r') as file:
            d = json.load(file)
        door = d['hall_w_door']
        return bytearray(door)

    def load_start_screen(self):
        d = None
        with open('intro.json', 'r') as file:
            d = json.load(file)
        screen = d['screen']
        return bytearray(screen)
    
    def gen_ran_enemy_h(self):
        vals = [(71,55), (81,65), (35,50)]
        names = ['alien', 'screw_bot', 'jar']
        r = random.randint(0, len(self.esprites) - 1)
        return self.esprites[r], vals[r], names[r]
    
    
    def gen_ran_enemy_e(self):
        vals = [(55,28), (62,38), (48,41), (47,34)]
        names = ['slime', 'snail', 'fat', 'k_deformed']
        r = random.randint(0, len(self.besprites) - 1)
        return self.besprites[r], vals[r], names[r]

class RPG_Player:
    def __init__(self, lvl, hp=None, max_hp=None, acc=None, defense=None, attack=None, mana=None, max_mana=None, choice=None, class_type=None, speed=None, w=None, h=None, atk_w=None, atk_h=None, atk_ba=None, money=None, bank_account=None, victories=0):
        self.lvl = lvl
        self.hp = hp
        self.max_hp = max_hp
        self.defense = defense
        self.acc = acc
        self.attack = attack
        self.mana = mana
        self.max_mana = max_mana
        self.choice = choice # the ba for sprite
        self.class_type = class_type
        self.w = w
        self.h = h
        self.x = 0
        self.y = 0
        self.atk_ba = atk_ba
        self.atk_w = atk_w
        self.atk_h = atk_h
        self.victories = victories
        self.speed = speed
        self.money = money
        self.bank_account = bank_account
        self.items = {}
        self.attack_list = []
        self.exp = 0
        self.expReq = self.lvl * 100
        self.bank_interest = 103
        
    def handle_money_interst(self):
        value = self.bank_account * self.bank_interest
        value /= 100
        self.bank_account += math.ceil(value)
        
    def be_born(self, choice, letter, atk_ba):
        self.choice = choice
        self.atk_ba = atk_ba
        self.money = 0
        self.bank_account = 1
        speed = 5
        aw, ah = (24,25)
        acc = 60
        attack = 6
        mana = 5
        max_mana = 5
        class_type = 'Knight'
        hp = 30
        max_hp = 30
        defense = 25
        w, h = (28,62)
        if letter == 'r':
            speed = 10
            hp = 18
            aw, ah = (22,13)
            max_hp = 18
            acc = 70
            attack = 3
            mana = 15
            max_mana = 15
            defense = 18
            class_type = 'Rougue'
            w, h = (28,49)
        elif letter == 'w':
            speed = 10
            hp = 15
            max_hp = 15
            aw, ah = (18,18)
            acc = 65
            attack = 3
            class_type = 'Wizard'
            mana = 15
            max_mana = 15        
            defense = 15
            w, h = (27,64)

        self.speed = speed
        self.max_mana = max_mana
        self.attack = attack
        self.acc = acc
        self.mana = mana
        self.hp = hp
        self.max_hp = max_hp
        self.defense = defense
        self.class_type = class_type
        self.w = w
        self.h = h
        self.atk_w = aw
        self.atk_h = ah
        
    def get_item(self, item):
        if item in self.items:
            self.items[item] += 1
        else:
            self.items[item] = 1
            
    def level_up(self):
        self.lvl += 1
        self.exp %= self.expReq
        self.expReq += 100
        # will come back to
        self.attack += 1
        self.defense += 1
        self.acc += 2
        self.speed += 1
        self.max_mana += 2
        self.max_hp += 3
            
    def loot_victory(self, loot_table_values, elvl):
        loot_exp, loot_money, loot_dr = loot_table_values
        roll = random.randint(0, 100)
        base = 5 * elvl
        if roll < math.ceil(loot_dr * base):
            self.get_item('RD')
        self.exp += math.ceil(loot_exp * base)
        if self.exp >= self.expReq:
            self.level_up()
        self.money += math.ceil(loot_money * base)
        self.handle_money_interst()

# E lvl 3 seems better of a start so modify stats for that
class RPG_Enemy:
    def __init__(self, lvl, w, h, name):
        self.lvl = lvl
        self.name = name
        self.hp = 6 * ((1 + 0.07) ** lvl-1)
        self.acc = 60 + (2 ** lvl-1) - 2
        self.speed = 5 * ((1 + 0.03) ** lvl-1)
        self.attack = 5 * ((1 + 0.05) ** lvl-1)
        self.defense = 4 * ((1 + 0.04) ** lvl-1)
        self.w = w
        self.h = h
        
    
    def loot_table(self):
        # All mults: exp, money, drop rarity
        loot_table = {
            "alien": [1.8, 1.6, 1.8],
            "screw_bot": [2.0, 1.4, 1.6],
            "jar": [1.4, 1.8, 2.0],
            "slime": [1.2, 1.1, 1.0],
            "snail": [1.2, 1.3, 1.1],
            "fat": [1.4, 1.4, 1.0],
            "k_deformed": [0.8, 0.6, 2.0]
        }
        return loot_table[self.name]
        
        
    
    