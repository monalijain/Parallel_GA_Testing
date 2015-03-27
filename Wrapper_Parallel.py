__author__ = 'MJ'

import threading
import time
from datetime import timedelta, datetime
import Queue
import csv
from DB_DBUtils import *

exitFlag = 0

from WFList import CreateWFList
from NonSortedGANewVersion import *
import GlobalVariables as gv
from DB_MakePerf import Make_Performance_Measures
#from Calculate_Performance_Measures import Calculate_Performance_Measures_Generation

class ParallelWrapper(threading.Thread):

    def __init__(self, threadName, q):
        threading.Thread.__init__(self)
        self.threadName = threadName
        self.q = q

    def run(self):
        print("Starting : " + str(self.threadName))
        processIndividual(self.q)
        print("Exiting : " + str(self.threadName))

def processIndividual(q):
    if not exitFlag:
        if not workQueue.empty():
            data = q.get()
            print data,"data"
            walkNo = data
            dbObject = DBUtils()
            dbObject.dbConnect()
            print "Making MYFILE CSV and NetPL Ratio csv for walkforward ", walkNo+1
            walkforward_number=walkNo+1
            stringMyFile="MYFILE"+str(walkforward_number)+ "_" + "stock"+ str(gv.stock_number)+".csv"
            stringNetPLRatio="NetPLRatio"+str(walkforward_number)+ "_" + "stock"+ str(gv.stock_number)+".csv"
            c=csv.writer(open(stringMyFile,"wb"))
            PLRatio=csv.writer(open(stringNetPLRatio,"wb"))


            string_1= "CREATE TABLE performance_measures_"+"Training"+"_walk" + str(walkforward_number)+ "_" + "stock"+ str(gv.stock_number)
            print "Executing Query ",string_1
            dbObject.dbQuery(" " + string_1 + " "
                             "("
                             "individual_id int,"
                             "netpl_trades float,"
                             "netpl_drawdown float,"
                             "total_drawup float,"
                             "total_drawdown float,"
                             "netpl float,"
                             "total_trades int,"
                             "profit_epochs float"
                             ")")

            string_1= "CREATE TABLE performance_measures_"+"Reporting"+"_walk" + str(walkforward_number)+ "_" + "stock"+ str(gv.stock_number)
            print "Executing Query ",string_1
            dbObject.dbQuery(" " + string_1 + " "
                             "("
                             "individual_id int,"
                             "netpl_trades float,"
                             "netpl_drawdown float,"
                             "total_drawup float,"
                             "total_drawdown float,"
                             "netpl float,"
                             "total_trades int,"
                             "profit_epochs float"
                             ")")

            print "Calculating Performance Measures of Training Period for walkforward ",walkforward_number
            Make_Performance_Measures(TBeginList[walkNo],TendList[walkNo],Train_Or_Report="Training",walkforward_number=walkforward_number)
            Make_Performance_Measures(RBeginList[walkNo],REndList[walkNo],Train_Or_Report="Reporting",walkforward_number=walkforward_number)

            c.writerow(["Walkforward",walkforward_number,TBeginList[walkNo],TendList[walkNo],RBeginList[walkNo],REndList[walkNo]])

            print "Calling NonSorted Genetic Algorithm for walkforward ",walkNo+1
            [A,C,StoreParetoID]=NonSortedGA(walkforward_number,gv.MaxIndividualsInGen,MaxGen,MaxIndividuals)
            #[A,B,C]=NonSortedGA("Tradesheets","PriceSeries",6,'20120622','20121109','20121112','20130111',0.0,2,12)
            c.writerow(["IndividualID","TrainingPeriod"])
            c.writerow(["","NetPL/Trades ratio","NetPL/Drawdown ratio","total_Gain", "total_DD", "NetPL", "TotalTrades", "ProfitMakingEpochs",""])
            #PLRatio.writerow(["Walkforward",walkNo+1,TBeginList[walkNo],TendList[walkNo],RBeginList[walkNo],REndList[walkNo]])

            for key in A.keys():
                c.writerow([key,A[key][0],A[key][1],A[key][2],A[key][3],A[key][4],A[key][5],A[key][6]])

            c.writerow([])

            for key in C.keys():
                PLRatio.writerow([key,C[key][0],C[key][1]])

            PLRatio.writerow([])

        #    Calculate_Performance_Measures_Generation(TBeginList[walkNo],TendList[walkNo],Train_Or_Report="Training",walkforward_number=walkforward_number,StoreParetoID=StoreParetoID)
        #    Calculate_Performance_Measures_Generation(RBeginList[walkNo],REndList[walkNo],Train_Or_Report="Reporting",walkforward_number=walkforward_number,StoreParetoID=StoreParetoID)

        #    queueLock.release()

        #else:
        #    queueLock.release()

if __name__ == "__main__":
#making a database object
    dbObject1 = DBUtils()
    dbObject1.dbConnect()
    print("Calculating number of individuals in database")
    #Calculates number of individuals in tradesheet table
    Number=dbObject1.dbQuery("SELECT COUNT(DISTINCT(individualid)),1 FROM "+gv.name_Tradesheet_Table)

    for num1,num2 in Number:
        MaxIndividuals=num1
        print( "Number Of individuals in database: ",MaxIndividuals )

    MaxGen=MaxIndividuals/gv.MaxIndividualsInGen
    
    #Commenting the code to make a price series table
    '''
    dbObject1.dbQuery("CREATE TABLE price_series_table"
                             "("
                             "date date,"
                             "time time,"
                             "price float"
                             ")")

    query2 = "LOAD DATA INFILE 'C:/Program Files/MariaDB 10.0/data/"+gv.name_database+"/PriceSeries.csv'" \
                 " INTO TABLE price_series_table" \
                 " FIELDS TERMINATED BY ','" \
                 " LINES TERMINATED BY '\\r\\n'"

    print(query2)
    dbObject1.dbQuery(query2)
    '''
    dbObject1.dbClose()
    
    #Creates Walkforward List
    [TBeginList,TendList,RBeginList,REndList]=CreateWFList(gv.priceSeriesTable, gv.numDaysInTraining, gv.numDaysInReporting) #Creates Walkforward List
    #[TBeginList,TendList,RBeginList,REndList]=[["20120622","20120625"],["20120623","20120626"],["20120625","20120627"],["20130626","20120629"]]

    '''
    #Calculates number of rows in tradesheet table
    Number=dbObject1.dbQuery("SELECT COUNT(*),1 FROM "+gv.name_Tradesheet_Table)
    for num1,num2 in Number:
        NumberOfRows=num1
        print( "Number Of rows in tradesheet database: ",NumberOfRows )

    '''

    exitFlag = 0
    threads = []
    threadList = []
    threadNum = 1
    #for i in range (0,3):
    for i in range(0,len(TBeginList)):
        threadList.append("Thread" + str(threadNum))
        threadNum += 1

    print threadList,"threadList"
    queueLock = threading.Lock()
    print queueLock,"queueLock"
    workQueue = Queue.Queue(0)
    print workQueue
    queueLock.acquire()

    #for walkNo in range(0,3):
    for walkNo in range(0,len(TBeginList)):
        workQueue.put(walkNo)
    print(workQueue)
    queueLock.release()

    for tName in threadList:
        threadObj = ParallelWrapper(tName, workQueue)
        threadObj.start()
        threads.append(threadObj)

    while not workQueue.empty():
        pass
    exitFlag = 1

    for t in threads:
        t.join()


    print('Finished at : ' + str(datetime.now()))

