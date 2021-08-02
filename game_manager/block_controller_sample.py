#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
import pprint
import copy
import numpy as np

class Block_Controller(object):

    # init parameter
    board_backboard = 0
    board_data_width = 0
    board_data_height = 0
    ShapeNone_index = 0
    CurrentShape_class = 0
    NextShape_class = 0

    # GetNextMove is main function.
    # input
    #    nextMove : nextMove structure which is empty.
    #    GameStatus : block/field/judge/debug information. 
    #                 in detail see the internal GameStatus data.
    # output
    #    nextMove : nextMove structure which includes next shape position and the other.
    def GetNextMove(self, nextMove, GameStatus):

        t1 = datetime.now()

        # print GameStatus
        print("=================================================>")
        pprint.pprint(GameStatus, width = 61, compact = True)

        # get data from GameStatus
        # current shape info
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        self.CurrentShape_class = GameStatus["block_info"]["currentShape"]["class"]
        # next shape info
        NextShapeDirectionRange = GameStatus["block_info"]["nextShape"]["direction_range"]
        self.NextShape_class = GameStatus["block_info"]["nextShape"]["class"]
        # current board info
        self.board_backboard = GameStatus["field_info"]["backboard"]
        # default board definition
        self.board_data_width = GameStatus["field_info"]["width"]
        self.board_data_height = GameStatus["field_info"]["height"]
        self.ShapeNone_index = GameStatus["debug_info"]["shape_info"]["shapeNone"]["index"]

        # search best nextMove -->
        strategy = None
        #EvalValue = 0
        LatestEvalValue = -100000
        # search with current block Shape
        for direction0 in CurrentShapeDirectionRange:
            # search with x range
            x0Min, x0Max = self.getSearchXRange(self.CurrentShape_class, direction0)
            for x0 in range(x0Min, x0Max):
                # get board data, as if dropdown block
                board = self.getBoard(self.board_backboard, self.CurrentShape_class, direction0, x0)

                # evaluate board
                EvalValue = self.calcEvaluationValueSample(board)
                #EvalValue += self.calcEvaluationValueSample(board)
                # update best move
                #if EvalValue > LatestEvalValue:
                #    strategy = (direction0, x0, 1, 1)
                #    LatestEvalValue = EvalValue
                ###test
                for direction1 in NextShapeDirectionRange:
                    x1Min, x1Max = self.getSearchXRange(self.NextShape_class, direction1)
                    for x1 in range(x1Min, x1Max):
                        board2 = self.getBoard(board, self.NextShape_class, direction1, x1)
                        EvalValue += self.calcEvaluationValueSample(board)
                    if EvalValue > LatestEvalValue:
                        strategy = (direction0, x0, 1, 1)
                        LatestEvalValue = EvalValue
        # search best nextMove <--

        print("===", datetime.now() - t1)
        nextMove["strategy"]["direction"] = strategy[0]
        nextMove["strategy"]["x"] = strategy[1]
        nextMove["strategy"]["y_operation"] = strategy[2]
        nextMove["strategy"]["y_moveblocknum"] = strategy[3]
        print(nextMove)
        print("###### SAMPLE CODE ######")
        return nextMove

    def getSearchXRange(self, Shape_class, direction):
        #
        # get x range from shape direction.
        #
        minX, maxX, _, _ = Shape_class.getBoundingOffsets(direction) # get shape x offsets[minX,maxX] as relative value.
        xMin = -1 * minX
        xMax = self.board_data_width - maxX
        return xMin, xMax

    def getShapeCoordArray(self, Shape_class, direction, x, y):
        #
        # get coordinate array by given shape.
        #
        coordArray = Shape_class.getCoords(direction, x, y) # get array from shape direction, x, y.
        return coordArray

    def getBoard(self, board_backboard, Shape_class, direction, x):
        # 
        # get new board.
        #
        # copy backboard data to make new board.
        # if not, original backboard data will be updated later.
        board = copy.deepcopy(board_backboard)
        _board = self.dropDown(board, Shape_class, direction, x)
        return _board

    def dropDown(self, board, Shape_class, direction, x):
        # 
        # internal function of getBoard.
        # -- drop down the shape on the board.
        # 
        dy = self.board_data_height - 1
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        # update dy
        for _x, _y in coordArray:
            _yy = 0
            while _yy + _y < self.board_data_height and (_yy + _y < 0 or board[(_y + _yy) * self.board_data_width + _x] == self.ShapeNone_index):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        _board = self.dropDownWithDy(board, Shape_class, direction, x, dy)
        return _board

    def dropDownWithDy(self, board, Shape_class, direction, x, dy):
        #
        # internal function of dropDown.
        #
        _board = board
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        for _x, _y in coordArray:
            _board[(_y + dy) * self.board_data_width + _x] = Shape_class.shape
        return _board


    def calcEvaluationValueSample_(self, board):
        #
        # my evaluate function
        #

        # calc Evaluation Value
        score = 0
        score = score + self.cnt_full_9column_lines(board) * 10.0
        if self.check_full_4lines(board):
            score = score + 100.0

        return score
    

    def check_is_hole(self, board):
        #
        # 穴(空のブロックの上にブロックがある状態)ならTrue、
        # そうでなければFalseを返す
        #

        width = self.board_data_width
        height = self.board_data_height

        # for debag
        #board = self.board

        a = np.array(board).reshape(height, width)

        # for debag
        #a[:, 0] = 0
        #a[2, 1] = 0
        
        # for debag
        #print("a=\n",a)

        w = 0
        ret = 1
        for i in range(width):
            # for debag
            #print("a[:, {}]={}".format(i,a[:, i]))
            
            if (np.any(a[:, i]) == 0):
                ret *= 1

                # for debag
                #print("kita1 i={}".format(i))
            else:
                b = np.amin(np.nonzero(a[:, i]))
                c = np.count_nonzero(a[:, i])

                # for debag
                #print("b=\n",b)
                #print("c=\n",c)

                if (b == 1):
                    ret *= 1
                    
                    # for debag
                    #print("kita2 i={}".format(i))
                    
                elif (b == (height - c)):
                    ret *= 1

                    # for debag
                    #print("kita3 i={}".format(i))
                    
                else:
                    ret = 0
                    
                    # for debag
                    #print("kita4 i={}".format(i))
                    
                    break

        # for debag
        #print("ret=",ret)
        return ret
        

    def check_empty_column0(self, board):
        #
        # 列0が空ならTrue、そうでなければFalseを返す
        #

        width = self.board_data_width
        height = self.board_data_height

        # for debag
        #board = self.board

        a = np.array(board).reshape(height, width)

        # for debag
        #a[:, 0] = 0

        b = np.sum(a[:, 0])
        # for debag
        #print("a=",a)
        #print("b=",b)

        if (b == 0):
            return True
        else:
            return False
        
    
    def cnt_full_9column_lines(self, board):
        #
        # 列0〜列9のブロックが埋まっている行の数を返す
        #
        
        width = self.board_data_width
        height = self.board_data_height

        # for debag
        #board = self.board
        #board = self.getCurrentBoard(self.board_backboard)

        # for debag
        #a = np.random.randint(0, 7, 220).reshape(height, width)
        a = np.array(board).reshape(height, width)

        # for debag
        #a[:, 0] = 0

        b = np.sum(a[:, 0])
        c = np.prod(a[:, 1:width], axis=1)

        # for debag
        #print("a=",a)
        #print("b=",b)
        #print("c=",c)

        full_9lines = 0
        cnt = 0
        for i in range(height):
            # for debag
            #print("a[{},0] = {}  c[{}] = {}".format(i, a[i, 0], i, c[i]))

            if ((a[i, 0] == 0) and (c[i] != 0)):
                cnt += 1
            else:
                if (full_9lines < cnt):
                    full_9lines = cnt
                cnt = 0

        if (full_9lines < cnt):
            full_9lines = cnt

        # for debag
        #print("full_9lines={}".format(full_9lines))

        return full_9lines
        

    def check_full_4lines(self, board):
        #
        # 4行埋まっていたらTrue、そうでなければFalseを返す
        #
        if (self.check_full_lines(board) >= 4):
            return True
        else:
            return False

        
    def check_full_lines(self, board):
        #
        # 列0〜列9まですべて埋まっている行が連続しているmax値を返す
        #
        
        width = self.board_data_width
        height = self.board_data_height

        # for debag
        #board = self.board
        #board = self.getCurrentBoard(self.board_backboard)

        # for debag
        #a = np.random.randint(1, 7, 220).reshape(height, width)
        a = np.array(board).reshape(height, width)

        # for debag
        #a[:-4, :] = 0

        c = np.prod(a, axis=1)

        # for debag
        #print("a=",a)
        #print("c=",c)

        full_lines = 0
        cnt = 0
        for i in range(height):
            # for debag
            #print("c[{}] = {}".format(i, c[i]))

            if (c[i] != 0):
                cnt += 1
            else:
                if (full_lines < cnt):
                    full_lines = cnt
                cnt = 0

        if (full_lines < cnt):
            full_lines = cnt

        # for debag
        #print("full_lines={}".format(full_lines))

        return full_lines


        
    def calcEvaluationValueSample(self, board):
        #
        # sample function of evaluate board.
        #
        width = self.board_data_width
        height = self.board_data_height

        # evaluation paramters
        ## lines to be removed
        fullLines = 0
        ## number of holes or blocks in the line.
        nHoles, nIsolatedBlocks = 0, 0
        ## absolute differencial value of MaxY
        absDy = 0
        ## how blocks are accumlated
        BlockMaxY = [0] * width
        holeCandidates = [0] * width
        holeConfirm = [0] * width

        ### check board
        # each y line
        for y in range(height - 1, 0, -1):
            hasHole = False
            hasBlock = False
            # each x line
            for x in range(width):
                ## check if hole or block..
                if board[y * self.board_data_width + x] == self.ShapeNone_index:
                    # hole
                    hasHole = True
                    holeCandidates[x] += 1  # just candidates in each column..
                else:
                    # block
                    hasBlock = True
                    BlockMaxY[x] = height - y                # update blockMaxY
                    if holeCandidates[x] > 0:
                        holeConfirm[x] += holeCandidates[x]  # update number of holes in target column..
                        holeCandidates[x] = 0                # reset
                    if holeConfirm[x] > 0:
                        nIsolatedBlocks += 1                 # update number of isolated blocks

            if hasBlock == True and hasHole == False:
                # filled with block
                fullLines += 1
            elif hasBlock == True and hasHole == True:
                # do nothing
                pass
            elif hasBlock == False:
                # no block line (and ofcourse no hole)
                pass

        # nHoles
        for x in holeConfirm:
            nHoles += abs(x)

        ### absolute differencial value of MaxY
        BlockMaxDy = []
        for i in range(len(BlockMaxY) - 1):
            val = BlockMaxY[i] - BlockMaxY[i+1]
            BlockMaxDy += [val]
        for x in BlockMaxDy:
            absDy += abs(x)

        #### maxDy
        #maxDy = max(BlockMaxY) - min(BlockMaxY)
        #### maxHeight
        #maxHeight = max(BlockMaxY) - fullLines

        ## statistical data
        #### stdY
        #if len(BlockMaxY) <= 0:
        #    stdY = 0
        #else:
        #    stdY = math.sqrt(sum([y ** 2 for y in BlockMaxY]) / len(BlockMaxY) - (sum(BlockMaxY) / len(BlockMaxY)) ** 2)
        #### stdDY
        #if len(BlockMaxDy) <= 0:
        #    stdDY = 0
        #else:
        #    stdDY = math.sqrt(sum([y ** 2 for y in BlockMaxDy]) / len(BlockMaxDy) - (sum(BlockMaxDy) / len(BlockMaxDy)) ** 2)


        # calc Evaluation Value
        score = 0
        if self.check_is_hole(self.board_backboard):
            if self.check_is_hole(board):
                score = score + 10.0
                score = score + self.cnt_full_9column_lines(board) * 10.0
                if self.check_empty_column0(board):
                    score = score + 10.0
                if self.check_full_4lines(board):
                    score = score + 100.0
        score = score + fullLines * 10.0           # try to delete line 
        score = score - nHoles * 100.0               # try not to make hole
        score = score - nIsolatedBlocks * 1.0      # try not to make isolated block
        score = score - absDy * 1.0                # try to put block smoothly
        #score = score - maxDy * 0.3                # maxDy
        #score = score - maxHeight * 5              # maxHeight
        #score = score - stdY * 1.0                 # statistical data
        #score = score - stdDY * 0.01               # statistical data

        # print(score, fullLines, nHoles, nIsolatedBlocks, maxHeight, stdY, stdDY, absDy, BlockMaxY)
        return score


BLOCK_CONTROLLER_SAMPLE = Block_Controller()

