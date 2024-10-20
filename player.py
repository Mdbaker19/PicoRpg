from constants import Constants
class Player:
    def __init__(self, x, y, lvl, exp, expReq, hp, attack, defense, speed, mana, money):
        self.lvl = lvl
        self.exp = exp
        self.expReq = expReq * 100
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.mana = mana
        self.money = money

    def change_value(self, attr, value, isReplacing=False):
        if hasattr(self, attr):
            if isReplacing:
                setattr(self, attr, value)
            else:
                setattr(self, attr, getattr(self, attr) + value)
        else:
            print(f"What is /{attr}/ for Player")
            
    # will return the new x, y and profiles, and optional has_moved_screens
    def handle_movement(self, x, y, spriteH, spriteW, player_ba_list, b1v, b2v, starting_on_top_screen=False):
        on_top_screen = starting_on_top_screen
        crossed_screens = False

        profile, xmover, ymover = self.get_dir_profile(player_ba_list, b1v, b2v)

        x += xmover
        y += ymover

        spriteAtTop = y > Constants.max_y(spriteH)
        spriteAtLeft = x >= Constants.max_x(spriteW)

        if spriteAtLeft:
            x = Constants.max_x(spriteW)
        elif x <= 0:
            x = 0

        if spriteAtTop and on_top_screen:  # bound to top screen top
            y = Constants.max_y(spriteH)
        elif y <= 0 and on_top_screen:  # move from top screen to bottom screen
            y = Constants.max_y(spriteH)
            on_top_screen = False
            crossed_screens = True
        elif spriteAtTop and not on_top_screen:  # move from bottom screen to top screen
            y = 0
            on_top_screen = True
            crossed_screens = True
        elif y <= 0 and not on_top_screen:  # bound to bottom of bottom screen
            y = 0

        return profile, x, y, crossed_screens, on_top_screen

            
    def get_dir_profile(self, profiles, b1v, b2v):
        left = bytearray(profiles['sprite_left'])
        right = bytearray(profiles['sprite_right'])
        front = bytearray(profiles['sprite_front'])
        back = bytearray(profiles['sprite_back'])
        going_left = b1v == 1 and b2v == 0
        going_right = b1v == 0 and b2v == 1
        going_up = b1v == 1 and b2v == 1
        going_down = b1v == 0 and b2v == 0
        sprite_arr = front
        ymover = 0
        xmover = 0
        if going_down:
            sprite_arr = back
            ymover = 4
            xmover = 0
        elif going_up:
            sprite_arr = front
            ymover = -4
            xmover = 0
        elif going_left:
            sprite_arr = left
            xmover = 5
            ymover = 0
        elif going_right:
            sprite_arr = right
            xmover = -5
            ymover = 0
        return sprite_arr, xmover, ymover