# -*- coding: utf-8 -*-

"""
Created on sep 8, 2022

Modified on , 2022

@author: hilee
"""

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from ui_dcs_sub import *

import time as ti

class SaveAsDlg(Ui_Dialog, QDialog):

    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Save As...")

        thatday = ti.strftime("%04Y%02m%02d", ti.localtime())
        self.e_user_file.setText(thatday)

        self.btn_find_user_dir.clicked.connect(lambda: self.find_dir())
        self.btn_save.clicked.connect(self.copy_fits)

        self.buttonBox.accepted.connect(self.exit)
        self.buttonBox.rejected.connect(self.reject)
        

    
    def closeEvent(self, event: QCloseEvent) -> None:

        return super().closeEvent(event)


    def showModal(self):
        return super().exec()

    
    def find_dir(self):
        loader = self.e_user_dir.text()
        folder = QFileDialog.getExistingDirectory(self, "select Directory", loader)
        if folder:
            self.e_user_dir.setText(folder)


    def copy_fits(self):
        # copy
        pass


    def exit(self):
        print("ok")
        self.accept()


  
    



