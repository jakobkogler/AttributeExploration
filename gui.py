#-------------------------------------------------------------------------------
# Name:        gui.py
# Purpose:     GUI for attribute exploration
#
# Author:      Jakob Kogler
#-------------------------------------------------------------------------------

import sys
import pickle
from AttributeExploration import *
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QTableWidgetItem, QFileDialog, QTableWidget
from PyQt5.QtCore import QSettings
from ui_attribute_exploration import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # variables
        self.attribute_names = []
        self.object_names = []

        # last table
        self.settings = QSettings("settings.ini", QSettings.IniFormat)
        filename = self.settings.value("last_file", None);
        if filename:
            self.loadTable(filename)
        else:
            self.newTable()

        # connect signals and slots
        self.ui.addAttributeButton.clicked.connect(self.addAttribute)
        self.ui.addObjectButton.clicked.connect(self.addObject)
        self.ui.actionSave.triggered.connect(self.saveTable)
        self.ui.actionLoad.triggered.connect(self.browseLoadTable)
        self.ui.actionNew.triggered.connect(self.newTable)
        self.ui.startExplorationButton.clicked.connect(self.startExploration)
        self.ui.counterExampleLineEdit.textChanged.connect(self.updateCounterExampleName)
        self.ui.nextImplication.clicked.connect(self.respondToImplication)

    ##############################
    ## Methods for:             ##
    ##    -saving tables        ##
    ##    -loading tables       ##
    ##    -creating new table ##
    ##############################

    def saveTable(self):
        filename = self.settings.value('last_file', 'untitled.fc')
        filename = QFileDialog.getSaveFileName(self, "Save File", filename, "Formal Context (*.fc)")[0];

        if filename:
            f = open(filename, "wb")
            pickle.dump(self.attribute_names, f)
            pickle.dump(self.object_names, f)
            pickle.dump(self.ui.tableWidget.getTable(), f)
            f.close()
            self.settings.setValue("last_file", filename);

    def browseLoadTable(self):
        self.newTable()
        filename = QFileDialog.getOpenFileName(self, "Open File", "", "Formal Context (*.fc)")[0];
        self.loadTable(filename)

    def loadTable(self, filename):
        try:
            f = open(filename, "rb")
            self.attribute_names = pickle.load(f)
            self.object_names = pickle.load(f)
            table = pickle.load(f)
            f.close()

            self.ui.tableWidget.loadTable(self.attribute_names, self.object_names, table)
            self.ui.counterExampleTable.loadTable(self.attribute_names, ['ce'], [[False] * len(self.attribute_names)])
            self.ui.suggestedImplicationGroupBox.setEnabled(False)

            self.settings.setValue("last_file", filename);
        except:
            self.newTable()

    def newTable(self):
        self.settings.setValue('last_file', '')
        self.attribute_names = []
        self.object_names = []
        self.ui.tableWidget.clear()
        self.ui.counterExampleTable.clear()
        self.ui.counterExampleTable.appendRow('ce')
        self.ui.suggestedImplicationGroupBox.setEnabled(False)

    ##########################################
    ## Methods for manipulationg the table: ##
    ##   -adding new attributes or objects  ##
    ##   -updating the row name             ##
    ##########################################

    def addAttribute(self):
        name = self.ui.attributeLineEdit.text()
        if name:
            self.ui.tableWidget.appendColumn(name)
            self.ui.counterExampleTable.appendColumn(name)
            self.attribute_names.append(name)
        self.ui.attributeLineEdit.clear()

    def addObject(self):
        name = self.ui.objectLineEdit.text()
        if name:
            self.ui.tableWidget.appendRow(name)
            self.object_names.append(name)
        self.ui.objectLineEdit.clear()

    def updateCounterExampleName(self, name):
        self.ui.counterExampleTable.setVerticalHeaderLabels([name])

    #####################################################
    ## Methods for operating the attribute exploration ##
    #####################################################

    def startExploration(self):
        table = self.ui.tableWidget.getTable()
        formal_objects = [self.rowToInt(row) for row in table]
        self.ui.implicationTextEdit.clear()
        self.ui.suggestedImplicationGroupBox.setEnabled(True)

        self.attributeExploration = AttributeExploration(self.attribute_names, formal_objects)
        self.getNextImplication()

    def rowToInt(self, row):
        row = ['1' if entry else '0' for entry in row]
        return int(''.join(row), 2)

    def intToRow(self, value):
        size = len(self.attribute_names)
        row = [False] * size
        for i in reversed(range(size)):
            if value % 2:
                row[i] = True
            value //= 2
        return row

    def rowToString(self, row):
        return ', '.join([attribute for (entry, attribute) in zip(row, self.attribute_names) if entry])

    def getNextImplication(self):
        implication = self.attributeExploration.getNextImplication()
        if implication:
            P_list = self.intToRow(implication[0])
            PSS_list = self.intToRow(implication[1] - implication[0])
            self.suggested_implication = self.rowToString(P_list) + ' => ' + self.rowToString(PSS_list)

            self.ui.implicationLineEdit.setText(self.suggested_implication)
            self.ui.acceptRadioButton.setChecked(True)
            self.ui.counterExampleLineEdit.setText('ce')
            for i, condition in enumerate(P_list):
                self.ui.counterExampleTable.item(0, i).setText('X' if condition else '')
        else:
            self.ui.suggestedImplicationGroupBox.setEnabled(False)

    def respondToImplication(self):
        if self.ui.acceptRadioButton.isChecked():
            self.attributeExploration.acceptImplication()
            implications = self.ui.implicationTextEdit.toPlainText()
            self.ui.implicationTextEdit.setPlainText(implications + str(len(self.attributeExploration.implicationsBasis)) + ': ' + self.suggested_implication + '\n')
        elif self.ui.counterExampleRadioButton.isChecked() and self.ui.counterExampleLineEdit.text():
            row = self.ui.counterExampleTable.getTable()[0]
            name = self.ui.counterExampleLineEdit.text()
            self.ui.tableWidget.appendRow(name)
            for i, entry in enumerate(row):
                self.ui.tableWidget.item(len(self.object_names), i).setText('X' if entry else '')
            self.attributeExploration.rejectImplication(self.rowToInt(row))
            self.object_names.append(name)
        self.getNextImplication()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())