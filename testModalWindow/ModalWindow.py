from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QTableWidgetItem
import design
import Modal

class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self, parent=None):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super(ExampleApp,self).__init__(parent)
        self.parent=parent
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.pushButton_4.clicked.connect(self.createDialog)

    def createDialog(self):
            #        self.dialog = PreDialog(self)
        self.dialog = ModalWindow(self.parent)
        self.dialog.show()

class ModalWindow(QtWidgets.QMainWindow, Modal.Ui_Form):
    def __init__(self, parent=None):
        # Это здесь нужно для доступа к переменным, методам
         # и т.д. в файле design.py
        super(ModalWindow,self).__init__(parent)
        self.parent = parent
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()

    sys.exit(app.exec_())