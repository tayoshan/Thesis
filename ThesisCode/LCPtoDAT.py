#Script to convert LCP output file to DAT format for use in Ariadne

import numpy as np
import math

lcp = np.loadtxt(open('C:\Users\ImAwesome\Desktop\ThesisData\LCP5\LCP_length.txt'), delimiter = "\t", dtype = str)
sites = np. loadtxt(open('C:\Users\ImAwesome\Desktop\ThesisData\SiteDataAfter.csv'), delimiter = ",", dtype = str)

num_sites = np.size(sites[1:,1]) #Count number of sites in the data

datFile = np.zeros((5+num_sites, num_sites+1), dtype = 'S17')

datFile[4,0] = "*Distance"
for site in range(len(sites[:,0])):
    datFile[0,site] =  "Name"
    datFile[1,site] = "Size"
    datFile[2,site] = "Latitude_N"
    datFile[3,site] = "Longitude_E"
    if site > 0:
        datFile[0,site] =  sites[site,0]
        datFile[1,site] = sites[site,5]
        datFile[2,site] = float(sites[site,3])
        datFile[3,site] = float(sites[site,4])
        datFile[4,site] = sites[site,0]
        origin = sites[site,1]
        datFile[(int(origin)+4), 0] = sites[site,0]
        for destination in range(1,(num_sites+1)):
            if lcp[origin, destination] > 0:
                datFile[(int(origin)+4),destination] = (math.floor(float(lcp[origin, destination]))/1000)
            else:
                 datFile[(int(origin)+4),destination] = 0


np.savetxt("after_input.DAT", datFile, delimiter="\t", fmt = '%s')


