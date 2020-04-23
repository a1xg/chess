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
        self.start = np.array([0,0], dtype=object)      # Координаты x, y стартовой позиции.
        self.finish = np.array([0,0], dtype=object)     # Координаты x, y конечной позиции.
        self.track = 0                                  # Разница стартовой и конечной позиции.
        self.figureConstructor()                        # Сборщик фигур.
        self.traectory = []                             # Массив индексов ячеек для проверки массива board.array.
        self.movecolor = 0                              # Цвет фигуры совершающей ход.
        self.movefightdirect = 0                        # Направление фигуры совершающей ход.
        self.yourTurn = 'white'                         # Цвет текущего хода
        self.whitecount = 0                             # Счетчики оставшихся белых фигур, не задействован
        self.blackcount = 0                             # Счетчики оставшихся черных фигур, не задействован

    def movePositionSetter(self, way):
        """
        Установщик позиции по клику.
        Метод принимает от gui.click() кортеж координат "way", распаковывает его в атрибуты action.start и action.finish.
        Инициирует проверку action.yourTurnChecker()
        """
        self.start[0], self.start[1], self.finish[0], self.finish[1] = way
        self.track = (self.start - self.finish)
        self.yourTurnChecker()

#---------------------------GAME-RULES-MOVE-CHECKERS---------------------------

    def yourTurnChecker(self):
        """
        Проверка соблюдения очередости хода.
        """
        if board.array[self.start[0], self.start[1]] != 0:
            if self.yourTurn == board.array[self.start[0], self.start[1]].color:
                self.moveColorInitializer()
            elif self.yourTurn != board.array[self.start[0], self.start[1]].color:
                print('yourTurnChecker ошибка, не ваш ход')
        elif board.array[self.start[0], self.start[1]] == 0:
            print('yourTurnChecker ошибка, стартовая клетка пуста')

    def permitValueChecker(self):
        """
        Проверка стартовой позиции на наличие фигуры.
        """
        if board.array[self.start[0], self.start[1]] != 0:
            self.yourTurnChecker()
        elif board.array[self.start[0], self.start[1]] == 0:
            print('permitValueChecker ошибка, стартовая клетка пуста')

    def moveColorInitializer(self):
        """
        Метод установки атрибута action.movecolor для обозначения цвета текущего хода
        """
        if board.array[self.start[0], self.start[1]].color == 'white':
           self.movecolor = 'white'
        elif board.array[self.start[0], self.start[1]].color == 'black':
            self.movecolor = 'black'
        self.moveArray()

    def stepmaxChecker(self):
        """
        Проверка атрибута stepmax
        При длине хода в 1 клетку, запускается метод проверки checkFinish()
        При длине хода более чем 1 клетка, запускается метод  проверки checkWay()
        """
        stepmax = board.array[self.start[0], self.start[1]].stepmax
        if abs(self.track[0]) <= stepmax and abs(self.track[1]) <= stepmax:
            if len(self.traectory) == 1:
                self.checkFinish()     
            elif len(self.traectory) > 1:
                self.checkWay()
        elif abs(self.track[0]) > stepmax or abs(self.track[1]) > stepmax:
            print("stepmaxChecker ошибка, длина хода больше разрешенного значения")

    def checkWay(self):
        """
        Выборочная проверка массива board.array на наличие фигур, используя массив индексов action.traectory.
        """
        for i in range(len(self.traectory)-1):
            for j in range(len(self.traectory[i])): 
                if board.array[self.traectory[i][0]][self.traectory[i][1]] != 0:
                    break
                elif board.array[self.traectory[i][0]][self.traectory[i][1]] == 0:
                    if board.array[self.traectory[-2,0]][self.traectory[-2,1]] == 0:
                        self.checkFinish()
                    break

    def checkFinish(self):
        """
        Проверка конечной ячейки хода на занятость фигурами.
        """
        if board.array[self.traectory[-1,0]][self.traectory[-1,1]] == 0:
            self.permitMoveChecker()
        elif board.array[self.traectory[-1,0]][self.traectory[-1,1]] != 0:
            self.friendOrEnemyChecker()

    def permitMoveChecker(self):
        """
        Проверка атрибута разрешенных ходов permitmove, для фигуры совершающей ход
        """
        moverules = board.array[self.start[0], self.start[1]].permitmove
        for i in moverules:
            if i == self.movefightdirect:
                self.movefight()
                break                                                
            elif i != self.movefightdirect:
                print("permitMoveChecker ошибка, правила не допускают такой ход")

    def friendOrEnemyChecker(self):
        """
        Проверка фигур типа "свой или чужой"
        """
        if board.array[self.finish[0], self.finish[1]].color == self.movecolor:
            print("friendOrEnemyChecker ошибка, нельзя побить фигуру союзника")
        elif board.array[self.finish[0], self.finish[1]].color != self.movecolor:
            self.permitFightChecker()

    def permitFightChecker(self):
        """
        Проверка атрибута разрешенных направлений боя permitfight для фигуры совершающей ход.
        """
        self.fightrules = board.array[self.start[0], self.start[1]].permitfight
        for i in self.fightrules:
            if i == self.movefightdirect:
                self.movefight() 
                break
            elif i != self.fightrules:
                print("permitFightChecker ошибка, правила не допускают возможность боя")

