import pygame
import sys
import random
import math
import time




class powerup:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.eraseType = 'powerup'
        self.type = type
        if type == 'gravity':
            self.radius = 30
            self.color = blue
            self.duration = 2
        if type == 'time':
            self.radius = 30
            self.color = red
            self.duration = 5
        if type == 'dash':
            self.radius = 30
            self.color = green
            self.duration = 1
        self.timer = self.duration
        self.active = 0

    def update(self):
        #detect if hit by player
        if self.active == 0:
            if abs(self.x - (world.player.x + world.player.sx / 2)) < world.player.sx / 2 + self.radius:
                if abs(self.y - (world.player.y + world.player.sy / 2)) < world.player.sy / 2 + self.radius:
                    self.trigger()
        else:
            if self.timer > 0:
                self.timer -= fps
                if self.timer < 0:
                    self.trigger()
    def trigger(self):
        if self.active == 0:
            self.active = 1
            if self.type == 'gravity':
                world.gravity *= .5
            elif self.type == 'time':
                world.gameRunSpeed *= .5
            elif self.type == 'dash':
                world.player.swordDashFlag = 0
                world.player.dashTimer = 0
        else:
            self.active = 0
            self.timer = self.duration
            if self.type == 'gravity':
                world.gravity *= 2
            elif self.type == 'time':
                world.gameRunSpeed *= 2

    def draw(self):
        if self.active == 0:
            pygame.draw.circle(screen, self.color, [round(self.x), round(self.y)], self.radius)



class player:
    def __init__(self, x, y):
        # basic init
        self.x = x
        self.y = y



class end:
    def __init__(self, x, y):
        # basic init
        self.x = x
        self.y = y



class rect:
    def __init__(self,rect, color):
        self.eraseType = 'rect'
        self.type = 'rect'
        self.rect = rect
        self.color = color

    def update(self):
        pass

    def draw(self):
        pygame.draw.rect(screen,self.color,self.rect)



class pathpoint:
    def __init__(self,rect, num):
        self.eraseType = 'rect'
        self.type = 'pathpoint'
        self.rect = rect
        self.color = red
        self.num = num

    def update(self):
        pass

    def draw(self):
        pygame.draw.rect(screen,self.color,self.rect, 5)
        message_display(str(self.num), 20,self.rect[0] + self.rect[2] / 2, self.rect[1] + self.rect[3] / 2, black)





class guiItem:
    def __init__(self, rect,action,text, textColor, fontSize, rectColor):
        self.rect = rect
        self.actionNumber = action
        self.text = text
        self.fontSize = fontSize
        self.rectColor = rectColor
        self.textColor = textColor
        self.clicked = 0
        self.timer = 0
        self.darknessTime = .2
        self.darknessRatio = .5

    def update(self):
        #detect if clicked
        if self.clicked == 0:
            if mouse == 1:
                x , y = pygame.mouse.get_pos()
                if abs(self.rect[0] + self.rect[2] / 2  - x) < self.rect[2] / 2:
                    if abs(self.rect[1] + self.rect[3] / 2 - y) < self.rect[3] / 2:
                        self.clicked = 1
                        self.timer = self.darknessTime
                        self.doAction()
                        editor.placeTimer = editor.placeLockout
        if self.clicked == 1:
            self.timer -= fps
            if self.timer < 0:
                self.clicked = 0

    def draw(self):
        if self.clicked == 1:
            color = ((self.rectColor[0] / 255 * self.darknessRatio) * 255,(self.rectColor[1] / 255 * self.darknessRatio)
                     * 255, (self.rectColor[2] / 255 * self.darknessRatio) * 255)
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, black, self.rect,2)
        else:
            pygame.draw.rect(screen, self.rectColor, self.rect)
            pygame.draw.rect(screen, black, self.rect, 2)
        message_display(self.text, self.fontSize, self.rect[0] + self.rect[2] / 2, self.rect[1] + self.rect[3] / 2, self.textColor)

    def doAction(self):
        #set editor to rect mode
        if self.actionNumber == 1:
            editor.mode = 1
        elif self.actionNumber == 2:
            editor.mode = 2
        elif self.actionNumber == 3:
            editor.mode = 3
        elif self.actionNumber == 4:
            printLevel()
        elif self.actionNumber == 5:
            editor.mode = 5
        elif self.actionNumber == 6:
            editor.mode = 6
        elif self.actionNumber == 7:
            editor.undo()
        elif self.actionNumber == 8:
            editor.mode = 7
        elif self.actionNumber == 9:
            editor.loadLevel()
        elif self.actionNumber == 10:
            editor.mode = 10
        elif self.actionNumber == 11:
            if editor.doScroll == 0:
                editor.doScroll = 1
            else:
                editor.doScroll = 0
        elif self.actionNumber == 12:
            editor.mode = 12



