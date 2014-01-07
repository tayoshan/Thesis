#-------------------------------------------------------------------------------
#AgentTest
#-------------------------------------------------------------------------------

import pylab as plt
import numpy as np
import graphics as gp
import time as tm
import math
import results


#Functon to generate unique colors for settlements and respective humans
def colors(numSites):
    r = np.arange(0,255, (255/numSites))
    g = np.arange(0,255, (255/numSites))
    b = np.arange(0,255, (255/numSites))
    np.random.shuffle(r)
    np.random.shuffle(g)
    np.random.shuffle(b)
    colorBook = {}
    for i in range(numSites):
        color =  gp.color_rgb(r[i], g[i], b[i])
        colorBook[i] = color
    return colorBook

#Function to calculate distance between two sites using their lat/long (km) (may replace with a functional distance)
def get_dist(lat1, long1, lat2, long2):
    degrees_to_radians = math.pi/180.0
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )
    return arc*6378


#Function to load data (site size, and position) and process it into format for input to model
def get_data(file_path):
    data = np.loadtxt(open(file_path),delimiter=",",skiprows=1, dtype = str)
    leastCP = np.loadtxt(open('C:\Users\ImAwesome\Desktop\ThesisData\LCP5\LCP_Length.txt'),delimiter="\t",skiprows=1, dtype = str)
    dists = np.array(leastCP[:,1:], dtype = float)/1000
    numSites = data.shape[0]
    siteSizes = []
    pos = np.zeros((numSites, 2))
    for site in range(numSites):
        pos[int(site)] = (float(data[site][4]), float(data[site][3]))
        siteSizes.append(int(data[site][5]))
    #dists = np.zeros((numSites,numSites))
    #rows,cols = np.shape(dists)
    #for r in range(rows):
        #for c in range(cols):
            #if r == c:
                #dists[r,c] = 0
            #else:
                #dists[r,c] = get_dist(float(data[r][3]),float(data[r][4]),float(data[c][3]),float(data[c][4]))
    return numSites, dists, pos, siteSizes


#Human agents that will move from site to site
class agentH:
    def __init__(self, win, site, dists, pos, color):
        #Settlement attirbutes
        self.home = site    #Site a human starts during iteration 0
        self.currentSite = site   #Humans current site location
        self.visits = []    #List of all sites visited
        self.originImp = 1 #Hold importance value for site where traveler is coming from; defaults to 1
        #Graphics parameters
        self.win = win  #Add agent to app window
        self.color = color  #Humans color assignment
        self.originalColor = color #Store starting color
        self.pos = pos  #Stores lat/long coordinates
        self.loc = gp.Point(pos[self.currentSite][0], pos[self.currentSite][1]) #Assigns the lat/long coordinates for plotting
        self.loc.setFill(self.color)    #Fill grahpics with color
        self.startx = 0
        self.starty = 0
        self.endx = 0
        self.endy = 0
        #Spatial Parameters
        self.dists = dists  #Stores distances from site to all other sites
        #Draw agent as a graphic in the window
        self.loc.draw(self.win)

    #Function to return the distance from this agent to another settlement
    def distance(self, settlement):
        return self.dists[self.currentSite][settlement]

    #Function that updates location and color of each agent at the end of move
    def updateLoc(self, destImp, choiceSiteNum, color):
        self.loc.undraw()   #First undraw graphic at old location
        if destImp >= self.originImp:
            self.color = color  #Update to color which is passed into the function
        self.loc.setFill(self.color)    #Fill that new color
        self.visits.append(choiceSiteNum)  #Append newly chosen site to the visited sites log for that agent
        self.startx, self.starty = self.pos[self.currentSite][0], self.pos[self.currentSite][1] #Assign x1 and y1 from the coordinate of the old site
        self.loc = gp.Point(self.pos[self.currentSite][0], self.pos[self.currentSite][1])   #Change location to the coordinate of the new site
        self.endx, self.endy = self.pos[choiceSiteNum][0], self.pos[choiceSiteNum][1] #Assign x2 and y2 from the coordinates of the new site that the agent visited
        self.loc.draw(self.win) #Redraw agent
        return self.startx, self.starty, self.endx, self.endy, self.color   #return starting and ending location and ending color

    def updateAttbs(self, choiceSiteNum, destImp):
        self.currentSite = choiceSiteNum   #Update current site attribute to the new site passed into the function
        self.originImp = destImp  #Origin importance is updated to new site which was the destination importance passed into the function

    #Function to return the color of a human agent
    def getColor(self):
        return self.color


