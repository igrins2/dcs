# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dcs_subCokUrH.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QLabel, QLineEdit, QSizePolicy, QToolButton,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(464, 136)
        self.label_27 = QLabel(Dialog)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setGeometry(QRect(10, 19, 81, 21))
        self.label_27.setLayoutDirection(Qt.LeftToRight)
        self.label_27.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_user_dir = QLineEdit(Dialog)
        self.e_user_dir.setObjectName(u"e_user_dir")
        self.e_user_dir.setGeometry(QRect(100, 20, 231, 23))
        self.label_28 = QLabel(Dialog)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setGeometry(QRect(330, 50, 31, 21))
        self.label_28.setLayoutDirection(Qt.LeftToRight)
        self.label_28.setAlignment(Qt.AlignCenter)
        self.btn_find_user_dir = QToolButton(Dialog)
        self.btn_find_user_dir.setObjectName(u"btn_find_user_dir")
        self.btn_find_user_dir.setGeometry(QRect(330, 20, 28, 23))
        self.e_user_file = QLineEdit(Dialog)
        self.e_user_file.setObjectName(u"e_user_file")
        self.e_user_file.setGeometry(QRect(100, 50, 231, 23))
        self.e_user_file.setAlignment(Qt.AlignCenter)
        self.btn_save = QToolButton(Dialog)
        self.btn_save.setObjectName(u"btn_save")
        self.btn_save.setGeometry(QRect(370, 20, 71, 51))
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(270, 90, 166, 27))
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.label_29 = QLabel(Dialog)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setGeometry(QRect(10, 50, 81, 21))
        self.label_29.setLayoutDirection(Qt.LeftToRight)
        self.label_29.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Save As", None))
        self.label_27.setText(QCoreApplication.translate("Dialog", u"Directory:", None))
        self.e_user_dir.setText(QCoreApplication.translate("Dialog", u"/home/dcs", None))
        self.label_28.setText(QCoreApplication.translate("Dialog", u".fits", None))
        self.btn_find_user_dir.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.e_user_file.setText(QCoreApplication.translate("Dialog", u"name", None))
        self.btn_save.setText(QCoreApplication.translate("Dialog", u"save", None))
        self.label_29.setText(QCoreApplication.translate("Dialog", u"Filename:", None))
    # retranslateUi

