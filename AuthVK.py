
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from PyQt5.QtWidgets import QApplication, QCheckBox, QDialog, QDialogButtonBox, QLabel, QMainWindow, QMessageBox, QStatusBar, QVBoxLayout
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLineEdit

import vk_api, json, os

class VkApiInteraction(vk_api.VkApi):
    def prapareApi(self):
        self.api = self.get_api()
        self.profileInfo = self.api.account.getProfileInfo()

    def logOut(self):
        # End session
        vkSession = None

        # Remove access data file
        try:
            os.remove(VK_ACCESS_DATA_FILE)
        except:
            pass
        
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
        # Make new session
        vkSession = VkApiInteraction(login=self.loginField.text(), password=self.pwdField.text(), config_filename=VK_ACCESS_DATA_FILE)

        try:
            vkSession.auth(reauth=False)
            self.close()
        except vk_api.exceptions.AuthError as exception:
            self.showAuthVkWarning(exception.args[-1])
        except vk_api.exceptions.Captcha as exception:
            self.captchaVkDialog.exception = exception
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

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.authVkDialog = AuthVkDialog(self)

        self.setWindowTitle('Calisto')
        self.setFixedSize(500, 500)

        self.mainLabel = QLabel("Main widget")
        self.setCentralWidget(self.mainLabel)

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

        if vkSession.profileInfo:
            welcomeString = "Hello, {} {}".format(vkSession.profileInfo['first_name'], vkSession.profileInfo['last_name'])
        else:
            welcomeString = "You are not authorized"

        self.statusBar.showMessage(welcomeString)

    def logOutVk(self):
        vkSession.logOut()

        alertMsgBox = QMessageBox()
        alertMsgBox.setWindowTitle("VK Session")
        alertMsgBox.setText("Now, you are not authorized.")
        alertMsgBox.exec()

# Function returns first key from VK_ACCESS_FILE if it exist
def getUserLogin(filename):
    try:
        with open(filename, 'r') as f:
            jsondata = json.load(f)
    except (IOError, ValueError):
        return None

    keysList = list(jsondata.keys())

    return keysList[0]

if __name__ == '__main__':

    VK_ACCESS_DATA_FILE = 'accessData.json'

    vkLogin = getUserLogin(VK_ACCESS_DATA_FILE)
        
    vkSession = VkApiInteraction(login=vkLogin, config_filename=VK_ACCESS_DATA_FILE)
    vkSession.profileInfo = {}

    try:
        vkSession.auth()
        vkSession.prapareApi()
    except (vk_api.exceptions.AuthError, vk_api.exceptions.Captcha) as exception:
        print(exception)
    
    app = QApplication(sys.argv)

    mainWin = MainWindow()
    mainWin.show()
    
    sys.exit(app.exec())