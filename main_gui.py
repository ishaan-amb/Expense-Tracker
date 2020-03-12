# import packages required
import sys
import random
import time
from datetime import datetime, timedelta

# import styles
from qtmodernEdited import styles, windows

# helper functions
from db import *
from graphs_bar import *
from graphs_pie import *
from send_mail import *

# pyQt5 widgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout, \
    QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QProgressBar, QRadioButton, QSplashScreen
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import *


class MyTable(QTableWidget):
    def __init__(self):
        QTableWidget.__init__(self)

        # initialise table
        self.no_of_cols = 5
        self.setColumnCount(self.no_of_cols)
        tableHeader = self.horizontalHeader()

        self.setHorizontalHeaderItem(0, QTableWidgetItem('Name'))
        self.setHorizontalHeaderItem(1, QTableWidgetItem('Amount'))
        self.setHorizontalHeaderItem(2, QTableWidgetItem('Category'))
        self.setHorizontalHeaderItem(3, QTableWidgetItem(' '))
        self.setHorizontalHeaderItem(4, QTableWidgetItem(' '))

        tableHeader.setSectionResizeMode(0, QHeaderView.Stretch)
        tableHeader.setSectionResizeMode(1, QHeaderView.Stretch)
        tableHeader.setSectionResizeMode(2, QHeaderView.Stretch)

        # set edit and delete button to be as small as their text
        tableHeader.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        tableHeader.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        headerFont = QFont('SansSerif', 12)
        tableHeader.setFont(headerFont)

    def updateTable(self):
        global records
        records = get_records_by_date(currDate)

        self.no_of_recs = len(records)
        no_of_data_cols = self.no_of_cols - 2

        # Set/Reset the row count for the new rows added
        self.setRowCount(self.no_of_recs)

        keys = ["name", "amount", "category"]

        for row in range(self.no_of_recs):
            for col in range(self.no_of_cols):
                if (col < no_of_data_cols):
                    item = QTableWidgetItem(str(records[row][keys[col]]))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.setItem(row, col, item)

                elif (col == no_of_data_cols):
                    editButton = QPushButton('Edit')
                    editButton.clicked.connect(self.processEdit)
                    self.setCellWidget(row, col, editButton)

                elif (col == no_of_data_cols + 1):
                    delButton = QPushButton('Delete')
                    delButton.clicked.connect(self.processDel)
                    self.setCellWidget(row, col, delButton)

        print('TABLE: Updated table...')

    def processEdit(self):
        button = self.sender()
        if button:
            self.editRow = self.indexAt(button.pos()).row()

            # get the record ID from the row to be edited
            editID = records[self.editRow]

            # create new edit object with the id of row as parameter
            self.dialog = EditExpense(editID, self)
            self.dialog.show()

    def processDel(self):
        button = self.sender()
        if button:
            self.deletionRow = self.indexAt(button.pos()).row()

            # get the record ID from the row to be deleted
            self.deletionID = records[self.deletionRow]["_id"]
            # print(deletionID)

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)

            msg.setText("Are you sure you want to delete this item?")
            msg.setInformativeText("This item would be permanently deleted")
            msg.setWindowTitle("Delete")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.buttonClicked.connect(self.processDeleteDB)
            msg.exec_()

    def processDeleteDB(self, button):
        response = button.text()
        if response == 'OK':
            # delete record from DB
            delete_record(self.deletionID)
            print('GUI: Record Deleted from DB')
            self.removeRow(self.deletionRow)
            # pass


