from graphics import *
import time
import math
import random

#testing modifiers
playerspeed = 15
_bulletspeed = 1
hitboxsize = 10
focusMode = False

class player(Circle):
    pos = [300, 300] #we store our own position because internal position is private
    def __init__(self):
        super().__init__(Point(height/2, width/2), 10)
        self.draw(win)
        self.hitbox = Circle(Point(height/2, width/2), 10/4) #hitbox moves with the player object and is what gets checked for collision
    def move(self, dx, dy):
        super().move(dx, dy)
        self.pos[0] += dx
        self.pos[1] += dy
        self.hitbox.move(dx, dy)
    def checkcollide(self,point): #checks all 4 sides of the hitbox, this isn't really the most optimal way but because of the amount of bullets it's hard to use other methods 
        if point.getX() <= (self.pos[0]+hitboxsize) and point.getX() >=(self.pos[0]-hitboxsize) and point.getY() >= (self.pos[1]-hitboxsize) and point.getY() <= (self.pos[1]+hitboxsize):
                        return True
        else:
            return False
    def doDeath(self): #death animation, turns black, teleports to bottom middle, and moves up.
        self.setFill("black")
        self.move((300-self.pos[0]),(600-self.pos[1]))
        for i in range(20):
            time.sleep(.02)
            self.move(0,-10)
            for i in hazards:
               if not i.nextmove():
                  hazards.remove(i)
        self.setFill("red")
    def doShot(self): #uses the same bullet object as enemies, 
        global attacks
        attacks.append(bullet(Point(self.pos[0]-2.5, self.pos[1]-2.5),Point(self.pos[0]+2.5, self.pos[1]+2.5),math.pi,10,.1,.1))

class bullet(Rectangle):
    def __init__(self, p1, p2, direction, velocity, level,shot):
         super().__init__(p1, p2)
         self.pos = [p1.getX(),p1.getY(),p2.getX() - p1.getX() ,p2.getY() - p1.getY()]
         self.draw(win)
         self.direction = direction #angle that the bullet goes, in radians
         self.velocity = velocity *_bulletspeed
         self.level = level
         self.fuse = .6 * level
         self.shot = shot
         if level == 3:
            self.setOutline("red")
         if level == 2:
            self.setOutline("green")
         if level == 1:
            self.setOutline("blue")
    def nextmove(self):
        nextX = (math.sin(self.direction)) * self.velocity
        nextY = (math.cos(self.direction)) * self.velocity
        self.move(nextX, nextY)
        self.pos[0] += nextX
        self.pos[1] += nextY
        if self.pos[1] >= 650 or self.pos[1] <-50 or self.pos[0] >= 650 or self.pos[0] <= -50:
            return False
        return True
    def getpos(self):
        return Point(self.pos[0], self.pos[1])
    def updatePos(self,index, newval):
        self.pos[index] = newval
    def split(self): #bullets split into more bullets. This is governed by the "level" of a bullet (e.g. level 3 bullets make level 2 bullets which make level 1 bullets)
        spread = []
        if self.level == 3:
            for i in range(8):
                spread.append(bullet(self.getpos(), Point(self.pos[0]+self.pos[2], self.pos[1]+self.pos[3]),self.direction + self.shot *i,self.velocity *2,2,self.shot))
            self.level = 0
        if self.level == 2:
           spread.append(bullet(self.getpos(), Point(self.pos[0]+self.pos[2], self.pos[1]+self.pos[3]),self.direction, self.velocity*1.5, 1,self.shot))
           spread.append(bullet(self.getpos(), Point(self.pos[0]+self.pos[2], self.pos[1]+self.pos[3]),self.direction- self.shot, self.velocity*1.5, 1,self.shot))
           spread.append(bullet(self.getpos(), Point(self.pos[0]+self.pos[2], self.pos[1]+self.pos[3]),self.direction+ self.shot, self.velocity*1.5, 1,self.shot))
           self.level = 0
        if self.level == 1:
            spread.append(bullet(self.getpos(), Point(self.pos[0]+self.pos[2], self.pos[1]+self.pos[3]),self.direction - self.shot, self.velocity *2, 0,self.shot))
            spread.append(bullet(self.getpos(), Point(self.pos[0]+self.pos[2], self.pos[1]+self.pos[3]),self.direction + self.shot, self.velocity *2, 0, self.shot))
            self.level = 0
        if self.level==.1:
            spread.append(bullet(self.getpos(), Point(self.pos[0]+self.pos[2], self.pos[1]+self.pos[3]),self.direction, self.velocity*1.5, 0,self.shot))
            spread.append(bullet(self.getpos(), Point(self.pos[0]+self.pos[2], self.pos[1]+self.pos[3]),self.direction- self.shot, self.velocity*1.5, 0,self.shot))
            spread.append(bullet(self.getpos(), Point(self.pos[0]+self.pos[2], self.pos[1]+self.pos[3]),self.direction+ self.shot, self.velocity*1.5, 0,self.shot))
            self.level = 0
        return spread

