
from re import search
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from PyQt5.QtWidgets import *
from datetime import date, datetime
import calendar

from VkInteractionTools import *

class CaptchaDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Captcha")

        dlgLayout = QVBoxLayout()
        
        self.captchaLabel = QLabel("Captcha is not loaded")
        self.captchaLabel.setFixedHeight(50)
        self.captchaLabel.setAlignment(Qt.AlignCenter)

        self.captchaAnswerField = QLineEdit()
        self.captchaAnswerField.setAlignment(Qt.AlignCenter)
    
        self.formBtns = QDialogButtonBox()
        self.formBtns.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.formBtns.rejected.connect(self.close)

        dlgLayout.addWidget(self.captchaLabel)
        dlgLayout.addWidget(self.captchaAnswerField)
        dlgLayout.addWidget(self.formBtns, 0, Qt.AlignCenter)
        self.setLayout(dlgLayout)

    def setCaptchaImage(self):
        captchaImage = self.exception.get_image()

        captchaPixmap = QPixmap()
        captchaPixmap.loadFromData(captchaImage, "JPG")
        self.captchaLabel.setPixmap(captchaPixmap)

class AuthVkDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.mainWindow = parent

        # Making captha window for Vk authentication window
        self.captchaVkDialog = CaptchaDialog(self)
        self.captchaVkDialog.formBtns.accepted.connect(self.capthaAceccept)

        self.setWindowTitle('AuthVK')
        
        dlgLayout = QVBoxLayout()
        formLayout = QFormLayout()
        
        self.loginField = QLineEdit()
        
        self.pwdField   = QLineEdit()
        self.pwdField.setEchoMode(QLineEdit.EchoMode.Password)

        self.showPwdCheckBox = QCheckBox()
        self.showPwdCheckBox.stateChanged.connect(self.pwdVisibilityChange)
        
        formLayout.addRow('Login or phone number:', self.loginField)
        formLayout.addRow('Password:', self.pwdField)
        formLayout.addRow('Show password:', self.showPwdCheckBox)
        
        dlgLayout.addLayout(formLayout)

        formBtns = QDialogButtonBox()
        formBtns.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        formBtns.accepted.connect(self.enterAuthData)
        formBtns.rejected.connect(self.close)

        dlgLayout.addWidget(formBtns)
        self.setLayout(dlgLayout)

    def enterAuthData(self):       

        self.mainWindow.vkSession.setAuthData(login=self.loginField.text(), password=self.pwdField.text())

        try:
            self.mainWindow.vkSession.getConnection()
            self.mainWindow.updateStatusBar()
            self.close()
        except vk_api.exceptions.AuthError as connectException:
            self.showAuthVkWarning(connectException.args[-1])
        except vk_api.exceptions.Captcha as connectException:
            self.captchaVkDialog.exception = connectException
            self.captchaVkDialog.setCaptchaImage()
            self.captchaVkDialog.open()

    def capthaAceccept(self):
        captchaAnswer = self.captchaVkDialog.captchaAnswerField.text() 
        self.captchaVkDialog.captchaAnswerField.setText("")

        if captchaAnswer:
            try:
                self.captchaVkDialog.exception.try_again(captchaAnswer)
                self.captchaVkDialog.close()
            except vk_api.exceptions.AuthError as exception:
                self.captchaVkDialog.close()
                self.showAuthVkWarning(exception.args[-1])
            except vk_api.exceptions.Captcha as exception:
                self.showAuthVkWarning("Wrong captcha")
                self.captchaVkDialog.exception = exception
                self.captchaVkDialog.setCaptchaImage()
        else:
            self.showAuthVkWarning("Enter the captcha")

    def showAuthVkWarning(self, warningMessage):
        alertMsgBox = QMessageBox()
        alertMsgBox.setWindowTitle("VK Auth")
        alertMsgBox.setText(warningMessage)
        alertMsgBox.exec()

    def pwdVisibilityChange(self):
        if (self.showPwdCheckBox.isChecked()):
            self.pwdField.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.pwdField.setEchoMode(QLineEdit.EchoMode.Password)

