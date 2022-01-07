# Evidence class.
class Evidence:

    def __init__(self, evidenceStr):
        self.evidenceStr = evidenceStr

    def createEvidenceDict(self):
        evidenceDict = {}
        for index in range(2, len(self.evidenceStr) - 2, 4):
            evidenceDict["var_" + self.evidenceStr[index]] = self.evidenceStr[index + 2]

        return evidenceDict
