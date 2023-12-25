import random
import math 
import pygame

class RRTMap:
    def __init__(self,start,goal,mapDimensions,obsdim,obsnum):
        self.start=start
        self.goal=goal
        self.MapDimensions = mapDimensions
        self.Maph,self.Mapw=self.MapDimensions

        #window settings
        self.MapWindowName='RRT path planning' 
        pygame.display.set_caption(self.MapWindowName)
        self.map=pygame.display.set_mode((self.Mapw,self.Maph))
        self.map.fill ((255,255,255))
        self.nodeRad=2
        self.nodeThickness=0
        self.edgeThickness=1

        self.obstacles=[]
        self.obsdim = obsdim
        self.obsNumber = obsnum 

        #Colors
        self.grey = (70,70,70)
        self.blue = (0,0,255)
        self.green = (0,255,0)
        self.red = (255,0,0)
        self.white = (255,255,255)




    def drawMap(self,obstacles):
        pygame.draw.circle(self.map,self.green,self.start,self.nodeRad+30,0)
        pygame.draw.circle(self.map,self.green,self.goal,self.nodeRad+20,1)
        self.drawobs(obstacles)

    def drawPath(self, path): 
        for node in path:
            pygame.draw.circle(self.map, self.blue, node, self.nodeRad+3, 0)

    def drawPath_1(self, path_smoothed): 
        for node in path_smoothed:
            pygame.draw.circle(self.map, self.red, node, self.nodeRad+3, 0)        

    def drawobs(self,obstacles): 
        obstaclesList=obstacles.copy()
        while (len(obstaclesList)>0):
            obstacle = obstaclesList.pop(0)
            pygame.draw.rect(self.map,self.grey,obstacle)

