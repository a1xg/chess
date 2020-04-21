import numpy as np
from chessboard import board
from figure import KingFigure, KnightFigure, QueenFigure, BishopFigure, CastleFigure, PawnFigure
from figure import king, knight, queen, bishop, castle, pawn
import copy
from tkinter import *
from PIL import Image, ImageTk
import functools

root = Tk()
class ChessEngine:
    def __init__(self):
        self.start = np.array([0,0], dtype=object)      # массивы-заглушки с тестовыми значениями
        self.finish = np.array([0,0], dtype=object)     # массив заглушка с тестовыми значениями
        self.track = 0         # разница стартовой и конечной позиции
        self.figureConstructor()    # сборщик фигур
        self.traectory = []          #массив ячеек траектории хода для проверки
        self.movecolor = 0          #цвет фигуры которая ходит, присваивается методом rulesInitializer()
        self.movefightdirect = 0    #методом moveWhiteArray() присваивается значение направления фигуры которая хочет сходить
        self.yourTurn = 'white'           #чья очередь ходить
        self.whitecount = 0         #счетчики оставшихся белых фигур
        self.blackcount = 0         #счетчики оставшихся черных фигур
        self.errMessage = str

    def movePositionSetter(self, way):
        """
        Установщик позиции по клику.
        Метод устанавливает значения self.start и self.finish.
        """
        self.start[0], self.start[1], self.finish[0], self.finish[1] = way
        self.track = (self.start - self.finish)
        print('###############################')
        print('movePositionSetter координаты: \n', self.start, self.finish)
        self.yourTurnChecker()

