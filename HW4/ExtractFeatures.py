import scapy
import sys
import os
from scapy.all import *
import numpy as np
import pandas as pd
import pprint
import sklearn
from sklearn.svm import LinearSVC,SVC
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
import pickle

### Read all pcap data
namelist = ['canvas','autolab','bing','craigslist','neverssl','tor','wikipedia']
pcaps = [[],[],[],[],[],[],[]]

count = 0;
for i in range(7):
    for j in range(10):
        filename = 'trainingdata/'+namelist[i]+'/'+ namelist[i] + str(j) +'.pcap'
        if not os.path.exists(filename):
            print(filename + " does not exist")
        else:
            pcap = rdpcap(filename)
            pcaps[i].append(pcap)
            count+=1;
            print(count)

### Extract features
#There are five different features
#[0]Averagelen: average length of all data packets' load
#[1]Smallratio: The ratio of small packets which are no greater than 100
#[2]Medianratio: The ratio of median packets which are no greater than 100
#[3]Largeratio: The ratio of large packets which are no greater than 100
#[4]Numberfeature: This is define by (incoming packets numbers * outcoming packets numbers)/all data numbers
X = []
Y = []
tempx = []
count = 0
for i in range(7):
    for j in range(10):
        outnum = 0
        innum = 0
        outlen = 0
        inlen = 0
        totallen = len(pcaps[i][j])
        incount = 0
        outcount = 0
        templen = 0
        countsmall = 0
        countmedian = 0
        countlarge = 0
        for k in range(totallen):
            if not pcaps[i][j][k].haslayer(IP):
                continue
            #print("src",pcaps[i][j][k][IP].src)
            #print("dst",pcaps[i][j][k][IP].dst)
            if pcaps[i][j][k][IP].dst == '10.226.115.2':
                innum+=1
                if pcaps[i][j][k].haslayer(Raw):
                    templen = len(pcaps[i][j][k].load)
                    inlen+= templen
                    incount+=1
                    if templen<=100:
                        countsmall+=1
                    elif templen<=600:
                        countmedian +=1
                    else:
                        countlarge += 1
            elif pcaps[i][j][k][IP].src == '10.226.115.2':
                outnum += 1
                if pcaps[i][j][k].haslayer(Raw):
                    templen = len(pcaps[i][j][k].load)
                    inlen+= templen
                    outcount+=1
                    if templen<=100:
                        countsmall+=1
                    elif templen<=600:
                        countmedian +=1
                    else:
                        countlarge += 1
            else:
                print('wrong packet')
        print(i,j)
        print('total',totallen)
        print("innum",innum)
        print("outnum",outnum)
        print("inlen",inlen)
        print("outlen",outlen)
        print("incount",incount)
        print("outcount",outcount)
        print("countsmall",countsmall)
        print("countmedian",countmedian)
        print("countlarge",countlarge)
        sumlen = inlen+outlen
        sumnum = outcount+incount
        averagelen = sumlen/sumnum
        numfeature =(innum*outnum)/sumnum
        smallratio = countsmall/sumnum
        medianratio = countmedian/sumnum
        largeratio = countlarge/sumnum
        print("averagelen",averagelen)
        print("numfeature",numfeature)
        print("smallratio",smallratio)
        print("medianratio",medianratio)
        print("largeratio",largeratio)
        X.append([averagelen,smallratio,medianratio,largeratio,numfeature])


### Create training data, both X and Y
datax = np.array(X)
Y = []
for i in range(7):
    for j in range(10):
        Y.append(i)
datay = np.array(Y)

### save the training data file
np.savetxt('feature.csv', datax, delimiter = ',')

### Because there are only 70 data, so I choose a simple model: linear SVC
clf = SVC(kernel = 'linear')
clf.fit(datax, datay)

### Save the model for future use
with open('clf.pickle', 'wb') as f:
    pickle.dump(clf, f)
