from time import sleep
class Life():
    def __init__(self, grid, generations, size, rate, width, height):
        self.grid = grid
        self.generations = generations
        self.size = size
        self.rate = rate
        self.width = width
        self.height = height

    
    def count_neighbors(self, grid, x, y):
        neighbors = 0
        for px in [-1, 0, 1]:
            for py in [-1, 0, 1]:
                if px == 0 and py == 0:
                    continue
                xv = x + px
                yv = y + py
                if xv >= self.width:
                    xv %= self.width
                if xv < 0:
                    xv = self.width + xv
                if yv >= self.height:
                    yv %= self.height
                if yv < 0:
                    yv = self.height + yv
                neighbors += grid[xv][yv]
        return neighbors
    
    def update_grid(self, grid):
        new_grid = [[0 for _ in range(len(grid[0]))] for _ in range(len(grid))]
        #for gen in range(self.generations):
        for row_idx, row in enumerate(grid):
            for col_idx, ele in enumerate(row):
                live = self.count_neighbors(grid, row_idx, col_idx)
                if grid[row_idx][col_idx] == 1:
                    new_grid[row_idx][col_idx] = 1 if live in (2, 3) else 0
                else:
                    new_grid[row_idx][col_idx] = 1 if live == 3 else 0
            #sleep(self.rate)
        return new_grid
   
        
            
    # determine grid inner width -> that will be image width like my profiles above
    def show_self(self, g, nextGen=False):
        byteArrayWidthTotal = 0
        gridDisplayW = 0
        gridY = len(g)
        live_count = 0
        dead_count = 0
        for x in range(gridY):
            gridDisplayW = len(g[x])
            byteArrayWidthTotal += gridDisplayW
        lifeArray = bytearray(byteArrayWidthTotal)
        for x in range(gridY):
            for y in range(gridDisplayW):
                byteIdx = y + (gridDisplayW * x)
                if g[x][y] == 1:
                    live_count+=1
                    lifeArray[byteIdx] = 255
                else:
                    lifeArray[byteIdx] = 0
                    dead_count+=1

        print(f"live_count: {live_count} && dead_count: {dead_count}")
        if nextGen:
            return (lifeArray, live_count)
        return (lifeArray, gridDisplayW, gridY)
