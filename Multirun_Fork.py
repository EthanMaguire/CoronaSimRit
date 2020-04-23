import pygame
import sys
import random
import math
import time
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter




class guiItem:
    def __init__(self, rect, action, text, textColor, fontSize, rectColor):
        self.rect = rect
        self.actionNumber = action
        self.text = text
        self.fontSize = fontSize
        self.rectColor = rectColor
        self.textColor = textColor
        self.clicked = 0
        self.timer = 0
        self.darknessTime = .5
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
            if world.socialDistancing == 0:
                world.socialDistancing = 1
            else:
                world.socialDistancing = 0
        elif self.actionNumber == 2:
            world.humans[random.randint(0, len(world.humans) - 1)].health = 1
        elif self.actionNumber == 3:
            world.infectionChance += .0001
        elif self.actionNumber == 4:
            world.infectionChance -= .0001
        elif self.actionNumber == 5:
            world.infectionRange += 1
        elif self.actionNumber == 6:
            world.infectionRange -= 1
        elif self.actionNumber == 7:
            world.infectionRemoval += .1
        elif self.actionNumber == 8:
            world.infectionRemoval -= .1
        elif self.actionNumber == 9:
            if world.masks == 0:
                world.infectionRange = world.maskRangeBonus
                world.infectionChance = world.maskInfectionBonus
                world.masks = 1
            else:
                world.infectionRange = 30
                world.infectionChance = .002
                world.masks = 0
        elif self.actionNumber == 10:
            if world.handwashing == 0:
                world.infectionRemoval = world.handwashingBonus
                world.handwashing = 1
            else:
                world.infectionRemoval = .2
                world.handwashing = 0
        elif self.actionNumber == 11:
            if world.testing == 0:
                world.testing = 1
            else:
                world.testing = 0
                world.contactTracing = 0
                world.testingTime = .4
        elif self.actionNumber == 12:
            if world.contactTracing == 0 and world.testing == 1:
                world.contactTracing = 1
                world.testingTime = world.contactTracingBonus
            else:
                world.contactTracing = 0
                world.testingTime = .4



class pathpoint:
    def __init__(self, rect, num):
        self.rect = rect
        self.num = num
        self.validPaths = []
        self.doDraw = 0
        self.students = []

    def update(self):
        pass

    def draw(self):
        if self.doDraw == 1:
            pygame.draw.rect(screen, red,self.rect, 5)
            message_display(str(self.num), 20,self.rect[0] + self.rect[2] / 2, self.rect[1] + self.rect[3] / 2, black)



class rect:
    def __init__(self, rect, color):
        self.eraseType = 'rect'
        self.type = 'rect'
        self.rect = rect
        self.color = color

    def update(self):
        pass

    def draw(self):
        pygame.draw.rect(screen,self.color,self.rect)