#---------------------------GAME-RULES-MOVE-CHECKERS---------------------------

    def yourTurnChecker(self):
        """
        Метод проверки соблюдения очередости хода
        """
        if board.array[self.start[0], self.start[1]] != 0:
            if self.yourTurn == board.array[self.start[0], self.start[1]].color:
                print('yourTurnChecker Ок ваш ход')
                self.moveColorInitializer()
            elif self.yourTurn != board.array[self.start[0], self.start[1]].color:
                print('yourTurnChecker ошибка, не ваш ход')
        elif board.array[self.start[0], self.start[1]] == 0:
            print('yourTurnChecker ошибка, стартовая клетка пуста')

    def permitValueChecker(self):
        """
        Проверка допустимости значений стартовой и финишной позиции
        """
        if board.array[self.start[0], self.start[1]] != 0:
            if abs(self.track[0]) >= 8 or abs(self.track[1]) >= 8:
                print('permitValueChecker ошибка')
            elif abs(self.track[0]) < 8 and abs(self.track[1]) < 8:
                print('permitValueChecker Ok > self.yourTurnChecker()')
                self.yourTurnChecker()
        elif board.array[self.start[0], self.start[1]] == 0:
            print('permitValueChecker ошибка, стартовая клетка пуста')

    def moveColorInitializer(self):
        """
        Метод инициализации правил для просчета хода в зависимости от цвета фигуры
        """
        if board.array[self.start[0], self.start[1]].color == 'white':
           self.movecolor = 'white'
        elif board.array[self.start[0], self.start[1]].color == 'black':
            self.movecolor = 'black'
        self.moveArray()

    def stepmaxChecker(self):
        """
        Проверка атрибута stepmax
        При длине хода в == 1 клетку, запускается метод checkFinish()
        При длине хода в > 1 клетку, запускается метод checkWay()
        """
        stepmax = board.array[self.start[0], self.start[1]].stepmax
        if abs(self.track[0]) <= stepmax and abs(self.track[1]) <= stepmax:
            if len(self.traectory) == 1:
                print('stepmaxChecker OK > self.checkFinish()')
                self.checkFinish()     
            elif len(self.traectory) > 1:
                print('stepmaxChecker OK > self.checkWay()')
                self.checkWay()
        elif abs(self.track[0]) > stepmax or abs(self.track[1]) > stepmax:
            print("stepmaxChecker ошибка")

    def checkWay(self):
        """
        Проверка массива traectory хода на занятость
        """
        for i in range(len(self.traectory)-1):
            for j in range(len(self.traectory[i])): 
                if board.array[self.traectory[i][0]][self.traectory[i][1]] != 0:
                    print("checkWay, ошибка, путь занят")
                    break
                elif board.array[self.traectory[i][0]][self.traectory[i][1]] == 0:
                    if board.array[self.traectory[-2,0]][self.traectory[-2,1]] == 0:
                        print("checkWay Ok > self.checkFinish()")
                        self.checkFinish()
                    break

    def checkFinish(self):
        """
        Проверка позиции хода на занятость
        """
        if board.array[self.traectory[-1,0]][self.traectory[-1,1]] == 0:
            print("checkFinish Ok > self.permitMoveChecker()")
            self.permitMoveChecker()
        elif board.array[self.traectory[-1,0]][self.traectory[-1,1]] != 0:
            print("checkFinish Ok > self.friendOrEnemyChecker()")
            self.friendOrEnemyChecker()

    def permitMoveChecker(self):
        """
        Проверка атрибута разрешенных ходов permitmove
        """
        moverules = board.array[self.start[0], self.start[1]].permitmove
        for i in moverules:
            if i == self.movefightdirect:
                print('permitMoveChecker Ok > self.movefight()')
                self.movefight()
                break                                                
            elif i != self.movefightdirect:
                print('permitMoveChecker ошибка')

    def friendOrEnemyChecker(self):
        """
        Проверка свой или чужой
        """
        if board.array[self.finish[0], self.finish[1]].color == self.movecolor:
            print('friendOrEnemyChecker ошибка')
        elif board.array[self.finish[0], self.finish[1]].color != self.movecolor:
            print("friendOrEnemyChecker Ok >  self.permitFightChecker()")
            self.permitFightChecker()

    def permitFightChecker(self):
        """
        Проверка атрибута разрешенных направлений боя permitfight
        """
        self.fightrules = board.array[self.start[0], self.start[1]].permitfight
        for i in self.fightrules:
            if i == self.movefightdirect:
                print("permitFightChecker Ok >  self.movefight()")
                self.movefight() 
                break
            elif i != self.fightrules:
                print("permitFightChecker ошибка")

#------------------------------MOVE-FIGHT-METHODS-----------------------------------
    def movefight(self):
        """
        Метод перемещения фигуры из позиции start в позицию finish и метод
        боя, вызывается после прохождения всех проверок
        """
        if board.array[self.start[0], self.start[1]].__class__ == PawnFigure:
            self.pawnCounterChanger()
        elif board.array[self.finish[0], self.finish[1]].__class__ == KingFigure:
            self.kingDeath()
        board.array[self.finish[0], self.finish[1]] = board.array[self.start[0], self.start[1]]
        board.array[self.start[0], self.start[1]] = 0
        self.yourTurnCnanger()    #меняем цвет текущего хода для соблюдения очередности
        self.gameStatistic()      #подсчитываем количество оставшихся фигур
        gui.initCell()              #вызов метода отрисовки
        print('movefight Ok, делаем ход или бъем')
        print("Белых фигур:", self.whitecount, "\n", "Черных фигур:", self.blackcount)

    def pawnCounterChanger(self):
        """
        Метод изменения атрибута pawn.stepmax для пешки
        """
        board.array[self.start[0], self.start[1]].stepmax = 1

    def kingDeath(self):
        """
        Метод окончания игры
        """
        if board.array[self.finish[0], self.finish[1]].color == 'white':
            print('Победа черных, вызов события в графической оболочке')
        elif board.array[self.finish[0], self.finish[1]].color == 'black':
            print('Победа белых, вызов события gameOver в графической оболочке')

    def gameStatistic(self):
        """
        Метод подсчитывает количество фигур определенного цвета на шахматной
        доске присваивая значение атрибутам:  whitecount, blackcount
        """
        self.whitecount = 0                         #обнуляем предыдущие значения
        self.blackcount = 0                         #обнуляем предыдущие значения
        for i in range(len(board.array)):
            for j in range(len(board.array[i])):
                if board.array[i, j] != 0:    
                    if board.array[i, j].color == 'black':
                        self.blackcount += 1
                    elif board.array[i, j].color == 'white':
                        self.whitecount += 1

    def yourTurnCnanger(self):
        """
        Метод изменения атрибута self.yourTurn отвечающего за очередность
        хода в зависимости от состояния счетчика gameCounter
        """
        if self.yourTurn == 'black':
            self.yourTurn = 'white'
        elif self.yourTurn == 'white':
            self.yourTurn = 'black'