class enemy(bullet): #an enemy is a subclass of bullet, it has HP, can die, and uses more complex movement styles.
    def __init__(self, p1, p2, path, fuse, hp, shotlevel,shottype, amount):
        super().__init__(p1, p2, 0, 6, 1,0)
        self.setFill("black")
        self.path = path #different types of movement paths, modified with numbers after spaces.
        #Current types of movement:
        #line[L or R]: move in a straight line, modifier used for moving left or right
        #slow [modifier]: move in a straight line, modifier used for amount of slowed pixels, center justified
        self.fuse = fuse #amount of time before shoots
        self.hp = hp #amount of hits to kill
        self.shotlevel = shotlevel #what level bullet it shoots
        self.shottype = shottype #spread of shots
        self.amount = amount
    def nextmove(self):
        if "lineR" in self.path:
            self.move(6,0)
            self.pos[0] += 6
            if self.pos[0] >= 650 or self.pos[0] <= -50:
                return False
            return True
        if "lineL" in self.path:
            self.move(-6,0)
            self.pos[0] -= 6
            if self.pos[0] >= 650 or self.pos[0] <= -50:
                return False
            return True
        if "slow" in self.path:
            slow = 50
            splitpath = self.path.split(" ")
            if splitpath[1]:
                slow = int(splitpath[1])/2
            if self.pos[0] >= 300-slow and self.pos[0] <= 300+slow:
                self.move(2,0)
                self.pos[0] += 2
                return True
            else:
                self.move(6,0)
                self.pos[0] += 6
            if self.pos[0] >= 650 or self.pos[0] <= -50:
                return False
            return True

    def split(self): #uses the split method to "shoot" from itself
        if self.amount >0:
            self.amount -= 1
            self.fuse = .2
            return [bullet(self.getpos(), Point(self.pos[0]+5, self.pos[1]+5),(random.randint(0,1000)-800)/1000,4,self.shotlevel,self.shottype)]
        return[]
    def checkcollide(self,point):
        if point.getX() <= (self.pos[0]+2.5) and point.getX() >=(self.pos[0]-2.5) and point.getY() >= (self.pos[1]-2.5) and point.getY() <= (self.pos[1]+2.5):
                        return True
        else:
            return False
    def doDeath(self):
        global objects
        self.hp = self.hp -1
        if self.hp <= 0:
            self.undraw()
            return True
        return False


    


#initialize visuals
win = GraphWin(width= 600, height=600)
height = win.getHeight()
width = win.getWidth()
open = True
player1 = player()
player1.setFill("red")
win.addItem(player1)
debugtextpos = Text(Point(65, 585), "Position" + str(player1.pos))
debugtextpos.draw(win)
debugtextframes = Text(Point(540, 585), "Frames passed" + str(0))
debugtextframes.draw(win)
tutorialText = Text(Point(95,75), "Controls:\nZ:Shoot\nShift:Focus/Show Hitbox\n1:Spawn enemy example 1\n2:Spawn enemy example 2\n3:Spawn bullet example 1\n4:Spawn bullet example 2\n5:Start example level")
tutorialText.draw(win)
levelText = Text(Point(550, 20), "Level Started")


#creating hitboxes

upKey = "Up"    # Controls settings
downKey = "Down"
leftKey = "Left"
rightKey = "Right"
time.sleep(.5)