class human:
    def __init__(self, rect):
        self.rect = rect
        # 0 = Healthy, 1 = Infected, 2 = Recovered, 3 = Dead
        self.health = 0
        #schedule is where to do and how long to stay
        self.numMoves = 200
        self.schedule = []
        self.makeSchedule()
        self.currentVector = [0, 0]
        self.currentTarget = [0, 0]
        self.currentMove = 0
        self.scheduleTimer = 0
        self.atLocation = 1
        #movement and Collision
        self.speed = 40
        self.collideFlag = 0
        #infection chance updating
        self.infectionTimer = 0
        self.infectionInterval = 2 + random.uniform(-.1, .1)
        self.infectionRating = 0
        #infection field updateing
        self.infectUpdateTimer = 0
        self.infectUpdateInterval = 1 + random.uniform(-.1, .1)
        #Death and other unfun stuff
        self.sickTime = world.infectionTime  + random.uniform(-25, 25)
        self.sickTimer = 0
        #testing
        self.testResult = 0
        self.testFlag = 0


    def update(self):
        self.scheduleTimer += fps
        if self.health == 3:
            return
        #Picking where to go
        if self.atLocation == 1:
            if self.scheduleTimer > self.schedule[self.currentMove][1]:
                self.scheduleTimer = 0
                self.atLocation = 0
                self.collideFlag = 0
                self.currentMove += 1
                targetRect = world.pathpoints[self.schedule[self.currentMove][0]].rect
                #pick a random spot in the target pathpoint to go to
                self.currentTarget = [random.randint(targetRect[0] + self.rect[2] / 2, targetRect[0] + targetRect[2] - self.rect[2] / 2), \
                                     random.randint(targetRect[1] + self.rect[3] / 2, targetRect[1] + targetRect[3] - self.rect[3] / 2)]
                self.currentVector = [self.currentTarget[0] - self.rect[0], self.currentTarget[1] - self.rect[1]]
                dist = math.sqrt(self.currentVector[0] ** 2 + self.currentVector[1] ** 2)
                self.currentVector = [self.currentVector[0] / dist, self.currentVector[1] / dist]
            elif world.socialDistancing == 1 and self.collideFlag == 0:
                for object in world.level:
                    if isinstance(object, rect) == True:
                        if checkCollision(self.rect, object.rect) == True:
                            self.collideFlag = 1
                            break
                #find those nearby using classlists
                for human in world.pathpoints[self.schedule[self.currentMove][0]].students:
                    if abs(human.rect[0] - self.rect[0]) < world.socialDistance:
                        if abs(human.rect[1] - self.rect[1]) < world.socialDistance:
                            #make them move away in x
                            if human.rect[0] == self.rect[0]:
                                break
                            elif human.rect[0] < self.rect[0]:
                                self.rect[0] += 5 * fps
                                if human.collideFlag == 0 and human.atLocation == 1:
                                    human.rect[0] -= 5 * fps
                            else:
                                self.rect[0] -= 5 * fps
                                if human.collideFlag == 0 and human.atLocation == 1:
                                    human.rect[0] += 5 * fps
                            # make them move away in y
                            if human.rect[1] < self.rect[1]:
                                self.rect[1] += 5 * fps
                                if human.collideFlag == 0 and human.atLocation == 1:
                                    human.rect[1] -= 5 * fps
                            else:
                                self.rect[1] -= 5 * fps
                                if human.collideFlag == 0 and human.atLocation == 1:
                                    human.rect[1] += 5 * fps
                            break

        #stop movement if they made it to the goal destination
        if abs(self.rect[0] - self.currentTarget[0]) < 10 and abs(self.rect[1] - self.currentTarget[1]) < 10:
            self.atLocation = 1
        #movement
        if self.atLocation == 0:
            self.rect[0] += self.currentVector[0] * fps * self.speed
            self.rect[1] += self.currentVector[1] * fps * self.speed
        #dont let them leave the screen
        if self.rect[0] < 5:
            self.rect[0] == 5
        elif self.rect[0] + self.rect[2] > screenx - 5:
            self.rect[0] = screenx - self.rect[2] - 5
        if self.rect[1] < 5:
            self.rect[1] == 5
        elif self.rect[1] + self.rect[3] > screeny - 5:
            self.rect[1] = screeny - self.rect[3] - 5
        #infection field update
        if self.health == 0:
            self.infectionTimer += fps
            if self.infectionTimer > self.infectionInterval:
                self.infectionTimer = 0
                fieldx = round((self.rect[0] + self.rect[2] / 2) / world.infectionField.dx)
                fieldy = round((self.rect[1] + self.rect[3] / 2) / world.infectionField.dy)
                self.infectionRating += world.infectionField.grid[fieldx][fieldy] * self.infectionInterval
                self.infectionRating -= world.infectionRemoval * self.infectionInterval
                infectionChance = self.infectionRating * world.infectionChance * self.infectionInterval
                if self.infectionRating > 0:
                    if random.randint(0, round(1 / infectionChance)) == 0:
                        self.health = 1

        elif self.health == 1:
            self.infectUpdateTimer += fps
            self.sickTimer += fps
            if self.sickTimer > self.sickTime:
                if random.randint(0, round(1 / world.deathRate)) == 0:
                    self.health = 3
                else:
                    self.health = 2
            elif self.sickTimer / self.sickTime > world.testingTime and world.testing == 1 and self.testFlag == 0:
                self.testFlag = 1
                if random.uniform(0,1) < world.testingChance:
                    self.testResult = 1
            if self.infectUpdateTimer > self.infectUpdateInterval and self.testResult == 0 and \
                    self.sickTimer / self.sickTime > world.incubationTime:
                self.infectUpdateTimer = 0
                #update the infection field around the infected person with infectivity decreasing linearly over the distance
                numx = world.infectionRange / world.infectionField.dx
                numy = world.infectionRange / world.infectionField.dy
                fieldx = round((self.rect[0] + self.rect[2] / 2) / world.infectionField.dx - numx)
                fieldy = round((self.rect[1] + self.rect[3] / 2) / world.infectionField.dy - numy)
                for x in range(int(2 * numx - 1)):
                    if fieldx + x < world.fieldxMax:
                        for y in range(int(2 * numy - 1)):
                            if fieldy + y < world.fieldyMax:
                                #Calculates infectivness based on distance from the person
                                val = 0
                                if x < numx:
                                    val += x
                                else:
                                    val += 2 * x - numx
                                if y < numy:
                                    val += y
                                else:
                                    val += 2 * y - numy
                                val /= numx + numy
                                if world.infectionField.grid[fieldx + x][fieldy + y] < 0:
                                    world.infectionField.grid[fieldx + x][fieldy + y] = world.infectivity * self.infectUpdateInterval * val
                                else:
                                    world.infectionField.grid[fieldx + x][fieldy + y] += world.infectivity * self.infectUpdateInterval * val


    def draw(self):
        posx = round(self.rect[0] + self.rect[2] / 2)
        posy = round(self.rect[1] + self.rect[3] / 2)
        radius = round(self.rect[2] / 2)
        if self.health == 0:
            pygame.draw.circle(screen, green, [posx, posy], radius)
        elif self.health == 1:
            if self.testResult == 0:
                pygame.draw.circle(screen, red, [posx, posy], radius)
            elif self.testResult == 1:
                pygame.draw.circle(screen, gold, [posx, posy], radius)
        elif self.health == 2:
            pygame.draw.circle(screen, blue, [posx, posy], radius)
        elif self.health == 3:
            pygame.draw.rect(screen, black, self.rect)


    def makeSchedule(self):
        self.classLength = 50
        #find which zone the human started in
        for object in world.pathpoints:
            if checkCollision(self.rect, object.rect) == True:
                if len(object.validPaths) == 1:
                    # make them stay longer in classrooms
                    self.schedule.append([object.num, 10])
                else:
                    self.schedule.append([object.num, 1])
                break
        #iterate through numMoves to make a schedule
        for move in range(self.numMoves):
            #find out how many connections are from current position in schedule
            for object in world.pathpoints:
                if object.num == self.schedule[move][0]:
                    choices = len(object.validPaths)
                    while 1:
                        pick = random.randint(0, choices - 1)
                        choice = object.validPaths[pick]
                        if move == 0:
                            break
                        if len(object.validPaths) == 1:
                            break
                        #make it not repeat the previous choice
                        if world.pathpoints[choice].num != self.schedule[move - 1][0]:
                            break
                        # print(world.pathpoints[choice].num)
                        # print(object.validPaths)
                    if len(world.pathpoints[choice].validPaths) == 1:
                        #make them stay longer in classrooms
                        self.schedule.append([choice, self.classLength])
                    else:
                        self.schedule.append([choice, 1])
                    break
        # print(self.schedule)



