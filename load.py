import threading

from PyQt5 import QtCore, uic, QtWidgets, QtGui
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush
from PyQt5.QtWidgets import QDialog

import fetch
import _thread
import sys
import os

UIClass, QtBaseClass = uic.loadUiType("launch.ui")
QDialog, BLQDialog = uic.loadUiType("blacklist_tabs.ui")


class QDialogClass(QDialog, BLQDialog):

    def __init__(self, tabs, selected, parent=None):
        BLQDialog.__init__(self, parent)
        self.setupUi(self)
        model = QStandardItemModel(self.tabsSelectList)
        self.parent = parent
        self.tabs = tabs
        self.selected = selected
        self.selectedIndexes = []
        #find the index id of selected tabs.
        for tab in selected:
            self.selectedIndexes.append(tab["i"])
        for tab in tabs:
            item = QStandardItem(tab["n"] +" - " +tab["type"])
            color = QColor(tab["colour"]["r"] , tab["colour"]["g"] , tab["colour"]["b"] , 150)
            item.setCheckable(True)
            if tab["i"] in self.selectedIndexes:
                item.setCheckState(QtCore.Qt.Checked)
            item.setBackground(QBrush(color))
            #item.setForeground(QBrush(QColor(100,100,100)))
            model.appendRow(item)
        self.tabsSelectList.setModel(model)
        self.setWindowTitle("Select stash tabs for Chaos Recipe")
        self.selectAll.clicked.connect(self.selectAllEvent)
        self.clear.clicked.connect(self.clearEvent)
        self.buttonBox.accepted.connect(self.accept)

    def selectAllEvent(self):
        model = self.tabsSelectList.model()
        model.blockSignals(True)
        try:
            for index in range(model.rowCount()):
                item = model.item(index)
                if item.isCheckable():
                    item.setCheckState(QtCore.Qt.Checked)
        finally:
            model.blockSignals(False)

    def clearEvent(self):
        model = self.tabsSelectList.model()
        model.blockSignals(True)
        try:
            for index in range(model.rowCount()):
                item = model.item(index)
                if item.isCheckable():
                    item.setCheckState(QtCore.Qt.Unchecked)
        finally:
            model.blockSignals(False)

    def accept(self):
        model = self.tabsSelectList.model()
        model.blockSignals(True)
        tabs = []
        try:
            for index in range(model.rowCount()):
                item = model.item(index)
                if item.isCheckable() and item.checkState() == QtCore.Qt.Checked:
                    tabs.append(index) #create list with selected indexes
        finally:
            model.blockSignals(False)

        self.parent.setTabsSelected(tabs)
        self.close()



class MyApp(UIClass, QtBaseClass):

    def __init__(self):
        UIClass.__init__(self)
        QtBaseClass.__init__(self)
        self.setupUi(self)
        self.startButton.clicked.connect(self.connect)
        self.startFetch.clicked.connect(self.fetchEvent)
        self.stopFetch.clicked.connect(self.stopFetchEvent)
        self.blacklistButton.clicked.connect(self.showBlacklist)
        self.progressBar.setVisible(False)
        self.etaLabel.setVisible(False)
        self.stopFetch.setVisible(False)
        self.established.setStyleSheet("color:transparent;")
        self.tabsSelectedLabel.setStyleSheet("color:transparent;")

        self.stash_monitor = fetch.StashMonitor()
        self.thread = QtCore.QThread(self)
        self.stash_monitor.packet_signal.connect(self.progressPacket)
        self.stash_monitor.moveToThread(self.thread)

        self.fetchThread = QtCore.QThread(self)


    def populateLeagueComboBox(self):
        leagueInfo = self.stash_monitor.fetchLeagueInfo()
        leagueBoxFill = []
        for league_name in leagueInfo:
            print(league_name["id"])
            leagueBoxFill.append(league_name["id"])
        self.leagueComboBox.addItems(leagueBoxFill)
        self.leagueComboBox.setEnabled(True)
        self.blacklistButton.setEnabled(True)
        self.tabsSelectedLabel.setStyleSheet("color:black;")

    def connect(self):
        # print(self.accountEdit.text())
        # print(self.poesessidEdit.text())
        self.thread = QtCore.QThread(self)
        self.stash_monitor.moveToThread(self.thread)
        if not self.accountEdit.text() is None \
                and not self.poesessidEdit.text() is None:
            self.accountEdit.setStyleSheet("border: solid black;")
            self.established.setStyleSheet("color:transparent;")
            self.tabsSelectedLabel.setStyleSheet("color:transparent;")
            self.leagueComboBox.setEnabled(False)
            self.blacklistButton.setEnabled(False)
            self.startFetch.setEnabled(False)
            self.stopFetch.setVisible(False)
            self.thread.started.connect(lambda: self.stash_monitor.checkAccount(
                    self.accountEdit.text()
                    , self.poesessidEdit.text()
                    , self.wrongAccountName
                    , self.wrongPOESessID
                    , self.connected))
            self.thread.start()

        else:
            if self.accountEdit.text() is None:
                self.wrongAccountName()
            if self.poesessidEdit.text() is None:
                self.wrongPOESessID()

    def fetchEvent(self):
        self.stopFetch.setVisible(True)
        self.thread.exit()
        self.stash_monitor.moveToThread(self.fetchThread)
        self.stash_monitor.fetchTabInfoGUI(self.setEstimatedTime) #set the eta and progress bar
        self.fetchThread.started.connect(self.stash_monitor.fetchStash)
        self.fetchThread.start()

    def stopFetchEvent(self):
        self.thread = QtCore.QThread(self)

    def wrongAccountName(self):
        self.accountEdit.setStyleSheet("border: solid red;")
        self.established.setStyleSheet("color:transparent;")

    def wrongPOESessID(self):
        self.poesessidEdit.setStyleSheet("border: solid red;")
        self.established.setStyleSheet("color:transparent;")

    def connected(self):
        self.accountEdit.setStyleSheet("border: solid black;")
        self.established.setStyleSheet("color:black;")
        self.populateLeagueComboBox()
        self.startFetch.setEnabled(True)

    @QtCore.pyqtSlot(dict)
    def progressPacket(self, packet):
        print("hello?")
        self.progressBar.setValue(packet["id"] + 1)
        self.progressEdit.setPlainText(self.progressEdit.toPlainText() + "\n" + packet["message"])
        self.progressEdit.moveCursor(QtGui.QTextCursor.End)

    def setEstimatedTime(self, time, maxValue):
        self.progressBar.setVisible(True)
        self.etaLabel.setVisible(True)
        self.etaLabel.setText("Eta : " + time + " Sec")
        self.progressBar.setMaximum(maxValue)
        self.progressBar.setValue(0)

    def showBlacklist(self):
        self.stash_monitor.setLeague(self.leagueComboBox.currentText())
        dialog = QDialogClass(self.stash_monitor.fetchTabInfo(), self.stash_monitor.selected_tabs,self)
        dialog.exec_()

    def setTabsSelected(self, tabs):
        if not tabs:
            self.tabsSelectedLabel.setText("No Tabs Selected")
        else:
            if len(self.stash_monitor.tabs_loaded) == len(tabs):
                self.tabsSelectedLabel.setText("All Tabs Selected")
            else:
                self.tabsSelectedLabel.setText("Selected Tabs : " + str(len(tabs)))
        self.stash_monitor.setTabsSelected(tabs)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