#Settlement agents that will keep track of interaction attributes
class agentS:
    def __init__(self, win, siteNum, pos, colorBook, siteSizes):
        #Graphics parameters
        self.win = win  #set window to draw settlement in
        self.x = pos[siteNum][0]    #Store x and y coords of this settlement
        self.y = pos[siteNum][1]
        self.size = .01 #Set the starting size for the settlement (effectively 0)
        self.loc = gp.Circle(gp.Point(self.x,self.y),self.size) #set shape and location of settlement
        self.color = colorBook  #set settlemnt color to color passed in from the colorbook
        self.loc.setFill(self.color)    #Fill shape with color
        #Settlement attributes
        self.siteNum = siteNum  #Store number assigned to this settlement in the data
        self.importance = siteSizes #Set starting importance to the default of 1
        self.visitors = 0   #Visitor count starts at 1 at beginning of simulation (visitor count per iteration -- reset efter each iteration)
        self.visitorLog = []    #Records all visitors that come to the site
        self.visitorOriginLog = []  #Records the home settlement of all visitors that come to the site
        self.reflectedGlory = [0]
        self.updated = False    #Set updated status to default of false
        #Draw settlement as agent in the window
        self.loc.draw(self.win)



    #Function to update sites importance and drawing size
    def updateGraphic(self, maxVisitors):
        self.loc.undraw()   #First undraw settlement
        #if self.updated == True:
        self.increaseImp(maxVisitors)  #Increase importance according the importance of the site the visitor originated from
        #if self.updated == False:  #If a site was not visited
            #self.decreaseImp()  #Decrease its importance
        self.reflectedGlory = [0]
        #self.visitors = 1
        self.loc = gp.Circle(gp.Point(self.x,self.y),self.size) #Re-apply size parameter to graphic
        self.loc.setFill(self.color)    #Fill graphic
        self.updated = False #Reset this attribute for the next round
        self.loc.draw(self.win) #Redraw graphic


    def updateAttbs(self, originImp, currentSite, home):
        self.reflectedGlory.append(originImp)  #Update reflected glory of site
        self.visitorLog.append(currentSite)
        self.visitorOriginLog.append(home)
        self.visitors = self.visitors + 1   #Add 1 to visitor counter
        self.updated = True #Change status to true for whether or not this site received visitors this iteration



    def increaseImp(self, maxVisitors):
      #  if self.visitors > maxVisitors * .5:
       self.importance += (self.visitors * math.sqrt((sum(self.reflectedGlory)/len(self.reflectedGlory))))
       # else:
        #    self.importance += (self.visitors * math.sqrt((sum(self.reflectedGlory)/len(self.reflectedGlory))))
         #   self.importance -= self.importance/10
          #  if self.importance < 10:
           #     self.importance = 10
       self.noise()
       self.size = .01 + (self.visitors*.001)  #Increase size accordingly


    #Function to decrease importance if the site does not receive any visitors this iteration
    def decreaseImp(self):
        self.importance *= .75    #Decrease importance
        self.size *= .75  #Decrease size


    #Functiont to return the assigned site number of a settlement
    def getSiteNum(self):
        return self.siteNum

    #Function to return the current color of a settlement
    def getColor(self):
        return self.color

    #Function to return the current importance of a site
    def getSiteImp(self):
        return self.importance

    #Function to return the current visitor count of a site
    def getSiteVis(self):
       return self.visitors


    def noise(self):
        sign = np.random.random(1)
        if sign > .5:
            self.importance += abs(self.importance - np.random.poisson(self.importance))
        else:
            self.importance -= abs(self.importance -  np.random.poisson(self.importance))
