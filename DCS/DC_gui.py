# -*- coding: utf-8 -*-

"""
Created on Aug 4, 2022

Modified on Jan 19, 2023

@author: hilee
"""

import sys, os
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

from ui_dcs import *
from DC_def import *
from DC_core import *

import threading
import subprocess
import time as ti
import datetime

from shutil import copyfile

class MainWindow(Ui_Dialog, QMainWindow):

    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Detector Control System 0.2")

        self.log = LOG(WORKING_DIR + "DCS")

        self.core = DC()

        self.log.send(IAM, INFO, "start DCS gui!!!")        

        #start core!!!
        self.proc_core = None
        self.proc_core = subprocess.Popen(['python', WORKING_DIR + 'workspace/dcs/DCS/DC_core.py'])

        #-------------------------------------------------------
        # load ini file
        cfg = sc.LoadConfig(WORKING_DIR + "DCS/DCS.ini")

        # ICS
        self.ics_ip_addr = cfg.get('ICS', 'ip_addr')
        self.ics_id = cfg.get('ICS', 'id')
        self.ics_pwd = cfg.get('ICS', 'pwd')

        self.ics_ex = cfg.get('ICS', 'ics_exchange')
        self.ics_q = cfg.get('ICS', 'ics_routing_key')

        self.dcs_ex = cfg.get('ICS', 'dcs_exchange')
        self.dcs_q = cfg.get('ICS', 'dcs_routing_key')
        
        self.asic_Vreset = cfg.get("DC", 'Vreset')
        self.asic_Dsub = cfg.get("DC", 'Dsub')
        self.asic_VBiasGate = cfg.get("DC", 'VBiasGate')
        self.asic_VrefMain = cfg.get("DC", 'VrefMain')

        self.e_write_Vreset.setText(self.asic_Vreset)
        self.e_write_Dsub.setText(self.asic_Dsub)
        self.e_write_Vbiasgate.setText(self.asic_VBiasGate)
        self.e_write_Vrefmain.setText(self.asic_VrefMain)

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
        self.e_config_dir.setText(self.core.loadfile_path)
        self.e_MACIE_reg.setText(self.core.macie_file)
        self.e_ASIC_firmware.setText(self.core.asic_file)
        self.e_img_dir.setText(self.core.exe_path)
        
        #Load: version, SetGigeTimeout, Output Channel
        self.e_timeout.setText(self.gige_timeout)
        self.cmb_ouput_channels.setCurrentText(self.output_channel)

        self.radio_UTR.setChecked(True)

        self.set_param_ui(1, 1, 1, 0, 1)
        self.e_exp_time.setText(str(self.core.expTime))
        self.cal_waittime = 0.0        

        self.radio_exp_time.setChecked(True)
        self.radio_fowler_number.setChecked(False)

        self.chk_autosave.setText("Save AS")
        self.chk_autosave.setChecked(False)

        self.use_saveAs()
        self.e_user_dir.setText(WORKING_DIR + "DCS/Data/")

        self.cur_cnt = 0
        self.fitsfullpath = ""

        self.prog_sts.setValue(0)

        self.simulation_mode = False

        self.init1 = False  #for ics

        self.producer_ics = None
        self.consumer_ics = None

        self.busy = False
        self.stop_clicked = False

        self.cur_prog_step = 0
        self.prog_timer = QTimer(self)
        self.prog_timer.timeout.connect(self.show_progressbar)

        self.elapsed_timer = QTimer(self)
        self.elapsed_timer.setInterval(0.001)
        self.elapsed_timer.timeout.connect(self.show_elapsed)
        
        self.connect_to_server_ics_ex()
        self.connect_to_server_ics_q()    

        # ----------------------------

        self.label_ver.setText(self.core.LibVersion())

    
    def closeEvent(self, event: QCloseEvent) -> None:
        self.log.send(IAM, INFO, "DCS closing...")

        for th in threading.enumerate():
            self.log.send(IAM, INFO, th.name + " exit.")

        if self.proc_core != None:
            self.proc_core.terminate()

        self.log.send(IAM, INFO, "DCS closed!")

        self.producer_ics.__del__()

        return super().closeEvent(event)


    #-------------------------------
    def connect_to_server_ics_ex(self):
        # RabbitMQ connect        
        self.producer_ics = MsgMiddleware(IAM, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dcs_ex)
        self.producer_ics.connect_to_server()
        self.producer_ics.define_producer()


    def connect_to_server_ics_q(self):
        # RabbitMQ connect
        self.consumer_ics = MsgMiddleware(IAM, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.ics_ex)
        self.consumer_ics.connect_to_server()
        self.consumer_ics.define_consumer(self.ics_q, self.callback_ics)

        th = threading.Thread(target=self.consumer_ics.start_consumer)
        th.daemon = True
        th.start() 


    def callback_ics(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()

        if param[0] == ALIVE:
            if self.init1:
                param = cmd.split()
                msg = "%s %s" % (ALIVE, IAM)
                self.producer_ics.send_message(self.dcs_q, msg)   
            return 

        if param[1] != IAM:
            return

        msg = "receive: %s" % cmd
        self.log.send(IAM, INFO, msg)

        self.simulation_mode = bool(int(param[2]))

        if self.simulation_mode:
            ti.sleep(1)

            _t = datetime.datetime.utcnow()
            cur_datetime = [_t.year, _t.month, _t.day, _t.hour, _t.minute, _t.second, _t.microsecond]
            folder_name = "%04d%02d%02d_%02d%02d%02d" % (cur_datetime[0], cur_datetime[1], cur_datetime[2], cur_datetime[3], cur_datetime[4], cur_datetime[5])

            msg = "%s %s %s" % (param[0], IAM, folder_name)
            self.producer_ics.send_message(self.dcs_q, msg)
            
            msg = "send: %s" % msg
            self.log.send(IAM, INFO, msg)
            return

        if self.init1 is False:
            msg = "%s %s TRY" % (param[0], IAM)
            self.producer_ics.send_message(self.dcs_q, msg)
            return     
                
        if param[0] == CMD_INITIALIZE2:
            self.producer.send_message(self.gui_q, CMD_INITIALIZE2_ICS)

        elif param[0] == CMD_SETFSPARAM:
            msg = "%s %s %s %s %s %s %s" % (CMD_SETFSPARAM_ICS, param[3], param[4], param[5], param[6], param[7], param[8])
            self.producer.send_message(self.gui_q, msg)

        elif param[0] == CMD_STOPACQUISITION:
            self.producer.send_message(self.gui_q, CMD_STOPACQUISITION_ICS)
    
        #------------------------------

        elif param[0] == CMD_INITIALIZE2_ICS:
            msg = "%s %s" % (CMD_INITIALIZE2, IAM)
            self.producer_ics.send_message(self.dcs_q, msg)

        elif param[0] == CMD_SETFSPARAM_ICS:
            msg = "%s %s %.3f %s " % (CMD_SETFSPARAM, IAM, float(param[1]), param[2])   #folder_name
            self.producer_ics.send_message(self.dcs_q, msg)

        elif param[0] == CMD_STOPACQUISITION_ICS:
            msg = "%s %s" % (CMD_STOPACQUISITION, IAM)
            self.producer_ics.send_message(self.dcs_q, msg)   



    def set_param_ui(self, resets, reads, groups, drops, ramps):
        if self.core.samplingMode == UTR_MODE:
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

            if self.core.samplingMode == FOWLER_MODE:
                
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
        self.btn_download_MCD.clicked.connect(self.downloadMCD)
        self.btn_set_detector.clicked.connect(self.set_detector)
        self.btn_error_cnt.clicked.connect(self.err_count)

        self.radio_UTR.clicked.connect(self.click_UTR)
        self.radio_CDS.clicked.connect(self.click_CDS)
        self.radio_CDSNoise.clicked.connect(self.click_CDSNoise)
        self.radio_Fowler.clicked.connect(self.click_Fowler)

        self.radio_exp_time.clicked.connect(self.judge_exp_time)
        self.radio_fowler_number.clicked.connect(self.judge_fowler_number)

        self.btn_set_param.clicked.connect(self.set_parameter)

        self.chk_ROI_mode.clicked.connect(self.set_ROImode)

        self.btn_acquireramp.clicked.connect(self.acquireramp)
        self.btn_stop.clicked.connect(self.stop_acquistion)

        self.chk_show_fits.clicked.connect(self.show_fits)

        self.btn_get_telemetry.clicked.connect(self.get_telemetry)

        self.btn_connect_icsq.setHidden(True)
        self.btn_connect_guiq.setHidden(True)
        self.btn_connect_coreq.setHidden(True)

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

        self.QWidgetBtnColor(self.btn_initialize1, "yellow", "blue")
        if self.core.Initialize(int(self.e_timeout.text())):
            self.busy = False
            self.init1 = True
            self.QWidgetBtnColor(self.btn_initialize1, "white", "green")

            info = "%s (%s)" % (self.label_ver.text(), self.core.macieSN)
            self.label_ver.setText(info)
            self.btn_initialize1.setEnabled(False)


    def initialize2(self):
        if self.busy:
            return
        self.busy = True

        self.QWidgetBtnColor(self.btn_initialize2, "yellow", "blue")
        if self.core.Initialize2():
            self.busy = False
            self.QWidgetBtnColor(self.btn_initialize2, "black", "white")


    def reset(self):
        if self.busy:
            return
        self.busy = True

        self.QWidgetBtnColor(self.btn_reset, "yellow", "blue")

        if self.core.ResetASIC():
            self.busy = False
            self.QWidgetBtnColor(self.btn_reset, "black", "white")


    def downloadMCD(self):
        if self.busy:
            return
        self.busy = True

        self.QWidgetBtnColor(self.btn_download_MCD, "yellow", "blue")

        if self.core.DownloadMCD():
            self.busy = False
            self.QWidgetBtnColor(self.btn_download_MCD, "black", "white")


    def set_detector(self):
        if self.busy:
            return
        self.busy = True

        self.QWidgetBtnColor(self.btn_set_detector, "yellow", "blue")
        if self.core.SetDetector(MUX_TYPE, int(self.cmb_ouput_channels.currentText())):
            self.busy = False
            self.QWidgetBtnColor(self.btn_set_detector, "black", "white")


    def err_count(self):
        if self.busy:
            return
        self.busy = True

        self.QWidgetBtnColor(self.btn_error_cnt, "yellow", "blue")
        if self.core.GetErrorCounters():
            self.busy = False
            self.QWidgetBtnColor(self.btn_error_cnt, "black", "white")

            self.read_addr(self.e_addr_Vreset.text())
            self.read_addr(self.e_addr_Dsub.text())
            self.read_addr(self.e_addr_Vbiasgate.text())
            self.read_addr(self.e_addr_Vrefmain.text())


    def click_UTR(self):
        self.core.samplingMode = UTR_MODE
        self.set_param_ui(1, 1, 1, 0, 1)


    def click_CDS(self):
        self.core.samplingMode = CDS_MODE
        self.set_param_ui(1, 1, 1, T_minFowler, 1)


    def click_CDSNoise(self):
        self.core.samplingMode = CDSNOISE_MODE
        self.set_param_ui(1, 1, 1, T_minFowler, 2)


    def click_Fowler(self):
        self.core.samplingMode = FOWLER_MODE
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
        self.core.expTime = float(self.e_exp_time.text())
        _fowler_num = int(self.e_fowler_number.text())

        _fowler_time = float(self.e_drops.text())

        if self.radio_exp_time.isChecked():
            _max_fowler_number = int((self.core.expTime - T_minFowler) / T_frame)
            if _fowler_num > _max_fowler_number:
                #dialog box
                QMessageBox.warning(self, WARNING, "please change 'exposure time'!")
                self.log.send(IAM, WARNING, "please change 'exposure time'!")
                return False

        elif self.radio_fowler_number.isChecked():
            _fowler_time = self.core.expTime - T_frame * _fowler_num
            if _fowler_time < T_minFowler:
                #dialog box
                QMessageBox.warning(self, WARNING, "please change 'fowler sampling number'!")
                self.log.send(IAM, WARNING, "please change 'fowler sampling number'!")
                return False            

        else:
            self.log.send(IAM, WARNING, "Please select 'Exp. Time' or 'N. Fowler' for judgement!")
            return False

        return True
        

    def set_parameter(self):
        if self.busy:
            return
        self.busy = True

        self.QWidgetBtnColor(self.btn_set_param, "yellow", "blue")

        if self.core.samplingMode == FOWLER_MODE and self.judge_param() == False:
            self.busy = False
            return

        resets = int(self.e_resets.text())
        reads = int(self.e_reads.text())
        groups = int(self.e_groups.text())
        ramps = int(self.e_ramps.text())

        self.cal_waittime = 0.0
        if self.core.samplingMode == UTR_MODE:
            drops = int(self.e_drops.text())

            self.core.expTime = (T_frame * reads * groups) + (T_frame * drops * (groups -1 ))
            self.cal_waittime = T_br + ((T_frame * resets) + self.core.expTime) * ramps
            #print('---------------')
            #print(resets, reads, groups, drops, ramps)
            #print('---------------')
            
            if self.core.SetRampParam(resets, reads, groups, drops, ramps):
                self.busy = False
                self.QWidgetBtnColor(self.btn_set_param, "black", "white")

            str_exp_time = "%.3f" % self.core.expTime
            self.e_exp_time.setText(str_exp_time)     

        else:
            self.core.expTime = float(self.e_exp_time.text())
            if self.core.samplingMode == FOWLER_MODE:
                #if self.radio_fowler_number.isChecked():
                self.e_reads.setText(self.e_fowler_number.text())
                reads = int(self.e_reads.text())
                if self.radio_fowler_number.isChecked():
                    self.e_reads.setText(self.e_fowler_number.text())
                    reads = int(self.e_reads.text())

                fowlerTime = self.core.expTime - T_frame * reads
                str_fowlerTime = "%.3f" % fowlerTime
                
                self.e_drops.setText(str_fowlerTime)
            
            else:
                fowlerTime = float(self.e_drops.text())
                self.core.expTime = fowlerTime + T_frame * reads

                str_exp_time = "%.3f" % self.core.expTime
                self.e_exp_time.setText(str_exp_time)

            self.e_reads.setText(self.e_fowler_number.text())
            self.cal_waittime = T_br + ((T_frame * resets) + fowlerTime + (2 * T_frame * reads)) * ramps
  
            if self.core.SetFSParam(resets, reads, groups, fowlerTime, ramps):
                self.busy = False
                self.QWidgetBtnColor(self.btn_set_param, "black", "white")
        
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
        self.stop_clicked = False

        self.QWidgetBtnColor(self.btn_acquireramp, "yellow", "blue")

        if self.chk_ROI_mode.isChecked():
            self.core.x_start = int(self.e_x_start.text())
            self.core.x_stop = int(self.e_x_stop.text())
            self.core.y_start = int(self.e_y_start.text())
            self.core.y_stop = int(self.e_y_stop.text())
        
        self.cur_cnt += 1

        self.label_measured_time.setText("0.0")
        self.label_elapsed.setText("0.0")

        self.prog_timer.setInterval(int(self.cal_waittime*10))
        self.cur_prog_step = 0
        self.prog_sts.setValue(self.cur_prog_step)
        self.prog_timer.start()
        
        self.elapsed = ti.time()
        self.elapsed_timer.start()

        if self.core.AcquireRamp():
            if self.core.ImageAcquisition():
                self.busy = False
                val = "%.3f" % self.core.measured_durationT
                self.label_measured_time.setText(val)
                
                if self.chk_autosave.isChecked():
                    self.fitsfullpath = self.core.file_name
                    file = self.core.file_name.split("/")
                    path = ""
                    for i in file[1:-1]:
                        path += "/"
                        path += i
                    self.e_user_dir.setText(path)
                    self.e_user_file.setText(file[-1][:-5] + "_")

                self.QWidgetBtnColor(self.btn_acquireramp, "black", "white")

                self.cur_prog_step = 100
                self.prog_sts.setValue(self.cur_prog_step)

                show_cur_cnt = "%d / %s" % (self.cur_cnt, self.e_repeat.text())
                self.label_cur_num.setText(show_cur_cnt)
                if self.cur_cnt < int(self.e_repeat.text()):
                    self.btn_acquireramp.click()
                else:
                    self.cur_cnt = 0

        
    def show_progressbar(self):
        if self.cur_prog_step >= 100 or self.stop_clicked:
            #self.log.send(IAM, INFO, "progress bar end!!!")
            self.prog_timer.stop()
            return
        
        self.cur_prog_step += 100/self.cal_waittime
        self.prog_sts.setValue(self.cur_prog_step)       
        #self.log.send(IAM, DEBUG, self.cur_prog_step)


    def show_elapsed(self):
        cur_elapsed = ti.time() - self.elapsed
        measured = float(self.label_measured_time.text())
        if (measured > 0 and cur_elapsed >= measured) or self.stop_clicked:
            self.elapsed_timer.stop()
            return

        msg = "%.3f" % cur_elapsed
        self.label_elapsed.setText(msg)
        #print(ti.time() - self.elapsed)


    def stop_acquistion(self):
        if self.cur_prog_step > 0:
            self.prog_timer.stop()
            self.elapsed_timer.stop()
            self.stop_clicked = True

        if self.core.StopAcquisition():
            pass


    def show_fits(self):
        self.core.showfits = bool(self.chk_show_fits.isChecked())

        
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

        self.QWidgetBtnColor(self.btn_get_telemetry, "yellow", "blue")

        if self.core.GetTelemetry():
            self.busy = False
            self.QWidgetBtnColor(self.btn_get_telemetry, "black", "white")


    def find_dir_file(self, find_option):
        if find_option == IMG_DIR:
            loader = self.e_img_dir.text()
            folder = QFileDialog.getExistingDirectory(self, "Select Directory", loader)
            if folder:
                self.e_img_dir.setText(folder)
                self.core.exe_path = folder

        else:
            loader = self.e_config_dir.text()
            folder = QFileDialog.getExistingDirectory(self, "Select Directory", loader)
            if find_option == CONFIG_DIR:   
                if folder:
                    self.e_config_dir.setText(folder)
                    self.core.loadfile_path = folder
            
            elif find_option == MACIE_FILE:
                path = QFileDialog.getOpenFileName(self, "Choose File", folder, filter='*.mrf')
                if path[0]:
                    file = path[0].split('/')
                    self.e_MACIE_reg.setText(file[-1])
                    self.core.macie_file = file[-1]
            
            elif find_option == ASIC_FILE:
                path = QFileDialog.getOpenFileName(self, "Choose File", folder, filter='*.mcd')
                if path[0]:
                    file = path[0].split('/')
                    self.e_ASIC_firmware.setText(file[-1])
                    self.core.asic_file = file[-1]

    
    def asic_load(self):        

        self.write_addr(self.e_addr_Vreset.text(), self.e_write_Vreset.text(), True)
        self.write_addr(self.e_addr_Dsub.text(), self.e_write_Dsub.text(), True)
        self.write_addr(self.e_addr_Vbiasgate.text(), self.e_write_Vbiasgate.text(), True)
        self.write_addr(self.e_addr_Vrefmain.text(), self.e_write_Vrefmain.text(), True)



    def write_addr(self, addr, value, click=False):
        if value == "":
            return 

        addr_n = int("0x" + addr, 16)
        _value = int("0x" + value, 16)

        res = self.core.write_ASIC_reg(addr_n, _value)
        if res == MACIE_OK:
            result = RET_OK

            _addr = str(hex(addr_n))[2:6]

            if click and _addr == self.e_addr_Vreset.text():
                self.read_addr(self.e_addr_Vreset.text())
            elif click and _addr == self.e_addr_Dsub.text():
                self.read_addr(self.e_addr_Dsub.text())
            elif click and _addr == self.e_addr_Vbiasgate.text():
                self.read_addr(self.e_addr_Vbiasgate.text())
            elif click and _addr == self.e_addr_Vrefmain.text():
                self.read_addr(self.e_addr_Vrefmain.text())
            elif click and _addr == self.e_addr_input.text():
                self.read_addr(self.e_read_input.text())
                
        else:
            result = RET_FAIL

        msg = "WriteASICReg %s - h%04x = %04x" % (result, addr_n, _value)
        self.log.send(IAM, INFO, msg)

        
    def read_addr(self, addr):   
        if addr == "":
            return

        addr_n = int("0x" + addr, 16)

        val, sts = self.core.read_ASIC_reg(addr_n)
        if sts == MACIE_OK:
            result = RET_OK
            _value = val[0]

            _addr = str(hex(addr_n))[2:6]
            _text = str(hex(_value))[2:6]
            
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
        
        else:
            result = RET_FAIL
            _vale = 0

        msg = "ReadASICReg %s - h%04x = %04x" % (result, addr_n, _value)
        self.log.send(IAM, INFO, msg)


    def QWidgetBtnColor(self, widget, textcolor, bgcolor=None):
        if bgcolor == None:
            label = "QPushButton {color:%s}" % textcolor
            widget.setStyleSheet(label)
        else:
            label = "QPushButton {color:%s;background:%s}" % (textcolor, bgcolor)
            widget.setStyleSheet(label)

        
if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False

    app = QApplication(sys.argv)

    dc = MainWindow()
    dc.show()

    app.exec()