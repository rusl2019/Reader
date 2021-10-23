from PyQt5 import uic
from PyQt5.QtWidgets import (QApplication, QFileDialog, QLabel, QLineEdit,
                             QMainWindow, QPushButton, QSpinBox)
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import sys, os, time


class Worker(QObject):

    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, file, wpm):

        super().__init__()
        self.file = file
        self.wpm = wpm

    def run(self):

        t_wait = 60 / self.wpm

        f = open(self.file, "r")
        for line in f:
            for word in line.split():
                time.sleep(t_wait)
                self.progress.emit(word)
        self.finished.emit()
        f.close()


class UI(QMainWindow):

    def __init__(self):

        super(UI, self).__init__()

        uic.loadUi("reader.ui", self)

        self.file = f"{os.getcwd()}/sample/text.txt"

        self.prev_path = self.findChild(QLineEdit, "lineEdit")
        self.select_file = self.findChild(QPushButton, "pushButton_4")
        self.wpm = self.findChild(QSpinBox, "spinBox")
        self.dis_text = self.findChild(QLabel, "label_4")
        self.run = self.findChild(QPushButton, "pushButton")
        self.quit = self.findChild(QPushButton, "pushButton_2")

        self.select_file.clicked.connect(self.get_file)
        self.run.clicked.connect(self.running)
        self.quit.clicked.connect(QApplication.instance().quit)

        self.show()

    def reportProgress(self, word):

        self.dis_text.setText(word)

    def running(self):

        self.thread = QThread()
        self.worker = Worker(self.file, wpm=self.wpm.value())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.thread.start()

        self.run.setEnabled(False)
        self.thread.finished.connect(lambda: self.run.setEnabled(True))
        self.thread.finished.connect(lambda: self.dis_text.setText("Done !!!"))

    def get_file(self):

        self.file = QFileDialog.getOpenFileName(self, "Select File",
                                                os.getcwd(),
                                                "Text file (*.txt)")
        self.prev_path.clear()
        self.prev_path.setText(self.file[0])
        self.prev_path.isReadOnly()
        self.file = self.file[0]


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = UI()
    app.exec_()
