#-----------------------FIGURE------------------------------
"""
Атрибуты фигур:
{stepmin}   минимальный шаг
{stepmax}   максимальный шаг
{permitmove}  список разрешенных направлений хода
{permitfight}   список разрешенных направлений боя
{color} атрибут цвета фигуры, присваиваемый сборщиком фигуры
"""
class Figure():
    def __init__(self, stepmax, color, permitmove, permitfight):
        self.stepmax = stepmax
        self.color = color
        self.permitmove = permitmove
        self.permitfight = permitfight

class BishopFigure(Figure):
    def __init__(self, stepmax, color):
        self.permitmove = ('upright', 'upleft', 'downright', 'downleft')
        self.permitfight = self.permitmove
        self.stepmax = stepmax
        self.color = color

class KingFigure(Figure):
    def __init__(self, stepmax, color):
        self.permitmove = ('up', 'down', 'right', 'left', 'upright',
        'upleft', 'downright', 'downleft')
        self.permitfight = self.permitmove
        self.stepmax = stepmax
        self.color = color

class QueenFigure(Figure):
    def __init__(self, stepmax, color):
        self.permitmove = ('up', 'down', 'right', 'left', 'upright',
        'upleft', 'downright', 'downleft')
        self.permitfight = self.permitmove
        self.stepmax = stepmax
        self.color = color

class KnightFigure(Figure):
    def __init__(self, stepmax, color):
        self.permitmove = ('k_upright', 'k_upleft', 'k_downright', 'k_downleft', 
        'k_leftup', 'k_leftdown', 'k_rightup', 'k_rightdown')
        self.permitfight = self.permitmove  
        self.stepmax = stepmax
        self.color = color

class CastleFigure(Figure):
    def __init__(self, stepmax, color):
        self.permitmove = ('up','down', 'left', 'right')
        self.permitfight = self.permitmove
        self.stepmax = stepmax
        self.color = color

class PawnFigure(Figure):
    def __init__(self, stepmax, color):
        self.permitmove = ('up',)
        self.permitfight = ('upleft', 'upright')
        self.stepmax = stepmax
        self.color = color


bishop = BishopFigure(stepmax=7, color='')
king = KingFigure(stepmax=1, color='')
queen = QueenFigure(stepmax=7, color='')
knight = KnightFigure(stepmax=2, color='')
pawn = PawnFigure(stepmax=2, color='')
castle = CastleFigure(stepmax=7, color='')