class HeaderWidget(QVBoxLayout):
    def __init__(self):
        super().__init__()

        smallFont = QFont('SansSerif', 15)
        bigFont = QFont('SansSerif', 25)

        mainLayout = QHBoxLayout()

        # Income Widget
        incomeWidget = QVBoxLayout()

        incomeLabel = QLabel('Daily Limit')
        incomeLabel.setFont(smallFont)
        incomeLabel.setAlignment(Qt.AlignCenter)

        self.incomeVal = QLabel()
        self.incomeVal.setFont(bigFont)
        self.incomeVal.setAlignment(Qt.AlignCenter)

        incomeWidget.addWidget(incomeLabel)
        incomeWidget.addWidget(self.incomeVal)

        # Balance Widget
        balanceWidget = QVBoxLayout()

        balanceLabel = QLabel('Balance')
        balanceLabel.setFont(smallFont)
        balanceLabel.setAlignment(Qt.AlignCenter)

        self.balanceVal = QLabel()
        self.balanceVal.setFont(bigFont)
        self.balanceVal.setAlignment(Qt.AlignCenter)

        balanceWidget.addWidget(balanceLabel)
        balanceWidget.addWidget(self.balanceVal)

        # Expense Widget
        expensesWidget = QVBoxLayout()

        expensesLabel = QLabel('Current Expenses')
        expensesLabel.setFont(smallFont)
        expensesLabel.setAlignment(Qt.AlignCenter)

        self.expensesVal = QLabel()
        self.expensesVal.setFont(bigFont)
        self.expensesVal.setAlignment(Qt.AlignCenter)

        expensesWidget.addWidget(expensesLabel)
        expensesWidget.addWidget(self.expensesVal)

        # Progress Bar
        self.progressBar = QProgressBar()
        self.progressBar.setGeometry(200, 80, 250, 20)

        mainLayout.addLayout(incomeWidget)
        mainLayout.addLayout(expensesWidget)
        mainLayout.addLayout(balanceWidget)

        self.addLayout(mainLayout)
        self.addWidget(self.progressBar)

    def updateHeader(self):
        global dailyAllowanceValue
        global totalExpensesValue
        global records
        global userEmail
        # totalExpensesValue = get_sum_of_day(currDate)[0]['total']

        # calculate sum of all records locally
        totalExpensesValue = sum([int(rec['amount']) for rec in records])
        balanceValue = dailyAllowanceValue - totalExpensesValue
        percentageUsed = int((totalExpensesValue / dailyAllowanceValue) * 100)

        self.incomeVal.setText(str(dailyAllowanceValue))
        self.expensesVal.setText(str(totalExpensesValue))
        self.balanceVal.setText(str(balanceValue))

        if (balanceValue > 0):
            self.progressBar.setValue(percentageUsed)
        else:
            send_mail(userEmail,totalExpensesValue)
            self.progressBar.setValue(100)
            self.progressBar.setTextVisible(False)
            # self.progressBar.setFormat(str(percentageUsed) + '%')
            self.progressBar.setAlignment(Qt.AlignCenter)
            self.progressBar.setStyleSheet("""QProgressBar::chunk { background: %s; }""" % '#ff4000')


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Expense Manager'
        self.left = 200
        self.top = 200
        self.width = 900
        self.height = 700

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # update widgets once before staring app
        updateAllWidgets()
        self.buttonsWidget()
        self.dateScrollerWidget()

        self.mainLayout = QVBoxLayout()
        self.tableLayout = QHBoxLayout()
        self.tableLayout.addWidget(mainTable)

        self.mainLayout.addLayout(header)
        self.mainLayout.addStretch()
        self.mainLayout.addLayout(self.buttonsLayout)
        self.mainLayout.addStretch()
        self.mainLayout.addLayout(self.dateScrollerLayout)
        self.mainLayout.addStretch()
        self.mainLayout.addLayout(self.tableLayout)

        self.setLayout(self.mainLayout)

        # Show widget
        self.show()

    def buttonsWidget(self):
        buttonsLayoutObj = QHBoxLayout()
        addButton = QPushButton('Add Expense')
        addButton.setFixedHeight(35)

        analyzeButton = QPushButton('Analaysis')
        analyzeButton.setFixedHeight(35)

        settingsButton = QPushButton('Settings')
        settingsButton.setFixedHeight(35)

        buttonsLayoutObj.addStretch()
        buttonsLayoutObj.addWidget(addButton)
        buttonsLayoutObj.addWidget(analyzeButton)
        buttonsLayoutObj.addWidget(settingsButton)
        buttonsLayoutObj.addStretch()

        addButton.clicked.connect(self.createNewExpense)
        analyzeButton.clicked.connect(self.createAnalysisPage)
        settingsButton.clicked.connect(self.createSettingsPage)

        self.buttonsLayout = buttonsLayoutObj

    def dateScrollerWidget(self):
        scrollerLayoutObj = QHBoxLayout()

        prevDateButton = QPushButton('Previous Date')
        prevDateButton.setFixedHeight(25)

        nextDateButton = QPushButton('Next Date')
        nextDateButton.setFixedHeight(25)

        bigFont = QFont('SansSerif', 20)
        self.dateText = QLabel()
        self.dateText.setText(currDate.strftime('%d %b %Y'))
        self.dateText.setFont(bigFont)

        scrollerLayoutObj.addWidget(prevDateButton)
        scrollerLayoutObj.addStretch()
        scrollerLayoutObj.addWidget(self.dateText)
        scrollerLayoutObj.addStretch()
        scrollerLayoutObj.addWidget(nextDateButton)

        prevDateButton.clicked.connect(self.gotoPrevDate)
        nextDateButton.clicked.connect(self.gotoNextDate)

        self.dateScrollerLayout = scrollerLayoutObj

    def gotoNextDate(self):
        global currDate
        currDate = currDate + timedelta(days=1)
        self.dateText.setText(currDate.strftime('%d %b %Y'))

        updateAllWidgets()

    def gotoPrevDate(self):
        global currDate
        currDate = currDate - timedelta(days=1)
        self.dateText.setText(currDate.strftime('%d %b %Y'))
        updateAllWidgets()

    def createNewExpense(self):
        self.dialog = AddExpense(self)
        self.dialog.show()

    def createSettingsPage(self):
        self.dialog = SettingsPage(self)
        self.dialog.show()

    def createAnalysisPage(self):
        self.dialog = AnalysisPage(self)
        self.dialog.show()