class field:
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy
        #generates a matrix across the entire simulation space that has form (x,y,z) with z being infectivity
        self.grid = np.zeros((round(screenx / self.dx), round(screeny / self.dy)))
        #grid offset is used to not need to scroll the grid
        self.offsetx = 0
        self.offsety = 0

    def update(self):
        self.grid *= world.latentInfectivityMult
        self.grid -= world.latentInfectivity * world.fieldUpdateInteval



class engine:
    def __init__(self):
        #level
        self.levelNumber = 2
        self.level = []
        self.loadLevel()
        self.findValidPaths()

        #Gui
        self.gui = []
        self.loadGui()

        #entities and humans
        self.humans = []
        self.numHumans = 700
        #scrolling / zoom
        self.zoom = 1
        self.scrollSpeed = 1
        #create infection field with grid size dx,dy
        dx = 5
        dy = 5
        self.infectionField = field(dx, dy)
        self.fieldxMax = round(screenx / dx - 1)
        self.fieldyMax = round(screeny / dy - 1)
        self.fieldUpdateInteval = 1
        self.fieldUpdateTimer = 0
        #infection variables
        #infectivity affects how much the virus is spread by those infected
        self.infectivity =  1.5
        #latentInfectivity affects how long the virus lingers after being spread by a infected person
        self.latentInfectivity = .3
        self.latentInfectivityMult = .9
        #infectionRange affects how far away an infected person causes infection
        self.infectionRange = 30
        #infectionChance affects the chance that exposure will infect, more exposure means a higher chance regardless
        self.infectionChance = .002
        # deathrate explains itself
        self.deathRate = .15
        #how long someone is sick
        self.infectionTime = 250
        #how long infection stays on someone if they dont get infected
        self.infectionRemoval = .2
        # incubation time, time before human is infective
        self.incubationTime = .1


        # testing is the chance that someone will be quarantined after being infected for some percentage of the total infection time
        self.testing = 0
        self.testingChance = .5
        self.testingTime = .4
        self.contactTracing = 0
        self.contactTracingBonus = .25

        #Social Distancing
        self.socialDistancing = 0
        self.socialDistance = 20

        # handwashing
        self.handwashing = 0
        self.handwashingBonus = .3

        # masks
        self.masks = 0
        self.maskRangeBonus = 25
        self.maskInfectionBonus = .0015



        #data
        self.numInfected = 0
        self.numDead = 0
        self.numRecovered = 0

        #multirun flags
        #what percentage of ppl infected for social distancing to turn on
        self.socialFlag = 0
        self.socialDistanceTrigger = .8
        self.maskTrigger = .8
        self.handwashingTrigger = .8
        self.testingTrigger = .8
        self.contactTracingTrigger = .8
        self.infectedStart = 5
        self.testTurnoff = 0
        self.turnoff = 0
        self.firstframe = 0


        #data
        self.timeControl = 0

    def update(self):
        #first frame stuff for multirun
        if self.firstframe == 0:
            self.firstframe = 1
            for i in range(self.infectedStart):
                self.humans[i].health = 1
        if self.socialDistancing == 0 and self.socialFlag == 0:
            if self.numInfected / self.numHumans > self.socialDistanceTrigger:
                self.socialDistancing = 1
                self.socialFlag = 1
        elif self.socialDistancing == 1 and self.turnoff == 1:
            if self.numInfected / self.numHumans < self.socialDistanceTrigger:
                self.socialDistancing = 0
        if self.masks == 0:
            if self.numInfected / self.numHumans > self.maskTrigger:
                self.masks = 1
                world.infectionRange = world.maskRangeBonus
                world.infectionChance = world.maskInfectionBonus
        elif self.masks == 1 and self.turnoff == 1:
            if self.numInfected / self.numHumans < self.maskTrigger:
                world.infectionRange = 30
                world.infectionChance = .002
        if self.handwashing == 0:
            if self.numInfected / self.numHumans > self.handwashingTrigger:
                self.handwashing = 1
                world.infectionRemoval = world.handwashingBonus
        elif self.handwashing == 1 and self.turnoff == 1:
            if self.numInfected / self.numHumans < self.handwashingTrigger:
                world.infectionRemoval = .2
        if self.testing == 0:
            if self.numInfected / self.numHumans > self.testingTrigger:
                self.testing = 1
        elif self.testing == 1 and self.testTurnoff == 1:
            if self.numInfected / self.numHumans < self.testingTrigger:
                self.testing = 0
        if self.contactTracing == 0:
            if self.numInfected / self.numHumans > self.contactTracingTrigger:
                self.testingTime = self.contactTracingBonus
        elif self.contactTracing == 1 and self.testTurnoff == 1:
            if self.numInfected / self.numHumans < self.contactTracingTrigger:
                self.testing = .4
        #take data for graphing
        self.takeData()
        for item in self.gui:
            item.update()
        #update humans
        self.numInfected = 0
        self.numRecovered = 0
        for human in self.humans:
            human.update()
            if human.health == 1:
                self.numInfected += 1
            elif human.health == 2:
                self.numRecovered += 1
            elif human.health == 3:
                self.numDead += 1
        #cull dead humans
        for i in range(len(self.humans)):
            if self.humans[i].health == 3:
                del self.humans[i]
                self.numHumans -= 1
                break
        #place humans in classroom lists
        for object in self.pathpoints:
            object.students = []
        for human in self.humans:
            if human.atLocation == 1:
                currentPathpoint = human.schedule[human.currentMove][0]
                self.pathpoints[currentPathpoint].students.append(human)

        #update level
        for object in self.level:
            object.update()

        #update infection field
        self.fieldUpdateTimer += fps
        if self.fieldUpdateTimer > self.fieldUpdateInteval:
            self.fieldUpdateTimer = 0
            self.infectionField.update()

        #scrolling
        self.scroll()

    def draw(self):
        for human in self.humans:
            human.draw()
        for object in self.level:
            object.draw()
        for item in self.gui:
            item.draw()
        #draw red boxes around GUI items that are on
        if self.socialDistancing == 1:
            pygame.draw.rect(screen, green, [screenx - 300,100,300,50], 2)
        else:
            pygame.draw.rect(screen, red, [screenx - 300, 100, 300, 50], 2)
        if self.masks == 1:
            pygame.draw.rect(screen, green, [screenx - 300, 50, 100, 50], 2)
        else:
            pygame.draw.rect(screen, red, [screenx - 300, 50, 100, 50], 2)
        if self.handwashing == 1:
            pygame.draw.rect(screen, green, [screenx - 200, 50, 200, 50], 2)
        else:
            pygame.draw.rect(screen, red, [screenx - 200, 50, 200, 50], 2)
        if self.testing == 1:
            pygame.draw.rect(screen, green, [screenx - 300, 0, 100, 50], 2)
        else:
            pygame.draw.rect(screen, red, [screenx - 300, 0, 100, 50], 2)
        if self.contactTracing == 1:
            pygame.draw.rect(screen, green, [screenx - 200, 0, 200, 50], 2)
        else:
            pygame.draw.rect(screen, red, [screenx - 200, 0, 200, 50], 2)

    def loadLevel(self):
        self.level = []
        if self.levelNumber == 1:
            ############## Start Level ################
            # Level Geometry
            # rects
            self.level.append(rect([120, 120, 1760, 40], (0, 0, 0)))
            self.level.append(rect([1840, 160, 40, 880], (0, 0, 0)))
            self.level.append(rect([120, 1000, 1720, 40], (0, 0, 0)))
            self.level.append(rect([120, 160, 40, 880], (0, 0, 0)))
            ############## End Level ################
        elif self.levelNumber == 2:
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
            self.level.append(pathpoint([280, 480, 60, 80], 27))
            self.level.append(pathpoint([300, 900, 60, 60], 28))
            self.level.append(pathpoint([620, 900, 120, 60], 29))
            self.level.append(pathpoint([1320, 500, 20, 80], 30))
            self.level.append(pathpoint([1420, 500, 20, 80], 31))
            self.level.append(pathpoint([1160, 840, 60, 20], 32))
            self.level.append(pathpoint([1160, 920, 60, 20], 33))
            self.level.append(pathpoint([1100, 960, 200, 100], 34))
            self.level.append(pathpoint([1460, 960, 180, 100], 35))
            self.level.append(pathpoint([1700, 960, 200, 100], 36))
            self.level.append(pathpoint([1460, 460, 440, 180], 37))
            self.level.append(pathpoint([1460, 700, 440, 120], 38))
            self.level.append(pathpoint([1600, 840, 60, 20], 39))
            self.level.append(pathpoint([1520, 920, 60, 20], 40))
            self.level.append(pathpoint([1780, 920, 100, 20], 41))
            self.level.append(pathpoint([1360, 540, 40, 40], 42))
            self.level.append(pathpoint([1360, 880, 40, 40], 43))
            self.level.append(pathpoint([1160, 880, 60, 20], 44))
            self.level.append(pathpoint([1780, 880, 60, 20], 45))
            self.level.append(pathpoint([1560, 880, 60, 20], 46))
            ############## End Level ################
        elif self.levelNumber == 3:
            ############## Start Level ################
            # Level Geometry
            # rects
            self.level.append(rect([420, 460, 920, 40], (0, 0, 0)))
            # PathingRectangles
            self.level.append(pathpoint([400, 600, 160, 140], 0))
            self.level.append(pathpoint([780, 260, 240, 140], 1))
            self.level.append(pathpoint([980, 880, 180, 80], 2))
            ############## End Level ################
        else:
            self.levelNumber -= 1
            self.loadLevel()

        #index pathpoints
        self.pathpoints = []
        for object in self.level:
            if isinstance(object, pathpoint) == True:
                self.pathpoints.append(object)
        # print(len(self.pathpoints))

    def findValidPaths(self):
        for object in self.level:
            if isinstance(object, pathpoint) == True:
                objectCenter = object.rect[0] + object.rect[2] / 2, object.rect[1] + object.rect[3] / 2
                for check in self.level:
                    if isinstance(check, pathpoint) == True:
                        if object.num != check.num:
                            checkCenter = check.rect[0] + check.rect[2] / 2, check.rect[1] + check.rect[3] / 2
                            blockFlag = 0
                            for block in self.level:
                                if isinstance(block, pathpoint) == True:
                                    if block.num != object.num and block.num != check.num:
                                        #check if open path from center to center
                                        if lineRect(objectCenter, checkCenter, block.rect) == True:
                                            blockFlag = 1
                                            break
                                else:
                                    if lineRect(objectCenter, checkCenter, block.rect) == True:
                                        blockFlag = 1
                                        break
                            if blockFlag == 0:
                                object.validPaths.append(check.num)
                # print("Valid Paths from " + str(object.num) + ": " + str(object.validPaths))

    def scroll(self):
        xScroll = 0
        yScroll = 0
        #keeps player in middle of screen
        if wkey == 1:
            yScroll  += screeny * self.scrollSpeed * self.zoom * fps
        elif skey == 1:
            yScroll -= screeny * self.scrollSpeed * self.zoom * fps
        if akey == 1:
            xScroll += screenx * self.scrollSpeed * self.zoom * fps
        elif dkey == 1:
            xScroll -= screenx * self.scrollSpeed * self.zoom * fps
        #do the scrolling
        for object in self.level:
            object.rect[1] += yScroll
            object.rect[0] += xScroll
        for human in self.humans:
            human.rect[1] += yScroll
            human.rect[0] += xScroll
        self.infectionField.offsetx += xScroll
        self.infectionField.offsety += yScroll

    def spawnHumans(self):
        # spawn humans
        for i in range(self.numHumans):
            placement = random.randint(0, len(self.pathpoints) - 1)
            for object in self.pathpoints:
                if placement == object.num:
                    placementRect = object.rect
                    break
            rect = [placementRect[0] + random.randint(0 + humanSize / 2, placementRect[2] - humanSize / 2), placementRect[1] + random.randint(0 + humanSize / 2, placementRect[3] - humanSize / 2), humanSize, humanSize]
            self.humans.append(human(rect))

    def loadGui(self):
        self.gui.append(guiItem([screenx - 300,100,300,50], 1, "Social Distancing", black, 30, grey))
        self.gui.append(guiItem([screenx - 300, 150, 300, 50], 2, "Add Infected", black, 30, grey))
        self.gui.append(guiItem([screenx - 300, 200, 200, 50], 100, "Infectivity", black, 30, grey))
        self.gui.append(guiItem([screenx - 100, 200, 50, 50], 3, "+", black, 30, grey))
        self.gui.append(guiItem([screenx - 50, 200, 50, 50], 4, "-", black, 30, grey))
        self.gui.append(guiItem([screenx - 300, 250, 200, 50], 100, "Infect Range", black, 30, grey))
        self.gui.append(guiItem([screenx - 100, 250, 50, 50], 5, "+", black, 30, grey))
        self.gui.append(guiItem([screenx - 50, 250, 50, 50], 6, "-", black, 30, grey))
        self.gui.append(guiItem([screenx - 300, 300, 200, 50], 100, "Hygiene", black, 30, grey))
        self.gui.append(guiItem([screenx - 100, 300, 50, 50], 7, "+", black, 30, grey))
        self.gui.append(guiItem([screenx - 50, 300, 50, 50], 8, "-", black, 30, grey))
        self.gui.append(guiItem([screenx - 300, 50, 100, 50], 9, "Masks", black, 27, grey))
        self.gui.append(guiItem([screenx - 200, 50, 200, 50], 10, "Hand Washing", black, 27, grey))
        self.gui.append(guiItem([screenx - 300, 0, 100, 50], 11, "Testing", black, 25, grey))
        self.gui.append(guiItem([screenx - 200, 0, 200, 50], 12, "Contact Tracing", black, 23, grey))

    def takeData(self):
        suseptable = 0
        infected = 0
        recovered = 0
        dead = 0
        for human in self.humans:
            if human.health == 0:
                suseptable += 1
            elif human.health == 1:
                infected += 1
            elif human.health == 2:
                recovered += 1
            elif human.health == 3:
                dead += 1
        if totalTimer > self.timeControl:
            self.timeControl += 1
            InfectionData[0].append(totalTimer)
            InfectionData[1].append(suseptable)
            InfectionData[2].append(infected)
            InfectionData[3].append(recovered)
            InfectionData[4].append(dead)




