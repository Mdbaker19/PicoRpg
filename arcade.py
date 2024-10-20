import random

class Arcade():
    def __init__(self, ba, goals):
        self.ba = ba
        self.goals = goals
        

class Ball():
    def __init__(start_x, x, y):
        self.start_x = start_x
        self.x = x
        self.y = y
        
    def get_dir(self):
        return random.randint(0, 100) >= 50
    
    def set_x_by_portal(self, x, portal_entry):
        portal = 0
        return portal