class AddExpense(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        super().__init__()
        self.title = 'Add Expense'
        self.left = 300
        self.top = 300
        self.width = 300
        self.height = 150
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createExpenseForm()

        addButton = QPushButton('Add Expense')
        cancelButton = QPushButton('Cancel')

        addButton.clicked.connect(self.addToDB)
        cancelButton.clicked.connect(self.close)

        mainLayout = QVBoxLayout()

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(addButton)
        buttonsLayout.addWidget(cancelButton)

        mainLayout.addLayout(self.expenseForm)
        mainLayout.addLayout(buttonsLayout)

        self.setLayout(mainLayout)

    def createExpenseForm(self):
        expenseFormLayout = QFormLayout()

        self.nameBox = QLineEdit()
        self.amountBox = QLineEdit()
        self.categoryBox = QLineEdit()

        expenseFormLayout.addRow('Expense Name: ', self.nameBox)
        expenseFormLayout.addRow('Expense Amount: ', self.amountBox)
        expenseFormLayout.addRow('Expense Category: ', self.categoryBox)

        self.expenseForm = expenseFormLayout

    def addToDB(self):
        insert_record(self.nameBox.text(), self.amountBox.text(), self.categoryBox.text(), currDate)
        print('GUI: Adding to Database')

        updateAllWidgets()
        self.close()


class EditExpense(QWidget):
    def __init__(self, editID, parent=None, ):
        QWidget.__init__(self)
        super().__init__()
        self.title = 'Edit Expense'
        self.left = 300
        self.top = 300
        self.width = 300
        self.height = 150

        self.editID = editID
        self.initUI()

    def initUI(self):
        # print('Editing ID is:', self.editID)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.recordID = self.editID["_id"]
        self.previousName = self.editID["name"]
        self.previousAmount = self.editID["amount"]
        self.previousCategory = self.editID["category"]

        self.createExpenseForm()

        editButton = QPushButton('Edit Expense')
        cancelButton = QPushButton('Cancel')

        editButton.clicked.connect(self.editToDB)
        cancelButton.clicked.connect(self.close)

        mainLayout = QVBoxLayout()
        buttonsLayout = QHBoxLayout()
        
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(editButton)
        buttonsLayout.addWidget(cancelButton)

        mainLayout.addLayout(self.expenseEditForm)
        mainLayout.addLayout(buttonsLayout)

        self.setLayout(mainLayout)

    def createExpenseForm(self):
        expenseEditFormLayout = QFormLayout()

        self.nameBox = QLineEdit()
        self.amountBox = QLineEdit()
        self.categoryBox = QLineEdit()

        # Set previous records as placeholders
        self.nameBox.setText(str(self.previousName))
        self.amountBox.setText(str(self.previousAmount))
        self.categoryBox.setText(str(self.previousCategory))

        expenseEditFormLayout.addRow('Expense Name: ', self.nameBox)
        expenseEditFormLayout.addRow('Expense Amount: ', self.amountBox)
        expenseEditFormLayout.addRow('Expense Category: ', self.categoryBox)

        self.expenseEditForm = expenseEditFormLayout

    def editToDB(self):
        print('GUI: Editing dataBase id', self.recordID)
        # Edit to DB
        print('GUI: New Edited Record:', self.recordID, self.nameBox.text(), self.amountBox.text(),
              self.categoryBox.text())
        edit_record(self.recordID, self.nameBox.text(), self.amountBox.text(), self.categoryBox.text())
        print('GUI: Succesfully Edited Record')

        updateAllWidgets()
        self.close()


class AnalysisPage(QWidget):
    def __init__(self, parent=None, ):
        QWidget.__init__(self)
        super().__init__()
        self.title = 'Analysis'
        self.left = 300
        self.top = 300
        self.width = 300
        self.height = 150

        self.initUI()

    def initUI(self):
        # print('Editing ID is:', self.editID)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createAnalysisForm()

        applyButton = QPushButton('OK')

        applyButton.clicked.connect(self.close)

        # Add box layout, add table to box layout and add box layout to widget
        mainLayout = QVBoxLayout()

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(applyButton)

        mainLayout.addLayout(self.analysisForm)
        mainLayout.addLayout(buttonsLayout)

        self.setLayout(mainLayout)

    def createAnalysisForm(self):
        analysisFormLayout = QVBoxLayout()

        byBar = QLabel('Bar Graph')
        plotByCategoryBarBtn = QPushButton('Show by Category')
        plotByDateBarBtn = QPushButton('Show By Date')

        byPie = QLabel('Pie Graph')
        plotByCategoryPieBtn = QPushButton('Show by Category')
        plotByDatePieBtn = QPushButton('Show by Date')

        plotByCategoryBarBtn.clicked.connect(plotByCategoryBar)
        plotByDateBarBtn.clicked.connect(plotByDateBar)

        plotByCategoryPieBtn.clicked.connect(plotByCategoryPie)
        plotByDatePieBtn.clicked.connect(plotByDatePie)

        analysisFormLayout.addWidget(byBar)
        analysisFormLayout.addWidget(plotByCategoryBarBtn)
        analysisFormLayout.addWidget(plotByDateBarBtn)

        analysisFormLayout.addWidget(byPie)
        analysisFormLayout.addWidget(plotByCategoryPieBtn)
        analysisFormLayout.addWidget(plotByDatePieBtn)

        self.analysisForm = analysisFormLayout


class SettingsPage(QWidget):
    def __init__(self, parent=None, ):
        QWidget.__init__(self)
        super().__init__()
        self.title = 'Settings'
        self.left = 300
        self.top = 300
        self.width = 300
        self.height = 150

        global theme, userEmail
        self.themeSelected = theme

        self.initUI()

    def initUI(self):

        # print('Editing ID is:', self.editID)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createSettingsForm()

        applyButton = QPushButton('Apply')

        applyButton.clicked.connect(self.applySettings)

        # Add box layout, add table to box layout and add box layout to widget
        mainLayout = QVBoxLayout()

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(applyButton)

        mainLayout.addLayout(self.settingsForm)
        mainLayout.addLayout(buttonsLayout)

        self.setLayout(mainLayout)

    def createSettingsForm(self):
        getUserSettings()
        settingsFormLayout = QFormLayout()

        self.dailyAllowance = QLineEdit()
        self.dailyAllowance.setText(str(dailyAllowanceValue))

        self.userEmail = QLineEdit()
        self.userEmail.setText(str(userEmail))

        self.b1 = QRadioButton("Light Mode")
        self.b1.toggled.connect(lambda: self.setTheme('light'))

        self.b2 = QRadioButton("Dark Mode")
        self.b2.toggled.connect(lambda: self.setTheme('dark'))

        if (theme == 'light'):
            self.b1.setChecked(True)
        elif (theme == 'dark'):
            self.b2.setChecked(True)

        settingsFormLayout.addRow('Daily Limit: ', self.dailyAllowance)
        settingsFormLayout.addRow("User Email",self.userEmail  )

        settingsFormLayout.addRow('Theme: ', self.b1)
        settingsFormLayout.addWidget(self.b2)
        self.settingsForm = settingsFormLayout

    def setTheme(self, selectedTheme):
        self.themeSelected = selectedTheme

    def applySettings(self):
        global theme
        global dailyAllowanceValue
        global email

        dailyAllowanceValue = int(self.dailyAllowance.text())
        theme = self.themeSelected
        email = self.userEmail.text()

        # update to database here
        change_settings(theme, dailyAllowanceValue, email)

        # HACK: Why does this work?
        applyTheme(theme)
        applyTheme(theme)
        updateAllWidgets()

        self.close()


def updateAllWidgets():
    mainTable.updateTable()
    header.updateHeader()


def applyTheme(theme):
    if (theme == 'light'):
        print('GUI: Setting theme to light')
        app.setStyle('windowsvista')
        styles.light(app)
    elif (theme == 'dark'):
        print('GUI: Setting theme to dark')
        app.setStyle('fusion')
        styles.dark(app)
    else:
        print('GUI: Unknown theme')


def getUserSettings():
    userSettings = get_settings()[0]
    print('User Settings:', userSettings)

    if (len(userSettings) > 0):
        theme = userSettings['theme']
        dailyAllowanceValue = int(userSettings['dailyLimit'])
        userEmail = userSettings['email']


    else:
        theme = 'dark'
        dailyAllowanceValue = 10000
        userEmail=""

    return theme, dailyAllowanceValue, userEmail

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create and display the splash screen
    splash_pix = QPixmap('splash_names_dark.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    theme, dailyAllowanceValue, userEmail = getUserSettings()
    applyTheme(theme)

    # global variables
    currDate = datetime.now()
    records = None
    totalExpensesValue = 0

    splash.hide()

    # global objects
    mainTable = MyTable()
    header = HeaderWidget()
    mainApp = App()

    mw = windows.ModernWindow(mainApp)
    mw.show()

    app.exec_()