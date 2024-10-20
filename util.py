import math

class Util():
    def __init__(self):
        pass
    

    # returns binary array to then be rendered
    # or collision detection
    
    # maybe need to address this hitbox since i am getting centerX and Y, maybe /2 here or before calling?
    # assign enemy objects or such a needToCheckCollision property so this is not done unecessarily 
    def check_for_collision(self, obj1_x, obj1_y, obj1_w, obj1_h, obj2_x, obj2_y, obj2_w, obj2_h, hit_box_mult=0.8):
        hitbox = math.sqrt(obj2_w * obj2_w + obj2_h * obj2_h) * hit_box_mult
        dist = self._distance_check(obj1_x, obj1_y, obj1_w, obj1_h, obj2_x, obj2_y, obj2_w, obj2_h)
        if dist < hitbox:
            return self._collision_check(obj1_x, obj1_y, obj1_w, obj1_h, obj2_x, obj2_y, obj2_w, obj2_h)
        return False
    
    def _collision_check(self, obj1_x, obj1_y, obj1_w, obj1_h, obj2_x, obj2_y, obj2_w, obj2_h):
        is1X = obj1_x < obj2_x + obj2_w
        if not is1X: return False
        is2X = obj1_x + obj1_w > obj2_w
        if not is2X: return False
        is1Y = obj1_y < obj2_y + obj2_h
        if not is1Y: return False
        is2Y = obj1_y + obj1_h > obj2_y
        return is1X and is2X and is1Y and is2Y
    
    def _distance_check(self, obj1_x, obj1_y, obj1_w, obj1_h, obj2_x, obj2_y, obj2_w, obj2_h):
        (cx1, cy1) = self._get_center_x(obj1_x, obj1_y, obj1_w, obj1_h)
        (cx2, cy2) = self._get_center_x(obj2_x, obj2_y, obj2_w, obj2_h)
        dx = cx1  - cx2
        dy = cy1 - cy2
        return math.sqrt(dx * dx + dy * dy)
        
    def get_slope_path(self, one, two):
        try:
            slope = (two.y - one.y) / (two.x - one.x)
            if isinstance(slope, int):
                return slope, 1
            return math.modf(slope)
        except ZeroDivisionError:
            return (two.y - one.y), 0
        
        '''
    def zip_longest(l1, l2, dfv=None):
        max_len = max(len(l1), len(l2))
        for i in range(max_len):
            v1 = l1[i] if i < len(l1)
            v2 = l2[i] if i < len(l2)
            yield v1, v2
    '''
    
    def _get_center_x(self, obj_x, obj_y, obj_w, obj_h):
        cx = obj_x + obj_w / 2
        cy = obj_y + obj_h / 2
        return (cx, cy)