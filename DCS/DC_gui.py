# -*- coding: utf-8 -*-

"""
Created on Aug 4, 2022

Modified on Dec 15, 2022

@author: hilee
"""

import sys, os
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import Libs.SetConfig as sc
#import Libs.rabbitmq_server as serv
from Libs.MsgMiddleware import *
from Libs.logger import *

from ui_dcs import *
from DC_def import *

import threading
import subprocess
import time as ti
from shutil import copyfile

class MainWindow(Ui_Dialog, QMainWindow):

    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Detector Control System 1.0")
        self.setFixedSize(906, 570)

        self.log = LOG(WORKING_DIR + "DCS")

        self._iam = "GUI"
        self._target = "CORE"

        self.log.send(self._iam, INFO, "start DCS gui!!!")        

        #start core!!!
        self.proc_core = None
        self.proc_core = subprocess.Popen(['python', WORKING_DIR + 'workspace/dcs/DCS/DC_core.py'])

        #-------------------------------------------------------
        # load ini file
        cfg = sc.LoadConfig(WORKING_DIR + "DCS/DCS.ini")

        # server id, pwd
        self.myid = cfg.get(IAM, 'myid')
        self.pwd = cfg.get(IAM, 'pwd')

        # exchange - queue
        self.gui_ex = cfg.get("DC", 'gui_exchange')
        self.gui_q = cfg.get("DC", 'gui_routing_key')
        self.core_ex = cfg.get("DC", 'core_exchange')
        self.core_q = cfg.get("DC", 'core_routing_key')

        self.asic_Vreset = cfg.get("DC", 'Vreset')
        self.asic_Dsub = cfg.get("DC", 'Dsub')
        self.asic_VBiasGate = cfg.get("DC", 'VBiasGate')
        self.asic_VrefMain = cfg.get("DC", 'VrefMain')

        self.e_write_Vreset.setText(self.asic_Vreset)
        self.e_write_Dsub.setText(self.asic_Dsub)
        self.e_write_Vbiasgate.setText(self.asic_VBiasGate)
        self.e_write_Vrefmain.setText(self.asic_VrefMain)

        self.loadfile_path = cfg.get('DC', 'config-dir')
        self.loadfile_path = WORKING_DIR + self.loadfile_path

        self.macie_file = cfg.get('DC', 'MACIE-Register')
        self.asic_file = cfg.get('DC', 'ASIC-Firmware')

        self.exe_path = cfg.get('DC', 'Img-dir')
        self.exe_path = WORKING_DIR + self.exe_path

        self.gige_timeout = cfg.get('DC', 'timeout')
        self.output_channel = cfg.get('DC', 'channel')

        #-------------------------------------------------------

        self.init_events()

        self.label_IAM.setText(IAM)

        self.chk_ROI_mode.setEnabled(False)

        self.e_x_start.setEnabled(False)
        self.e_x_stop.setEnabled(False)
        self.e_y_start.setEnabled(False)
        self.e_y_stop.setEnabled(False)
            
        #Load: cofiguration files
        self.e_config_dir.setText(self.loadfile_path)
        self.e_MACIE_reg.setText(self.macie_file)
        self.e_ASIC_firmware.setText(self.asic_file)
        self.e_img_dir.setText(self.exe_path)
        
        #Load: version, SetGigeTimeout, Output Channel
        self.e_timeout.setText(self.gige_timeout)
        self.cmb_ouput_channels.setCurrentText(self.output_channel)

        self.samplingMode = UTR_MODE
        self.radio_UTR.setChecked(True)

        self.set_param_ui(1, 1, 1, 0, 1)
        self.e_exp_time.setText("1.63")
        self.expTime = 1.63
        self.cal_waittime = 0.0        

        self.radio_exp_time.setChecked(True)
        self.radio_fowler_number.setChecked(False)

        self.chk_autosave.setText("Save AS")
        self.chk_autosave.setChecked(False)

        self.use_saveAs()
        self.e_user_dir.setText(WORKING_DIR + "DCS/Data/")

        self.cur_cnt = 0
        self.cur_prog_step = 0
        self.fitsfullpath = ""
        self.asic_load_click = False

        self.prog_sts.setValue(0)

        self.producer = None
        self.consumer = None

        self.connect_to_server_ex()
        self.connect_to_server_q()

        self.busy = False
       

    
    def closeEvent(self, event: QCloseEvent) -> None:
        self.log.send(self._iam, INFO, "DCS gui closing...")

        self.producer.send_message(self.gui_q, CMD_EXIT)

        for th in threading.enumerate():
            self.log.send(self._iam, INFO, th.name + " exit.")

        if self.proc_core != None:
            self.proc_core.terminate()

        self.log.send(self._iam, INFO, "DCS gui closed!")

        if self.producer != None:
            self.producer.__del__()

        return super().closeEvent(event)


    def connect_to_server_ex(self):
        # RabbitMQ connect
        self.producer = MsgMiddleware(self._iam, "localhost", self.myid, self.pwd, self.gui_ex)
        self.producer.connect_to_server()
        self.producer.define_producer()

            
    def connect_to_server_q(self):
        # RabbitMQ connect
        self.consumer = MsgMiddleware(self._iam, "localhost", self.myid, self.pwd, self.core_ex)
        self.consumer.connect_to_server()
        self.consumer.define_consumer(self.core_q, self.callback)

        th = threading.Thread(target=self.consumer.start_consumer)
        th.daemon = True
        th.start() 


    def callback(self, ch, method, properties, body):
        cmd = body.decode()
        #msg = "receive: %s" % cmd
        #self.log.send(self._iam, INFO, msg)

        param = cmd.split()

        self.busy = False

        if param[0] == CMD_CORESTART:
            self.producer.send_message(self.gui_q, CMD_VERSION)

        elif param[0] == CMD_VERSION:
            self.label_ver.setText(param[1])

        elif param[0] == CMD_MEASURETIME:
            self.label_measured_time.setText(param[1])
            
            if self.chk_autosave.isChecked():
                self.fitsfullpath = param[2]
                file = param[2].split("/")
                path = ""
                for i in file[1:-1]:
                    path += "/"
                    path += i
                self.e_user_dir.setText(path)
                self.e_user_file.setText(file[-1][:-5] + "_")

        elif param[0] == CMD_INITIALIZE1:            
            info = "%s (%s)" % (param[1], param[2])
            self.label_ver.setText(info)

            self.btn_initialize1.setEnabled(False)
        
        elif param[0] == CMD_INITIALIZE2:
            pass
        elif param[0] == CMD_RESET:
            pass
        #elif param[0] == CMD_DOWNLOAD:
        #    pass
        #elif param[0] == CMD_SETDETECTOR:
        #    pass
        #elif param[0] == CMD_ERRCOUNT:
        #    self.read_addr(self.e_addr_Vreset.text())
        #    self.read_addr(self.e_addr_Dsub.text())
        #    self.read_addr(self.e_addr_Vbiasgate.text())
        #    self.read_addr(self.e_addr_Vrefmain.text())

        elif param[0] == CMD_SETRAMPPARAM:
            self.acquireramp()  

        elif param[0] == CMD_SETFSPARAM:
            self.acquireramp()         

        elif param[0] == CMD_ACQUIRERAMP:
            self.prog_timer.stop()
            self.cur_prog_step = 100
            self.prog_sts.setValue(self.cur_prog_step)

            self.elapsed_timer.stop()

            show_cur_cnt = "%d / %s" % (self.cur_cnt, self.e_repeat.text())
            self.label_cur_num.setText(show_cur_cnt)
            if self.cur_cnt < int(self.e_repeat.text()):
                #self.acquireramp()
                self.btn_acquireramp.click()
            else:
                self.cur_cnt = 0

        elif param[0] == CMD_STOPACQUISITION:
            pass

        elif param[0] == CMD_WRITEASICREG:
            _addr = str(hex(int(param[1])))[2:6]

            if self.asic_load_click and _addr == self.e_addr_Vreset.text():
                self.read_addr(self.e_addr_Vreset.text())
            elif self.asic_load_click and _addr == self.e_addr_Dsub.text():
                self.read_addr(self.e_addr_Dsub.text())
            elif self.asic_load_click and _addr == self.e_addr_Vbiasgate.text():
                self.read_addr(self.e_addr_Vbiasgate.text())
            elif self.asic_load_click and _addr == self.e_addr_Vrefmain.text():
                self.read_addr(self.e_addr_Vrefmain.text())
            elif self.asic_load_click and _addr == self.e_addr_input.text():
                self.read_addr(self.e_read_input.text())

        elif param[0] == CMD_READASICREG:
            _addr = str(hex(int(param[1])))[2:6]
            _text = str(hex(int(param[2])))[2:6]
            
            if _addr == self.e_addr_Vreset.text():
                self.e_read_Vreset.setText(_text)
            elif _addr == self.e_addr_Dsub.text():
                self.e_read_Dsub.setText(_text)
            elif _addr == self.e_addr_Vbiasgate.text():
                self.e_read_Vbiasgate.setText(_text)
            elif _addr == self.e_addr_Vrefmain.text():
                self.e_read_Vrefmain.setText(_text)
            else:
                self.e_read_input.setText(_text)

        elif param[0] == CMD_GETTELEMETRY:
            pass
        else:
            pass
    


    def set_param_ui(self, resets, reads, groups, drops, ramps):
        if self.samplingMode == UTR_MODE:
            self.e_reads.setEnabled(True)
            self.e_groups.setEnabled(True)
            self.e_drops.setEnabled(True)
            self.e_ramps.setEnabled(True)

            self.radio_exp_time.hide()
            self.radio_fowler_number.hide()

            self.e_exp_time.setEnabled(False)
            self.e_fowler_number.setEnabled(False)

            self.label_drops.setText("Drops")

        else:
            self.e_reads.setEnabled(False)
            self.e_groups.setEnabled(False)
            self.e_drops.setEnabled(False)
            self.e_ramps.setEnabled(False)
            
            self.label_drops.setText("T.Fowler")

            self.e_fowler_number.setText(str(reads))

            if self.samplingMode == FOWLER_MODE:
                
                self.e_exp_time.setEnabled(True)
                self.e_fowler_number.setEnabled(False)
                self.radio_exp_time.show()
                self.radio_fowler_number.show()
            
            else:
                self.e_exp_time.setEnabled(False)
                self.e_fowler_number.setEnabled(False)

                self.radio_exp_time.hide()
                self.radio_fowler_number.hide()

        self.e_resets.setText(str(resets))
        self.e_reads.setText(str(reads))
        self.e_groups.setText(str(groups))
        self.e_drops.setText(str(drops))
        self.e_ramps.setText(str(ramps))


    def init_events(self):
        
        self.cmb_ouput_channels.currentTextChanged.connect(self.change_channel)
        self.btn_initialize1.clicked.connect(self.initialize1)
        self.btn_initialize2.clicked.connect(self.initialize2)
        self.btn_reset.clicked.connect(self.reset)
        #self.btn_download_MCD.clicked.connect(self.downloadMCD)
        #self.btn_set_detector.clicked.connect(self.set_detector)
        #self.btn_error_cnt.clicked.connect(self.err_count)

        self.radio_UTR.clicked.connect(self.click_UTR)
        self.radio_CDS.clicked.connect(self.click_CDS)
        self.radio_CDSNoise.clicked.connect(self.click_CDSNoise)
        self.radio_Fowler.clicked.connect(self.click_Fowler)

        self.radio_exp_time.clicked.connect(self.judge_exp_time)
        self.radio_fowler_number.clicked.connect(self.judge_fowler_number)

        #self.e_fowler_number.returnPressed.connect(self.judge_param)

        #self.btn_set_param.clicked.connect(self.set_parameter)

        self.chk_ROI_mode.clicked.connect(self.set_ROImode)

        self.btn_acquireramp.clicked.connect(self.acquireramp)
        self.btn_stop.clicked.connect(self.stop_acquistion)

        self.chk_show_fits.clicked.connect(self.show_fits)

        self.btn_get_telemetry.clicked.connect(self.get_telemetry)

        # path
        self.btn_find_config_dir.clicked.connect(lambda: self.find_dir_file(CONFIG_DIR))
        self.btn_find_MACIE_reg.clicked.connect(lambda: self.find_dir_file(MACIE_FILE))
        self.btn_find_ASIC_firware.clicked.connect(lambda: self.find_dir_file(ASIC_FILE))
        self.btn_find_img_dir.clicked.connect(lambda: self.find_dir_file(IMG_DIR))

        self.btn_ASIC_load.clicked.connect(self.asic_load)

        self.btn_write_Vreset.clicked.connect(lambda: self.write_addr(self.e_addr_Vreset.text(), self.e_write_Vreset.text()))
        self.btn_read_Vreset.clicked.connect(lambda: self.read_addr(self.e_addr_Vreset.text()))

        self.btn_write_Dsub.clicked.connect(lambda: self.write_addr(self.e_addr_Dsub.text(), self.e_write_Dsub.text()))
        self.btn_read_Dsub.clicked.connect(lambda: self.read_addr(self.e_addr_Dsub.text()))

        self.btn_write_Vbiasgate.clicked.connect(lambda: self.write_addr(self.e_addr_Vbiasgate.text(), self.e_write_Vbiasgate.text()))
        self.btn_read_Vbiasgate.clicked.connect(lambda: self.read_addr(self.e_addr_Vbiasgate.text()))

        self.btn_write_Vrefmain.clicked.connect(lambda: self.write_addr(self.e_addr_Vrefmain.text(), self.e_write_Vrefmain.text()))
        self.btn_read_Vrefmain.clicked.connect(lambda: self.read_addr(self.e_addr_Vrefmain.text()))
        
        self.btn_write_input.clicked.connect(lambda: self.write_addr(self.e_addr_input.text(), self.e_write_input.text()))
        self.btn_read_input.clicked.connect(lambda: self.read_addr(self.e_addr_input.text()))

        self.chk_autosave.clicked.connect(self.use_saveAs)
        self.btn_find_user_dir.clicked.connect(self.find_dir)
        self.btn_save.clicked.connect(self.copy_fits)

    # ----------------------------------------------------------------------
    # Buttons           

    def change_channel(self):
        if self.cmb_ouput_channels.currentText() == "1":
            self.chk_ROI_mode.setEnabled(True)

            if self.chk_ROI_mode.isChecked():
                self.e_x_start.setEnabled(True)
                self.e_x_stop.setEnabled(True)
                self.e_y_start.setEnabled(True)
                self.e_y_stop.setEnabled(True)
        else:
            self.chk_ROI_mode.setEnabled(False)

            self.e_x_start.setEnabled(False)
            self.e_x_stop.setEnabled(False)
            self.e_y_start.setEnabled(False)
            self.e_y_stop.setEnabled(False)
            
            

    def initialize1(self):

        if self.busy:
            return
        self.busy = True

        msg = "%s %s" % (CMD_INITIALIZE1, self.e_timeout.text())
        self.producer.send_message(self.gui_q, msg)


    def initialize2(self):

        if self.busy:
            return
        self.busy = True

        msg = "%s %d %s" % (CMD_INITIALIZE2, MUX_TYPE, self.cmb_ouput_channels.currentText())
        self.producer.send_message(self.gui_q, msg)


    def reset(self):

        if self.busy:
            return
        self.busy = True

        self.producer.send_message(self.gui_q, CMD_RESET)

    '''
    def downloadMCD(self):

        if self.busy:
            return
        self.busy = True

        self.producer.send_message(self.gui_q, CMD_DOWNLOAD)
    '''

    '''
    def set_detector(self):

        #if self.busy:
        #    return
        #self.busy = True

        msg = "%s %d %s" % (CMD_SETDETECTOR, MUX_TYPE, self.cmb_ouput_channels.currentText())
        self.producer.send_message(self.gui_q, msg)
    '''

    '''
    def err_count(self):

        if self.busy:
            return
        self.busy = True

        self.producer.send_message(self.gui_q, CMD_ERRCOUNT)
    '''


    def click_UTR(self):
        self.samplingMode = UTR_MODE
        self.set_param_ui(1, 1, 1, 0, 1)


    def click_CDS(self):
        self.samplingMode = CDS_MODE
        self.set_param_ui(1, 1, 1, T_minFowler, 1)


    def click_CDSNoise(self):
        self.samplingMode = CDSNOISE_MODE
        self.set_param_ui(1, 1, 1, T_minFowler, 2)


    def click_Fowler(self):
        self.samplingMode = FOWLER_MODE
        self.set_param_ui(1, 1, 1, T_minFowler, 1)


    def judge_exp_time(self):
        #self.radio_exp_time.setChecked(True)
        self.radio_fowler_number.setChecked(False)
        self.e_exp_time.setEnabled(True)
        self.e_fowler_number.setEnabled(False)

        #self.judge_param()


    def judge_fowler_number(self):
        self.radio_exp_time.setChecked(False)
        #self.radio_fowler_number.setChecked(True)
        self.e_exp_time.setEnabled(False)
        self.e_fowler_number.setEnabled(True)


    def judge_param(self):
        # calculation fowler number & exp time
        self.expTime = float(self.e_exp_time.text())
        _fowler_num = int(self.e_fowler_number.text())

        _fowler_time = float(self.e_drops.text())

        if self.radio_exp_time.isChecked():
            _max_fowler_number = int((self.expTime - T_minFowler) / T_frame)
            if _fowler_num > _max_fowler_number:
                #dialog box
                QMessageBox.warning(self, WARNING, "please change 'exposure time'!")
                self.log.send(self._iam, WARNING, "please change 'exposure time'!")
                return False

        elif self.radio_fowler_number.isChecked():
            _fowler_time = self.expTime - T_frame * _fowler_num
            if _fowler_time < T_minFowler:
                #dialog box
                QMessageBox.warning(self, WARNING, "please change 'fowler sampling number'!")
                self.log.send(self._iam, WARNING, "please change 'fowler sampling number'!")
                return False            

        else:
            self.log.send(self._iam, WARNING, "Please select 'Exp. Time' or 'N. Fowler' for judgement!")
            return False

        return True
        

    def set_parameter(self):

        #if self.busy:
        #    return
        #self.busy = True

        if self.samplingMode == FOWLER_MODE and self.judge_param() == False:
            #self.busy = False
            return False

        resets = int(self.e_resets.text())
        reads = int(self.e_reads.text())
        groups = int(self.e_groups.text())
        ramps = int(self.e_ramps.text())

        msg = "%s %d" % (CMD_SETFSMODE, self.samplingMode)
        self.producer.send_message(self.gui_q, msg)

        self.cal_waittime = 0.0
        if self.samplingMode == UTR_MODE:
            drops = int(self.e_drops.text())

            self.expTime = (T_frame * reads * groups) + (T_frame * drops * (groups -1 ))
            self.cal_waittime = T_br + ((T_frame * resets) + self.expTime) * ramps
            
            msg = "%s %.3f %d %d %d %d %d" % (CMD_SETRAMPPARAM, self.expTime, resets, reads, groups, drops, ramps)
            self.producer.send_message(self.gui_q, msg)

            str_exp_time = "%.3f" % self.expTime
            self.e_exp_time.setText(str_exp_time)     

        else:
            self.expTime = float(self.e_exp_time.text())
            if self.samplingMode == FOWLER_MODE:
                #if self.radio_fowler_number.isChecked():
                self.e_reads.setText(self.e_fowler_number.text())
                reads = int(self.e_reads.text())
                if self.radio_fowler_number.isChecked():
                    self.e_reads.setText(self.e_fowler_number.text())
                    reads = int(self.e_reads.text())

                fowlerTime = self.expTime - T_frame * reads
                str_fowlerTime = "%.3f" % fowlerTime
                
                self.e_drops.setText(str_fowlerTime)
            
            else:
                fowlerTime = float(self.e_drops.text())
                self.expTime = fowlerTime + T_frame * reads

                str_exp_time = "%.3f" % self.expTime
                self.e_exp_time.setText(str_exp_time)

            self.e_reads.setText(self.e_fowler_number.text())
            self.cal_waittime = T_br + ((T_frame * resets) + fowlerTime + (2 * T_frame * reads)) * ramps
  
            msg = "%s %.3f %d %d %d %.3f %d" % (CMD_SETFSPARAM, self.expTime, resets, reads, groups, fowlerTime, ramps)
            self.producer.send_message(self.gui_q, msg)
        
        str_caltime = "%.3f" % self.cal_waittime
        self.label_calculated_time.setText(str_caltime)

        return True




    def set_ROImode(self):
        if self.chk_ROI_mode.isChecked():
            self.e_x_start.setEnabled(True)
            self.e_x_stop.setEnabled(True)
            self.e_y_start.setEnabled(True)
            self.e_y_stop.setEnabled(True)
        else:
            self.e_x_start.setEnabled(False)
            self.e_x_stop.setEnabled(False)
            self.e_y_start.setEnabled(False)
            self.e_y_stop.setEnabled(False)
       

    # thread
    def acquireramp(self):

        if self.cur_cnt == 0:
            if self.set_parameter() == False:
                return

        if self.busy:
            return
        self.busy = True

        if self.chk_ROI_mode.isChecked():
            self.x_start = int(self.e_x_start.text())
            self.x_stop = int(self.e_x_stop.text())
            self.y_start = int(self.e_y_start.text())
            self.y_stop = int(self.e_y_stop.text())
            msg = "%s %d %d %d %d" % (CMD_SETWINPARAM, self.x_start, self.x_stop, self.y_start, self.y_stop)
            self.producer.send_message(self.gui_q, msg)
        
        self.cur_cnt += 1

        self.label_measured_time.setText("0.0")

        self.prog_timer = QTimer(self)
        self.prog_timer.setInterval(int(self.cal_waittime*10))
        self.prog_timer.timeout.connect(self.show_progressbar)

        self.cur_prog_step = 0
        self.prog_sts.setValue(self.cur_prog_step)
        self.prog_timer.start()

        self.elapsed_timer = QTimer(self)
        self.elapsed_timer.setInterval(0.001)
        self.elapsed_timer.timeout.connect(self.show_elapsed)
        
        self.elapsed = ti.time()
        self.label_elapsed.setText("0.0")
        self.elapsed_timer.start()
        
        msg = "%s %d" % (CMD_ACQUIRERAMP, self.chk_ROI_mode.isChecked())
        self.producer.send_message(self.gui_q, msg)  
        
        
    def show_progressbar(self):
    #    th = threading.Thread(target=self.progressbar)
    #    th.start() 
    #def progressbar(self):
        if self.cur_prog_step >= 100:
            self.log.send(self._iam, INFO, "progress bar end!!!")
            self.prog_timer.stop()
            self.elapsed_timer.stop()
            return
        
        self.cur_prog_step += 1
        self.prog_sts.setValue(self.cur_prog_step)       
        #self.log.send(self._iam, DEBUG, self.cur_prog_step)


    def show_elapsed(self):
        msg = "%.3f" % (ti.time() - self.elapsed)
        self.label_elapsed.setText(msg)
        #print(ti.time() - self.elapsed)


    def stop_acquistion(self):
        if self.cur_prog_step == 0:
            return

        self.prog_timer.stop()
        self.elapsed_timer.stop()
        
        self.producer.send_message(self.gui_q, CMD_STOPACQUISITION)


    def show_fits(self):
        msg = "%s %d" % (CMD_SHOWFITS, self.chk_show_fits.isChecked())
        self.producer.send_message(self.gui_q, msg)

        
    def use_saveAs(self):
        use = self.chk_autosave.isChecked()
        
        self.e_user_dir.setEnabled(use)
        self.e_user_file.setEnabled(use)
        self.btn_find_user_dir.setEnabled(use)
        self.btn_save.setEnabled(use)


    def find_dir(self):
        loader = self.e_user_dir.text()
        folder = QFileDialog.getExistingDirectory(self, "Select Directory", loader)
        if folder:
            self.e_user_dir.setText(folder)


    def copy_fits(self):

        if self.fitsfullpath == "":
            return

        newfile = self.e_user_dir.text() + "/" + self.e_user_file.text() + ".fits"
        copyfile(self.fitsfullpath, newfile)

        self.fitsfullpath = ""


    def get_telemetry(self):

        if self.busy:
            return
        self.busy = True

        self.producer.send_message(self.gui_q, CMD_GETTELEMETRY)


    def find_dir_file(self, find_option):
        if find_option == IMG_DIR:
            loader = self.e_img_dir.text()
            folder = QFileDialog.getExistingDirectory(self, "Select Directory", loader)
            if folder:
                self.e_img_dir.setText(folder)

        else:
            loader = self.e_config_dir.text()
            folder = QFileDialog.getExistingDirectory(self, "Select Directory", loader)
            if find_option == CONFIG_DIR:   
                if folder:
                    self.e_config_dir.setText(folder)
            
            elif find_option == MACIE_FILE:
                path = QFileDialog.getOpenFileName(self, "Choose File", folder, filter='*.mrf')
                if path[0]:
                    file = path[0].split('/')
                    self.e_MACIE_reg.setText(file[-1])
            
            elif find_option == ASIC_FILE:
                path = QFileDialog.getOpenFileName(self, "Choose File", folder, filter='*.mcd')
                if path[0]:
                    file = path[0].split('/')
                    self.e_ASIC_firmware.setText(file[-1])

    
    def asic_load(self):        

        self.write_addr(self.e_addr_Vreset.text(), self.e_write_Vreset.text(), True)
        self.write_addr(self.e_addr_Dsub.text(), self.e_write_Dsub.text(), True)
        self.write_addr(self.e_addr_Vbiasgate.text(), self.e_write_Vbiasgate.text(), True)
        self.write_addr(self.e_addr_Vrefmain.text(), self.e_write_Vrefmain.text(), True)



    def write_addr(self, addr, value, click=False):
        if value == "":
            return 

        self.asic_load_click = click

        _addr = int("0x" + addr, 16)
        _value = int("0x" + value, 16)

        msg = "%s %d %d" % (CMD_WRITEASICREG, _addr, _value)
        self.producer.send_message(self.gui_q, msg)
        


    def read_addr(self, addr):   
        if addr == "":
            return

        _addr = int("0x" + addr, 16)

        msg = "%s %d" % (CMD_READASICREG, _addr)
        self.producer.send_message(self.gui_q, msg)

        
if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False

    app = QApplication(sys.argv)

    dc = MainWindow()
    dc.show()

    app.exec()