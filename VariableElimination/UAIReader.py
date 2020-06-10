import numpy as np


class UAIReader:

    def __init__(self, UAIfile):
        self.edges = []
        self.tables = []
        self.variables = []
        self.cardinality = {}
        self.cliques = 0
        self.networkType = ""
        self.file = UAIfile
        self.tableDict = {}

    def instantiateUAI(self):
        varPrefix = "Var_"
        with open(self.file) as fp:
            for cnt, line in enumerate(fp):
                if cnt == 0:
                    self.networkType = line.strip()
                elif cnt == 1:
                    for i in range(int(line.strip())):
                        self.variables.append(varPrefix + str(i))
                elif cnt == 2:
                    cardinalityList = line.split()
                    for i, var in enumerate(self.variables):
                        self.cardinality[var] = int(cardinalityList[i])
                elif cnt == 3:
                    self.cliques = int(line.strip())
                elif 3 < cnt <= 3 + self.cliques:
                    values = line.split()
                    values = values[1:]
                    keyForTableDict = []
                    for v in values:
                        keyForTableDict.append(varPrefix + v)

                    for i in range(len(values) - 1, 0, -1):
                        x = 0
                        while (x < i):
                            self.edges.append((varPrefix + values[x], varPrefix + values[i]))
                            x += 1
                    self.tableDict[tuple(keyForTableDict)] = []

                else:
                    if len(line.strip()) > 0:
                        values = line.split()
                        if len(values) > 1:
                            for key, val in self.tableDict.items():
                                if len(self.tableDict[key]) == 0:
                                    self.tableDict[key] = values
                                    break

        for key, val in self.tableDict.items():
            k = list(key)
            v = [float(i) for i in val]
            v = np.array(v, dtype=np.float64)
            self.tables.append((k, v))

    def getEdges(self):
        return self.edges

    def getTables(self):
        return self.tables

    def getTableDict(self):
        return self.tableDict

    def getVariables(self):
        return self.variables

    def getCardinality(self):
        return self.cardinality

    def getNetwork(self):
        return self.networkType