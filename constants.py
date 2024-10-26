class Constants:
    @staticmethod
    def max_x(value):
        return 128 - value
    @staticmethod
    def max_y(value):
        return 64 - value
    @staticmethod
    def constrained_between(coord, wh, isX=False):
        coord = max(coord, 0)
        if isX:
            if coord >= max_x(wh):
                coord = max_x(wh)
        else:
            if coord >= max_y(wh):
                coord = max_y(wh)
        return coord
