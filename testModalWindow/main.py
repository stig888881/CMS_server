from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5.QtWidgets import (QMainWindow, QAction, qApp, QApplication,
                             QWidget, QDialog)
from PyQt5.QtGui import QIcon


# окно диалога создания новой сессии
class PreDialog(QDialog):
    def __init__(self, parent=None):                      # + parent
        super(PreDialog,self).__init__(parent)            #
        self.parent = parent                              #

        self.setWindowTitle('Host Parameters')
        self.setModal(True)
        self.line_host = QtWidgets.QLineEdit()
        self.line_user = QtWidgets.QLineEdit()
        self.line_pass = QtWidgets.QLineEdit()
        self.line_pass.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.connect = QtWidgets.QPushButton("connect")
        self.spinBox_port = QtWidgets.QSpinBox()
        self.spinBox_port.setProperty("value", 22)
        self.hbox = QtWidgets.QHBoxLayout()
        self.ssh_radio = QtWidgets.QRadioButton("SSH")
        self.telnet_radio = QtWidgets.QRadioButton("Telnet")

        self.hbox.addWidget(self.ssh_radio)
        self.hbox.addWidget(self.telnet_radio)

        self.form = QtWidgets.QFormLayout()
        self.form.setSpacing(20)

        self.form.addRow("&Host:",self.line_host)
        self.form.addRow("&User:",self.line_user)
        self.form.addRow("&Password:",self.line_pass)
        self.form.addRow("&Port:",self.spinBox_port)
        self.form.addRow("Session:",self.hbox)
        self.form.addRow(self.connect)

        self.setLayout(self.form)

    def closeEvent(self, event):                            # +++
        self.parent.show()


class CentralWidget(QWidget):
    def __init__(self, parent=None):                        # + parent
        super(CentralWidget, self).__init__(parent)         #
        self.parent = parent                                #

        self.label = QtWidgets.QLabel("<center>Hello, PyQt5!</center>")
        self.btnQuit = QtWidgets.QPushButton("&Открыть диалоговое окно")
        self.btnQuit.clicked.connect(self.createDialog)
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.btnQuit)
        self.setLayout(self.vbox)

    def createDialog(self):
#        self.dialog = PreDialog(self)
        self.dialog = PreDialog(self.parent)
        self.dialog.show()

    def stopDialog(self):
        self.dialog.destroy()


# класс главного окна
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network monitor")
        self.resize(900,600)


        # инициализация центрального виджета
#        self.centrWidg = self.CentralWidget()
        self.centrWidg = CentralWidget(self)                   # + self
        self.setCentralWidget(self.centrWidg)

        # Поле менюбара
        # вызывается по нажатию клавиш Ctrl+N
        # при нажатии вызывается функция создания диалогового окна PreDialog
        exitAction = QAction(QIcon('open.png'), 'New &Session', self)
        exitAction.setShortcut('Ctrl+N')
        exitAction.setStatusTip('Create the new Session')
        exitAction.triggered.connect(self.centrWidg.createDialog)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Session')
        fileMenu.addAction(exitAction)

        self.setGeometry(300, 300, 300, 200)

# -        self.show()
        self.centrWidg.createDialog()                             # +++


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
# -   window.show()

    sys.exit(app.exec_())
