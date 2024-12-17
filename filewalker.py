import sys
import os
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QFileDialog

extensions = [".cs", ".cshtml"]

class FileWalkerThread(QThread):
    # Define a signal to send file names to the main thread
    file_found = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def run(self):
        # Walk through the directory and emit each file name
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith(tuple(extensions)):
                    full_path = os.path.join(root, file)
                    self.file_found.emit(full_path)
        self.finished.emit()


class FileWalkerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('File Walker')
        self.setGeometry(100, 100, 600, 400)

        # Create a QTextEdit to display file names
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)

        # Button to start the file-walking process
        self.start_button = QPushButton('Select Directory and Start', self)
        self.start_button.clicked.connect(self.start_walking)

        # Layout to arrange widgets
        layout = QVBoxLayout()
        layout.addWidget(self.text_area)
        layout.addWidget(self.start_button)
        self.setLayout(layout)

    def start_walking(self):
        # Open a directory selection dialog
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if directory:
            self.text_area.append(f"Scanning directory: {directory}\n")
            # Initialize and start the file walker thread
            self.thread = FileWalkerThread(directory)
            self.thread.file_found.connect(self.append_file)
            self.thread.finished.connect(self.scan_finished)
            self.thread.start()

    def append_file(self, file_path):
        # Append the file path to the text area
        self.text_area.append(file_path)

    def scan_finished(self):
        # Notify when the scan is complete
        self.text_area.append("\nScan Complete!")

    def closeEvent(self, event):
        # Ensure the thread is stopped properly when closing the window
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileWalkerApp()
    window.show()
    sys.exit(app.exec_())
