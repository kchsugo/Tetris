from matrix import *
import random
from enum import Enum
from collections import deque
from abc import ABC, abstractmethod

DEFINE_DX = 10
DEFINE_DY = 15
DEFINE_DW = 4
DEFINE_BLOCK = 7

class TetrisState(Enum):
    Running = 0
    NewBlock = 1
    Finish = 2

class ActionHandler(ABC):
    @abstractmethod
    def run(self, tetris):
        pass

class OnLeft(ActionHandler):
    def run(self, tetris):
        tetris._move_block(dx = -1, dy = 0)

class OnRight(ActionHandler):
    def run(self, tetris):
        tetris._move_block(dx = 1, dy = 0)

class OnDown(ActionHandler):
    def run(self, tetris):
        tetris._move_block(dx = 0, dy = 1)

class OnDrop(ActionHandler):
    def run(self, tetris):
        while not tetris.check_collision(tetris.iScreen,
                tetris.currBlk,
                tetris.top,
                tetris.left):

            tetris.top += 1

class OnCw(ActionHandler):
    def run(self, tetris):
        tetris._rotate_block(deg = 1)

class OnCcw(ActionHandler):
    def run(self, tetris):
        tetris._rotate_block(deg = -1)

class NewBlock(ActionHandler):
    def __init__(self, blockType = None, blockDegree = None):
        self.blockType = blockType
        self.blockDegree = blockDegree

    def run(self, tetris):
        tetris.new_block(self.blockType, self.blockDegree)

class OnUp(ActionHandler):
    def run(self, tetris):
        tetris._move_block(dx = 0, dy = -1)


class TetrisOperation:
    def __init__(self, handler, postAState, counterHandler = None, postCState = None):
        self.handler = handler
        self.postAState = postAState
        self.counterHandler = counterHandler
        self.postCState = postCState



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
   
    def _merge_block(self):
        tmp = self.iScreen.clip(self.top, self.left, 
                self.top + self.currBlk.get_dy(), 
                self.left + self.currBlk.get_dx()
                )
        tmp = tmp + self.currBlk
        self.iScreen.paste(tmp, self.top, self.left)
   
    def _clear_filled_lines(self):
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
        self.operate = {}
        Tetris.init_static_blocks()
        self.new_block()

    def _update_oScreen(self):
        self.oScreen = Matrix(self.iScreen)   
        tempBlk = self.oScreen.clip(self.top, self.left, 
                self.top + self.currBlk.get_dy(), 
                self.left + self.currBlk.get_dx()
                )
        tempBlk += self.currBlk
        self.oScreen.paste(tempBlk, self.top, self.left)

    def new_block(self, blockType = None, blockDegree = None):
        self.idxBlockType = blockType if blockType is not None else random.randrange(DEFINE_BLOCK)
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
        
        self._update_oScreen()
    
    def _move_block(self, dx, dy):
        self.top += dy
        self.left += dx



    def _rotate_block(self, deg):
        deg = (self.idxBlockDegree + deg) %4
        self.idxBlockDegree = deg
        self.currBlk = Tetris.rotateBlk[self.idxBlockType][deg]

        

    def accept(self, key):
        op = self.operate.get((self.state, str(key)))
        
        if op is None:
            print("wrong key entered")
            return

        op.handler.run(self)
        if Tetris.check_collision(self.iScreen, self.currBlk, self.top, self.left):
            if op.counterHandler:
                op.counterHandler.run(self)
            if op.postCState:
                self.state = op.postCState
        else:
            self.state = op.postAState
         
        self._update_oScreen()
        
        if self.state == TetrisState.NewBlock:
            self._merge_block()
            self._clear_filled_lines()
            self.accept(random.randrange(DEFINE_BLOCK))
            
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

    def _set_operate(self, state, key, operation):
        if (state, key) in self.operate:
            print("키 등록 불가")
            return 

        self.operate[state, key] = operation

    def set_default_operate(self):
        self._set_operate(TetrisState.Running, 'a',
             TetrisOperation(OnLeft(), TetrisState.Running,
                  OnRight(), TetrisState.Running))

        self._set_operate(TetrisState.Running, 's',
             TetrisOperation(OnDown(), TetrisState.Running,
                  OnUp(), TetrisState.NewBlock))

        self._set_operate(TetrisState.Running, 'd',
            TetrisOperation(OnRight(), TetrisState.Running,
                 OnLeft(), TetrisState.Running))

        self._set_operate(TetrisState.Running, 'w',
             TetrisOperation(OnCw(), TetrisState.Running,
                  OnCcw(), TetrisState.Running))
        
        self._set_operate(TetrisState.Running, 'q',
             TetrisOperation(OnCcw(), TetrisState.Running,
                  OnCw(), TetrisState.Running))

        self._set_operate(TetrisState.Running, ' ',
             TetrisOperation(OnDrop(), TetrisState.NewBlock,
                  OnUp(), TetrisState.NewBlock))

        for i in range(DEFINE_BLOCK):
            self._set_operate(TetrisState.NewBlock, str(i),
                     TetrisOperation(NewBlock(i), TetrisState.Running))

    #Getter method
    def get_state(self):
        return self.state
    
    def get_currBlk(self):
        return self.currBlk

class OnCLeft(ActionHandler):
    def run(self, tetris):
        tetris._move_block(dx = -1, dy = 0)

class OnCRight(ActionHandler):
    def run(self, tetris):
        tetris._move_block(dx = 1, dy = 0)

class OnCDown(ActionHandler):
    def run(self, tetris):
        tetris._move_block(dx = 0, dy = 1)

class OnCDrop(ActionHandler):
    def run(self, tetris):           
        while not tetris.check_collision(tetris.iScreen, tetris.currBlk, tetris.top, tetris.left):                                                  
            tetris.top += 1

class OnCUp(ActionHandler):
    def run(self, tetris):
        tetris._move_block(dx = 0, dy = -1)

class OnCCw(ActionHandler):
    def run(self, tetris):
        tetris._rotate_block(deg = 1)

class OnCCcw(ActionHandler):
    def run(self, tetris):
        tetris._rotate_block(deg = -1)

class OnCNewBlock(ActionHandler):
    def __init__(self, blockType = None, blockDegree = None):
        self.blockType = blockType
        self.blockDegree = blockDegree

    def run(self, tetris):
        tetris.new_block(self.blockType, self.blockDegree)

class OnCFinish(ActionHandler):
    def run(self, tetris):
        tetris.state = TetrisState.Finish

class CTetris(Tetris):
    def __init__(self, dy = DEFINE_DY, dx = DEFINE_DX, dw = DEFINE_DW):
        super().__init__(dy, dx, dw)
    
    def set_default_operate(self):
        super().set_default_operate()
        self._set_operate(TetrisState.Running, 'x', TetrisOperation(OnCFinish(), TetrisState.Finish))


if __name__ == "__main__":
    t = CTetris()
    
    t.set_default_operate() 

    while True: 
        t.draw_matrix()
        print()
        key = input('Enter a key from [ q (Left rotate), a (left), d (right), s (down), w (Right rotate), \' \' (drop), x (exit) ] : ') 

        t.accept(key)
        if t.state == TetrisState.Finish:
            print("Game Over!")
            break
            
