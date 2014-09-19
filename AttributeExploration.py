#-------------------------------------------------------------------------------
# Name:        AttributeExploration.py
# Purpose:     class for attribute exploration
#
# Author:      Jakob Kogler
#-------------------------------------------------------------------------------

class AttributeExploration:
    def __init__(self, attributes, objects):
        self.attributes = attributes
        self.attributeCount = len(attributes)
        self.objects = objects
        self.B = 0
        self.implicationsBasis = []
        self.waitForResponse = False

    def getNextImplication(self):
        def Lstar(X):
            B = [b for (a,b) in self.implicationsBasis if a & X == a  and a != X]
            for b in B:
                X |= b
            return X

        if not self.waitForResponse:
            for i in reversed(range(self.attributeCount)):
                j = self.attributeCount - 1 - i

                # m = {m_1, m_2, ..., m_i-1}
                m = 2**self.attributeCount - 2 * 2**j

                # P = (B cut {m_1, m_2, ..., m_i-1}) union m_i
                P = (self.B & m) | 2**j

                # L*-operator
                LstarP, P = P, -1
                while LstarP != P:
                    LstarP, P = Lstar(LstarP), LstarP

                # B <_i L*
                if (P & ~self.B & 2**j == 0) or (self.B & m != P & m):
                    continue

                # P**
                Pstar = [obj for obj in self.objects if obj & P == P]
                Pstarstar = 2**self.attributeCount - 1
                for obj in Pstar:
                    Pstarstar &= obj

                if P == Pstarstar:
                    # P => P, not interesting
                    self.B = P
                    return self.getNextImplication()
                else:
                    # interesting implication found
                    self.implication = (P, Pstarstar)
                    self.waitForResponse = True
                    return self.implication
        return None

    def acceptImplication(self):
        if self.waitForResponse:
            self.waitForResponse = False
            self.implicationsBasis.append(self.implication)
            self.B = self.implication[0]

    def rejectImplication(self, counterExample):
        if self.waitForResponse:
            self.waitForResponse = False
            self.objects.append(counterExample)