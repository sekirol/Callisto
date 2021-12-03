
import sys
from PyQt5.QtCore import QThreadPool, Qt
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

        vkSession.setAuthData(login=self.loginField.text(), password=self.pwdField.text())

        try:
            vkSession.getConnection()
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
        if vkSession.connectionStatus():
            self.countriesList = vkSession.getCountriesList()
            self.countryComoBox.addItems(self.countriesList.keys())
            
            self.countryComoBox.currentTextChanged.connect(self._fillingCityComboBox)

    def _fillingCityComboBox(self):
        countryName = self.countryComoBox.currentText()
        self.citiesComoBox.clear()          # Clear cities combo box
        self.citiesComoBox.addItems([''])   # Add empty item

        if countryName:
            countryId = self.countriesList[countryName]
            self.citiesList = vkSession.getCitiesList(countryId)
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

        usersList = vkSession.getUsers(searchQuery.getQuery())
        
        accounts = []
        for user in usersList:
            userInfo = VkAccountInfo(user)
            accounts.append(userInfo)

        self.showSearchSummary(accounts)
        self.mainWindow.vkSearchResults.addSearchResults(accounts)

        # Show top of results list
        self.scrollingToTopOfList()

    def showSearchSummary(self, accounts):
        summaryString = "Users found: {}. Closed pages: {}".format(len(accounts), len([account for account in accounts if account.status == 'closed']))
        self.mainWindow.searchInfoLabel.setText(summaryString)
    
    def scrollingToTopOfList(self):
        verticalScrollBar = self.mainWindow.resultsScrollArea.verticalScrollBar()
        verticalScrollBar.setValue(verticalScrollBar.minimum())

