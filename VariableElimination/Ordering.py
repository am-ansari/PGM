class MinOrder:

    def __init__(self, edges, evidenceStr):
        self.edges = edges
        self.evidenceStr = evidenceStr

    def _createVarDict(self):
        varDict = {}
        for edge in self.edges:
            if edge[0] not in varDict.keys():
                varDict[edge[0]] = [edge[1]]
            else:
                varDict[edge[0]].append(edge[1])

            if edge[1] not in varDict.keys():
                varDict[edge[1]] = [edge[0]]
            else:
                varDict[edge[1]].append(edge[0])

        return varDict

    def getOrdering(self):
        varDict = self._createVarDict()
        ordering = []

        while len(varDict) > 0:
            degreeDict = {}
            for var in sorted(varDict.keys()):
                # print("Variable " + var + " : " + str(len(varDict[var])))
                degreeDict[var] = len(varDict[var])

            sortedBasedOnDegree = sorted(degreeDict.items(), key=lambda x: x[1])

            minDegreeVariable = sortedBasedOnDegree[0][0]
            ordering.append(minDegreeVariable)
            varDict.pop(minDegreeVariable)
            for var in sorted(varDict.keys()):
                if minDegreeVariable in varDict[var]:
                    varDict[var].remove(minDegreeVariable)

        print("\nOrdering : " + str(ordering))
        return ordering