class editor:
    def __init__(self):
        self.level = []
        self.gui = []
        self.loadgui()
        # 1 = draw rect , 2 = gravity, 3 = timeslow
        self.mode = 0
        self.colorSelect = black
        #placing stuff management
        self.gridSize = 20
        self.p1 = 0,0
        self.placeFlag = 0
        self.placeTimer = 0
        self.placeLockout = .2
        #scrolling
        self.xScroll = 0
        self.yScroll = 0
        self.scrollSpeed = self.gridSize
        self.doScroll = 1
        self.scrollTimer = 0
        self.scrollCooldown = .1
        #pathpoints
        self.pathpointNum = 32

    def update(self):
        if self.doScroll == 1:
            self.scroll()
        self.placeTimer -= fps
        #update gui
        for item in self.gui:
            item.update()
        #rect placement
        if self.mode == 1:
            if self.placeFlag == 0:
                if mouse == 1:
                    self.placeFlag = 1
                    self.p1 = pygame.mouse.get_pos()
                    #round to nearest 50
                    self.p1 = round(self.p1[0] * (1 / self.gridSize)) * self.gridSize, round(self.p1[1] * (1 / self.gridSize)) * self.gridSize
            else:
                if mouse == 0:
                    self.placeFlag = 0
                    self.p2 = pygame.mouse.get_pos()
                    self.p2 = round(self.p2[0] * (1 / self.gridSize)) * self.gridSize, round(self.p2[1] * (1 / self.gridSize)) * self.gridSize
                    if abs(self.p1[0] - self.p2[0]) >= self.gridSize:
                        if abs(self.p1[1] - self.p2[1]) >= self.gridSize:
                            p1 = self.p1[0], self.p1[1]
                            p2 = self.p2[0], self.p2[1]
                            if self.p2[0] < self.p1[0]:
                                temp = p1[0]
                                p1 = p2[0], p1[1]
                                p2 = temp, p2[1]
                            if self.p2[1] < self.p1[1]:
                                temp = p1[1]
                                p1 = p1[0], p2[1]
                                p2 = p2[0], temp
                            self.level.append(rect([p1[0], p1[1], abs(p1[0] - p2[0]), abs(p1[1] - p2[1])], self.colorSelect))
                else:
                    self.p2 = pygame.mouse.get_pos()
                    self.p2 = round(self.p2[0] * (1 / self.gridSize)) * self.gridSize, round(self.p2[1] * (1 / self.gridSize)) * self.gridSize
                    p1 = self.p1[0], self.p1[1]
                    p2 = self.p2[0], self.p2[1]
                    if self.p2[0] < self.p1[0]:
                        temp = p1[0]
                        p1 = p2[0] , p1[1]
                        p2 = temp , p2[1]
                    if self.p2[1] < self.p1[1]:
                        temp = p1[1]
                        p1 = p1[0] , p2[1]
                        p2 = p2[0] , temp
                    pygame.draw.rect(screen, self.colorSelect, [p1[0], p1[1], abs(p1[0] - p2[0]), abs(p1[1] - p2[1])])
        #erase
        elif self.mode == 7:
            if self.placeFlag == 0:
                if self.placeTimer < 0:
                    if mouse == 1:
                        self.placeFlag = 1
                        self.p1 = pygame.mouse.get_pos()
                        # find what is clicked
                        temp = 0
                        for object in self.level:
                            temp += 1
                            if object.eraseType == 'rect':
                                if abs(object.rect[0] + object.rect[2] / 2 - self.p1[0]) < object.rect[2] / 2:
                                    if abs(object.rect[1] + object.rect[3] / 2 - self.p1[1]) < object.rect[3] / 2:
                                        del self.level[temp - 1]
                            if object.eraseType == 'powerup':
                                if abs(object.x - self.p1[0]) < object.radius:
                                    if abs(object.y - self.p1[1]) < object.radius:
                                        del self.level[temp -1]

            else:
                if mouse == 0:
                    self.placeFlag = 0
        #pathpoint
        elif self.mode == 12:
            if self.placeFlag == 0:
                if mouse == 1:
                    self.placeFlag = 1
                    self.p1 = pygame.mouse.get_pos()
                    #round to nearest 50
                    self.p1 = round(self.p1[0] * (1 / self.gridSize)) * self.gridSize, round(self.p1[1] * (1 / self.gridSize)) * self.gridSize
            else:
                if mouse == 0:
                    self.placeFlag = 0
                    self.p2 = pygame.mouse.get_pos()
                    self.p2 = round(self.p2[0] * (1 / self.gridSize)) * self.gridSize, round(self.p2[1] * (1 / self.gridSize)) * self.gridSize
                    if abs(self.p1[0] - self.p2[0]) >= self.gridSize:
                        if abs(self.p1[1] - self.p2[1]) >= self.gridSize:
                            p1 = self.p1[0], self.p1[1]
                            p2 = self.p2[0], self.p2[1]
                            if self.p2[0] < self.p1[0]:
                                temp = p1[0]
                                p1 = p2[0], p1[1]
                                p2 = temp, p2[1]
                            if self.p2[1] < self.p1[1]:
                                temp = p1[1]
                                p1 = p1[0], p2[1]
                                p2 = p2[0], temp
                            self.level.append(pathpoint([p1[0], p1[1], abs(p1[0] - p2[0]), abs(p1[1] - p2[1])], self.pathpointNum))
                            self.pathpointNum += 1
                else:
                    self.p2 = pygame.mouse.get_pos()
                    self.p2 = round(self.p2[0] * (1 / self.gridSize)) * self.gridSize, round(self.p2[1] * (1 / self.gridSize)) * self.gridSize
                    p1 = self.p1[0], self.p1[1]
                    p2 = self.p2[0], self.p2[1]
                    if self.p2[0] < self.p1[0]:
                        temp = p1[0]
                        p1 = p2[0] , p1[1]
                        p2 = temp , p2[1]
                    if self.p2[1] < self.p1[1]:
                        temp = p1[1]
                        p1 = p1[0] , p2[1]
                        p2 = p2[0] , temp
                    pygame.draw.rect(screen, red, [p1[0], p1[1], abs(p1[0] - p2[0]), abs(p1[1] - p2[1])], 5)






    def loadgui(self):
        self.gui.append(guiItem([0,0,100,50], 1, "Rect", black, 30, grey))
        self.gui.append(guiItem([100, 0, 100, 50], 12, "Pathpoint", black, 20, grey))
        self.gui.append(guiItem([600, 0, 200, 50], 4, "Print Level", black, 30, grey))
        self.gui.append(guiItem([1200, 0, 200, 50], 7, "Undo", black, 30, grey))
        self.gui.append(guiItem([1400, 0, 200, 50], 8, "Erase", black, 30, grey))
        self.gui.append(guiItem([1600, 0, 200, 50], 9, "Load Level", black, 30, grey))
        self.gui.append(guiItem([1800, 0, 100, 50], 11, "Scroll", black, 30, grey))


    def draw(self):
        for object in self.level:
            object.draw()
        for item in self.gui:
            item.draw()


    def undo(self):
        if len(self.level) > 0:
            del self.level[len(self.level) - 1]

    def loadLevel(self):
        ############## Start Level ################
        # Level Geometry
        # rects
        self.level.append(rect([460, 80, 800, 20], (0, 0, 0)))
        self.level.append(rect([460, 100, 20, 240], (0, 0, 0)))
        self.level.append(rect([480, 320, 300, 20], (0, 0, 0)))
        self.level.append(rect([1240, 100, 20, 240], (0, 0, 0)))
        self.level.append(rect([880, 320, 360, 20], (0, 0, 0)))
        self.level.append(rect([1020, 100, 20, 160], (0, 0, 0)))
        self.level.append(rect([880, 180, 140, 20], (0, 0, 0)))
        self.level.append(rect([700, 180, 140, 20], (0, 0, 0)))
        self.level.append(rect([760, 100, 20, 80], (0, 0, 0)))
        self.level.append(rect([560, 180, 100, 20], (0, 0, 0)))
        self.level.append(rect([560, 240, 20, 80], (0, 0, 0)))
        self.level.append(rect([560, 100, 20, 80], (0, 0, 0)))
        self.level.append(rect([0, 160, 380, 20], (0, 0, 0)))
        self.level.append(rect([360, 180, 20, 340], (0, 0, 0)))
        self.level.append(rect([360, 600, 20, 260], (0, 0, 0)))
        self.level.append(rect([380, 840, 300, 20], (0, 0, 0)))
        self.level.append(rect([760, 840, 240, 20], (0, 0, 0)))
        self.level.append(rect([980, 860, 20, 220], (0, 0, 0)))
        self.level.append(rect([800, 860, 20, 40], (0, 0, 0)))
        self.level.append(rect([800, 960, 20, 120], (0, 0, 0)))
        self.level.append(rect([620, 980, 180, 20], (0, 0, 0)))
        self.level.append(rect([400, 980, 160, 20], (0, 0, 0)))
        self.level.append(rect([500, 1000, 20, 80], (0, 0, 0)))
        self.level.append(rect([240, 980, 120, 20], (0, 0, 0)))
        self.level.append(rect([240, 1000, 20, 80], (0, 0, 0)))
        self.level.append(rect([240, 880, 20, 100], (0, 0, 0)))
        self.level.append(rect([240, 720, 20, 100], (0, 0, 0)))
        self.level.append(rect([0, 760, 240, 20], (0, 0, 0)))
        self.level.append(rect([240, 500, 20, 180], (0, 0, 0)))
        self.level.append(rect([0, 560, 240, 20], (0, 0, 0)))
        self.level.append(rect([240, 360, 20, 80], (0, 0, 0)))
        self.level.append(rect([0, 340, 240, 20], (0, 0, 0)))
        self.level.append(rect([240, 340, 60, 20], (0, 0, 0)))
        self.level.append(rect([1060, 840, 20, 240], (0, 0, 0)))
        self.level.append(rect([1320, 420, 600, 20], (0, 0, 0)))
        self.level.append(rect([1320, 420, 20, 80], (0, 0, 0)))
        self.level.append(rect([1320, 580, 20, 280], (0, 0, 0)))
        self.level.append(rect([1220, 840, 100, 20], (0, 0, 0)))
        self.level.append(rect([1060, 840, 100, 20], (0, 0, 0)))
        self.level.append(rect([1080, 920, 80, 20], (0, 0, 0)))
        self.level.append(rect([1220, 920, 120, 20], (0, 0, 0)))
        self.level.append(rect([1320, 940, 20, 140], (0, 0, 0)))
        self.level.append(rect([1420, 440, 20, 60], (0, 0, 0)))
        self.level.append(rect([1420, 580, 20, 280], (0, 0, 0)))
        self.level.append(rect([1420, 920, 20, 160], (0, 0, 0)))
        self.level.append(rect([1420, 920, 100, 20], (0, 0, 0)))
        self.level.append(rect([1580, 920, 200, 20], (0, 0, 0)))
        self.level.append(rect([1860, 920, 60, 20], (0, 0, 0)))
        self.level.append(rect([1660, 940, 20, 140], (0, 0, 0)))
        self.level.append(rect([1440, 840, 160, 20], (0, 0, 0)))
        self.level.append(rect([1660, 840, 260, 20], (0, 0, 0)))
        self.level.append(rect([1440, 660, 480, 20], (0, 0, 0)))
        # PathingRectangles
        self.level.append(pathpoint([500, 120, 40, 180], 0))
        self.level.append(pathpoint([600, 120, 140, 40], 1))
        self.level.append(pathpoint([800, 120, 200, 40], 2))
        self.level.append(pathpoint([1060, 120, 160, 180], 3))
        self.level.append(pathpoint([840, 180, 40, 20], 4))
        self.level.append(pathpoint([1020, 260, 20, 60], 5))
        self.level.append(pathpoint([660, 180, 40, 20], 6))
        self.level.append(pathpoint([560, 200, 20, 40], 7))
        self.level.append(pathpoint([780, 320, 100, 20], 8))
        self.level.append(pathpoint([300, 340, 60, 20], 9))
        self.level.append(pathpoint([240, 440, 20, 60], 10))
        self.level.append(pathpoint([240, 680, 20, 40], 11))
        self.level.append(pathpoint([240, 820, 20, 60], 12))
        self.level.append(pathpoint([360, 980, 40, 20], 13))
        self.level.append(pathpoint([560, 980, 60, 20], 14))
        self.level.append(pathpoint([800, 900, 20, 60], 15))
        self.level.append(pathpoint([360, 520, 20, 80], 16))
        self.level.append(pathpoint([680, 840, 80, 20], 17))
        self.level.append(pathpoint([620, 240, 360, 60], 18))
        self.level.append(pathpoint([460, 420, 720, 360], 19))
        self.level.append(pathpoint([840, 880, 120, 180], 20))
        self.level.append(pathpoint([540, 1020, 240, 40], 21))
        self.level.append(pathpoint([280, 1020, 200, 40], 22))
        self.level.append(pathpoint([20, 800, 200, 260], 23))
        self.level.append(pathpoint([20, 600, 200, 140], 24))
        self.level.append(pathpoint([20, 380, 200, 160], 25))
        self.level.append(pathpoint([20, 200, 320, 120], 26))
        self.level.append(pathpoint([280, 480, 60, 80], 29))
        self.level.append(pathpoint([300, 900, 60, 60], 30))
        self.level.append(pathpoint([620, 900, 120, 60], 31))
        ############## End Level ################

    def scroll(self):
        self.scrollTimer -= fps
        if self.scrollTimer < 0:
            self.scrollTimer = self.scrollCooldown
            if wkey == 1:
                self.yScroll -= self.scrollSpeed
                for i in range(len(self.level)):
                    if self.level[i].eraseType == 'rect':
                        self.level[i].rect[1] += self.scrollSpeed
                    if self.level[i].eraseType == 'powerup':
                        self.level[i].y += self.scrollSpeed

            if skey == 1:
                self.yScroll += self.scrollSpeed
                for i in range(len(self.level)):
                    if self.level[i].eraseType == 'rect':
                        self.level[i].rect[1] -= self.scrollSpeed
                    if self.level[i].eraseType == 'powerup':
                        self.level[i].y -= self.scrollSpeed

            if dkey == 1:
                self.xScroll += self.scrollSpeed
                for i in range(len(self.level)):
                    if self.level[i].eraseType == 'rect':
                        self.level[i].rect[0] -= self.scrollSpeed
                    if self.level[i].eraseType == 'powerup':
                        self.level[i].x -= self.scrollSpeed

            if akey == 1:
                self.xScroll -= self.scrollSpeed
                for i in range(len(self.level)):
                    if self.level[i].eraseType == 'rect':
                        self.level[i].rect[0] += self.scrollSpeed
                    if self.level[i].eraseType == 'powerup':
                        self.level[i].x += self.scrollSpeed



        def unScroll(self):
            for i in range(len(self.level)):
                if self.level[i].eraseType == 'rect':
                    self.level[i].rect[1] = round(self.level[i].rect[1] + self.yScroll)
                    self.level[i].rect[0] = round(self.level[i].rect[0] + self.xScroll)
                if self.level[i].eraseType == 'powerup':
                    self.level[i].y = round(self.level[i].y + self.yScroll)
                    self.level[i].x = round(self.level[i].x + self.xScroll)
            self.player.x = round(self.player.x + self.xScroll)
            self.end.x = round(self.end.x + self.xScroll)
            self.player.y = round(self.player.y + self.yScroll)
            self.end.y = round(self.end.y + self.yScroll)


    def unScroll(self):
        for object in self.level:
            if object.eraseType == 'rect':
                object.rect[0] += self.xScroll
                object.rect[1] += self.yScroll






