import numpy as np
import networkx as nx
import matplotlib as plt
import results

data = (np. loadtxt(open('C:\Users\ImAwesome\Documents\ThesisCode\SiteData.csv'), delimiter = ",", dtype = str))[1:,]
sizes = data[:,5].astype(int)
pos = {} #Tuple to store coordinates for plotting results
numSites = len(sizes)
for site in range(numSites):
    pos[int(site)] =(float(data[site][4]), float(data[site][3])) #Add each sites coordinates
edgeData = np.loadtxt(open('C:\Users\ImAwesome\Desktop\TaylorThesis\AriadneBefore100\AB1001.txt'), delimiter = "\t", dtype = str)[:,]
flows = np.ndarray((numSites, numSites))
for link in iter(edgeData):
    flows[int(link[0])][int(link[1])] = link[3]

data = results.initiate(flows, .0175, pos, sizes)

network = results.plotGraph(data)

nodesOutput, netOutput = results.metrics(network, 'after')

nodesOutput = np.array(nodesOutput)
np.savetxt('ariadneA100.csv', nodesOutput.transpose(), delimiter = ",")