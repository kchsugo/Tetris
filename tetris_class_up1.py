from matrix import *
import random
from enum import Enum
from collections import deque
DEFINE_DX = 10
DEFINE_DY = 15
DEFINE_DW = 4

class TetrisState(Enum):
    Running = 0
    NewBlock = 1
    Finish = 2


class Tetris:
    arrayBlk = [[[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]], 
        [[1, 1, 0], [0, 1, 1], [0, 0, 0]],
        [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
        [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
        [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
        [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
        [[1, 1], [1, 1]]]

    rotateBlk = []

    @classmethod
    def init_static_blocks(cls):
        if cls.rotateBlk:
            return

        for base_rot in cls.arrayBlk:
            rotations = [Matrix(base_rot)]
            tmp = base_rot
            for _ in range(3):
                tmp = cls.rotate_arr(tmp)
                rotations.append(Matrix(tmp))
            cls.rotateBlk.append(rotations)
    
    @staticmethod
    def start_line(arr):
        for i, row in enumerate(arr):
            if any(cell != 0 for cell in row):
                return i
        return 0

    @staticmethod
    def rotate_arr(arr):
        dx = len(arr)
        dy = len(arr[0])
        return [[arr[j][i] for j in range(dx-1, -1, -1)] for i in range(dy)]

    @staticmethod
    def check_collision(screen, block, top, left):
        tmp = screen.clip(top, left, 
                top + block.get_dy(), 
                left + block.get_dx()
                )
        tmp = tmp + block
        return tmp.anyGreaterThan(1)
    
    def merge_block(self):
        tmp = self.iScreen.clip(self.top, self.left, 
                self.top + self.currBlk.get_dy(), 
                self.left + self.currBlk.get_dx()
                )
        tmp = tmp + self.currBlk
        self.iScreen.paste(tmp, self.top, self.left)
   
    def clear_filled_lines(self):
        array = self.iScreen.get_array()
        write_row = self.dy - 1
        for read_row in range(self.dy - 1, -1, -1):
            row_data = array[read_row][self.dw:self.dw + self.dx]
            if sum(row_data) < self.dx:
                if write_row != read_row:
                    array[write_row][self.dw:self.dw + self.dx] = row_data[:]
                write_row -= 1

        for r in range(write_row, -1, -1):
            array[r][self.dw:self.dw + self.dx] = [0] * self.dx


    def __init__(self, dy = DEFINE_DY, dx = DEFINE_DX, dw = DEFINE_DW):
        self.dy = dy
        self.dx = dx
        self.dw = dw
        self.top = 0 
        self.left = dw + dx // 2 - 2
        self.state = TetrisState.NewBlock
        self.idxBlockType = -1
        self.idxBlockDegree = -1
        self.iScreen=Matrix([[1] * self.dw + [0] * self.dx + [1] * self.dw for _ in range(self.dy)] + [[1] * (self.dx + 2 * self.dw)] * self.dw)

        self.oScreen = Matrix(self.iScreen)
        self.currBlk = None

        Tetris.init_static_blocks()
        self.new_block()

    def update_oScreen(self):
        self.oScreen = Matrix(self.iScreen)   
        tempBlk = self.oScreen.clip(self.top, self.left, 
                self.top + self.currBlk.get_dy(), 
                self.left + self.currBlk.get_dx()
                )
        tempBlk += self.currBlk
        self.oScreen.paste(tempBlk, self.top, self.left)


    def new_block(self, blockType = None, blockDegree = None):
        self.idxBlockType = blockType if blockType is not None else random.randint(0, 6)
        self.idxBlockDegree = blockDegree if blockDegree is not None else random.randint(0, 3)
        self.currBlk = Tetris.rotateBlk[self.idxBlockType][self.idxBlockDegree]
        start = Tetris.start_line(self.currBlk.get_array()) 
        self.currBlk = Matrix(self.currBlk.get_array()[start:])
        self.top = 0
        self.left = self.dw + self.dx // 2 - self.currBlk.get_dx() // 2
        
        if Tetris.check_collision(self.iScreen, self.currBlk, self.top, self.left):
            self.state = TetrisState.Finish
        else:
            self.state = TetrisState.Running
        
        self.update_oScreen()

    def accept(self, key):
        if key == 'q':
            print("Game terminated...")
            self.state = TetrisState.Finish
            return self.oScreen


        if self.state == TetrisState.Finish:
            print("Game Over!")
            return self.oScreen
        
        elif self.state == TetrisState.NewBlock:
            self.new_block()
            if self.state == TetrisState.Finish:
                print("Game Over!")
                return self.oScreen
            self.state = TetrisState.Running
            return self.oScreen

        top = self.top
        left = self.left
        tempBlk = self.currBlk
        deg = self.idxBlockDegree
        idx = self.idxBlockType
        newBlockNeeded = False

        if key == 'a':
            left -= 1
        elif key == 'd':
            left += 1
        elif key == 's':
            top += 1
        elif key == 'w':
            deg = (deg + 1) % 4
            tempBlk = Tetris.rotateBlk[idx][deg]
        elif key == ' ':
            while not Tetris.check_collision(self.iScreen, tempBlk, top+1, left):
                top += 1
            newBlockNeeded = True
        elif key in '0123456':
            self.new_block(int(key))
            return self.oScreen
        else:
            print("wrong key")
            return self.oScreen

        if Tetris.check_collision(self.iScreen, tempBlk, top, left):
            if key == 'a':
                left += 1
            elif key == 'd':
                left -= 1
            elif key == 's':
                top -= 1
                newBlockNeeded = True
            elif key  == 'w':
                deg = (deg +3) % 4
                tempBlk = Tetris.rotateBlk[idx][deg]
            elif key == ' ':
                top -= 1
                newBlockNeeded = True
            else:
                print("wrond key")
                return self.oScreen
            
        self.top = top
        self.left = left
        self.currBlk = tempBlk
        self.idxBlockType = idx
        self.idxBlockDegree = deg
        self.update_oScreen()

        if newBlockNeeded:
            self.merge_block()
            self.clear_filled_lines()
            self.state = TetrisState.NewBlock
            self.new_block()

        return self.oScreen
    
    
    def draw_matrix(self):
            array = self.oScreen.get_array()
            for y in range(self.oScreen.get_dy()):
                for x in range(self.oScreen.get_dx()):
                    if array[y][x] == 0:
                        print("□", end = '')
                    elif array[y][x] == 1:
                        print("■", end = '')
                    else:
                        print("XX", end = '')
                print()


    #Getter method
    def get_state(self):
        return self.state
    
    def get_currBlk(self):
        return self.currBlk



if __name__ == "__main__":
    t = Tetris()
    t1 = Tetris(15,15,4)
   
    while True: 
        t.draw_matrix()
        print("<first tetris game key>")
        key = input('Enter a key from [ q (quit), a (left), d (right), s (down), w (rotate), \' \' (drop) ] : ') 

        print("\n\n")
        
        t1.draw_matrix()
        print("<second tetris game key>")
        key1 = input('Enter a key from [ q (quit), a (left), d (right), s (down), w (rotate), \' \' (drop) ] : ')
       
        print("\n-----------------------------------------------------------------------------------------------\n") 

        t.accept(key) 
        t1.accept(key1)
        if t.state == TetrisState.Finish or t1.state == TetrisState.Finish:
            print("Game Over!")
            break  