def plotInfectionField():
    for x in range(round(screenx / world.infectionField.dx)):
        for y in range(round(screeny / world.infectionField.dy)):
            if world.infectionField.grid[x][y] < 0:
                world.infectionField.grid[x][y] = 0
    cs = plt.contour(world.infectionField.grid)
    cs.cmap.set_over('red')
    cs.cmap.set_under('blue')
    cs.changed()
    plt.show()
    # print(np.amax(world.infectionField.grid))


def plotInfectionGraph():
    #the curve
    plt.plot(InfectionData[0], InfectionData[1], color='green')
    plt.plot(InfectionData[0], InfectionData[2], color='red')
    plt.plot(InfectionData[0], InfectionData[3], color='blue')
    plt.plot(InfectionData[0], InfectionData[4], color='black')
    plt.show()


def checkCollision(r1, r2):
    if (r1[0] < r2[0] + r2[2]) & \
        (r1[0] + r1[2] > r2[0]) & \
        (r1[1] < r2[1] + r2[3]) & \
        (r1[1] + r1[3] > r2[1]):
            return True
    else:
        return False


def lineRect(p1, p2, rect):
    r1 = [min(p1[0], p2[0]), min(p1[1], p2[1]), abs(p1[0] - p2[0]), abs(p1[1] - p2[1])]
    if checkCollision(r1, rect) == False:
        return False
    #if they are equal in x offset one slightly
    if p1[0] != p2[0]:
        if p1[1] != p2[1]:
            m = (p1[1] - p2[1]) / (p1[0] - p2[0])
        else:
            m = (p1[1] - p2[1] + 1) / (p1[0] - p2[0])
    else:
        m = (p1[1] - p2[1]) / (p1[0] - p2[0] + 1)
    yint = -m * p1[0] + p1[1]
    xint = p1[0] - p1[1] / m
    yLeft = m * rect[0] + yint
    yRight = m * (rect[0] + rect[2]) + yint
    xTop = rect[1] / m + xint
    xBot = (rect[1] + rect[3]) / m + xint
    if yLeft > rect[1] and yLeft < rect[1] + rect[3]:
        return True
    if yRight > rect[1] and yRight < rect[1] + rect[3]:
        return True
    if xTop > rect[0] and xTop < rect[0] + rect[2]:
        return True
    if xBot > rect[0] and xBot < rect[0] + rect[2]:
        return True
    return False


