
from PyQt5.QtWidgets import QDialog

class ImageViewerDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Image Viewer")
        self.resize(500, 300)