#Trail agents just to visualize paths travelled by agents (was easier to draw these separately than to draw human agents as polylines)
class trails:
    def __init__(self, win, startx, starty, endx, endy, color):
        self.win = win
        self.startx = startx
        self.starty = starty
        self.endx = endx
        self.endy = endy
        self.color = color
        self.loc = gp.Line(gp.Point(startx,starty),gp.Point(endx,endy))
        self.loc.setFill(color)
        self.loc.draw(self.win)

#The context provides the run environment (window) and controls the flow of the simulation
class context:
    def __init__(self, numSites, numAgents, pos, dists, colorBook, siteSizes, state = "before"):
        self.dims = gp.Point(700, 700)  #assign dimensions of the window
        self.win = gp.GraphWin("Agent Model", self.dims.x, self.dims.y) #Set dimensions and title
        self.win.setCoords(10,41.5,13,44.5) #Set bounding coordinates for the window (lat/long)
        self.agentsS = []   #List to hold settlement agents
        self.agentsH = []   #List to hold human agents
        self.state = state
        #Instantiate each settlement agent with default parameters
        if self.state == "after":
            siteSizes[16] = 0
            for i in range(numSites):
                if i == 16:
                    self.agentsS.append(agentS(self.win, i, pos, colorBook[i], siteSizes[i]))
                #For each settlement agent instantiate given number of human agents with default parameters)
                else:
                    self.agentsS.append(agentS(self.win, i, pos, colorBook[i], siteSizes[i]))
                    #For each settlement agent instantiate given number of human agents with default parameters)
                    for each in range(numAgents):
                        self.agentsH.append(agentH(self.win, i, dists, pos, colorBook[i]))
        else:
            for i in range(numSites):
                self.agentsS.append(agentS(self.win, i, pos, colorBook[i], siteSizes[i]))
                #For each settlement agent instantiate given number of human agents with default parameters)
                for each in range(numAgents):
                    self.agentsH.append(agentH(self.win, i, dists, pos, colorBook[i]))

    #Maximum number of visitors any settlement recieved in a given round
    def maxVisitors(self):
        maxVisitors = 0
        for settlement in self.agentsS:
            if settlement.visitors > maxVisitors:
                maxVisitors = settlement.visitors
        return maxVisitors


    def move(self, human, resourceBenefits, communicationDifficulty):
        attractiveness = []     #Create a place to store calculations of each sites overall attractiveness
        for settlement in self.agentsS: #For each settlement in the list of all settlements
            settlementNum = settlement.getSiteNum()    #First get its assigned site number
            if self.agentsH[human].distance(settlementNum) > 0 and self.agentsH[human].distance(settlementNum) < 100:    #If distance from this agent to each settlement is not 0 or more than the limited vision distance
                x = settlement.getSiteImp() #Get the importance of the site
                y = self.agentsH[human].distance(settlementNum)   #Get the distance from the agent to that site
                z = settlement.getSiteVis() #Get the number of visitors the site has received
                if z == 0:  #If z has no visitors then assign it 1 for the sake of calculations
                    z = 1   #This is from the netlogo code but it seems like there has to be a better method; there is then no difference between unvisited sites and single visitor sites in the calculation comparison
                #Calculate the attractiveness and add it to the list as a tuple
                attractiveness.append((settlementNum, (((x**resourceBenefits) * (math.e**(-(communicationDifficulty * y)))) / ((z**resourceBenefits) * (math.e**(-(communicationDifficulty * y)))))))
        dtype = [("settlement", int), ('attractiveness', float)]    #Set the data types of mixed array
        attractiveness = np.array(attractiveness, dtype)    #Turn list into np array

        return attractiveness

    def output(self):
        out = file("importance18.csv", "w")
        numList = []
        imp = []
        for each in self.agentsS:
            numList.append(each.siteNum)
            imp.append(each.importance)
            out.writelines("%s\n" %  ( each.importance ))
        out.close()
        return zip(numList, imp)

    def run(self, iterations, numAgents, pos, numSites):
        IM = np.zeros((numSites,numSites))
        maxVisitors = 1
        if self.state == "after":
            allAgents = np.arange(0, numAgents*(numSites-1))  #Number of settlements times then number of agents that start at each settlement
        else:
            allAgents = np.arange(0, numAgents*(numSites-1))  #Number of settlements times then number of agents that start at each settlement
        for i in range(iterations):
            #print "Iteration: {0}".format(i)
            counter = 0
            for human in allAgents:  #For each agent
                #print i, human, counter
                #Go through the move routine
                resourceBenefits = 1
                communicationDifficulty = 1
                attractiveness = self.move(human, resourceBenefits, communicationDifficulty)
                if attractiveness.size != 0:    #If there is at least 1 site that meets the minimum critera then choose the most attractive one
                    choice = np.sort(attractiveness, order = 'attractiveness')[-1]  #Sort the options based on attractiveness and store the one with the largest
                    agentColor = self.agentsH[human].getColor()    #Get current color of the agent
                    originImp = self.agentsH[human].originImp
                    currentSite = self.agentsH[human].currentSite
                    home = self.agentsH[human].home
                    #Update agent based on chosen site, its importance and its color
                    settColor = self.agentsS[choice[0]].getColor()    #Get color of the chosen settlement
                    choiceImp = self.agentsS[choice[0]].getSiteImp()  #Get Importance of destination site
                    startx, starty, endx, endy, agentColor = self.agentsH[human].updateLoc(choice[1], choice[0], settColor)
                    trails(self.win, startx,starty,endx,endy, agentColor)    #And leave a trail behind
                    self.agentsS[choice[0]].updateAttbs(originImp, currentSite, home)
                    self.agentsH[human].updateAttbs(choice[0], choiceImp)#This was choice[1] but I think it should be choiceImp
                    counter +=1
                    #tm.sleep(.1)
            maxVisitors = self.maxVisitors()
            for settlement in self.agentsS:   #At the end of the iteration
                settlement.updateGraphic(maxVisitors)
        for settlement in self.agentsS:
            interaction = settlement.visitorLog
            for trip in interaction:
                IM[trip][settlement.siteNum] += 1




        test = self.output()
        tm.sleep(5) #Wait 5 seconds after all iterations are finished
        self.win.close()    #Then close the window
        return IM