class RRTGraph: 
    def __init__(self,start,goal,mapDimensions,obsdim,obsnum):
        (x,y)=start
        self.start=start
        self.goal=goal
        self.goalFlag=False
        self.maph,self.mapw=mapDimensions
        self.x=[]
        self.y=[]
        self.parent=[]
        #initialize the tree
        self.x.append(x)
        self.y.append(y)
        self.parent.append(0)
        #the obstacle
        self.obsDim=obsdim 
        self.obsNum=obsnum 
        #path
        self.goalstate = None 
        self.path=[]
        #smoothed path
        self.refined_path=[]


    def addObstacles(self, obstacles):
        obs = []
        for pos in obstacles:
            x, y = pos
            rectang = pygame.Rect((x, y), (self.obsDim, self.obsDim))
            obs.append(rectang)

        self.obstacles = obs.copy()
        return obs
                 
    def add_node(self,n,x,y): 
        self.x.insert(n,x)
        self.y.append(y)

    def remove_node(self,n): 
        self.x.pop(n)
        self.y.pop(n)

    def add_edge(self,parent,child): 
        self.parent.insert(child,parent)

    def remove_edge(self,n): 
        self.parent.pop(n)

    def number_of_nodes(self): 
        return len(self.x)
    
    def distance(self,n1,n2): 
        x1 = self.x[n1]
        y1 = self.y[n1]
        x2 = self.x[n2]
        y2 = self.y[n2]
        px=(float(x1)-float(x2))**2
        py=(float(y1)-float(y2))**2
        return ((px+py)**(0.5))
    
    def sample_envir(self):
        x=int(random.uniform(0,self.mapw))
        y=int(random.uniform(0,self.maph))
        return x,y
    
    def nearest(self,n): 
        dmin = self.distance(0,n)
        nnear = 0 
        for i in range(0,n):
            if self.distance(i,n)<dmin:
                dmin=self.distance(i,n)
                nnear=i
        return nnear    

    def isFree(self):
        n = self.number_of_nodes()-1
        (x,y)=(self.x[n],self.y[n])
        obs=self.obstacles.copy()
        while len(obs) > 0:
            rectang = obs.pop(0)
            if (rectang.collidepoint(x,y)):
                self.remove_node(n)
                return False 
        return True     
    
    def crossObstacle(self, x1, x2, y1, y2, safety_distance):
        obs = self.obstacles.copy()
        for obstacle in obs:
            for i in range(0, 101):
                u = i / 100
                x = x1 * u + x2 * (1 - u)
                y = y1 * u + y2 * (1 - u)

                if math.hypot(x - obstacle.centerx, y - obstacle.centery) < (obstacle.width / 2 + safety_distance):
                    return True

        return False
    
    def connect(self, n1, n2, safety_distance=35):
        (x1, y1) = (self.x[n1], self.y[n1])
        (x2, y2) = (self.x[n2], self.y[n2])

        if self.crossObstacle(x1, x2, y1, y2, safety_distance):
            self.remove_node(n2)
            return False
        else:
            self.add_edge(n1, n2)
            return True

    def step(self, nnear, nrand, dmax=80, safety_distance=20):
        d = self.distance(nnear, nrand)

        if d > dmax:
            u = dmax / d
            (xnear, ynear) = (self.x[nnear], self.y[nnear])
            (xrand, yrand) = (self.x[nrand], self.y[nrand])
            (px, py) = (xrand - xnear, yrand - ynear)
            theta = math.atan2(py, px)
            (x, y) = (int(xnear + (dmax - safety_distance) * math.cos(theta)), int(ynear + (dmax - safety_distance) * math.sin(theta)))

            self.remove_node(nrand)

            if abs(x - self.goal[0]) < dmax and abs(y - self.goal[1]) < dmax:
                self.add_node(nrand, self.goal[0], self.goal[1])
                self.goalstate = nrand
                self.goalFlag = True
            else:
                self.add_node(nrand, x, y)
                

    def path_to_goal(self):
        if self.goalFlag:
            self.path = []
            if 0 <= self.goalstate < len(self.parent):
                newpos = self.parent[self.goalstate]

                while newpos != 0 and newpos in self.parent:
                    self.path.append(newpos)
                    newpos = self.parent[newpos]

                if not self.path:
                    return False

                self.path.append(0)  
                self.path.reverse()
                return True

            else:
                return False
        else:
            return False


    def getPathCoords(self): 
        pathCoords=[]
        for node in self.path:
            x,y=(self.x[node],self.y[node])
            pathCoords.append([x,y])
        x,y = self.goal[0],self.goal[1]    
        pathCoords.append([x,y])     
        print(pathCoords)    
        return pathCoords   

    def getPathCoords_1(self): 
        pathCoords=[]
        for node in self.refined_path:
            print(node)
            x,y=(self.x[node],self.y[node])
            pathCoords.append([x,y])   
        return pathCoords          

    def bias(self,ngoal):
        n=self.number_of_nodes()
        self.add_node(n,ngoal[0],ngoal[1])
        nnear=self.nearest(n)
        self.step(nnear,n)
        self.connect(nnear,n)
        return self.x,self.y,self.parent 

    def expand(self): 
        n = self.number_of_nodes()
        x,y=self.sample_envir()
        self.add_node(n,x,y)
        if self.isFree():
            xnearest=self.nearest(n)
            self.step(xnearest,n)
            self.connect(xnearest,n)
        return self.x,self.y,self.parent
        
    def optimize_path(self):
        temporary_path = self.getPathCoords()
        self.refined_path.append(temporary_path[0])

        i = 0  
        n = len(temporary_path)  


        while i < n:
            last_valid_node = temporary_path[i+1]  


            j = n - 1
            while j > i:
                if not self.crossObstacle(temporary_path[i][0], temporary_path[j][0], temporary_path[i][1], temporary_path[j][1], 15):
                    last_valid_node = temporary_path[j]
                    self.refined_path.append(last_valid_node)
                    n = len(temporary_path)-(j-i)
                    break
                else:
                    j -= 1

            i = j
        x,y = self.goal[0],self.goal[1]    
        self.refined_path.append([x,y])     

        print(self.refined_path)
        return self.refined_path