def parsecontrol(key):
    if not key:
        return [0]
    global playerspeed
    if key == rightKey:
        player1.move(1*playerspeed, 0)
    if key == downKey:
         player1.move(0, 1*playerspeed)
    if key == upKey:
         player1.move(0, -1*playerspeed)
    if key == leftKey:
         player1.move(-1*playerspeed, 0)
    if key == "Shift_L":
        global focusMode
        global hitboxsize
        if focusMode == False:
            focusMode = True
            playerspeed =  playerspeed /4
            hitboxsize = hitboxsize / 2.5
            player1.hitbox.draw(win)
            return [0]
        else:
            focusMode = False
            playerspeed =  playerspeed * 4
            hitboxsize = hitboxsize * 2.5
            player1.hitbox.undraw()
    if key == "z":
        player1.doShot()
    if key == "1":
        objects.append(enemy(Point(0,50),Point(10,60),"slow 300",.5,1,2,3,4))
    if key == "2":
        hazards.append(enemy(Point(590,70),Point(600,80),"lineL", 2, 1, 3, 2, 2))
    if key == "3":
        hazards.append(bullet(Point(200,40), Point(205,45), 25.1,4, 3,5))
    if key == "4":
        hazards.append(bullet(Point(300,40), Point(205,45),0,2,3,5))
    if key == "5":
        levelStart[0] = True
        levelStart[1] = framecount
        levelText.draw(win)
        
    
    return [0]

def doCollision():
    for i in objects:
        if type(i) == player:
            for j in hazards:
                if i.checkcollide(Point(j.pos[0], j.pos[1])):
                    i.doDeath()
                if i.checkcollide(Point(j.pos[0]+j.pos[2],j.pos[1])):
                    i.doDeath()
                if i.checkcollide(Point(j.pos[0],j.pos[1]+j.pos[3])):
                    i.doDeath()
                if i.checkcollide(Point(j.pos[0]+j.pos[3],j.pos[1]+j.pos[3])):
                    i.doDeath()
        if type(i) == enemy:
            for j in attacks:
                state = False
                if i.checkcollide(Point(j.pos[0], j.pos[1])):
                    state = i.doDeath()
                if i.checkcollide(Point(j.pos[0]+j.pos[2],j.pos[1])):
                    state = i.doDeath()
                if i.checkcollide(Point(j.pos[0],j.pos[1]+j.pos[3])):
                    state = i.doDeath()
                if i.checkcollide(Point(j.pos[0]+j.pos[3],j.pos[1]+j.pos[3])):
                    state = i.doDeath()
                if state:
                    if i in objects:
                        objects.remove(i)

def splitbullets(hazards):
    for i in hazards:
        spread = []
        i.fuse -= (.03)
        if i.fuse <= 0:
            spread = i.split()
        for i in spread:
            hazards.append(i)
    
def levelDesign():
    levelFrames = framecount - levelStart[1]
    if levelFrames == 50:
        objects.append(enemy(Point(590,50),Point(600,60),"lineL",1,1,1,1,1))
    if levelFrames == 70:
        objects.append(enemy(Point(590,60),Point(600,70),"lineL",1,1,1,1,1))
    if levelFrames == 90:
        objects.append(enemy(Point(590,70),Point(600,80),"lineL",1,1,1,1,1))
    if levelFrames == 110:
        objects.append(enemy(Point(590,80),Point(600,90),"lineL",1,1,1,1,1))
    if levelFrames == 200:
        objects.append(enemy(Point(0,50),Point(10,60),"lineR",1,1,2,3,4))
    if levelFrames == 250:
        objects.append(enemy(Point(0,70),Point(10,80),"lineR",1,1,2,3,4))
    if levelFrames == 300:
        objects.append(enemy(Point(0,80),Point(10,90),"lineR",1,1,2,3,4))
    if levelFrames == 350:
        objects.append(enemy(Point(0,100),Point(10,110),"lineR",1,1,2,3,4))
    if levelFrames == 400:
        objects.append(enemy(Point(0,120),Point(10,130),"lineR",1,1,2,3,4))


objects = [player1]
hazards = []
attacks = []
framecount = 0
levelStart = [True,0] #using a list for this because python gets mad when you edit variables in a function
while(open):
    clock = time.time()
    currentKey = win.checkKey()
    if levelStart[0]:
        levelDesign()
    action = parsecontrol(currentKey)
    if action[0] == 1:
        player1.move(action[1], action[2])
    for i in hazards:
        if not i.nextmove():
            hazards.remove(i)
    splitbullets(hazards)
    for i in attacks:
        if not i.nextmove():
            attacks.remove(i)
    splitbullets(attacks)
    for i in objects:
        if type(i) == enemy:
            if not i.nextmove():
                objects.remove(i)
            spread = []
            i.fuse -= (.03)
            if i.fuse <= 0:
                spread = i.split()
            for i in spread:
                hazards.append(i)
    doCollision()
    debugtextpos.setText("Position" + str(player1.pos))
    debugtextframes.setText("Frames:" + str(framecount))
    clock = time.time() - clock
    if ((clock) < .02):
        time.sleep(.02 - (clock))
    framecount += 1
    
    
