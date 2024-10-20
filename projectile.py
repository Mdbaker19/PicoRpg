class Projectile:
    def __init__(self, x, y, ide, ba=None, path=None):
        self.x = x
        self.y = y
        self.ba = ba
        self.ide = ide
        self.path = path
        
    def increment_x(self, val):
        self.x += val
        
    def increment_y(self, val):
        self.y += val