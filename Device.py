#!/usr/bin/python3
import json
from Map import point
from Map import carmessage
from copy import deepcopy

directionStr = ['North','East','South','West']

class trafficDevice():

    def __init__(self,x,y,devid):
        self.__posX = x
        self.__posY = y
        self.__deviceID = devid

    def getPosX(self):
        return self.__posX
    def getPosY(self):
        return self.__posY
    def getDeviceID(self):
        return self.__deviceID
    def setPosX(self,x):
        self.__posX = x
    def setPosY(self,y):
        self.__posY = y
    def setDeviceID(self,devid):
        self.__deviceID = devid

class Light(trafficDevice):

    def __init__(self,x,y,devid,r,trafficmap):
        trafficDevice.__init__(self,x,y,devid)
        self.__lightRule = r
        self.__xLightSignal = 0
        self.__yLightSignal = 1
        self.__curCycle = -1
        trafficmap[x][y].setLightID(devid)
        trafficmap[x][y].setPointLightRule(self.__lightRule)

    def getSignal(self,curcycle):
        if (int(curcycle/self.__lightRule)%2==0):
            #horizontal is green, vertical is red
            return 1
        else:
            #horizaontal is red, vertical is green
            return 0
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
class Car(trafficDevice):

    def __init__(self,x,y,devid,maxv,destx,desty,trafficmap):
        trafficDevice.__init__(self,x,y,devid)
        self.__maxVelocity = maxv
        self.__velocity = 0
        self.__destPosX = destx
        self.__destPosY = desty
        self.__arriveDest = 0
        self.__carPath = []#item is string as (x,y)
        self.__msgList = []
        self.__curPosInPath = 0
        self.__curCycle = -1
        self.__myMap = deepcopy(trafficmap)
        self.__mapSize = len(self.__myMap[0])
        self.__findCarPath()

    def __findCarPath(self):
        x = self.getPosX()
        y = self.getPosY()
        dist = [[-1 for i in range(self.__mapSize)] for i in range(self.__mapSize) ]
        dist[x][y] = 0
        self.__dfs(x,y,dist)
        #print (dist)
        pathx = self.__destPosX
        pathy = self.__destPosY
        self.__carPath.clear()
        while pathx!=x or pathy!=y:
            if pathy-1>=0 and dist[pathx][pathy-1]==dist[pathx][pathy]-1:
                pathy = pathy-1
            elif pathx+1<self.__mapSize and dist[pathx+1][pathy]==dist[pathx][pathy]-1:
                pathx = pathx+1
            elif pathy+1<self.__mapSize and dist[pathx][pathy+1]==dist[pathx][pathy]-1:
                pathy = pathy+1
            elif pathx-1>=0 and dist[pathx-1][pathy]==dist[pathx][pathy]-1:
                pathx = pathx-1
            else:
                print("Error in finding path")
            self.__carPath.insert(0,str(pathx)+','+str(pathy))
        self.__carPath.append(str(self.__destPosX)+','+str(self.__destPosY))
        print("Car",self.getDeviceID()," path:")
        print(self.__carPath)

    def __dfs(self,x,y,dist):
        #print ("current node:",x,",",y)
        if x==self.__destPosX and y==self.__destPosY:
            #print("arrive")
            return
        for direction in self.__myMap[x][y].getRoadDirecs():
            nextx = 0
            nexty = 0
            if direction==0:
                nextx = x-1
                nexty = y
            elif direction==1:
                nextx = x
                nexty = y+1
            elif direction==2:
                nextx = x+1
                nexty = y
            else:
                nextx = x
                nexty = y-1

            if nextx>=self.__mapSize or nextx<0 or nexty>=self.__mapSize or nexty<0:
                continue
            #print ("next node:",nextx,",",nexty)
            if dist[nextx][nexty]==-1 or dist[nextx][nexty]>dist[x][y]+1:
                dist[nextx][nexty] = dist[x][y]+1
                #print ("dist_",nextx,",",nexty," is ",dist[nextx][nexty])
                self.__dfs(nextx,nexty,dist)
    def printCarPath(self):
        print ("I am Car {0}".format(self.getDeviceID()))
        print ("My path is:")
        print (self.__carPath)
        print ("")
    def getVelocity(self):
        return self.__velocity
    def getDestPosX(self):
        return self.__destPosX
    def getDestPosY(self):
        return self.__destPosY
    def checkIfArrive(self):
        return self.__arriveDest
    def readLightSignal(self,rule):
        if (int(self.__curCycle/rule)%2==0):
            #horizontal is green, vertical is red
            return 1
        else:
            #horizaontal is red, vertical is green
            return 0
    def sendMsg(self):
        #print ("I am Car {0}".format(self.getDeviceID()))
        #print ("My path is:")
        #print (self.__carPath)
        #print ("I am sending message")
        #print ("")
        msg = carmessage(self.getDeviceID(),self.getPosX(),self.getPosY())
        return msg

    def receiveMsg(self,msglist,curcycle):
        self.__curCycle = curcycle
        for msg in self.__msgList:
            carx = msg.getMsgCarPosX()
            cary = msg.getMsgCarPosY()
            self.__myMap[carx][cary].clearCarIDs()
        self.__msgList.clear()
        self.__msgList = msglist.copy()
        for msg in self.__msgList:
            carx = msg.getMsgCarPosX()
            cary = msg.getMsgCarPosY()
            self.__myMap[carx][cary].addCarID(msg.getMsgCarID())
        #print ("I am Car {0}".format(self.getDeviceID()))
        #print ("My path is:")
        #print (self.__carPath)
        self.__carDecision()

    def __carDecision(self):
        self.__velocity = 0

        posOfLightAhead = []
        idOfLightAhead = []
        posOfCarAhead = []
        for i in range(1,self.__maxVelocity+1):
            if self.__curPosInPath+i>=len(self.__carPath):
                break
            cordinateStr = self.__carPath[self.__curPosInPath+i]
            posOfComma = int(cordinateStr.index(','))
            aheadPosX = (int)(cordinateStr[0:posOfComma])
            aheadPosY = (int)(cordinateStr[posOfComma+1:len(cordinateStr)])
            if self.__myMap[aheadPosX][aheadPosY].getLightID()!=-1:
                posOfLightAhead.append(i)
                idOfLightAhead.append(self.__myMap[aheadPosX][aheadPosY].getLightID())
            if len(self.__myMap[aheadPosX][aheadPosY].getCarIDs())!=0:
                posOfCarAhead.append(i)

        if len(posOfLightAhead)==0:
            #no light ahead
            if len(posOfCarAhead)==0:
                if self.__curPosInPath+self.__maxVelocity>=len(self.__carPath):
                    self.__velocity = len(self.__carPath)-1-self.__curPosInPath
                    #print ("no light no car dest ahead, my velocity is",self.__velocity)
                else:
                    self.__velocity = self.__maxVelocity
                    #print ("no light no car, my velocity is",self.__velocity)
            else:
                self.__velocity = posOfCarAhead[0]-1
                #print ("no light exist car, my velocity is",self.__velocity)
        else:
            #light ahead
            for p in range(1,self.__maxVelocity+1):
                if self.__curPosInPath+p>=len(self.__carPath):
                    break
                aheadCordinateStr = self.__carPath[self.__curPosInPath+p]
                aheadPosOfComma = int(aheadCordinateStr.index(','))
                aheadPosX = (int)(aheadCordinateStr[0:aheadPosOfComma])
                aheadPosY = (int)(aheadCordinateStr[aheadPosOfComma+1:len(aheadCordinateStr)])
                if self.__myMap[aheadPosX][aheadPosY].getLightID()!=-1:
                    aheadLightSignalRule = self.__myMap[aheadPosX][aheadPosY].getPointLightRule()
                    aheadLightSignal = self.readLightSignal(aheadLightSignalRule)
                    if self.getPosX()==aheadPosX and aheadLightSignal==0:
                        break
                    elif self.getPosY()==aheadPosY and aheadLightSignal==1:
                        break
                    elif self.getPosX()!=aheadPosX and self.getPosY()!=aheadPosY:
                        formerCordinateStr = self.__carPath[self.__curPosInPath+p-1]
                        formerPosOfComma = int(formerCordinateStr.index(','))
                        formerPosX = (int)(formerCordinateStr[0:formerPosOfComma])
                        formerPosY = (int)(formerCordinateStr[formerPosOfComma+1:len(formerCordinateStr)])
                        if formerPosX==aheadPosX and aheadLightSignal==0:
                            break
                        elif formerPosY==aheadPosY and aheadLightSignal==1:
                            break
                        else:
                            continue
                    else:
                        continue
                if len(self.__myMap[aheadPosX][aheadPosY].getCarIDs())!=0:
                    break
                self.__velocity = p

        self.__curPosInPath+=self.__velocity
        #print ("I am car {0}, I decide my velocity to be {1}, next PosInPath is {2}".format(self.getDeviceID(),self.__velocity,self.__curPosInPath))
        newCordinateStr = self.__carPath[self.__curPosInPath]
        newPosOfComma = int(newCordinateStr.index(','))
        newPosX = (int)(newCordinateStr[0:newPosOfComma])
        newPosY = (int)(newCordinateStr[newPosOfComma+1:len(newCordinateStr)])
        self.setPosX(newPosX)
        self.setPosY(newPosY)
        #print ("I am Car {0}, my velocity is {1}, I am goint to ({2},{3})".format(self.getDeviceID(),self.__velocity,newPosX,newPosY))
        #print ("My path is:")
        #print (self.__carPath)
        if newPosX==self.__destPosX and newPosY==self.__destPosY:
            self.__arriveDest = 1
            print ("Car {0} has arrived.".format(self.getDeviceID()))







#end
