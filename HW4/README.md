# README

##Relay packets
scapy

sys

os

numpy

collections

pickle

sklearn

## About the file
clf.pickle: the model for predict

feature.csv: feature file for 70 samples

fingerprinter.py: the main code take in a pcap file and do the prediction

ExtractFeatures.ipynb: notebook which is used to extract features and train the model

##About the features
avergelen: the average length of all data packets

smallratio: the ratio of all packets with no greater than 100 data length

medianratio: the ratio of all packets with no greater than 600 data length

largeratio: the ratio of all packets with greater than 600 data length

numfeature: this is defined by (outcoming packets' number * incoming packets' number)/all number. I set this value because without knowing which is the source ip, we cannot tell which is incoming traffic and which is outcoming traffic. So I set get both and multiply them together so that they are both important in this feature.

## model
Because the dataset is only 70-samples large so I choose a simple model(SVR with a linear kernel)
