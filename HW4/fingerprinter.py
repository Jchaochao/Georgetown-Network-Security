import scapy
import sys
import os
from scapy.all import *
import numpy as np
import pandas as pd
from collections import Counter
import pickle

def main():

    #open the pcap file
    argv = sys.argv
    filename = argv[1]
    if not os.path.exists(filename):
        print(filename+" do not exist")
        exit(0)
    else:
        pcaps = rdpcap(filename)
        #print('file open successfully')
        #exit(0)

    #find the ip address which is appearce the most in dst and src
    IPs = []
    test = pcaps
    packetlen = len(test)
    for k in range(packetlen):
        if(test[k].haslayer(IP)):
            IPs.append(test[k][IP].src)
            IPs.append(test[k][IP].dst)
    src= Counter(IPs).most_common(1)[0][0]

    #extract features, five features, define can be seen in README
    outnum = 0
    innum = 0
    outlen = 0
    inlen = 0
    totallen = len(test)
    incount = 0
    outcount = 0
    templen = 0
    countsmall = 0
    countmedian = 0
    countlarge = 0
    for k in range(totallen):
        if not test[k].haslayer(IP):
            continue
        if test[k][IP].dst == src:
            innum+=1
            if test[k].haslayer(Raw):
                templen = len(test[k].load)
                inlen+= templen
                incount+=1
                if templen<=100:
                    countsmall+=1
                elif templen<=600:
                    countmedian +=1
                else:
                    countlarge += 1
        elif test[k][IP].src == src:
            outnum += 1
            if test[k].haslayer(Raw):
                templen = len(test[k].load)
                inlen+= templen
                outcount+=1
                if templen<=100:
                    countsmall+=1
                elif templen<=600:
                    countmedian +=1
                else:
                    countlarge += 1

    sumlen = inlen+outlen
    sumnum = outcount+incount
    averagelen = sumlen/sumnum
    numfeature =(innum*outnum)/sumnum
    smallratio = countsmall/sumnum
    medianratio = countmedian/sumnum
    largeratio = countlarge/sumnum
    testX = [averagelen,smallratio,medianratio,largeratio,numfeature]

    #load model and do the prediction
    with open('clf.pickle', 'rb') as f:
        clf2 = pickle.load(f)
    testx = np.array(testX)
    result = clf2.predict(testx.reshape(1,5))

    #print the result
    namelist = ['canvas','autolab','bing','craigslist','neverssl','tor','wikipedia']
    left = result[0]-1
    right = result[0]+1
    resultlist = [namelist[result[0]]]
    while left>=0 or right<7:
        if left>=0:
            resultlist.append(namelist[left])
        if right<7:
            resultlist.append(namelist[right])
        left-=1
        right+=1

    print("\n")
    for i in range(7):
        print(resultlist[i])
        print("\n")


if __name__=='__main__':
    main()
