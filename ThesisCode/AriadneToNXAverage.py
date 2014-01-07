import numpy as np
import networkx as nx
import matplotlib as plt
import results

runs = 25

data = (np. loadtxt(open('C:\Users\ImAwesome\Documents\ThesisCode\SiteData.csv'), delimiter = ",", dtype = str))[1:,]
sizes = data[:,5].astype(int)
pos = {} #Tuple to store coordinates for plotting results
numSites = len(sizes)
for site in range(numSites):
    pos[int(site)] =(float(data[site][4]), float(data[site][3])) #Add each sites coordinates


for run in range(1, runs+1):

    edgeData = np.loadtxt(open("C:\Users\ImAwesome\Desktop\TaylorThesis\AriadneAfter100\AA100" + str(run) + ".txt"), delimiter = "\t", dtype = str)[:,]
    flows = np.ndarray((numSites, numSites))
    for link in iter(edgeData):
        flows[int(link[0])][int(link[1])] = link[3]

    print run
    print np.max(flows), np.min(flows)
    print np.mean(flows)
    data = results.initiate(flows, .006, pos, sizes)

    network = results.plotGraph(data)

    nodesOutput, netOutput = results.metrics(network, 'after')


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
            if run == 5:
                netTable = totalNets/run
            else:
                netTable = np.concatenate((netTable, (totalNets/run)), axis = 0)

totalNets = totalNets/runs
totalNodes = totalNodes/runs
np.savetxt('AriadneNetAfter100.csv', netTable, delimiter = ",")
np.savetxt('AriadneNodeAfter100.csv', totalNodes.transpose(), delimiter = ",")

