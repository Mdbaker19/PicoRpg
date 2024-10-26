import math

class Util():
    def __init__(self):
        pass
    
    def distance(p1, p2):
        return (p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2
    def is_point_in_range(tower, target, prange):
        return distance(tower, target) <= prange

    
    # maybe need to address this hitbox since i am getting centerX and Y, maybe /2 here or before calling?
    # assign enemy objects or such a needToCheckCollision property so this is not done unecessarily 
    def check_for_collision(self, obj1_x, obj1_y, obj1_w, obj1_h, obj2_x, obj2_y, obj2_w, obj2_h, hit_box_mult=0.8):
        hitbox = math.sqrt(obj2_w * obj2_w + obj2_h * obj2_h) * hit_box_mult
        dist = self._distance_check(obj1_x, obj1_y, obj1_w, obj1_h, obj2_x, obj2_y, obj2_w, obj2_h)
        if dist < hitbox:
            return self._collision_check(obj1_x, obj1_y, obj1_w, obj1_h, obj2_x, obj2_y, obj2_w, obj2_h)
        return False
    
    def _collision_check(self, obj1_x, obj1_y, obj1_w, obj1_h, obj2_x, obj2_y, obj2_w, obj2_h):
        #ob1_x, ob1_y = self._get_center_x(obj1_x, obj1_y, obj1_w, obj1_h)
        #ob2_x, ob2_y = self._get_center_x(obj2_x, obj2_y, obj2_w, obj2_h)
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
        
    def get_direction_vector(self, t, e):
        #tx, ty = self._get_center_x(t.x, t.y, 14, 19)
        #ex, ey = self._get_center_x(e.y, e.y, e.size, e.size)
        dx = e.x - t.x
        dy = e.y - t.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance != 0:
            dx /= distance
            dy /= distance
        return dx, dy
        
        '''
    def zip_longest(l1, l2, dfv=None):
        max_len = max(len(l1), len(l2))
        for i in range(max_len):
            v1 = l1[i] if i < len(l1)
            v2 = l2[i] if i < len(l2)
            yield v1, v2
    '''
    
    def is_on_screen(self, p):
        return p.x <= 128 and p.x >= 0 and p.y >= 0 and p.y <= p.y <= 64
    
    def _get_center_x(self, obj_x, obj_y, obj_w, obj_h):
        cx = obj_x + obj_w / 2
        cy = obj_y + obj_h / 2
        return (cx, cy)