#в разработке
    def errorMoveFight(self):
        """
        Метод должен вызывать событие графической оболочки по выводу ошибки
        """
        gui.error()

#----------------------------------ARRAY-GENERATOR-----------------------------
    def moveArray(self):
        """
        Генератор массива траектории хода для черных фигур.
        Принимает значения переменных track[0,0], start[0,0], finish[0,0],
        Возвращает двухмерный массив traectory[[0,0],[0,0],...] и значения self.movefightdirect
        """
        if self.track[1] == 0 and self.track[0] > 0:
            move_x = np.array([self.start[1]]*abs(self.track[0]))
            move_y = np.arange(self.start[0] - 1, self.finish[0] - 1, -1)
            self.traectory = np.column_stack((move_y, move_x))
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'up'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'down'
            self.stepmaxChecker()
        elif self.track[1] == 0 and self.track[0] < 0:
            move_x = np.array([self.start[1]]*abs(self.track[0]))
            move_y = np.arange(self.start[0] + 1, self.finish[0] + 1)
            self.traectory = np.column_stack((move_y, move_x))
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'down'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'up'
            self.stepmaxChecker()
        elif self.track[1] > 0 and self.track[0] == 0:
            move_x = np.arange(self.start[1] - 1, self.finish[1] - 1, -1)
            move_y = np.array([self.start[0]]*abs(self.track[1]))
            self.traectory = np.column_stack((move_y, move_x))
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'left'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'right'
            self.stepmaxChecker()
        elif self.track[1] < 0 and self.track[0] == 0:
            move_x = np.arange(self.start[1] + 1, self.finish[1] + 1)
            move_y = np.array([self.start[0]]*abs(self.track[1]))
            self.traectory = np.column_stack((move_y, move_x))
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'right'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'left'
            self.stepmaxChecker()
        elif self.track[1] < 0 and self.track[0] > 0 and abs(self.track[1]) == self.track[0]:
            move_x = np.arange(self.start[1] + 1, self.finish[1] + 1)
            move_y = np.arange(self.start[0] -1, self.finish[0] - 1, -1)
            self.traectory = np.column_stack((move_y, move_x))
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'upright'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'downleft'
            self.stepmaxChecker()
        elif self.track[1] > 0 and self.track[0] < 0 and self.track[1] == abs(self.track[0]):
            move_x = np.arange(self.start[1] -1, self.finish[1] - 1, -1)
            move_y = np.arange(self.start[0] + 1, self.finish[0] + 1)
            self.traectory = np.column_stack((move_y, move_x))
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'downright'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'upright'
            self.stepmaxChecker()
        elif self.track[1] > 0 and self.track[0] > 0 and self.track[1] == self.track[0]:
            move_x = np.arange(self.start[1] - 1, self.finish[1] - 1, -1)
            move_y = np.arange(self.start[0] - 1, self.finish[0] - 1, -1)
            self.traectory = np.column_stack((move_y, move_x))
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'upleft'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'downleft'
            self.stepmaxChecker()
        elif self.track[1] < 0 and self.track[0] < 0 and abs(self.track[1]) == abs(self.track[0]):
            move_x = np.arange(self.start[1] + 1, self.finish[1] + 1)
            move_y = np.arange(self.start[0] + 1, self.finish[0] + 1)
            self.traectory = np.column_stack((move_y, move_x))
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'downright'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'upleft'
            self.stepmaxChecker()
        elif self.track[0] == 2 and self.track[1] == -1:
            self.traectory = np.array([[self.finish[0], self.finish[1]]])
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'k_upright'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'k_downleft'
            self.stepmaxChecker()
        elif self.track[0] == 2 and self.track[1] == 1:
            self.traectory = np.array([[self.finish[0], self.finish[1]]])
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'k_upleft'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'k_downright'
            self.stepmaxChecker()
        elif self.track[0] == 1 and self.track[1] == -2:
            self.traectory = np.array([[self.finish[0], self.finish[1]]])
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'k_rightup'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'k_leftdown'
            self.stepmaxChecker()
        elif self.track[0] == -1 and self.track[1] == -2:
            self.traectory = np.array([[self.finish[0], self.finish[1]]])
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'k_rightdown'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'k_leftup'
            self.stepmaxChecker()
        elif self.track[0] == -2 and self.track[1] == -1:
            self.traectory = np.array([[self.finish[0], self.finish[1]]])
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'k_downright'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'k_upleft'
            self.stepmaxChecker()
        elif self.track[0] == -2 and self.track[1] == 1:
            self.traectory = np.array([[self.finish[0], self.finish[1]]])
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'k_downleft'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'k_upright'
            self.stepmaxChecker()
        elif self.track[0] == -1 and self.track[1] == 2:
            self.traectory = np.array([[self.finish[0], self.finish[1]]])
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'k_leftdown'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'k_rightup'
            self.stepmaxChecker()
        elif self.track[0] == 1 and self.track[1] == 2:
            self.traectory = np.array([[self.finish[0], self.finish[1]]])
            if board.array[self.start[0], self.start[1]].color == 'black':
                self.movefightdirect = 'k_leftup'
            elif board.array[self.start[0], self.start[1]].color == 'white':
                self.movefightdirect = 'k_rightdown'
            self.stepmaxChecker()
        else:
            print('moveArray ошибка генератора, traectory:', self.traectory)
        print('Массив траектории: \n', self.traectory)
        print('Цвет фигуры:', self.movecolor, '\n', 'Направление хода:', self.movefightdirect)

        #----------------------FIGURE-CONSTRUCTOR---------------------------------------

    def figureConstructor(self):
        """
        Метод сборки и расстановки фигур по ячейкам массива
        """
        for i in range(len(board.array[1])):    #заполняем массив черными пешками
            board.array[1, i] = copy.deepcopy(pawn)
            board.array[6, i] = copy.deepcopy(pawn)              
        for i in range(len(board.array[0])): #заполняем позиции фигурами
            if i == 0 or i == 7:
                board.array[0, i] = copy.deepcopy(castle)
                board.array[7, i] = copy.deepcopy(castle)
            elif i == 1 or i == 6:    
                board.array[0, i] = copy.deepcopy(knight)
                board.array[7, i] = copy.deepcopy(knight)
            elif i == 2 or i == 5:
                board.array[0, i] = copy.deepcopy(bishop)
                board.array[7, i] = copy.deepcopy(bishop)            
            elif i == 3:
                board.array[0, i] = copy.deepcopy(king)
                board.array[7, i] = copy.deepcopy(king)
            elif i == 4:
                board.array[0, i] = copy.deepcopy(queen)
                board.array[7, i] = copy.deepcopy(queen)
        for i in range(len(board.array[0])):            #присваиваем значение цвета рядам фигур
            board.array[0, i].color = 'white'
            board.array[1, i].color = 'white'
            board.array[6, i].color = 'black'
            board.array[7, i].color = 'black'