#Function just to kick off the simulation (initalize context) and provide a status update for each part
def go():
    agents = 5
    #print "Step one: load data"
    #Load input data from csv (Site sizes, and lat/long)
    numSites, dists, pos, siteSizes = get_data(r'C:\Users\ImAwesome\Documents\ThesisCode\SiteData.csv')
    #Generate unique colors for visualization
    colorBook = colors(numSites)
    #print "Step one complete!"
    #print "Running model"
    #Initialize context (number of sites, number of agents at each site, site positions, inter-site distances, and colors)
    c = context(numSites, agents, pos, dists, colorBook, siteSizes)
    #Run the main function that loops through the iterations (provide number of iterations, site coords and  number of sites)
    IM = c.run(10, agents, pos, numSites)
    #print "Model run complete"


    def newPos(pos):
        newPos = {}

        for pair in range(len(pos)):
            newPos[pair] = pos[pair]
        return newPos

    pos = newPos(pos)
    return IM, pos, siteSizes

if __name__ == '__main__':

    runs = 5
    for run in range(1,runs+1):

        flows, pos, sizes = go()
        data = results.initiate(flows, 0, pos, sizes)

        network = results.plotGraph(data)

        nodesOutput, netOutput = results.metrics(network)
        nodesOutput = np.array(nodesOutput, dtype = float)
        netOutput = np.array([netOutput], dtype = float)

        if run == 1:
            totalNodes = nodesOutput
            totalNets = netOutput
        else:
            totalNodes += nodesOutput
            totalNets += netOutput
        if run % 5 == 0:
            print run
            print totalNets/run
            print totalNodes/run
            if run == 5:
                netTable = totalNets/run
            else:
                netTable = np.concatenate((netTable, (totalNets/run)), axis = 0)
        print totalNodes/run

    totalNets = totalNets/runs
    totalNodes = totalNodes/runs
np.savetxt('agentTest.csv', netTable, delimiter = ",")
np.savetxt('agentTest.csv', totalNodes.transpose(), delimiter = ",")