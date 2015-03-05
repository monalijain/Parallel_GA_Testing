from PerformanceMeasures_ShortVersion import CalculatePerformanceMeasures
from PerformanceMeasures_ShortVersion_Reporting import CalculatePerformanceMeasuresReporting
from MakeNewPopulationVersion2 import MakeNewPopulation
import csv
from datetime import datetime
from FastNonDominatedSort import FastNonDominatedSort
import GlobalVariables as gv

C={}

#For checking the convergence of the Pareto Optimal Front
ParetoOptimalFront={}

def NonSortedGA(walkforward_number,MaxIndividualsInGen,MaxGen,MaxIndividuals):

    StoreParetoID={}
    stringParetoFront= "ParetoFront Walkforward"+str(walkforward_number)+"_"+"stock"+"_"+str(gv.stock_number)+".csv"
    ParetoFront=csv.writer(open(stringParetoFront,"wb"))
    ParetoFront.writerow(["IndividualID","TrainingPeriod"," "," "," "," "," "," "," "," ","ReportingPeriod"])
    ParetoFront.writerow(["","NetPL/Trades ratio","NetPL/Drawdown ratio","total_Gain", "total_DD", "NetPL", "TotalTrades", "ProfitMakingEpochs","",
                          "NetPL/Trades ratio","NetPL/Drawdown ratio","total_Gain", "total_DD", "NetPL", "TotalTrades", "ProfitMakingEpochs"])

    Pt={}
    print str(datetime.now()),"Current Time"
    for num in range(1,MaxIndividualsInGen+1):
        PerfM=CalculatePerformanceMeasures(num,walkforward_number,gv.stock_number)
        #print "Performance Matrix: ",PerfM
        Pt[num]=[PerfM[0][0],PerfM[0][1],PerfM[0][2],PerfM[0][3],PerfM[0][4],PerfM[0][5],PerfM[0][6]]
        #print num

    print "We have Initial seed individuals"

    for gen in range(1,min(MaxGen,MaxIndividuals/MaxIndividualsInGen)):
        StoreParetoID_EachGen=[]
        print "This is generation ",gen-1
        print str(datetime.now()),"Current Time of Generation: ",gen-1
        print "Non Dominated Sorting of generation ",gen-1
        F=FastNonDominatedSort(Pt) #Create Fronts From Population
        print "Pareto Optimal Front of generation",gen-1,"is: ",F[1]
        ParetoFront.writerow([gen-1])
        print "Writing Front in pareto front file"

        for key in F[1].keys():
            F_Reporting=CalculatePerformanceMeasuresReporting(key,walkforward_number,gv.stock_number)
            ParetoFront.writerow([key,F[1][key][0],F[1][key][1],F[1][key][2],F[1][key][3],F[1][key][4],F[1][key][5],F[1][key][6],
                                  " ",F_Reporting[0][0],F_Reporting[0][1],F_Reporting[0][2],F_Reporting[0][3],F_Reporting[0][4],
                                  F_Reporting[0][5],F_Reporting[0][6]])
            StoreParetoID_EachGen.append(key)

        StoreParetoID[gen-1]=StoreParetoID_EachGen


        ParetoFront.writerow([])
        i=max(F.keys())
        #if(bool(F[2])):
        #    lengOfFront1and2=len(F[1])+len(F[2])
        #else:
        #    lengOfFront1and2=len(F[1])

        lengOfFront1and2=len(F[1])

        print "Making New Population"
        Q=MakeNewPopulation(F,Pt,i,gen,MaxIndividualsInGen,lengOfFront1and2)
        Qt={}
        counter=0
        for num in Q:
            PerfM=CalculatePerformanceMeasures(num,walkforward_number,gv.stock_number)
            Qt[num]=[PerfM[0][0],PerfM[0][1],PerfM[0][2],PerfM[0][3],PerfM[0][4],PerfM[0][5],PerfM[0][6]]
            counter =counter +1
        print "Number of children in generation ",gen-1,"is ",counter
        #Pt1=dict((F[1]).items()+(F[2]).items()+Qt.items())
        Pt1=dict((F[1]).items()+Qt.items())

        print "Checking Convergence"
        if(CheckConvergenceOfPopulation(F,gen)==0):
            print "Converged"
        Pt=Pt1

    StoreParetoID_EachGen=[]
    F=FastNonDominatedSort(Pt)

    NetPL_CurrentGen=0.0
    TotalTrades_CurrentGen=0

    print "Calculating NetPL/Total Trades of Pareto Optimal Front"
    for individual in F[1].keys():
        NetPL_CurrentGen=float(F[1][individual][4])+NetPL_CurrentGen
        TotalTrades_CurrentGen=float(F[1][individual][5])+TotalTrades_CurrentGen
        StoreParetoID_EachGen.append(individual)

    StoreParetoID[gen]=StoreParetoID_EachGen

    if(TotalTrades_CurrentGen==0):
        C[gen]=[-50000,0]
    else:
        C[gen]=[NetPL_CurrentGen/(1.0*TotalTrades_CurrentGen),TotalTrades_CurrentGen]
    print "NetPL/TotalTrades[gen=",gen,"]:",C[gen]

    print "Pareto Optimal Front of generation",gen,"is: ",F[1]
    ParetoFront.writerow([gen])
    for key in F[1].keys():
        ParetoFront.writerow([key,F[1][key][0],F[1][key][1],F[1][key][2],F[1][key][3],F[1][key][4],F[1][key][5],F[1][key][6]])

    #print "Performance Measure of evolved individuals in Training Period",Pt
    print "Returning From NonSorted GA New Version for walkforward ", walkforward_number
    return [Pt,C,StoreParetoID]