#-------------------------------GRAPHIC-SHELL----------------------------------

CELL_SIZE = 80
Q = 8
WIDTH = CELL_SIZE * Q
HEIGHT = CELL_SIZE * Q

class GraphicInterface(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack()
        self.initImage()
        self.initCell()
        #self.startGame()
        self.clickCounter = 0
        self.moveCoordinate = []


    def click(self, event, param):
        """
        Обработчик события мыши, принимает кортеж param дважды, затем вызывает метод
        action.movePositionSetter() и передает ему кортеж way,
        затем список очищается и счетчик обнуляется
        """
        if self.clickCounter == 0:
            self.moveCoordinate.extend(param)
            self.clickCounter = 1
        elif self.clickCounter == 1:
            self.moveCoordinate.extend(param)
            self.clickCounter = 0
            way = self.moveCoordinate
            action.movePositionSetter(way)
            self.moveCoordinate.clear()

#в разработке
    def startGame(self):
        self.startFrame = Frame(self.parent, width=WIDTH, height=HEIGHT)
        self.startButton = Button(text='Новая игра', command=self.initCell)
        self.startButton.pack()
        self.startFrame.pack()

#работает некорректно, не задействован
    def testEvent(self, event):
        self.cell.configure(bg="green")

# требуется написать обработчики action.kingDeath() action.errorMoveFight()
    def gameOver(self, message):
        if message == "white":
            print('Победа черных')
        elif message == "black":
            print('Победа белых')
        pass

    def error(self):
        pass

    def initCell(self):
        """
        Отрисовщик ячеек доски
        """
        for i in range(Q):
            for j in range(Q):
                if (i+j)%2 == 0:
                    if board.array[i, j] == 0:
                        self.arg = (i, j)
                        self.frame = Frame(self)
                        self.cell = Canvas(self.frame, width=CELL_SIZE, height=CELL_SIZE, bg="#696761", bd=0, highlightthickness=0)
                        self.cell.create_rectangle(0,0,CELL_SIZE, CELL_SIZE)
                        self.cell.bind('<Button-1>', functools.partial(self.click, param=self.arg))
                        self.cell.pack()
                        self.frame.grid(row=i, column=j)
                    elif board.array[i, j] != 0:
                        self.arg = (i, j)
                        self.frame = Frame(self)
                        self.cell = Canvas(self.frame, width=CELL_SIZE, height=CELL_SIZE, bg="#696761", bd=0, highlightthickness=0)
                        self.cell.create_rectangle(0,0,CELL_SIZE, CELL_SIZE)
                        self.cell.bind('<Button-1>', functools.partial(self.click, param=self.arg))
                        self.initFigure(i, j)
                        self.cell.pack()
                        self.frame.grid(row=i, column=j)
                elif (i+j)%2 == 1:
                    if board.array[i, j] == 0:
                        self.arg = (i, j)
                        self.frame = Frame(self)
                        self.cell = Canvas(self.frame, width=CELL_SIZE, height=CELL_SIZE, bg="#e3decc", bd=0, highlightthickness=0)
                        self.cell.create_rectangle(0,0,CELL_SIZE, CELL_SIZE)
                        self.cell.bind('<Button-1>', functools.partial(self.click, param=self.arg))
                        self.cell.pack()
                        self.frame.grid(row=i, column=j)
                    elif board.array[i, j] != 0:
                        self.arg = (i, j)
                        self.frame = Frame(self)
                        self.cell = Canvas(self.frame, width=CELL_SIZE, height=CELL_SIZE, bg="#e3decc", bd=0, highlightthickness=0)
                        self.cell.create_rectangle(0, 0, CELL_SIZE, CELL_SIZE)
                        self.cell.bind('<Button-1>', functools.partial(self.click, param=self.arg))
                        self.initFigure(i, j)
                        self.cell.pack()
                        self.frame.grid(row=i, column=j)
                        
    def initFigure(self,i, j):
        """
        Отрисовщик фигур
        """
        if PawnFigure == board.array[i, j].__class__ and board.array[i, j].color == "white":
            self.cell.create_image(0, 0, anchor=NW, image=self.wpawn)
        elif PawnFigure == board.array[i, j].__class__ and board.array[i, j].color == "black":
            self.cell.create_image(0, 0, anchor=NW, image=self.bpawn)
        elif KingFigure == board.array[i, j].__class__ and board.array[i, j].color == "white":
            self.cell.create_image(0, 0, anchor=NW, image=self.wking)
        elif KingFigure == board.array[i, j].__class__ and board.array[i, j].color == "black":
            self.cell.create_image(0, 0, anchor=NW, image=self.bking)
        elif QueenFigure == board.array[i, j].__class__ and board.array[i, j].color == "white":
            self.cell.create_image(0, 0, anchor=NW, image=self.wqueen)
        elif QueenFigure == board.array[i, j].__class__ and board.array[i, j].color == "black":
            self.cell.create_image(0, 0, anchor=NW, image=self.bqueen)
        elif CastleFigure == board.array[i, j].__class__ and board.array[i, j].color == "white":
            self.cell.create_image(0, 0, anchor=NW, image=self.wcastle)
        elif CastleFigure == board.array[i, j].__class__ and board.array[i, j].color == "black":
            self.cell.create_image(0, 0, anchor=NW, image=self.bcastle)
        elif KnightFigure == board.array[i, j].__class__ and board.array[i, j].color == "white":
            self.cell.create_image(0, 0, anchor=NW, image=self.wknight)
        elif KnightFigure == board.array[i, j].__class__ and board.array[i, j].color == "black":
            self.cell.create_image(0, 0, anchor=NW, image=self.bknight)
        elif BishopFigure == board.array[i, j].__class__ and board.array[i, j].color == "white":
            self.cell.create_image(0, 0, anchor=NW, image=self.wbishop)
        elif BishopFigure == board.array[i, j].__class__ and board.array[i, j].color == "black":
            self.cell.create_image(0, 0, anchor=NW, image=self.bbishop)

    def initImage(self):
        """
        Инициализация изображений
        """
        self.b_king = Image.open("image/black/king.png")
        self.bking = ImageTk.PhotoImage(self.b_king)
        self.w_king = Image.open("image/white/king.png")
        self.wking = ImageTk.PhotoImage(self.w_king)
        self.b_queen = Image.open("image/black/queen.png")
        self.bqueen = ImageTk.PhotoImage(self.b_queen)
        self.w_queen = Image.open("image/white/queen.png")
        self.wqueen = ImageTk.PhotoImage(self.w_queen)
        self.b_bishop = Image.open("image/black/bishop.png")
        self.bbishop = ImageTk.PhotoImage(self.b_bishop)
        self.w_bishop = Image.open("image/white/bishop.png")
        self.wbishop = ImageTk.PhotoImage(self.w_bishop)
        self.b_castle = Image.open("image/black/castle.png")
        self.bcastle = ImageTk.PhotoImage(self.b_castle)
        self.w_castle = Image.open("image/white/castle.png")
        self.wcastle = ImageTk.PhotoImage(self.w_castle)
        self.b_knight = Image.open("image/black/knight.png")
        self.bknight = ImageTk.PhotoImage(self.b_knight)
        self.w_knight = Image.open("image/white/knight.png")
        self.wknight = ImageTk.PhotoImage(self.w_knight)
        self.b_pawn = Image.open("image/black/pawn.png")
        self.bpawn = ImageTk.PhotoImage(self.b_pawn)
        self.w_pawn = Image.open("image/white/pawn.png")
        self.wpawn = ImageTk.PhotoImage(self.w_pawn)

#----------Инициализация объектов--------------
action = ChessEngine()
gui = GraphicInterface(root)
root.mainloop()