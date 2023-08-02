import sys
from app.app import App, Root
from PyQt5 import QtWidgets

if __name__ == '__main__':
    application = QtWidgets.QApplication(sys.argv)
    root = Root()
    app = App(root)
    root.show()
    sys.exit(application.exec_())