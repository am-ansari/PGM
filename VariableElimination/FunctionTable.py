from Evidence import Evidence
import copy


def _getReducedFactors(values, variable, evidenceVal):
    newList = []
    if variable == 'x':
        if evidenceVal == 0:
            newList.append(values[2])
            newList.append(values[3])
        else:
            newList.append(values[0])
            newList.append(values[1])
    else:
        if evidenceVal == 0:
            newList.append(values[0])
            newList.append(values[2])
        else:
            newList.append(values[1])
            newList.append(values[3])
    return newList


def _getFunctionTable(table):
    functionTable = []

    for x in table:
        functionTable.append({tuple(x[0]): list(map(float, x[1]))})

    return functionTable


def printFunctionTable(table):
    for val in table:
        print(str(val))


class CPT:

    def __init__(self, evidenceStr, table):
        self.evidenceStr = evidenceStr
        self.table = table

    def instantiateEvidence(self):
        if self.evidenceStr[0] == 0:
            return _getFunctionTable(self.table)

        evidenceString = Evidence(self.evidenceStr)
        evidenceDict = evidenceString.createEvidenceDict()

        newFunctionTable = []
        subTable = []
        for x in self.table:
            if len(x[0]) == 1:
                if x[0][0] in evidenceDict.keys() and len(x[1]) > 1:
                    newFunctionTable.append((x[0], [x[1][len(evidenceDict[x[0][0]])]]))
                    # continue
                else:
                    newFunctionTable.append(x)
            else:
                subTable.append(x)

        # printFunctionTable(subTable)

        subTableIdx = []
        subTableAfterEvidence = copy.deepcopy(subTable)
        for evidenceVariable in evidenceDict.keys():
            for index, row in enumerate(subTable):
                if evidenceVariable in row[0]:
                    if evidenceVariable == row[0][0]:
                        newFunctionTable.append(
                            ([row[0][1]], _getReducedFactors(row[1], 'x', evidenceDict[evidenceVariable])))
                    else:
                        newFunctionTable.append(
                            ([row[0][0]], _getReducedFactors(row[1], 'y', evidenceDict[evidenceVariable])))

                    if row in subTableAfterEvidence:
                        subTableAfterEvidence.remove(row)
                    subTableIdx.append(index)

        for j, z in enumerate(subTableAfterEvidence):
            newFunctionTable.append(z)

        # printFunctionTable(newFunctionTable)

        return _getFunctionTable(newFunctionTable)
