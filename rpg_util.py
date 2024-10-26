from random import randint
from math import ceil
class RPG_Util:
    def __init__(self):
        # poinson damage %, sleep/blind/slow/confuse -> chance to wake/chance to miss/speed reduction/chance to self hit
        self.ailment_dict = {
            "poison": .05,
            "sleep": .6,
            "blind": .6,
            "slow": .6,
            "confuse": .4
        }
        
    @staticmethod
    def max_x(value):
        return 128 - value
    @staticmethod
    def max_y(value):
        return 64 - value
    @staticmethod
    def constrained_between(coord, lower_bound, upper_bound):
        return max(lower_bound, min(coord, upper_bound))
    
    # attacker attack, defender defense, defender speed, attack accuracy, attacker cd + 1, any bonus modifier, attacker lvl, defender lvl
    def attack_calc(self, a, d, s, ac, cd, modifier, al, dl, isRage, isBlock, player_rds=None):
        roll = randint(0, 100)
        hit_chance = ac / (ac + s) + 30 # clearly needs rework 
        isHit = roll < hit_chance
        if not isHit:
            return 0
        
        base = (a ** 2) / (a + d)
        crit_chance = (s/200) + cd
        damage = base * (1 + modifier/100)

        if crit_chance > 100:
            over_accurate = crit_chance - 100
            if roll < over_accurate:
                damage *= cd
        
        is_crit = roll < crit_chance
        
        if is_crit:
            damage *= cd
        
        if isBlock:
            damage *= 0.5
        if isRage:
            damage *= 1.3

        al_mult = 1 + (al/100)
        dl_mult = 1 + (dl/100)

        damage *= al_mult
        damage *= dl_mult
        if not player_rds is None:
            damage *= (1 + 0.05) ** (player_rds - 1)
        
        return ceil(damage)
    
    # need to be able to diff if it is poison and how to actually handle these with a util
    def handle_ailmnts(self, ailments):
        modifiers = []
        for ailment in ailments:
            modifiers.append(self.ailment_dict[ailment])
        return modifiers