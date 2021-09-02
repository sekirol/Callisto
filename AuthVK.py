
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from PyQt5.QtWidgets import QApplication, QCheckBox, QComboBox, QDateEdit, QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QSpinBox, QStatusBar, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLineEdit

import vk_api, json, os

class VkApiInteraction():
    def __init__(self):

        self.login = None
        self.password = None
        self.connection = False

        self.setAuthData(login=self._getUserLogin(filename=VK_ACCESS_DATA_FILE))
        
        try:
            self.getConnection()
        except vk_api.exceptions.AuthError as connectException:
            print(connectException)
        except vk_api.exceptions.Captcha as connectException:
            print(connectException)

        if self.connection:
            self.api = self.session.get_api()
            self.profileInfo = self.api.account.getProfileInfo()

    # Function returns first key from VK_ACCESS_FILE if it exist
    def _getUserLogin(self, filename):

        try:
            with open(filename, 'r') as f:
                jsondata = json.load(f)
        except (IOError, ValueError):
            return None

        keysList = list(jsondata.keys())

        return keysList[0]

    def logOut(self):
        # End session
        self.session = None

        # Remove access data file
        try:
            os.remove(VK_ACCESS_DATA_FILE)
        except:
            pass

    def getConnection(self):
        self.session.auth()
        self.connection = True
    
    def setAuthData(self, login=None, password=None):
        self.login = login
        self.password = password

        self.session = vk_api.VkApi(login=login, password=password, config_filename=VK_ACCESS_DATA_FILE)

    def connectionStatus(self):
        return self.connection
        
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
        
        self.setFixedWidth(200)

        self.searchQueryField = QLineEdit()
        self.sexComoBox = QComboBox()
        self.birthDateField = QDateEdit()
        self.ageFromField = QSpinBox()
        self.ageToField = QSpinBox()
        self.countryComoBox = QComboBox()
        self.cityComoBox = QComboBox()      

        self.searchFormLayout = QVBoxLayout()
        
        self.createSearchFields()

        self.setLayout(self.searchFormLayout)
    
        self._fillingCountryComboBox()
        # Fills only after country selecting
        self._fillingCityComboBox()

    def createSearchFields(self):
        # Search query section
        self.searchFormLayout.addWidget(QLabel("Search query:"))
        self.searchFormLayout.addWidget(self.searchQueryField)
        # Selection sex section
        self.sexComoBox.addItems(["Any", "Man", "Woman"])
        self.searchFormLayout.addWidget(QLabel("Sex:"))
        self.searchFormLayout.addWidget(self.sexComoBox)
        # Birth date section
        self.searchFormLayout.addWidget(QLabel("Birth date:"))
        self.searchFormLayout.addWidget(self.birthDateField) 
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
        self.searchFormLayout.addWidget(self.cityComoBox)

        self.searchFormLayout.addStretch()

    def _fillingCountryComboBox(self):
        self.countryComoBox.addItems(["Russia", "Ukraine", "Belarus"])

    def _fillingCityComboBox(self):
        self.cityComoBox.addItems(["Saint-Petersburg", "Moscow"])

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.vkSession = VkApiInteraction()
        
        self.authVkDialog = AuthVkDialog(self)

        self.setWindowTitle('Calisto')

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(SearchVkForm(self))
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

        if self.vkSession.connectionStatus():
            welcomeString = "Hello, {} {}".format(self.vkSession.profileInfo['first_name'], self.vkSession.profileInfo['last_name'])
        else:
            welcomeString = "You are not authorized"

        self.statusBar.showMessage(welcomeString)

    def logOutVk(self):
        self.vkSession.logOut()

        alertMsgBox = QMessageBox()
        alertMsgBox.setWindowTitle("VK Session")
        alertMsgBox.setText("Now, you are not authorized.")
        alertMsgBox.exec()

if __name__ == '__main__':

    VK_ACCESS_DATA_FILE = 'accessData.json'

    app = QApplication(sys.argv)

    mainWin = MainWindow()
    mainWin.show()
    
    sys.exit(app.exec())