def printLevel():
    if editor.doScroll == 1:
        editor.unScroll()
    print('############## Start Level ################')
    print('#Level Geometry ')
    print('#rects')
    for object in editor.level:
        if object.type == 'rect':
            print('self.level.append(rect(' + str(object.rect) + ', ' + str(object.color) + '))')
    print('#PathingRectangles')
    for object in editor.level:
        if object.type == 'pathpoint':
            print('self.level.append(pathpoint(' + str(object.rect) + ', ' + str(object.num) + '))')
    print('############## End Level ################')





def gameupdate():
    editor.update()


def gamedraw():
    editor.draw()
    pygame.display.update()
    screen.fill(white)


def text_objects(text, font,color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()


def message_display(text,size,x,y,color):
    largeText = pygame.font.Font('freesansbold.ttf',size)
    TextSurf, TextRect = text_objects(text, largeText,color)
    TextRect.center = (x,y)
    screen.blit(TextSurf, TextRect)



# pygame screen init
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1920, 1080))
screenx = 1920
screeny = 1080
# fps init
t1 = time.perf_counter()
displayFps = 1
fpsTotal = 1
fps = .001
fpsReal = .1
timer = 0
# colors
gold = (212, 175, 55)
black = (0, 0, 0)
lightblack = (50, 50, 50)
grey = (200, 200, 200)
darkgrey = (150, 150, 150)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
#images
# init
pause = 0
gameSpeed = 1
editor = editor()
#key init
mouse = 0
wkey = 0
skey = 0
akey = 0
dkey = 0
spacekey = 0

while 1:
    t1 = time.perf_counter()
    gameupdate()
    gamedraw()
    # key detection
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
            if key == 'escape':
                pygame.quit()
                sys.exit()
            if key == 'w':
                wkey = 1
            if key == 's':
                skey = 1
            if key == 'a':
                akey = 1
            if key == 'd':
                dkey = 1
            if key == 'space':
                spacekey = 1
        elif event.type == pygame.KEYUP:
            key = pygame.key.name(event.key)
            if key == 'w':
                wkey = 0
            if key == 's':
                skey = 0
            if key == 'a':
                akey = 0
            if key == 'd':
                dkey = 0
            if key == 'space':
                spacekey = 0
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse = 1
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse = 0

    pygame.event.clear()
    # fps management
    fpsReal = time.perf_counter() - t1
    if fpsReal > 1 / 30:
        fps = 1 / 30
    else:
        fps = fpsReal
    if timer % 100 == 0:
        timer = 1
        displayFps = fpsTotal / 100
        fpsTotal = 0
    else:
        fpsTotal += fpsReal
    timer += 1
