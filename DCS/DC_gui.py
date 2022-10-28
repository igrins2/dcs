# -*- coding: utf-8 -*-

"""
Created on Aug 4, 2022

Modified on Aug 28, 2022

@author: hilee
"""

import sys, os
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import Libs.SetConfig as sc
import Libs.rabbitmq_server as serv
from Libs.logger import *

from ui_dcs import *
from DC_def import *

import threading
import subprocess
import time

class MainWindow(Ui_MainWindow, QMainWindow):

    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Detector Control System 0.2")

        self.log = LOG(WORKING_DIR + "DCS")

        self.iam = "GUI"
        self.target = "CORE"

        self.logwrite(INFO, "start DCS gui!!!")        

        #start core!!!
        self.proc_core = subprocess.Popen(['python', WORKING_DIR + 'workspace/dcs/DCS/DC_core.py'])

        #-------------------------------------------------------
        # load ini file
        cfg = sc.LoadConfig(WORKING_DIR + "DCS/DCS.ini")

        # server id, pwd
        self.myid = cfg.get(IAM, 'localhost_myid')
        self.pwd = cfg.get(IAM, 'localhost_pwd')

        # exchange - queue
        self.gui_ex = cfg.get("DC", 'gui_exchange')
        self.gui_q = cfg.get("DC", 'gui_routing_key')
        self.core_ex = cfg.get("DC", 'core_exchange')
        self.core_q = cfg.get("DC", 'core_routing_key')

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

        self.set_param_ui(1, 1, 1, 0, 1)
        self.e_exp_time.setText("1.63")
        self.expTime = 1.63
        self.cal_waittime = 0.0

        self.radio_exp_time.setChecked(True)
        self.radio_fowler_number.setChecked(False)

        self.chk_autosave.setText("Save AS")
        self.chk_autosave.setChecked(False)

        self.cur_cnt = 0
        self.cur_prog_step = 0

        self.prog_sts.setValue(0)

        self.connect_to_server_ex()
        self.connect_to_server_q()

        self.busy = False
       

    
    def closeEvent(self, event: QCloseEvent) -> None:
        self.logwrite(INFO, "DCS gui closing...")

        #need to test
        #self.send_message(CMD_EXIT)

        if self.proc_core != None:
            self.proc_core.terminate()

        for th in threading.enumerate():
            self.logwrite(INFO, th.name + " exit.")

        if self.queue:
            self.channel_q.stop_consuming()
            self.connection_q.close()

        self.logwrite(INFO, "DCS gui closed!")

        return super().closeEvent(event)


    def logwrite(self, level, message):
        level_name = ""
        if level == DEBUG:
            level_name = "DEBUG"
        elif level == INFO:
            level_name = "INFO"
        elif level == WARNING:
            level_name = "WARNING"
        elif level == ERROR:
            level_name = "ERROR"
        
        msg = "[%s:%s] %s" % (self.iam, level_name, message)
        self.log.send(level, msg)
        


    def connect_to_server_ex(self):
        # RabbitMQ connect
        self.connection_ex, self.channel_ex = serv.connect_to_server(self.iam, "localhost", self.myid, self.pwd)

        if self.connection_ex:
            # RabbitMQ: define producer 
            serv.define_producer(self.iam, self.channel_ex, "direct", self.gui_ex)


    def send_message(self, message):
        if self.connection_ex:
            serv.send_message(self.iam, self.target, self.channel_ex, self.gui_ex, self.gui_q, message)

            
    def connect_to_server_q(self):
        # RabbitMQ connect
        self.connection_q, self.channel_q = serv.connect_to_server(self.iam, "localhost", self.myid, self.pwd)

        if self.connection_q:
            # RabbitMQ: define consumer
            self.queue = serv.define_consumer(self.iam, self.channel_q, "direct", self.core_ex, self.core_q)

            th = threading.Thread(target=self.consumer)
            th.start() 


    # RabbitMQ communication    
    def consumer(self):
        try:
            self.channel_q.basic_consume(queue=self.queue, on_message_callback=self.callback, auto_ack=True)
            self.channel_q.start_consuming()
        except Exception as e:
            if self.channel_q:
                self.logwrite(ERROR, "The communication of server was disconnected!")
            


    def callback(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.logwrite(INFO, msg)

        param = cmd.split()

        self.busy = False

        if param[0] == CMD_CORESTART:
            self.send_message(CMD_VERSION)

        elif param[0] == CMD_VERSION:
            self.label_ver.setText(param[1])

        elif param[0] == CMD_MEASURETIME:
            str_mea_time = "%.3f" % self.measured_durationT
            self.label_measured_time.setText(str_mea_time)

        elif param[0] == CMD_INITIALIZE1:            
            info = "%s (%d)" % (self.label_ver.Text(), param[1])
            self.label_ver.setText(info)
        
        elif param[0] == CMD_INITIALIZE2:
            pass
        elif param[0] == CMD_RESET:
            pass
        elif param[0] == CMD_DOWNLOAD:
            pass
        elif param[0] == CMD_SETDETECTOR:
            pass
        elif param[0] == CMD_ERRCOUNT:
            pass
        elif param[0] == CMD_SETRAMPPARAM:
            pass
        elif param[0] == CMD_SETFSPARAM:
            pass         

        elif param[0] == CMD_ACQUIRERAMP:
            self.prog_timer.stop()
            self.cur_prog_step = 100
            self.prog_sts.setValue(self.cur_prog_step)

            show_cur_cnt = "%d / %s" % (self.cur_cnt, self.e_repeat.text())
            if self.cur_cnt < int(self.e_repeat.text()):
                self.acquireramp()
            else:
                self.cur_cnt = 0

        elif param[0] == CMD_STOPACQUISITION:
            pass

        elif param[0] == CMD_WRITEASICREG:
            pass

        elif param[0] == CMD_READASICREG:
            _text = str(hex(param[2]))[2:6]
            if param[1] == self.e_addr_Vreset.text():
                self.e_read_Vreset.setText(_text)
            elif param[1] == self.e_addr_Dsub.text():
                self.e_read_Dsub.setText(_text)
            elif param[1] == self.e_addr_Vbiasgate.text():
                self.e_read_Vbiasgate.setText(_text)
            elif param[1] == self.e_addr_Vrefmain.text():
                self.e_read_Vrefmain.setText(_text)
            else:
                self.e_read_input.setText(_text)

        elif param[0] == CMD_GETTELEMETRY:
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

        msg = "%s %d" % (CMD_SETFSMODE, self.samplingMode)
        self.send_message(msg)


    def init_events(self):
        
        self.cmb_ouput_channels.currentTextChanged.connect(self.change_channel)
        self.btn_initialize1.clicked.connect(self.initialize1)
        self.btn_initialize2.clicked.connect(self.initialize2)
        self.btn_reset.clicked.connect(self.reset)
        self.btn_download_MCD.clicked.connect(self.downloadMCD)
        self.btn_set_detector.clicked.connect(self.set_detector)
        self.btn_error_cnt.clicked.connect(self.err_count)

        self.radio_UTR.clicked.connect(self.click_UTR)
        self.radio_CDS.clicked.connect(self.click_CDS)
        self.radio_CDSNoise.clicked.connect(self.click_CDSNoise)
        self.radio_Fowler.clicked.connect(self.click_Fowler)

        self.radio_exp_time.clicked.connect(self.judge_exp_time)
        self.radio_fowler_number.clicked.connect(self.judge_fowler_number)

        #self.e_fowler_number.returnPressed.connect(self.judge_param)

        self.btn_set_param.clicked.connect(self.set_parameter)

        self.chk_ROI_mode.clicked.connect(self.set_ROImode)

        self.btn_acquireramp.clicked.connect(self.acquireramp)
        self.btn_stop.clicked.connect(self.stop_acquistion)

        self.chk_show_fits.clicked.connect(self.show_fits)

        self.btn_get_telemetry.clicked.connect(self.get_telemetry)

        # path
        self.btn_find_config_dir.clicked.connect(lambda: self.find_dir(CONFIG_DIR))
        self.btn_find_MACIE_reg.clicked.connect(lambda: self.find_dir(MACIE_FILE))
        self.btn_find_ASIC_firware.clicked.connect(lambda: self.find_dir(ASIC_FILE))
        self.btn_find_img_dir.clicked.connect(lambda: self.find_dir(IMG_DIR))

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
        self.send_message(msg)


    def initialize2(self):

        if self.busy:
            return
        self.busy = True

        self.send_message(CMD_INITIALIZE2)


    def reset(self):

        if self.busy:
            return
        self.busy = True

        self.send_message(CMD_RESET)


    def downloadMCD(self):

        if self.busy:
            return
        self.busy = True

        self.send_message(CMD_DOWNLOAD)


    def set_detector(self):

        if self.busy:
            return
        self.busy = True

        msg = "%s %d %s" % (CMD_SETDETECTOR, MUX_TYPE, self.cmb_ouput_channels.currentText())
        self.send_message(msg)


    def err_count(self):

        if self.busy:
            return
        self.busy = True

        self.send_message(CMD_ERRCOUNT)


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
                self.logwrite(WARNING, "please change 'exposure time'!")
                return False

        elif self.radio_fowler_number.isChecked():
            _fowler_time = self.expTime - T_frame * _fowler_num
            if _fowler_time < T_minFowler:
                #dialog box
                self.logwrite(WARNING, "please change 'fowler sampling number'!")
                return False            

        else:
            self.logwrite(WARNING, "Please select 'Exp. Time' or 'N. Fowler' for judgement!")
            return False

        return True
        

    def set_parameter(self):

        if self.busy:
            return
        self.busy = True

        if self.samplingMode == FOWLER_MODE and self.judge_param() == False:
            return

        resets = int(self.e_resets.text())
        reads = int(self.e_reads.text())
        groups = int(self.e_groups.text())
        ramps = int(self.e_ramps.text())

        self.cal_waittime = 0.0
        if self.samplingMode == UTR_MODE:
            drops = int(self.e_drops.text())

            self.expTime = (T_frame * reads * groups) + (T_frame * drops * (groups -1 ))
            self.cal_waittime = T_br + ((T_frame * resets) + self.expTime) * ramps
            
            msg = "%s %d %d %d %d %d" % (CMD_SETRAMPPARAM, resets, reads, groups, drops, ramps)
            self.send_message(msg)

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
                self.expTime = fowlerTime + T_frame * reads

                str_exp_time = "%.3f" % self.expTime
                self.e_exp_time.setText(str_exp_time)

            self.e_reads.setText(self.e_fowler_number.text())
            self.cal_waittime = T_br + ((T_frame * resets) + fowlerTime + (2 * T_frame * reads)) * ramps
  
            msg = "%s %d %d %d %.3f %d" % (CMD_SETFSPARAM, resets, reads, groups, fowlerTime, ramps)
            self.send_message(msg)
        
        str_caltime = "%.3f" % self.cal_waittime
        self.label_calculated_time.setText(str_caltime)


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

        if self.busy:
            return
        self.busy = True

        if self.chk_ROI_mode.isChecked():
            self.x_start = int(self.e_x_start.text())
            self.x_stop = int(self.e_x_stop.text())
            self.y_start = int(self.e_y_start.text())
            self.y_stop = int(self.e_y_stop.text())
            msg = "%s %d %d %d %d" % (CMD_SETWINPARAM, self.x_start, self.x_stop, self.y_start, self.y_stop)
            self.send_message(msg)

        msg = "%s %d" % (CMD_SAVEAS, self.chk_autosave.isChecked())
        self.send_message(msg)
        
        self.cur_cnt += 1

        self.label_measured_time.setText("0.0")

        self.prog_timer = QTimer(self)
        self.prog_timer.setInterval(self.cal_waittime*10)
        self.prog_timer.timeout.connect(self.show_progressbar)

        self.cur_prog_step = 0
        self.prog_sts.setValue(self.cur_prog_step)
        self.prog_timer.start()
        
        msg = "%s %d" % (CMD_ACQUIRERAMP, self.chk_ROI_mode.isChecked())
        self.send_message(msg)  


    def show_progressbar(self):
        if self.cur_prog_step >= 100:
            self.logwrite(INFO, "progress bar end!!!")
            return
        
        self.cur_prog_step += self.cal_waittime * 2
        self.prog_sts.setValue(self.cur_prog_step)       
        self.logwrite(INFO, self.cur_prog_step)



    def stop_acquistion(self):
        if self.cur_prog_step == 0:
            return

        self.prog_timer.stop()
        
        self.send_message(CMD_STOPACQUISITION)


    def show_fits(self):
        msg = "%s %d" % (CMD_SHOWFITS, self.chk_show_fits.isChecked())
        self.send_message(CMD_SHOWFITS)


    def get_telemetry(self):

        if self.busy:
            return
        self.busy = True

        self.send_message(CMD_GETTELEMETRY)


    def find_dir(self, find_option):
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

    
    def write_addr(self, addr, value):
        if self.busy:
            return
        self.busy = True

        if value == "":
            return 

        _addr = int("0x" + addr, 16)
        _value = int("0x" + value, 16)

        msg = "%s %d %d" % (CMD_WRITEASICREG, _addr, _value)
        self.send_message(msg)
        


    def read_addr(self, addr):        
        if addr == "":
            return

        _addr = int("0x" + addr, 16)

        msg = "%s %d" % (CMD_READASICREG, _addr)
        self.send_message(msg)

        
if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False

    app = QApplication(sys.argv)

    dc = MainWindow()
    dc.show()

    app.exec()