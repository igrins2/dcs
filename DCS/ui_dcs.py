# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dcsCVvajI.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGroupBox, QLabel, QLineEdit, QMainWindow,
    QProgressBar, QPushButton, QRadioButton, QSizePolicy,
    QStatusBar, QToolButton, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1129, 556)
        MainWindow.setAutoFillBackground(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(20, 20, 561, 111))
        self.btn_error_cnt = QPushButton(self.groupBox)
        self.btn_error_cnt.setObjectName(u"btn_error_cnt")
        self.btn_error_cnt.setGeometry(QRect(460, 60, 91, 41))
        self.label_ver = QLabel(self.groupBox)
        self.label_ver.setObjectName(u"label_ver")
        self.label_ver.setGeometry(QRect(110, 30, 41, 21))
        self.e_timeout = QLineEdit(self.groupBox)
        self.e_timeout.setObjectName(u"e_timeout")
        self.e_timeout.setGeometry(QRect(310, 30, 41, 23))
        self.e_timeout.setAlignment(Qt.AlignCenter)
        self.btn_reset = QPushButton(self.groupBox)
        self.btn_reset.setObjectName(u"btn_reset")
        self.btn_reset.setGeometry(QRect(180, 60, 51, 41))
        self.btn_initialize1 = QPushButton(self.groupBox)
        self.btn_initialize1.setObjectName(u"btn_initialize1")
        self.btn_initialize1.setGeometry(QRect(10, 60, 71, 41))
        self.cmb_ouput_channels = QComboBox(self.groupBox)
        self.cmb_ouput_channels.addItem("")
        self.cmb_ouput_channels.addItem("")
        self.cmb_ouput_channels.addItem("")
        self.cmb_ouput_channels.setObjectName(u"cmb_ouput_channels")
        self.cmb_ouput_channels.setGeometry(QRect(500, 30, 51, 23))
        self.cmb_ouput_channels.setLayoutDirection(Qt.LeftToRight)
        self.btn_download_MCD = QPushButton(self.groupBox)
        self.btn_download_MCD.setObjectName(u"btn_download_MCD")
        self.btn_download_MCD.setGeometry(QRect(240, 60, 111, 41))
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(370, 30, 121, 21))
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(60, 30, 41, 21))
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(150, 30, 151, 21))
        self.label_3.setLayoutDirection(Qt.LeftToRight)
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.btn_initialize2 = QPushButton(self.groupBox)
        self.btn_initialize2.setObjectName(u"btn_initialize2")
        self.btn_initialize2.setGeometry(QRect(90, 60, 81, 41))
        self.btn_set_detector = QPushButton(self.groupBox)
        self.btn_set_detector.setObjectName(u"btn_set_detector")
        self.btn_set_detector.setGeometry(QRect(360, 60, 91, 41))
        self.label_connection_sts = QLabel(self.groupBox)
        self.label_connection_sts.setObjectName(u"label_connection_sts")
        self.label_connection_sts.setGeometry(QRect(10, 30, 31, 21))
        self.label_connection_sts.setLayoutDirection(Qt.LeftToRight)
        self.label_connection_sts.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(620, 70, 491, 171))
        self.label_22 = QLabel(self.groupBox_2)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setGeometry(QRect(10, 70, 171, 21))
        self.label_22.setLayoutDirection(Qt.LeftToRight)
        self.label_22.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.btn_find_MACIE_reg = QToolButton(self.groupBox_2)
        self.btn_find_MACIE_reg.setObjectName(u"btn_find_MACIE_reg")
        self.btn_find_MACIE_reg.setGeometry(QRect(450, 70, 28, 23))
        self.e_MACIE_reg = QLineEdit(self.groupBox_2)
        self.e_MACIE_reg.setObjectName(u"e_MACIE_reg")
        self.e_MACIE_reg.setGeometry(QRect(190, 70, 261, 23))
        self.btn_find_config_dir = QToolButton(self.groupBox_2)
        self.btn_find_config_dir.setObjectName(u"btn_find_config_dir")
        self.btn_find_config_dir.setGeometry(QRect(450, 40, 28, 23))
        self.label_23 = QLabel(self.groupBox_2)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setGeometry(QRect(10, 40, 171, 21))
        self.label_23.setLayoutDirection(Qt.LeftToRight)
        self.label_23.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_config_dir = QLineEdit(self.groupBox_2)
        self.e_config_dir.setObjectName(u"e_config_dir")
        self.e_config_dir.setGeometry(QRect(190, 40, 261, 23))
        font = QFont()
        font.setPointSize(10)
        self.e_config_dir.setFont(font)
        self.btn_find_ASIC_firware = QToolButton(self.groupBox_2)
        self.btn_find_ASIC_firware.setObjectName(u"btn_find_ASIC_firware")
        self.btn_find_ASIC_firware.setGeometry(QRect(450, 100, 28, 23))
        self.label_24 = QLabel(self.groupBox_2)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setGeometry(QRect(10, 100, 171, 21))
        self.label_24.setLayoutDirection(Qt.LeftToRight)
        self.label_24.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_ASIC_firmware = QLineEdit(self.groupBox_2)
        self.e_ASIC_firmware.setObjectName(u"e_ASIC_firmware")
        self.e_ASIC_firmware.setGeometry(QRect(190, 100, 261, 23))
        self.label_25 = QLabel(self.groupBox_2)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setGeometry(QRect(10, 130, 171, 21))
        self.label_25.setLayoutDirection(Qt.LeftToRight)
        self.label_25.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_img_dir = QLineEdit(self.groupBox_2)
        self.e_img_dir.setObjectName(u"e_img_dir")
        self.e_img_dir.setGeometry(QRect(190, 130, 261, 23))
        self.btn_find_img_dir = QToolButton(self.groupBox_2)
        self.btn_find_img_dir.setObjectName(u"btn_find_img_dir")
        self.btn_find_img_dir.setGeometry(QRect(450, 130, 28, 23))
        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(20, 140, 131, 201))
        self.radio_UTR = QRadioButton(self.groupBox_3)
        self.radio_UTR.setObjectName(u"radio_UTR")
        self.radio_UTR.setGeometry(QRect(10, 40, 111, 21))
        self.radio_CDS = QRadioButton(self.groupBox_3)
        self.radio_CDS.setObjectName(u"radio_CDS")
        self.radio_CDS.setGeometry(QRect(10, 80, 100, 21))
        self.radio_CDSNoise = QRadioButton(self.groupBox_3)
        self.radio_CDSNoise.setObjectName(u"radio_CDSNoise")
        self.radio_CDSNoise.setGeometry(QRect(10, 120, 100, 21))
        self.radio_Fowler = QRadioButton(self.groupBox_3)
        self.radio_Fowler.setObjectName(u"radio_Fowler")
        self.radio_Fowler.setGeometry(QRect(10, 160, 100, 21))
        self.groupBox_4 = QGroupBox(self.centralwidget)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setGeometry(QRect(160, 140, 291, 151))
        self.e_reads = QLineEdit(self.groupBox_4)
        self.e_reads.setObjectName(u"e_reads")
        self.e_reads.setGeometry(QRect(90, 50, 41, 23))
        self.e_reads.setFont(font)
        self.e_reads.setAlignment(Qt.AlignCenter)
        self.e_reads.setReadOnly(True)
        self.e_resets = QLineEdit(self.groupBox_4)
        self.e_resets.setObjectName(u"e_resets")
        self.e_resets.setGeometry(QRect(40, 50, 41, 23))
        self.e_resets.setFont(font)
        self.e_resets.setAlignment(Qt.AlignCenter)
        self.e_groups = QLineEdit(self.groupBox_4)
        self.e_groups.setObjectName(u"e_groups")
        self.e_groups.setGeometry(QRect(140, 50, 41, 23))
        self.e_groups.setFont(font)
        self.e_groups.setAlignment(Qt.AlignCenter)
        self.e_groups.setReadOnly(True)
        self.e_drops = QLineEdit(self.groupBox_4)
        self.e_drops.setObjectName(u"e_drops")
        self.e_drops.setGeometry(QRect(190, 50, 41, 23))
        self.e_drops.setFont(font)
        self.e_drops.setAlignment(Qt.AlignCenter)
        self.e_drops.setReadOnly(True)
        self.e_ramps = QLineEdit(self.groupBox_4)
        self.e_ramps.setObjectName(u"e_ramps")
        self.e_ramps.setGeometry(QRect(240, 50, 41, 23))
        self.e_ramps.setFont(font)
        self.e_ramps.setAlignment(Qt.AlignCenter)
        self.e_ramps.setReadOnly(True)
        self.btn_set_param = QPushButton(self.groupBox_4)
        self.btn_set_param.setObjectName(u"btn_set_param")
        self.btn_set_param.setGeometry(QRect(200, 90, 81, 51))
        self.e_fowler_number = QLineEdit(self.groupBox_4)
        self.e_fowler_number.setObjectName(u"e_fowler_number")
        self.e_fowler_number.setGeometry(QRect(130, 120, 61, 23))
        self.e_fowler_number.setAlignment(Qt.AlignCenter)
        self.e_exp_time = QLineEdit(self.groupBox_4)
        self.e_exp_time.setObjectName(u"e_exp_time")
        self.e_exp_time.setGeometry(QRect(130, 90, 61, 23))
        self.e_exp_time.setAlignment(Qt.AlignCenter)
        self.label_fowler_number = QLabel(self.groupBox_4)
        self.label_fowler_number.setObjectName(u"label_fowler_number")
        self.label_fowler_number.setGeometry(QRect(30, 120, 91, 21))
        self.label_fowler_number.setLayoutDirection(Qt.LeftToRight)
        self.label_fowler_number.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_13 = QLabel(self.groupBox_4)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(30, 90, 91, 21))
        self.label_13.setLayoutDirection(Qt.LeftToRight)
        self.label_13.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_19 = QLabel(self.groupBox_4)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setGeometry(QRect(35, 30, 51, 21))
        self.label_19.setFont(font)
        self.label_19.setLayoutDirection(Qt.LeftToRight)
        self.label_19.setAlignment(Qt.AlignCenter)
        self.label_20 = QLabel(self.groupBox_4)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setGeometry(QRect(84, 30, 51, 21))
        self.label_20.setFont(font)
        self.label_20.setLayoutDirection(Qt.LeftToRight)
        self.label_20.setAlignment(Qt.AlignCenter)
        self.label_groups = QLabel(self.groupBox_4)
        self.label_groups.setObjectName(u"label_groups")
        self.label_groups.setGeometry(QRect(135, 30, 51, 21))
        self.label_groups.setFont(font)
        self.label_groups.setLayoutDirection(Qt.LeftToRight)
        self.label_groups.setAlignment(Qt.AlignCenter)
        self.label_drops = QLabel(self.groupBox_4)
        self.label_drops.setObjectName(u"label_drops")
        self.label_drops.setGeometry(QRect(185, 30, 51, 21))
        self.label_drops.setFont(font)
        self.label_drops.setLayoutDirection(Qt.LeftToRight)
        self.label_drops.setAlignment(Qt.AlignCenter)
        self.label_ramps = QLabel(self.groupBox_4)
        self.label_ramps.setObjectName(u"label_ramps")
        self.label_ramps.setGeometry(QRect(235, 30, 51, 21))
        self.label_ramps.setFont(font)
        self.label_ramps.setLayoutDirection(Qt.LeftToRight)
        self.label_ramps.setAlignment(Qt.AlignCenter)
        self.groupBox_5 = QGroupBox(self.centralwidget)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.groupBox_5.setGeometry(QRect(460, 140, 121, 201))
        self.chk_ROI_mode = QCheckBox(self.groupBox_5)
        self.chk_ROI_mode.setObjectName(u"chk_ROI_mode")
        self.chk_ROI_mode.setGeometry(QRect(20, 35, 85, 21))
        self.label_10 = QLabel(self.groupBox_5)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(10, 160, 51, 21))
        self.label_10.setLayoutDirection(Qt.LeftToRight)
        self.label_10.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_x_stop = QLineEdit(self.groupBox_5)
        self.e_x_stop.setObjectName(u"e_x_stop")
        self.e_x_stop.setGeometry(QRect(70, 100, 41, 23))
        self.e_x_stop.setAlignment(Qt.AlignCenter)
        self.label_11 = QLabel(self.groupBox_5)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(10, 130, 51, 21))
        self.label_11.setLayoutDirection(Qt.LeftToRight)
        self.label_11.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_12 = QLabel(self.groupBox_5)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(10, 100, 51, 21))
        self.label_12.setLayoutDirection(Qt.LeftToRight)
        self.label_12.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_14 = QLabel(self.groupBox_5)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setGeometry(QRect(10, 70, 51, 21))
        self.label_14.setLayoutDirection(Qt.LeftToRight)
        self.label_14.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_y_stop = QLineEdit(self.groupBox_5)
        self.e_y_stop.setObjectName(u"e_y_stop")
        self.e_y_stop.setGeometry(QRect(70, 160, 41, 23))
        self.e_y_stop.setAlignment(Qt.AlignCenter)
        self.e_y_start = QLineEdit(self.groupBox_5)
        self.e_y_start.setObjectName(u"e_y_start")
        self.e_y_start.setGeometry(QRect(70, 130, 41, 23))
        self.e_y_start.setAlignment(Qt.AlignCenter)
        self.e_x_start = QLineEdit(self.groupBox_5)
        self.e_x_start.setObjectName(u"e_x_start")
        self.e_x_start.setGeometry(QRect(70, 70, 41, 23))
        self.e_x_start.setAlignment(Qt.AlignCenter)
        self.label_16 = QLabel(self.centralwidget)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setGeometry(QRect(160, 310, 61, 21))
        self.label_16.setLayoutDirection(Qt.LeftToRight)
        self.label_16.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_repeat = QLineEdit(self.centralwidget)
        self.e_repeat.setObjectName(u"e_repeat")
        self.e_repeat.setGeometry(QRect(230, 310, 41, 23))
        self.e_repeat.setAlignment(Qt.AlignCenter)
        self.btn_stop = QPushButton(self.centralwidget)
        self.btn_stop.setObjectName(u"btn_stop")
        self.btn_stop.setGeometry(QRect(390, 300, 51, 41))
        self.btn_acquireramp = QPushButton(self.centralwidget)
        self.btn_acquireramp.setObjectName(u"btn_acquireramp")
        self.btn_acquireramp.setGeometry(QRect(280, 300, 101, 41))
        self.btn_get_telemetry = QPushButton(self.centralwidget)
        self.btn_get_telemetry.setObjectName(u"btn_get_telemetry")
        self.btn_get_telemetry.setGeometry(QRect(20, 490, 101, 41))
        self.groupBox_6 = QGroupBox(self.centralwidget)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.groupBox_6.setGeometry(QRect(20, 350, 561, 121))
        self.label_18 = QLabel(self.groupBox_6)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setGeometry(QRect(10, 30, 181, 21))
        self.label_18.setLayoutDirection(Qt.LeftToRight)
        self.label_18.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_measured_time = QLabel(self.groupBox_6)
        self.label_measured_time.setObjectName(u"label_measured_time")
        self.label_measured_time.setGeometry(QRect(200, 61, 81, 21))
        self.label_17 = QLabel(self.groupBox_6)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setGeometry(QRect(10, 60, 181, 21))
        self.label_17.setLayoutDirection(Qt.LeftToRight)
        self.label_17.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_calculated_time = QLabel(self.groupBox_6)
        self.label_calculated_time.setObjectName(u"label_calculated_time")
        self.label_calculated_time.setGeometry(QRect(200, 32, 81, 21))
        self.prog_sts = QProgressBar(self.groupBox_6)
        self.prog_sts.setObjectName(u"prog_sts")
        self.prog_sts.setGeometry(QRect(20, 90, 521, 23))
        self.prog_sts.setValue(24)
        self.label_21 = QLabel(self.groupBox_6)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setGeometry(QRect(290, 30, 191, 21))
        self.label_21.setLayoutDirection(Qt.LeftToRight)
        self.label_21.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.cmb_combine_line = QComboBox(self.groupBox_6)
        self.cmb_combine_line.addItem("")
        self.cmb_combine_line.addItem("")
        self.cmb_combine_line.addItem("")
        self.cmb_combine_line.setObjectName(u"cmb_combine_line")
        self.cmb_combine_line.setGeometry(QRect(490, 30, 51, 23))
        self.cmb_combine_line.setLayoutDirection(Qt.LeftToRight)
        self.chk_show_fits = QCheckBox(self.groupBox_6)
        self.chk_show_fits.setObjectName(u"chk_show_fits")
        self.chk_show_fits.setGeometry(QRect(450, 60, 91, 21))
        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(590, 40, 21, 471))
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(620, 30, 151, 41))
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(14)
        font1.setBold(True)
        self.label_2.setFont(font1)
        self.groupBox_9 = QGroupBox(self.centralwidget)
        self.groupBox_9.setObjectName(u"groupBox_9")
        self.groupBox_9.setGeometry(QRect(620, 250, 491, 221))
        self.e_addr_Vreset = QLineEdit(self.groupBox_9)
        self.e_addr_Vreset.setObjectName(u"e_addr_Vreset")
        self.e_addr_Vreset.setGeometry(QRect(130, 60, 51, 23))
        self.e_addr_Vreset.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_addr_Vreset.setReadOnly(True)
        self.e_addr_Dsub = QLineEdit(self.groupBox_9)
        self.e_addr_Dsub.setObjectName(u"e_addr_Dsub")
        self.e_addr_Dsub.setGeometry(QRect(130, 90, 51, 23))
        self.e_addr_Dsub.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_addr_Dsub.setReadOnly(True)
        self.e_addr_Vbiasgate = QLineEdit(self.groupBox_9)
        self.e_addr_Vbiasgate.setObjectName(u"e_addr_Vbiasgate")
        self.e_addr_Vbiasgate.setGeometry(QRect(130, 120, 51, 23))
        self.e_addr_Vbiasgate.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_addr_Vbiasgate.setReadOnly(True)
        self.e_addr_Vrefmain = QLineEdit(self.groupBox_9)
        self.e_addr_Vrefmain.setObjectName(u"e_addr_Vrefmain")
        self.e_addr_Vrefmain.setGeometry(QRect(130, 150, 51, 23))
        self.e_addr_Vrefmain.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_addr_Vrefmain.setReadOnly(True)
        self.label_5 = QLabel(self.groupBox_9)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(128, 40, 56, 12))
        self.label_6 = QLabel(self.groupBox_9)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(20, 60, 101, 20))
        self.label_6.setLayoutDirection(Qt.LeftToRight)
        self.label_6.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_7 = QLabel(self.groupBox_9)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(20, 90, 101, 20))
        self.label_7.setLayoutDirection(Qt.LeftToRight)
        self.label_7.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_8 = QLabel(self.groupBox_9)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(20, 120, 101, 20))
        self.label_8.setLayoutDirection(Qt.LeftToRight)
        self.label_8.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_9 = QLabel(self.groupBox_9)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(20, 150, 101, 20))
        self.label_9.setLayoutDirection(Qt.LeftToRight)
        self.label_9.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_write_Dsub = QLineEdit(self.groupBox_9)
        self.e_write_Dsub.setObjectName(u"e_write_Dsub")
        self.e_write_Dsub.setGeometry(QRect(190, 90, 51, 23))
        self.e_write_Dsub.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_write_Vbiasgate = QLineEdit(self.groupBox_9)
        self.e_write_Vbiasgate.setObjectName(u"e_write_Vbiasgate")
        self.e_write_Vbiasgate.setGeometry(QRect(190, 120, 51, 23))
        self.e_write_Vbiasgate.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_write_Vrefmain = QLineEdit(self.groupBox_9)
        self.e_write_Vrefmain.setObjectName(u"e_write_Vrefmain")
        self.e_write_Vrefmain.setGeometry(QRect(190, 150, 51, 23))
        self.e_write_Vrefmain.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_write_Vreset = QLineEdit(self.groupBox_9)
        self.e_write_Vreset.setObjectName(u"e_write_Vreset")
        self.e_write_Vreset.setGeometry(QRect(190, 60, 51, 23))
        self.e_write_Vreset.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_read_Dsub = QLineEdit(self.groupBox_9)
        self.e_read_Dsub.setObjectName(u"e_read_Dsub")
        self.e_read_Dsub.setGeometry(QRect(250, 90, 51, 23))
        self.e_read_Dsub.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_read_Dsub.setReadOnly(True)
        self.e_read_Vbiasgate = QLineEdit(self.groupBox_9)
        self.e_read_Vbiasgate.setObjectName(u"e_read_Vbiasgate")
        self.e_read_Vbiasgate.setGeometry(QRect(250, 120, 51, 23))
        self.e_read_Vbiasgate.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_read_Vbiasgate.setReadOnly(True)
        self.e_read_Vrefmain = QLineEdit(self.groupBox_9)
        self.e_read_Vrefmain.setObjectName(u"e_read_Vrefmain")
        self.e_read_Vrefmain.setGeometry(QRect(250, 150, 51, 23))
        self.e_read_Vrefmain.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_read_Vrefmain.setReadOnly(True)
        self.e_read_Vreset = QLineEdit(self.groupBox_9)
        self.e_read_Vreset.setObjectName(u"e_read_Vreset")
        self.e_read_Vreset.setGeometry(QRect(250, 60, 51, 23))
        self.e_read_Vreset.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_read_Vreset.setReadOnly(True)
        self.label_15 = QLabel(self.groupBox_9)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setGeometry(QRect(194, 40, 56, 12))
        self.label_26 = QLabel(self.groupBox_9)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setGeometry(QRect(254, 40, 56, 12))
        self.btn_write_Vreset = QPushButton(self.groupBox_9)
        self.btn_write_Vreset.setObjectName(u"btn_write_Vreset")
        self.btn_write_Vreset.setGeometry(QRect(310, 60, 71, 23))
        self.btn_read_Vreset = QPushButton(self.groupBox_9)
        self.btn_read_Vreset.setObjectName(u"btn_read_Vreset")
        self.btn_read_Vreset.setGeometry(QRect(390, 60, 71, 23))
        self.btn_read_Dsub = QPushButton(self.groupBox_9)
        self.btn_read_Dsub.setObjectName(u"btn_read_Dsub")
        self.btn_read_Dsub.setGeometry(QRect(390, 90, 71, 23))
        self.btn_write_Dsub = QPushButton(self.groupBox_9)
        self.btn_write_Dsub.setObjectName(u"btn_write_Dsub")
        self.btn_write_Dsub.setGeometry(QRect(310, 90, 71, 23))
        self.btn_read_Vbiasgate = QPushButton(self.groupBox_9)
        self.btn_read_Vbiasgate.setObjectName(u"btn_read_Vbiasgate")
        self.btn_read_Vbiasgate.setGeometry(QRect(390, 120, 71, 23))
        self.btn_write_Vbiasgate = QPushButton(self.groupBox_9)
        self.btn_write_Vbiasgate.setObjectName(u"btn_write_Vbiasgate")
        self.btn_write_Vbiasgate.setGeometry(QRect(310, 120, 71, 23))
        self.btn_read_Vrefmain = QPushButton(self.groupBox_9)
        self.btn_read_Vrefmain.setObjectName(u"btn_read_Vrefmain")
        self.btn_read_Vrefmain.setGeometry(QRect(390, 150, 71, 23))
        self.btn_write_Vrefmain = QPushButton(self.groupBox_9)
        self.btn_write_Vrefmain.setObjectName(u"btn_write_Vrefmain")
        self.btn_write_Vrefmain.setGeometry(QRect(310, 150, 71, 23))
        self.btn_write_input = QPushButton(self.groupBox_9)
        self.btn_write_input.setObjectName(u"btn_write_input")
        self.btn_write_input.setGeometry(QRect(310, 180, 71, 23))
        self.e_read_input = QLineEdit(self.groupBox_9)
        self.e_read_input.setObjectName(u"e_read_input")
        self.e_read_input.setGeometry(QRect(250, 180, 51, 23))
        self.e_read_input.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_read_input.setReadOnly(True)
        self.e_addr_input = QLineEdit(self.groupBox_9)
        self.e_addr_input.setObjectName(u"e_addr_input")
        self.e_addr_input.setGeometry(QRect(130, 180, 51, 23))
        self.e_addr_input.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_27 = QLabel(self.groupBox_9)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setGeometry(QRect(20, 180, 101, 20))
        self.label_27.setLayoutDirection(Qt.LeftToRight)
        self.label_27.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_write_input = QLineEdit(self.groupBox_9)
        self.e_write_input.setObjectName(u"e_write_input")
        self.e_write_input.setGeometry(QRect(190, 180, 51, 23))
        self.e_write_input.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.btn_read_input = QPushButton(self.groupBox_9)
        self.btn_read_input.setObjectName(u"btn_read_input")
        self.btn_read_input.setGeometry(QRect(390, 180, 71, 23))
        self.chk_autosave = QCheckBox(self.centralwidget)
        self.chk_autosave.setObjectName(u"chk_autosave")
        self.chk_autosave.setGeometry(QRect(150, 480, 91, 31))
        self.label_recent = QLabel(self.centralwidget)
        self.label_recent.setObjectName(u"label_recent")
        self.label_recent.setGeometry(QRect(140, 510, 121, 21))
        self.label_recent.setLayoutDirection(Qt.LeftToRight)
        self.label_recent.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.line_2 = QFrame(self.centralwidget)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setGeometry(QRect(120, 480, 20, 61))
        self.line_2.setFrameShape(QFrame.VLine)
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.label_recent_filename = QLabel(self.centralwidget)
        self.label_recent_filename.setObjectName(u"label_recent_filename")
        self.label_recent_filename.setGeometry(QRect(270, 510, 301, 21))
        self.label_recent_filename.setLayoutDirection(Qt.LeftToRight)
        self.label_recent_filename.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.radio_exp_time = QRadioButton(self.centralwidget)
        self.radio_exp_time.setObjectName(u"radio_exp_time")
        self.radio_exp_time.setGeometry(QRect(170, 230, 21, 25))
        self.radio_fowler_number = QRadioButton(self.centralwidget)
        self.radio_fowler_number.setObjectName(u"radio_fowler_number")
        self.radio_fowler_number.setGeometry(QRect(170, 260, 21, 25))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Detector Control System 0.1", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Initializing", None))
        self.btn_error_cnt.setText(QCoreApplication.translate("MainWindow", u"Error Count", None))
        self.label_ver.setText(QCoreApplication.translate("MainWindow", u"0.0", None))
        self.e_timeout.setText(QCoreApplication.translate("MainWindow", u"200", None))
        self.btn_reset.setText(QCoreApplication.translate("MainWindow", u"Reset", None))
        self.btn_initialize1.setText(QCoreApplication.translate("MainWindow", u"Initialize1", None))
        self.cmb_ouput_channels.setItemText(0, QCoreApplication.translate("MainWindow", u"1", None))
        self.cmb_ouput_channels.setItemText(1, QCoreApplication.translate("MainWindow", u"4", None))
        self.cmb_ouput_channels.setItemText(2, QCoreApplication.translate("MainWindow", u"32", None))

        self.btn_download_MCD.setText(QCoreApplication.translate("MainWindow", u"DownloadMCD", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Output channels:", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Ver.", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"SetGigeTimeout (ms):", None))
        self.btn_initialize2.setText(QCoreApplication.translate("MainWindow", u"Initialize2", None))
        self.btn_set_detector.setText(QCoreApplication.translate("MainWindow", u"SetDetector", None))
        self.label_connection_sts.setText(QCoreApplication.translate("MainWindow", u"ICS", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Configuration Files", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"MACIE Register (mrf):", None))
        self.btn_find_MACIE_reg.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.e_MACIE_reg.setText(QCoreApplication.translate("MainWindow", u"MACIE_Registers_Slow.mrf", None))
        self.btn_find_config_dir.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"Configuration Directory:", None))
        self.e_config_dir.setText(QCoreApplication.translate("MainWindow", u"/home/dcs/macie_v5.2_centos/LoadFiles", None))
        self.btn_find_ASIC_firware.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"ASIC Firmware (mcd):", None))
        self.e_ASIC_firmware.setText(QCoreApplication.translate("MainWindow", u"HxRG_Main.mcd", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"Image Directory:", None))
        self.e_img_dir.setText(QCoreApplication.translate("MainWindow", u"/DCS/Data", None))
        self.btn_find_img_dir.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Sampling Mode", None))
        self.radio_UTR.setText(QCoreApplication.translate("MainWindow", u"Up-The-Ramp", None))
        self.radio_CDS.setText(QCoreApplication.translate("MainWindow", u"CDS", None))
        self.radio_CDSNoise.setText(QCoreApplication.translate("MainWindow", u"CDS Noise", None))
        self.radio_Fowler.setText(QCoreApplication.translate("MainWindow", u"Fowler", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Sampling Parameters", None))
        self.e_reads.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.e_resets.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.e_groups.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.e_drops.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.e_ramps.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.btn_set_param.setText(QCoreApplication.translate("MainWindow", u"Set\n"
"Parameters", None))
        self.e_fowler_number.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.e_exp_time.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_fowler_number.setText(QCoreApplication.translate("MainWindow", u"N. Fowler:", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Exp. Time (s):", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"Resets", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"Reads", None))
        self.label_groups.setText(QCoreApplication.translate("MainWindow", u"Groups", None))
        self.label_drops.setText(QCoreApplication.translate("MainWindow", u"Drops", None))
        self.label_ramps.setText(QCoreApplication.translate("MainWindow", u"Ramps", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"Window Mode", None))
        self.chk_ROI_mode.setText(QCoreApplication.translate("MainWindow", u"ROI Mode", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Y stop:", None))
        self.e_x_stop.setText(QCoreApplication.translate("MainWindow", u"2047", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Y start:", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"X stop:", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"X start:", None))
        self.e_y_stop.setText(QCoreApplication.translate("MainWindow", u"2047", None))
        self.e_y_start.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.e_x_start.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Repeat:", None))
        self.e_repeat.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.btn_stop.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.btn_acquireramp.setText(QCoreApplication.translate("MainWindow", u"AcquireRamp", None))
        self.btn_get_telemetry.setText(QCoreApplication.translate("MainWindow", u"GetTelemetry", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("MainWindow", u"Acquiring Status", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"Calculated waiting time (s):", None))
        self.label_measured_time.setText(QCoreApplication.translate("MainWindow", u"0.0", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Measured waiting time (s):", None))
        self.label_calculated_time.setText(QCoreApplication.translate("MainWindow", u"0.0", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"row-by-row combining Line:", None))
        self.cmb_combine_line.setItemText(0, QCoreApplication.translate("MainWindow", u"5", None))
        self.cmb_combine_line.setItemText(1, QCoreApplication.translate("MainWindow", u"7", None))
        self.cmb_combine_line.setItemText(2, QCoreApplication.translate("MainWindow", u"9", None))

        self.chk_show_fits.setText(QCoreApplication.translate("MainWindow", u"Show FITS", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Manual Mode", None))
        self.groupBox_9.setTitle(QCoreApplication.translate("MainWindow", u"Single Register Read - Write (ASIC)", None))
        self.e_addr_Vreset.setText(QCoreApplication.translate("MainWindow", u"6000", None))
        self.e_addr_Dsub.setText(QCoreApplication.translate("MainWindow", u"6002", None))
        self.e_addr_Vbiasgate.setText(QCoreApplication.translate("MainWindow", u"6004", None))
        self.e_addr_Vrefmain.setText(QCoreApplication.translate("MainWindow", u"602c", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Addr (h)", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Vreset:", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Dsub:", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"VBiasGate:", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"VRef.Main:", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Val (W)", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"Val (R)", None))
        self.btn_write_Vreset.setText(QCoreApplication.translate("MainWindow", u"write", None))
        self.btn_read_Vreset.setText(QCoreApplication.translate("MainWindow", u"read", None))
        self.btn_read_Dsub.setText(QCoreApplication.translate("MainWindow", u"read", None))
        self.btn_write_Dsub.setText(QCoreApplication.translate("MainWindow", u"write", None))
        self.btn_read_Vbiasgate.setText(QCoreApplication.translate("MainWindow", u"read", None))
        self.btn_write_Vbiasgate.setText(QCoreApplication.translate("MainWindow", u"write", None))
        self.btn_read_Vrefmain.setText(QCoreApplication.translate("MainWindow", u"read", None))
        self.btn_write_Vrefmain.setText(QCoreApplication.translate("MainWindow", u"write", None))
        self.btn_write_input.setText(QCoreApplication.translate("MainWindow", u"write", None))
        self.e_addr_input.setText("")
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"Address:", None))
        self.btn_read_input.setText(QCoreApplication.translate("MainWindow", u"read", None))
        self.chk_autosave.setText(QCoreApplication.translate("MainWindow", u"Save As", None))
        self.label_recent.setText(QCoreApplication.translate("MainWindow", u"recent saved file:", None))
        self.label_recent_filename.setText(QCoreApplication.translate("MainWindow", u"file name", None))
        self.radio_exp_time.setText("")
        self.radio_fowler_number.setText("")
    # retranslateUi

