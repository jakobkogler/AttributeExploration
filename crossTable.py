#-------------------------------------------------------------------------------
# Name:        crossTable.py
# Purpose:     extended QTableWidget with functions for a cross table
#
# Author:      Jakob Kogler
#-------------------------------------------------------------------------------

from PyQt5.QtWidgets import QTableWidget, QAbstractItemView, QTableWidgetItem

class CrossTable(QTableWidget):
    def __init__(self, thestruct, *args):
        QTableWidget .__init__(self, *args)

        self.horizontalHeader = []
        self.verticalHeader = []

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)

        self.itemClicked.connect(self.cellClicked)

    def loadTable(self, horizontalHeader, verticalHeader, table):
        self.horizontalHeader = horizontalHeader[:]
        self.verticalHeader = verticalHeader[:]
        super(CrossTable, self).setRowCount(len(self.verticalHeader))
        super(CrossTable, self).setColumnCount(len(self.horizontalHeader))
        self.updateTable()

        for i, row in enumerate(table):
            for j, bool_value in enumerate(row):
                if bool_value:
                    self.item(i, j).setText('X')

    def getTable(self):
        table = table = []
        for row in range(self.rowCount()):
            entries = []
            for column in range(self.columnCount()):
                entries.append(self.item(row, column).text() == 'X')
            table.append(entries)
        return table

    def updateTable(self):
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                item = self.item(row, column)
                if not item:
                    item = QTableWidgetItem('')
                    item.setTextAlignment(0x0004 | 0x0080) #centered
                    self.setItem(row, column, item)
        self.setVerticalHeaderLabels(self.verticalHeader)
        self.setHorizontalHeaderLabels(self.horizontalHeader)

    def setRowCount(self, rowCount):
        super(CrossTable, self).setRowCount(rowCount)
        self.updateTable()

    def setColumnCount(self, columnCount):
        super(CrossTable, self).setColumnCount(columnCount)
        self.updateTable()

    def appendRow(self, name):
        self.insertRow(self.rowCount())
        self.verticalHeader.append(name)
        self.updateTable()

    def appendColumn(self, name):
        self.insertColumn(self.columnCount())
        self.horizontalHeader.append(name)
        self.updateTable()

    def getHorizontalHeaderLabels(self):
        return self.horizontalHeader

    def getVerticalHeaderLabels(self):
        return self.verticalHeader

    def cellClicked(self, item):
        item.setText('' if item.text() == 'X' else 'X')

    def clear(self):
        self.setRowCount(0)
        self.setColumnCount(0)
        self.verticalHeader = []
        self.horizontalHeader = []