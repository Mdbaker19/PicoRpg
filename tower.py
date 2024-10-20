class Tower():
    def __init__(self, x, y, distance, damage, projectiles, shoot_time, ba, target=None):
        self.x = x
        self.y = y
        self.ba = ba
        self.distance = distance
        self.damage = damage
        self.projectiles = projectiles
        self.target = target
        self.shoot_time = shoot_time
        
    def update_attr(self, attr, value, isReplacing=False):
        if hasattr(self, attr):
            if isReplacing:
                setattr(self, attr, value)
            else:
                setattr(self, attr, getattr(self, attr) + value)
        else:
            print(f"What is /{attr}/ for Tower")