def drawDead():
    message_display("Graveyard", 40, 30, 30, black)
    for i in range(world.numDead):
        pygame.draw.rect(screen, black, [20 + i * 10 - (i // 20) * 200, 60 + (i // 20) * 10, 8, 8])


def simupdate():
    world.update()


def simdraw():
    world.draw()
    # draw Gui info
    message_display(str(world.numInfected), 30, screenx - 330, 180, red)
    message_display(str(round(world.infectionChance * 10000)), 30, screenx - 330, 225, black)
    message_display(str(round(world.infectionRange)), 30, screenx - 330, 280, black)
    message_display(str(round(world.infectionRemoval * 10)), 30, screenx - 330, 320, black)
    drawDead()
    ############
    message_display(str(round(1 / displayFps)), 10, screenx - 20, 20, black)
    pygame.display.update()
    screen.fill(white)
    # Data
    if random.randint(0,100) == 0:
        print('#############################')
        print("Time: " + str(totalTimer))
        print("Infected: " + str(world.numInfected))
        print("Recovered: " + str(world.numRecovered))
        print("Dead: " + str(world.numDead))
        print('#############################')


def text_objects(text, font,color):
   textSurface = font.render(text, True, color)
   return textSurface, textSurface.get_rect()


def message_display(text,size,x,y,color):
   largeText = pygame.font.Font('freesansbold.ttf',size)
   TextSurf, TextRect = text_objects(text, largeText,color)
   TextRect.center = (x,y)
   screen.blit(TextSurf, TextRect)

#pygame screen init
pygame.init()
pygame.font.init()
screenx = 1920
screeny = 1080
# screenx = 2560
# screeny = 1440
screen = pygame.display.set_mode((screenx, screeny))


# fps init
t1 = time.perf_counter()
displayFps = 1
fpsTotal = 1
fps = 1 / 30
fpsReal = .1
fpsMax = 144
timer = 0
totalTimer = 0


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
# spikesImg = pygame.image.load('bin/assets/bigspikes.png')

#some base values
humanSize = 10

# init
pause = 0
simSpeed = 5
world = engine()
world.spawnHumans()

#key init
mouse = 0
pkey = 0
wkey = 0
skey = 0
akey = 0
dkey = 0
ikey = 0
okey = 0


#multirun init
currentRun = 0
numRuns = 10
InfectedTrigger = .8
timeTrigger = 2000
numInfectedTrigger = 5

#dataLogs
#infection Data , [time, Suseptable, Infected, Recovered, Dead]
InfectionData = [ [], [], [], [], [] ]
totalData = []

a = []
for i in range(timeTrigger):
    a.append(0)
averageData = [ a, a, a, a, a]



while 1:
    t1 = time.perf_counter()
    if pkey == 0:
        simupdate()
        # simdraw()
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
            if key == 'p':
                if pkey == 1:
                    pkey = 0
                else:
                    pkey = 1
            if key == 'i':
                #infect a random person
                world.humans[random.randint(0, len(world.humans) - 1)].health = 1
            if key == 'o':
                # plotInfectionField()
                plotInfectionGraph()

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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse = 1
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse = 0

    pygame.event.clear()
    # fps management
    fpsReal = time.perf_counter() - t1
    if fpsReal > 1 / 10:
        fps = 1 / 10 * simSpeed
    elif fpsReal < 1 / fpsMax:
        time.sleep(1 / fpsMax - fpsReal)
    else:
        fps = fpsReal * simSpeed
    if timer % 100 == 0:
        timer = 1
        displayFps = fpsTotal / 100
        fpsTotal = 0
    else:
        fpsTotal += fpsReal
    timer += 1
    totalTimer += fps


    #multirun stuff
    if timer % 100 == 0:
        print('#############################')
        print("Current Run: " + str(currentRun))
        print("Time: " + str(totalTimer))
        print("Infected: " + str(world.numInfected))
        print("Recovered: " + str(world.numRecovered))
        print("Dead: " + str(world.numDead))
        print('#############################')
    if totalTimer > timeTrigger or world.numInfected / world.numHumans > InfectedTrigger or (world.numInfected < numInfectedTrigger and totalTimer > 100):
        currentRun += 1
        del world
        world = engine()
        world.spawnHumans()
        totalTimer = 0
        totalData.append(InfectionData)
        InfectionData = [[], [], [], [], []]
        if currentRun > numRuns:
            # the curve
            for i in range(numRuns):
                plt.plot(totalData[i][0], totalData[i][2], color='red')
                plt.plot(totalData[i][0], totalData[i][3], color='blue')
                plt.plot(totalData[i][0], totalData[i][4], color='black')
            plt.show()
            #average data so frustrating
            # for i in range(numRuns):
            #     for k in range(len(totalData[i][0])):
            #         averageData[0][k] += totalData[i][0][k] / numRuns
            #         averageData[2][k] += totalData[i][2][k] / numRuns
            #         averageData[3][k] += totalData[i][3][k] / numRuns
            #         averageData[4][k] += totalData[i][4][k] / numRuns
            # print(averageData[2])
            # plt.plot(averageData[0], averageData[2], color='red')
            # plt.plot(averageData[0], averageData[3], color='blue')
            # plt.plot(averageData[0], averageData[4], color='black')
            # plt.show()
            #quit
            pygame.quit()
            sys.exit()