class ResultsList(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.searchResultsAccounts = []
        self.lastDisplayedAccount = 0
        self.resultsListLength = 10         # TODO Get number of displayed pages from configuration file

        self.searchResultsWidgets = []
        self.resultsLayout = QVBoxLayout()
        self.resultsLayout.setContentsMargins(0, 0, 0, 0)
        self.resultsLayout.setSpacing(0)
        self.setLayout(self.resultsLayout)

        self.expandListButton = QPushButton('Show more')
        self.expandListButton.pressed.connect(self.expandResultsList)

    def addSearchResults(self, users):
        # Remove old serach results
        self.clearResultsList()

        self.searchResultsAccounts = users
        self.displaySearchResultItems()

    def displaySearchResultItems(self):       
        accountFromIndex = self.lastDisplayedAccount
        self.lastDisplayedAccount += self.resultsListLength
        accountToIndex = self.lastDisplayedAccount
        accountsForDisplay = self.searchResultsAccounts[accountFromIndex : accountToIndex]

        for account in accountsForDisplay:
            widget = SearchResultsItem(self, account)
            self.searchResultsWidgets.append(widget)
            self.resultsLayout.addWidget(widget)

        # Place "Show more" button to end of list if search results exist
        if self.searchResultsWidgets and self.lastDisplayedAccount < len(self.searchResultsAccounts):
            self.addExpandListButton()

    def clearResultsList(self):
        # Remove "Show more" button from list if search results exist
        if self.searchResultsWidgets:
            self.removeExpandListButton()
        
        for widget in self.searchResultsWidgets:
            self.resultsLayout.removeWidget(widget)

        self.searchResultsWidgets = []
        self.lastDisplayedAccount = 0

    def addExpandListButton(self):
        self.expandListButton.setVisible(True)
        self.resultsLayout.addWidget(self.expandListButton)

    def removeExpandListButton(self):
        # Before removing the button, it must be hidden
        self.expandListButton.setVisible(False)
        self.resultsLayout.removeWidget(self.expandListButton)

    def expandResultsList(self):
        # Remove button from current list
        self.removeExpandListButton()
        self.displaySearchResultItems()

class SearchResultsItem(QWidget):
    def __init__(self, parent, userData):
        super().__init__(parent)

        self.accountInfo = userData

        self.textFieldsLayout = QVBoxLayout()
        self.mainLayout = QHBoxLayout()

        self.mainLayout.addLayout(self.textFieldsLayout)

        self.mainLayout.setContentsMargins(8, 2, 8, 2)
        self.mainLayout.setSpacing(0)
        
        self.addPageStatusData()
        self.addNameData()
        self.addAgeData()
        self.addResidenceData()
        self.addCountersWidget()
        self.textFieldsLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.addPhoto()

        # Getting counters values in new thread for each widget
        self.getExtendedInformation()

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
        # Place downloaded image
        imageSource = "./images/photo_200_{}.jpg".format(self.accountInfo.userId)   
        if not os.path.exists(imageSource):
            # Place dummy image
            imageSource = "./images/photo_200.jpg"

        imagePixmap = QPixmap(imageSource, "JPG")
        
        imageLabel = QLabel()
        imageLabel.setPixmap(imagePixmap)
        self.mainLayout.addWidget(imageLabel)
        self.mainLayout.setAlignment(imageLabel, Qt.AlignRight)

    def addCountersWidget(self):
        self.countersWidget = VkCountersWidget(self)
        self.countersWidget.setVisible(False)
        
        self.textFieldsLayout.addWidget(self.countersWidget)

    def showCountersData(self):
        self.countersWidget.updateData(self.accountInfo.counters)
        self.countersWidget.setVisible(True)
    
    # Gets more information for new account widget
    def getExtendedInformation(self):
        
        self.thread = QThread()

        self.apiQuery = VkApiQuery(vkSession, self.accountInfo)
        self.apiQuery.moveToThread(self.thread)

        # Running thread will start API query
        self.thread.started.connect(self.apiQuery.run)
        # When interaction with server finishes, the quit signal will be started
        self.apiQuery.finished.connect(self.thread.quit)        
        # Handler object marks himself for delete after end of work
        self.apiQuery.finished.connect(self.apiQuery.deleteLater)
        # Thread marks himself for delete after stop of thread
        self.thread.finished.connect(self.thread.deleteLater)
        # Display new information
        self.apiQuery.finished.connect(self.showCountersData)

        self.thread.start()

class VkCountersWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

    def updateData(self, counters):
        counterLabels = [{"friends":"Друзья"}, {"online_friends":"Онлайн"}, {"followers":"Подписчики"}, 
                         {"subscriptions":"Подписки"}, {"groups":"Группы"}, {"pages":"Интересно"},
                         {"gifts":"Подарки"}, {"videos":"Видео"}, {"clips":"Клипы"}, {"audios":"Музыка"},
                         {"photos":"Фотографии"}, {"albums":"Альбомы"}, {"user_photos":"Отмечен"}]

        labelWidgets = []
        for counter in counterLabels:
            counterName, counterLabel = list(counter.items())[0]
            if counters.get(counterName):
                counterInfoText = "{}: {}".format(counterLabel, counters[counterName])
                labelWidgets.append(QLabel(counterInfoText))
        
        LABELS_IN_ROW = 4

        row = 0
        col = 0
        for item in labelWidgets:
            self.layout.addWidget(item, row, col)
            col += 1
            if col >= LABELS_IN_ROW:
                col = 0
                row += 1

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.authVkDialog = AuthVkDialog(self)

        self.setWindowTitle('Calisto')

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(SearchVkForm(self))

        self.searchInfoLabel = QLabel("Press \"Search\" button to start searching")
        
        # Search results section
        self.resultsScrollArea = QScrollArea()
        self.vkSearchResults = ResultsList(self)
        self.resultsScrollArea.setWidget(self.vkSearchResults)
        self.resultsScrollArea.setWidgetResizable(True)
        self.resultsScrollArea.setMinimumWidth(900)

        searchResultsLayout = QVBoxLayout()
        searchResultsLayout.addWidget(self.searchInfoLabel)
        searchResultsLayout.addWidget(self.resultsScrollArea)

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
        if vkSession.connectionStatus():
            welcomeString = "Hello, {} {}".format(vkSession.profileInfo['first_name'], vkSession.profileInfo['last_name'])
        else:
            welcomeString = "You are not authorized"

        self.statusBar.showMessage(welcomeString)

    def logOutVk(self):
        vkSession.logOut()
        self.updateStatusBar()

        alertMsgBox = QMessageBox()
        alertMsgBox.setWindowTitle("VK Session")
        alertMsgBox.setText("Now, you are not authorized.")
        alertMsgBox.exec()

if __name__ == '__main__':

    vkSession = VkApiInteraction()
    
    app = QApplication(sys.argv)

    mainWin = MainWindow()
    mainWin.show()
    
    sys.exit(app.exec())