class SearchVkForm(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.birthYearsRange = 100                           # Number of years between current year and last year for searching
        self.currentYear     = date.today().year             # Current year is first year for searching

        self.mainWindow = parent
        
        self.setFixedWidth(200)

        self.searchQueryField = QLineEdit()
        self.sexComoBox = QComboBox()
        
        self.birthDayField = QSpinBox()
        self.birthDayField.setMaximum(31)   # Set maximum number of days in any month
        
        self.birthMonthField = QComboBox()
        # Month combo box filling
        self.birthMonthField.addItems(['', *[calendar.month_name[month] for month in range(1, 13)]]) # Don't remove first empty item
        self.birthMonthField.currentTextChanged.connect(self._birthMonthSelected)

        self.birthYearField = QComboBox()
        # Birth year combo box filling
        self.birthYearField.addItems(['', *[str(year) for year in range(self.currentYear, self.currentYear-self.birthYearsRange-1, -1)]])
        self.birthYearField.currentTextChanged.connect(self._birthYearSelected)
        
        self.ageFromField = QSpinBox()
        self.ageFromField.setMaximum(self.birthYearsRange)
        self.ageFromField.valueChanged.connect(self._birthYearRangeEdited)
        
        self.ageToField = QSpinBox()
        self.ageToField.setMaximum(self.birthYearsRange)
        
        self.countryComoBox = QComboBox()      
        self.countryComoBox.addItems([''])  # Country field first empty item
        self._fillingCountryComboBox()

        self.citiesComoBox = QComboBox()
        self.citiesComoBox.addItems([''])   # City field first empty item

        # Create current widget filling
        self.searchFormLayout = QVBoxLayout()
        self.createSearchFields()
        self.setLayout(self.searchFormLayout)

    def createSearchFields(self):
        # Search query section
        self.searchFormLayout.addWidget(QLabel("Search query:"))
        self.searchFormLayout.addWidget(self.searchQueryField)
        # Selection sex section
        self.sexComoBox.addItems(['', 'Woman', 'Man'])  # Don't change elements order
        self.searchFormLayout.addWidget(QLabel("Sex:"))
        self.searchFormLayout.addWidget(self.sexComoBox)
        # Birth date section
        self.searchFormLayout.addWidget(QLabel("Birth date:"))
        birthDateLayout = QHBoxLayout()
        birthDateLayout.addWidget(self.birthDayField)
        birthDateLayout.addWidget(self.birthMonthField)
        birthDateLayout.addWidget(self.birthYearField)
        self.searchFormLayout.addLayout(birthDateLayout) 
        # Age limits section
        ageFromToLayout = QHBoxLayout()
        ageFromToLayout.addWidget(QLabel("Age from:"))
        ageFromToLayout.addWidget(self.ageFromField)
        ageFromToLayout.addWidget(QLabel("Age to:"))
        ageFromToLayout.addWidget(self.ageToField)
        self.searchFormLayout.addLayout(ageFromToLayout)
        # Slection country section
        self.searchFormLayout.addWidget(QLabel("Country:"))
        self.searchFormLayout.addWidget(self.countryComoBox)
        # Slection city section
        self.searchFormLayout.addWidget(QLabel("City:"))
        self.searchFormLayout.addWidget(self.citiesComoBox)
        # Search button section
        searchButton = QPushButton('Search')
        searchButton.pressed.connect(self.getSearchResults)
        self.searchFormLayout.addWidget(searchButton)
        
        self.searchFormLayout.addStretch()

    # Set minimum value for end of age range
    def _birthYearRangeEdited(self):
        self.ageToField.setMinimum(self.ageFromField.value())

    # Change number of days in month
    def _birthMonthSelected(self):
        # When month is not selected, birth day max value is 31
        numberOfDays = 31

        if self.birthMonthField.currentIndex():
            if self.birthYearField.currentText():
                numberOfDays = calendar.monthrange(int(self.birthYearField.currentText()), self.birthMonthField.currentIndex())[1]
            else:
                # When year isn't selected
                if self.birthMonthField.currentIndex() == 2:
                    # For february set maximum 29 days
                    numberOfDays = 29
                else:
                    # For another month, set number of days in month, for current year
                    numberOfDays = calendar.monthrange(self.currentYear, self.birthMonthField.currentIndex())[1]
             
        self.birthDayField.setMaximum(numberOfDays)

    def _birthYearSelected(self):
        # Change number of days in february
        if self.birthMonthField.currentIndex() == 2:
            self._birthMonthSelected()

        if self.birthYearField.currentText() == '':
            self.ageFromField.setValue(0)
            self.ageToField.setValue(0)
            
            # Activate fields
            self.ageFromField.setEnabled(True)
            self.ageToField.setEnabled(True)
        else:
            # When birth year is selected, age is indicated in ageFromField and ageToField
            selectedBirthYear = int(self.birthYearField.currentText())
            selectedAge = self.currentYear-selectedBirthYear
            self.ageFromField.setValue(selectedAge)
            self.ageToField.setValue(selectedAge)

            # Deactivate fields
            self.ageFromField.setEnabled(False)
            self.ageToField.setEnabled(False)

    def _fillingCountryComboBox(self):
        if self.mainWindow.vkSession.connectionStatus():
            self.countriesList = self.mainWindow.vkSession.getCountriesList()
            self.countryComoBox.addItems(self.countriesList.keys())
            
            self.countryComoBox.currentTextChanged.connect(self._fillingCityComboBox)

    def _fillingCityComboBox(self):
        countryName = self.countryComoBox.currentText()
        self.citiesComoBox.clear()          # Clear cities combo box
        self.citiesComoBox.addItems([''])   # Add empty item

        if countryName:
            countryId = self.countriesList[countryName]
            self.citiesList = self.mainWindow.vkSession.getCitiesList(countryId)
            self.citiesComoBox.addItems(self.citiesList.keys())

    def getSearchResults(self):

        searchQuery = VkSearchQuery()
        
        if self.searchQueryField.text():
            searchQuery.setText(self.searchQueryField.text())
        if self.sexComoBox.currentIndex():
            searchQuery.setSex(self.sexComoBox.currentIndex())
        # Birth date section
        if self.birthDayField.value():
            searchQuery.setBirthDay(self.birthDayField.value())
        if self.birthMonthField.currentIndex():
            searchQuery.setBirthMonth(self.birthMonthField.currentIndex())
        # Set birth date year or age limits
        if self.birthYearField.currentText():
            searchQuery.setBirthYear(int(self.birthYearField.currentText()))
        else:
            searchQuery.setAgesLimits(self.ageFromField.value(), self.ageToField.value())
        # Country and city section
        if self.countryComoBox.currentText():
            searchQuery.setCountry(self.countriesList[self.countryComoBox.currentText()])
        if self.citiesComoBox.currentText():
            searchQuery.setCity(self.citiesList[self.citiesComoBox.currentText()])

        usersList = self.mainWindow.vkSession.getUsers(searchQuery.getQuery())
        
        accounts = []
        for user in usersList:
            # To obtain counters data need to make request for only one user
            #user['counters'] = self.getCountersData(user['id'])

            userInfo = VkAccountInfo(user)
            accounts.append(userInfo)

        self.showSearchSummary(accounts)
        self.mainWindow.vkSearchResults.addItems(accounts)

    def getCountersData(self, userId):
        userInfo = self.mainWindow.vkSession.api.users.get(user_ids=userId, fields='counters')[-1]
        return userInfo.get('counters')

    def showSearchSummary(self, accounts):
        summaryString = "Users found: {}. Closed pages: {}".format(len(accounts), len([account for account in accounts if account.status == 'closed']))
        self.mainWindow.searchInfoLabel.setText(summaryString)
    
class ResultsList(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.searchResultsWidgets = []
        self.resultsLayout = QVBoxLayout()
        self.setLayout(self.resultsLayout)

    def addItems(self, users):
        self.clearResultsList()

        for user in users:
            widget = SearchResultsItem(self, user)
            self.searchResultsWidgets.append(widget)
            self.resultsLayout.addWidget(widget)

    def clearResultsList(self):
        for widget in self.searchResultsWidgets:
            self.resultsLayout.removeWidget(widget)

        self.searchResultsWidgets = []

class SearchResultsItem(QWidget):
    def __init__(self, parent, userData):
        super().__init__(parent)

        self.accountInfo = userData

        self.textFieldsLayout = QVBoxLayout()
        self.mainLayout = QHBoxLayout()

        self.mainLayout.addLayout(self.textFieldsLayout)

        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        
        self.addPageStatusData()
        self.addNameData()
        self.addAgeData()
        self.addResidenceData()
        self.textFieldsLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.addPhoto()
        self.addPhoto()
        self.addPhoto()

        self.setLayout(self.mainLayout)

    def addPageStatusData(self):
        labelString = "id: <a href='https://vk.com/id{0}'>{0}</a> - {1}".format(self.accountInfo.userId, self.accountInfo.status)

        labelObject = QLabel(labelString)
        labelObject.setOpenExternalLinks(True)
        self.textFieldsLayout.addWidget(labelObject)

    def addNameData(self):
        namePartsList = [self.accountInfo.firstName, self.accountInfo.lastName, self.accountInfo.nickname]
        if namePartsList:
            labelString = ' '.join(namePartsList)
        else:
            labelString = "Name is not available"
        
        labelObject = QLabel(labelString)
        self.textFieldsLayout.addWidget(labelObject)

    def addAgeData(self):
        if self.accountInfo.bdate:
            try:
                bdate = datetime.strptime(self.accountInfo.bdate, "%d.%m.%Y")
            except:
                bdate = datetime.strptime(self.accountInfo.bdate, "%d.%m")
            
            if bdate.year == 1900:
                # When a birth year are hidden
                labelString = bdate.strftime("%d %b")
            else:
                labelString = bdate.strftime("%d %b %Y")

                today = datetime.now()
                # Show user age
                age = today.year - bdate.year
                if (bdate.month, bdate.day) > (today.month, today.day):
                    age -= 1 # hasnt't had birthday this year
                
                labelString += " ({})".format(age)

            labelObject = QLabel(labelString)
            self.textFieldsLayout.addWidget(labelObject)

    def addResidenceData(self):
        residencePartsList = []
        if self.accountInfo.country:
            residencePartsList.append(self.accountInfo.country)
        if self.accountInfo.city:
            residencePartsList.append(self.accountInfo.city)

        if residencePartsList:
            labelString = ', '.join(residencePartsList)            
            labelObject = QLabel(labelString)
            self.textFieldsLayout.addWidget(labelObject)

    def addPhoto(self):
        imageSource = "./images/photo_200.jpg"
        imagePixmap = QPixmap(imageSource, "JPG")
        
        imageLabel = QLabel()
        imageLabel.setPixmap(imagePixmap)
        self.mainLayout.addWidget(imageLabel)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.vkSession = VkApiInteraction()
        
        self.authVkDialog = AuthVkDialog(self)

        self.setWindowTitle('Calisto')

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(SearchVkForm(self))

        self.searchInfoLabel = QLabel("Press \"Search\" button to start searching")
        
        # Search results section
        resultsScrollArea = QScrollArea()
        self.vkSearchResults = ResultsList(self)
        resultsScrollArea.setWidget(self.vkSearchResults)
        resultsScrollArea.setWidgetResizable(True)
        
        searchResultsLayout = QVBoxLayout()
        searchResultsLayout.addWidget(self.searchInfoLabel)
        searchResultsLayout.addWidget(resultsScrollArea)

        mainLayout.addLayout(searchResultsLayout)

        self.mainWidget = QWidget()
        self.mainWidget.setLayout(mainLayout)
        self.setCentralWidget(self.mainWidget)

        self._createMenu()
        self._createStatusBar()
        
    def _createMenu(self):
        self.menu = self.menuBar().addMenu("&Menu")
        self.menu.addAction("&VK Auth", self.authVkDialog.open)
        self.menu.addAction("&Log Out", self.logOutVk)
        self.menu.addAction('&Exit', self.close)

    def _createStatusBar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.updateStatusBar()

    def updateStatusBar(self):
        if self.vkSession.connectionStatus():
            welcomeString = "Hello, {} {}".format(self.vkSession.profileInfo['first_name'], self.vkSession.profileInfo['last_name'])
        else:
            welcomeString = "You are not authorized"

        self.statusBar.showMessage(welcomeString)

    def logOutVk(self):
        self.vkSession.logOut()
        self.updateStatusBar()

        alertMsgBox = QMessageBox()
        alertMsgBox.setWindowTitle("VK Session")
        alertMsgBox.setText("Now, you are not authorized.")
        alertMsgBox.exec()

if __name__ == '__main__':

    
    app = QApplication(sys.argv)

    mainWin = MainWindow()
    mainWin.show()
    
    sys.exit(app.exec())