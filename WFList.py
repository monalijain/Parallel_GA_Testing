__author__ = 'MJ'
#Function which gives walkforward list, given the price series data; Number of Days in Training Data; Number of Days in Reporting Data

import GlobalVariables as gv
import csv
from datetime import date
def CreateWFList(SamplePriceSeries,T,R):
    iFile=open('C:/Program Files/MariaDB 10.0/data/'+gv.name_database+'/PriceSeries.csv','rb')
    rq=csv.reader(iFile)
    c=0
    Tcounter=0
    TrainingBegin=list()
    TrainingEnd=list()

    for row in rq:
        if(c==0):
            TrainingBegin.append(row[0])
            Tcounter+=1
            #print row[0]
        else:
            if(row1[0]!=row[0]):
                Tcounter+=1
                #print row[0]
                if(Tcounter%(R)==1):
                    TrainingBegin.append(row[0])
                if(Tcounter==T):
                    TrainingEnd.append(row[0])
                if(Tcounter>T and (Tcounter-T)%R==0):
                    TrainingEnd.append(row[0])
        c=c+1
        row1=row

    iFile=open('C:/Program Files/MariaDB 10.0/data/'+gv.name_database+'/PriceSeries.csv','rb')
    rq=csv.reader(iFile)
    Rcounter=1
    ReportingBegin=list()
    ReportingEnd=list()
    c=0
    Rcount=0
    for row in rq:
        if(c!=0):
            if(row1[0]!=row[0]):
                try:
                    i = TrainingEnd.index(row1[0])
                except ValueError:
                    i = -1 # no match

                if(i!=-1):
                    ReportingBegin.append(row[0])
                    Rcount=1
                    Rcounter=0

                if(Rcount==1):
                    Rcounter+=1
                if(Rcounter==R):
                    ReportingEnd.append(row[0])
                    Rcount=0
                    Rcounter=0

        c=c+1
        row1=row

    while(len(TrainingBegin)!= len(ReportingEnd)):
        TrainingBegin.pop()

    while(len(TrainingEnd)!= len(ReportingEnd)):
        TrainingEnd.pop()

    while(len(ReportingEnd)!= len(ReportingBegin)):
        ReportingBegin.pop()

    #return (['20120622','20120628'],['20120625','20120629'],['20120626','20120702'],['20120627','20120703'])
    return (TrainingBegin,TrainingEnd,ReportingBegin,ReportingEnd)

#[a,b,c,d]=CreateWFList("PriceSeries", 20, 10)
#print a
#print b
