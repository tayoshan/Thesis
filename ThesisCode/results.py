#ThesisResultsScript- This script will take the spatial interaction data generated from each model and plot it and then compute the necessary analysis metrics

import numpy as np
import matplotlib as plt
import math
import networkx as nx
import igraph as ig
from scipy.spatial import KDTree
from igraph.datatypes import UniqueIdGenerator
import igraph.drawing.edge as draw


def initiate(flows, cutoff, pos, sizes):

    if cutoff >= 0 and cutoff <= 1:
        cutoff = np.max(flows) * cutoff #Cutoff used to optionally filter flows
        links = []
        widths = []
        rows,cols = np.shape(flows)
        numSites = rows

        posIG = []
        for site in iter(pos):
            posIG.append((pos[site][0], pos[site][1]*-1))


        for row in range(rows):
            for col in range(cols):
                if flows[row,col] > cutoff:
                    links.append((int(row),int(col), (flows[row,col]*1)))
                    widths.append(flows[row,col]*1)
        oldMin = min(widths)
        oldMax = max(widths)
        newMin = .5
        newMax = 10
        newWidths = (((widths-oldMin)*(newMax-newMin))/(oldMax-oldMin)) + newMin

    else:
        raise Exception("Cutoff must be between 0 and 1: it represents a percentage.")

    return links, newWidths, pos, posIG, numSites, sizes

def plotGraph(data):
    #print "Graphing proposed network"
    G=nx.DiGraph()
    G.add_weighted_edges_from(data[0])
    #G.remove_node(16)
    nx.draw_networkx(G, data[2], width = data[1])
    #plt.pyplot.show()
    #plt.pyplot.savefig('flows.png')

    newLinks = []
    for link in data[0]:
        newLinks.append((int(link[0]),int(link[1])))


    IG = ig.Graph(25, newLinks, directed = True)
    IG.es["width"] = data[1]
    IG.vs["label"] = range(data[4])
    sizes = data[5]
    layout = data[3]

    oldMin = np.min(sizes)
    oldMax = np.max(sizes)
    newMin = 12.5
    newMax = 35
    newSizes = (((sizes-oldMin)*(newMax-newMin))/(oldMax-oldMin)) + newMin
    IG.vs["size"] = newSizes
    smallNodes = IG.vs.select(size_lt=20)["label_size"] = 10
    IG.vs.select(label_eq=16)["color"] = "#91CF60"
    IG.vs.select(label_ne=16)["color"] = "#FC8D59"
    ig.plot(IG, layout = layout, weighted =True, edge_arrow_size = .6, vertex_label_angle = 0)


    return G

def metrics(G, state ="before"):#Lets break this up into node level metrics vs. network level metrics
    nodeMets = [] #Node level Metrics
    nodeMetNames = []
    nodes = nx.nodes(G)
    if state == "after":
        nodes.insert(16,16)
    nodeMets.append(nodes)
    nodeMetNames.append('Node')
    if state == "after":
        intIn = np.zeros((G.order()+1,1))
        intOut = np.zeros((G.order()+1,1))
    else:
        intIn = np.zeros((G.order(),1))
        intOut = np.zeros((G.order(),1))
    #print len(nx.edges(G))
    for edge in nx.edges(G):
        intIn[edge[1]] += G[edge[0]][edge[1]]['weight']
        intOut[edge[0]] += G[edge[0]][edge[1]]['weight']
    intIn = intIn.flatten().tolist()
    intOut = intOut.flatten().tolist()
    #print sum(intIn), sum(intOut)
    nodeMets.append(intIn)
    nodeMetNames.append('InteractionIn')
    nodeMets.append(intOut)
    nodeMetNames.append('InteractionOut')
    degreeIn = []
    degreeOut = []
    for node in G.in_degree_iter():
        degreeIn.append(node[1])
    for node in G.out_degree_iter():
        degreeOut.append(node[1])
    if state == "after":
        degreeIn.insert(16,999)
    nodeMets.append(degreeIn)
    nodeMetNames.append('DegreeIn')
    if state == "after":
        degreeOut.insert(16,999)
    nodeMets.append(degreeOut)
    nodeMetNames.append('DegreeOut')
    nodeTrans = nx.clustering(G.to_undirected()).values()
    if state == "after":
        nodeTrans.insert(16,999)
    nodeMets.append(nodeTrans)
    nodeMetNames.append('Transitivity')
    pageRank = nx.pagerank(G, weight = 'weight').values()
    if state == "after":
        pageRank.insert(16,999)
    nodeMets.append(pageRank)
    nodeMetNames.append('PageRank')
    hitsHubs, hitsAuths = nx.hits(G)[0].values(), nx.hits(G)[1].values()
    if state == "after":
        hitsHubs.insert(16,999)
    nodeMets.append(hitsHubs)
    nodeMetNames.append('Hubs')
    if state == "after":
        hitsAuths.insert(16,999)
    nodeMets.append(hitsAuths)
    nodeMetNames.append('Authorities')
    nodesOutput = zip(nodeMetNames, nodeMets)

    #Network level metrics
    netMets = []
    netMetNames = []
    for each in G.nodes_iter():
        G.node[each]['totalInt'] = intIn[each] + intOut[each]
    assort = nx.attribute_assortativity_coefficient(G, 'totalInt')
    netMets.append(assort)
    netMetNames.append('Assortativity (total Int)')

    diameter = nx.diameter(G.to_undirected())
    netMets.append(diameter)
    netMetNames.append('Diameter')
    connect = float(sum(nx.degree(G).values()))/float(len(nodes))
    #print "Nodes: " + str(len(nodes))
    netMets.append(connect)
    netMetNames.append("Average Node Degree")
    transit = nx.transitivity(G)
    netMets.append(transit)
    netMetNames.append('Transitivity')
    density = nx.density(G)
    netMets.append(density)
    netMetNames.append('Density')
    beta = float(len(nx.edges(G)))/float(len(nx.nodes(G)))
    netMets.append(beta)
    netMetNames.append('BetaIndex')
    gamma = float(len(nx.edges(G)))/float(len(nx.nodes(G))**2)
    netMets.append(gamma)
    netMetNames.append("GammaIndex")
    netOutput = zip(netMetNames, netMets)
    #print nodeMetNames
    return nodeMets, netMets






'''
out = file('flows.csv', 'w') # create output file
    out.write("Origin, Destination, Flow\n")
    out.writelines("%s\t%s\t%s\n" %  (str(row) + ",", str(col) + ",", flows[row, col])) # write flows to output file
    out.close()
'''