def CheckConvergenceOfPopulation(F,gen):
    NetPL_CurrentGen=0.0
    TotalTrades_CurrentGen=0

    print "Calculating NetPL/Total Trades of Pareto Optimal Front"

    for individual in F[1].keys():
        NetPL_CurrentGen=float(F[1][individual][4])+NetPL_CurrentGen
        TotalTrades_CurrentGen=float(F[1][individual][5])+TotalTrades_CurrentGen

    if(TotalTrades_CurrentGen==0):
        C[gen-1]=[-50000,0]
    else:
        C[gen-1]=[NetPL_CurrentGen/(1.0*TotalTrades_CurrentGen),TotalTrades_CurrentGen]
    print "NetPL/TotalTrades[gen=",gen-1,"]:",C[gen-1]

    if(gen==1):
        return 1
    else:
        ParetoOptimalFront[gen]=abs(C[gen-1][0]-C[gen-2][0])

    #print "ParetoOptimalFront[",gen,"]:",ParetoOptimalFront
    if(gen<max(gv.CheckGen,gv.MinimumGen)):
        return 1
    done=0
    for i in range(gen-gv.CheckGen+1,gen+1):
        if(ParetoOptimalFront.has_key(i)):
            if(ParetoOptimalFront[i]<=gv.ConvergenceValue):
                done+=1
    if(done==gv.CheckGen):
        print("Converged algorithm in generation",gen)
        return 0

    return 1



#A=list()
#A=NonSortedGA("Tradesheets","PriceSeries",6,'20120622','20121109','20121112','20130111',0.0,2,12)
#print "Evolved individuals",A
#NonSortedGA(Tradesheets,PriceSeries,MaxIndividualsInGen,TrainingBegin,TrainingEnd,ReportingBegin, ReportingEnd, CostOfTrading,MaxGen,MaxIndividuals)
#print "total_Gain,total_DD,total_Profit_Long,total_Loss_Long,total_Win_Long_Trades,total_Loss_Long_Trades,total_Profit_Short,total_Loss_Short,total_Win_Short_Trades,total_Loss_Short_Trades"