#------------------------------MOVE-FIGHT-METHODS-----------------------------------
    def movefight(self):
        """
        Метод перемещения фигуры из позиции start в позицию finish и метод
        боя одновременно, вызывается после прохождения всех проверок.
        """
        if board.array[self.start[0], self.start[1]].__class__ == PawnFigure:
            self.pawnCounterChanger()
        elif board.array[self.finish[0], self.finish[1]].__class__ == KingFigure:
            self.kingDeath()
        board.array[self.finish[0], self.finish[1]] = board.array[self.start[0], self.start[1]]
        board.array[self.start[0], self.start[1]] = 0
        self.yourTurnCnanger()                          # Смена цвета текущего хода для соблюдения очередности.
        self.gameStatistic()                            # Подсчет количества оставшихся фигур.
        gui.initCell()                                  # Вызов отрисовки

    def pawnCounterChanger(self):
        """
        Метод изменения атрибута stepmax для пешки совершившей ход
        """
        board.array[self.start[0], self.start[1]].stepmax = 1

    def kingDeath(self):
        """
        Метод окончания игры
        """
        if board.array[self.finish[0], self.finish[1]].color == 'white':
            print('Победа черных')
        elif board.array[self.finish[0], self.finish[1]].color == 'black':
            print('Победа белых')

    def gameStatistic(self):
        """
        Метод подсчитывает количество фигур определенного цвета на шахматной
        доске присваивая значение атрибутам:  whitecount, blackcount
        """
        self.whitecount = 0
        self.blackcount = 0
        for i in range(len(board.array)):
            for j in range(len(board.array[i])):
                if board.array[i, j] != 0:
                    if board.array[i, j].color == 'black':
                        self.blackcount += 1
                    elif board.array[i, j].color == 'white':
                        self.whitecount += 1

    def yourTurnCnanger(self):
        """
        Метод изменения атрибута action.yourTurn отвечающего за очередность
        хода в зависимости от состояния счетчика gameCounter
        """
        if self.yourTurn == 'black':
            self.yourTurn = 'white'
        elif self.yourTurn == 'white':
            self.yourTurn = 'black'

    def errorMoveFight(self): #в разработке
        """
        Метод вызова отрисовки ошибки хода
        """
        gui.error()

#----------------------------------ARRAY-GENERATOR-----------------------------
    def moveArray(self):
        """
        1) Метод принимает входные данные(массив координат): action.track.
        2) Сравнивает значения action.track c паттернами хода соответствующими: линейным, диагональным или ходом конем
        3) После выбора паттерна - генерируется массив индексов action.traectory для дальнейших проверок board.array.
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
            return

        #----------------------FIGURE-CONSTRUCTOR---------------------------------------

    def figureConstructor(self):
        """
        Метод расстановки фигур по ячейкам массива путем глубокого копирования.
        """
        for i in range(len(board.array[1])):
            board.array[1, i] = copy.deepcopy(pawn)
            board.array[6, i] = copy.deepcopy(pawn)              
        for i in range(len(board.array[0])):
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
        for i in range(len(board.array[0])):
            board.array[0, i].color = 'white'
            board.array[1, i].color = 'white'
            board.array[6, i].color = 'black'
            board.array[7, i].color = 'black'

#-------------------------------GRAPHIC-SHELL----------------------------------

CELL_SIZE = 80                  # Размер клетки в пикселах.
Q = 8                           # Количествов клеток в длину и в ширину.
WIDTH = CELL_SIZE * Q           # Длина доски.
HEIGHT = CELL_SIZE * Q          # Высота доски.

class GraphicInterface(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack()
        self.initImage()
        self.initCell()
        self.clickCounter = 0
        self.moveCoordinate = []


    def click(self, event, param):
        """
        Обработчик события мыши, принимает кортеж param дважды, затем вызывает метод
        action.movePositionSetter() и передает ему список way,
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


    def startGame(self):
        pass
    def gameOver(self):
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


action = ChessEngine()
gui = GraphicInterface(root)
root.mainloop()