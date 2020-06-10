import math
import sys

import pandas as pd

from FunctionTable import CPT, printFunctionTable
from Ordering import MinOrder
from UAIReader import UAIReader

gPartition = 0
gOrdering = []


def _generateIdx(n, *variables):
    newList = []
    for i in range(1 << n):
        s = bin(i)[2:]
        s = '0' * (n - len(s)) + s
        newList.append(list(s))
    return newList


def _getCommonVariables(listA, listB):
    return set(listA) & set(listB)


def _rearrange(df1, df2, common):
    cols1 = df1.columns.tolist()
    cols2 = df2.columns.tolist()

    if gOrdering.index(cols2[0]) < gOrdering.index(cols1[0]):
        return df2[cols2], df1[cols1]

    return df1[cols1], df2[cols2]


def _generateDataframe(fiVariables, fiValues):
    fiIdx = pd.MultiIndex.from_tuples(_generateIdx(len(fiVariables), fiVariables), names=fiVariables)
    fiIdx = list(map(list, fiIdx))
    fiDf = pd.DataFrame(data=fiIdx, columns=fiVariables)
    fiDf['value'] = fiValues

    return fiDf


def _multiplyFactors(fi1, fi2):
    # print("In multiply factors ...")
    # print("Factor1 : " + str(fi1))
    # print("Factor2 : " + str(fi2))
    intermediateVariables = set()
    intermediateValues = []
    fi1Variables = sorted([x for x in list(fi1.keys())[0]])
    fi2Variables = sorted([x for x in list(fi2.keys())[0]])
    [intermediateVariables.add(x) for x in fi1Variables]
    [intermediateVariables.add(y) for y in fi2Variables]
    fi1Values = [x for x in list(fi1.values())[0]]
    fi2Values = [x for x in list(fi2.values())[0]]

    if len(fi1Values) == 1:
        _sumFactor(fi1, fi1Variables[0])
        intermediateFactor = fi2
    elif len(fi2Values) == 1:
        _sumFactor(fi2, fi2Variables[0])
        intermediateFactor = fi1
    else:
        fi1Df = _generateDataframe(fi1Variables, fi1Values)
        fi2Df = _generateDataframe(fi2Variables, fi2Values)
        commonVariables = sorted(_getCommonVariables(fi1Variables, fi2Variables))
        fi1Df, fi2Df = _rearrange(fi1Df, fi2Df, commonVariables[0])

        for i, row1 in fi1Df.iterrows():
            tempFi1 = []
            for x in range(len(commonVariables)):
                tempFi1.append(fi1Df.loc[i, commonVariables[x]])
            for j, row2 in fi2Df.iterrows():
                tempFi2 = []
                for y in range(len(commonVariables)):
                    tempFi2.append(fi2Df.loc[j, commonVariables[y]])
                if tempFi1 == tempFi2:
                    intermediateValues.append(fi1Df['value'][i] * fi2Df['value'][j])

        intermediateFactor = {tuple(sorted(intermediateVariables)): intermediateValues}
    # print("Intermediate factor : " + str(intermediateFactor))
    # print("End of multiply-factors")
    return intermediateFactor


def _sumFactor(fi, variable):
    global gPartition
    # print("In sum over factor ... ")
    # print("Summing over variable : " + variable)
    # print("On factor :" + str(fi))
    fiVariables = sorted([x for x in list(fi.keys())[0]])
    fiValues = [x for x in list(fi.values())[0]]
    if len(fiVariables) == 1:
        gPartition = gPartition + sum(fiValues)
        fiVariables.remove(variable)
        # print("Temp partition function Z : " + str(gPartition))
        return None, None

    fiDf = _generateDataframe(fiVariables, fiValues)
    fiDf = fiDf.drop([variable], axis=1)
    cols = fiDf.columns.tolist()
    cols.remove('value')
    fiDf = fiDf.groupby(cols)['value'].agg('sum')
    fiVariables.remove(variable)
    # print("End of sum-factor")
    return tuple(fiVariables), list(fiDf)


def _computeFactorProduct(toProcess, functionTable, var):
    # printFunctionTable(functionTable)
    if len(toProcess) == 0:
        return functionTable

    if len(toProcess) == 1:
        taoFactor, taoValue = _sumFactor(toProcess[0], var)
        # print("tao Factor : " + str({taoFactor: taoValue}))
        if taoFactor is not None:
            functionTable.append({taoFactor: taoValue})
        functionTable.remove(toProcess[0])
    else:
        # print("In computeFactorProduct: " + str(toProcess))

        if toProcess[0] in functionTable:
            functionTable.remove(toProcess[0])

        if toProcess[1] in functionTable:
            functionTable.remove(toProcess[1])
        intermediateFactor = _multiplyFactors(toProcess[0], toProcess[1])
        toProcess = toProcess[2:]
        if len(toProcess) > 0:
            toProcess = [intermediateFactor] + toProcess
            return _computeFactorProduct(toProcess, functionTable, var)

        taoFactor, taoValue = _sumFactor(intermediateFactor, var)
        # print("tao Factor : " + str({taoFactor: taoValue}))
        if taoFactor is not None:
            functionTable.append({taoFactor: taoValue})

    return functionTable


def _printEdges(edges):
    print("\nEdges : ")
    for edge in edges:
        print(str(edge))


def _printOrigCPT(table):
    print("\nOriginal factor table :\n", "-" * 50)
    for rec in table:
        print(rec)
    print("-" * 50)


def _printFileContent(readerPreamble):
    print(f'\nNetwork type : {readerPreamble.getNetwork()}')
    print(f'\nNumber of variables : {str(len(readerPreamble.getVariables()))}')
    print(f'\nVariables : {str(readerPreamble.getVariables())}')
    _printEdges(readerPreamble.getEdges())
    _printOrigCPT(readerPreamble.getTables())


def _performVariableElimination(evidence, readerPreamble):
    cpt = CPT(evidence, readerPreamble.getTables())
    functionTable = cpt.instantiateEvidence()
    minOrder = MinOrder(readerPreamble.getEdges(), evidence)
    ordering = minOrder.getOrdering()

    print("\n" + "-" * 30)
    print("Eliminating variable : ")
    for var in ordering:
        print(var + " | ", end="")
        toProcess = []
        for factorVariables in functionTable:
            for factorVariable in factorVariables:
                if var in factorVariable:
                    values = [x for x in list(factorVariables.values())[0]]
                    toProcess.append({factorVariable: values})
        if len(toProcess) > 0:
            functionTable = _computeFactorProduct(toProcess, functionTable, var)

    printFunctionTable(functionTable)


def _printPartitionFunction():
    print("\n" + "-" * 50)
    print("\nPartition function Z : " + str(round(math.log10(gPartition), 5)))


def main():
    global gOrdering

    if len(sys.argv) > 3:
        print("Invalid number of arguments. Correct arguments are: <filename> <network-file-uai> <evidence-file>")
        return

    readerPreamble = UAIReader(sys.argv[1])
    readerPreamble.instantiateUAI()
    evidenceFile = open(sys.argv[2])

    gOrdering = sorted(readerPreamble.getVariables())
    _printFileContent(readerPreamble)
    _performVariableElimination(evidenceFile.read().strip(), readerPreamble)
    _printPartitionFunction()


if __name__ == "__main__":
    main()
