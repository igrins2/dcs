# -*- coding: utf-8 -*-

"""
Created on Aug 4, 2022

Modified on Aug 28, 2022

@author: hilee
"""

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from ui_dcs import *
from DC_core import *
from DC_def import *
from DC_server import *

import threading

class MainWindow(Ui_MainWindow, QMainWindow):

    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Detector Control System 0.1")

        self.dc = DC()
        #self.dc.start()

        self.label_connection_sts.setText("ICS")

        # row-by-row combine fix!!! 9 line!
        self.label_21.hide()
        self.cmb_combine_line.hide()

        #Load: cofiguration files
        self.e_config_dir.setText(self.dc.loadfile_path)
        self.e_MACIE_reg.setText(self.dc.macie_file)
        self.e_ASIC_firmware.setText(self.dc.asic_file)
        self.e_img_dir.setText(self.dc.exe_path)
        
        #Load: version, SetGigeTimeout, Output Channel
        self.label_ver.setText(self.dc.LibVersion())
        self.e_timeout.setText(self.dc.gige_timeout)
        self.cmb_ouput_channels.setCurrentText(self.dc.output_channel)

        self.ics_sts = False

        self.set_samplingmode(self.dc.samplingMode)
        self.set_param_ui(1, 1, 1, 0, 1)
        self.e_exp_time.setText("1.63")

        self.radio_exp_time.setChecked(True)
        self.radio_fowler_number.setChecked(False)

        self.init_events()

        self.chk_autosave.setText("Save AS")
        self.chk_autosave.setChecked(False)

        self.cur_cnt = 0
        self.cur_prog_step = 0

        # RabbitMQ connect
        self.serv = ICS_SERVER(self.dc.ics_ip_addr, self.dc.ics_id, self.dc.ics_pwd, self.dc.ics_ex, self.dc.ics_q, "direct", self.dc.dcs_ex, self.dc.dcs_q)
        self.connection, self.channel = self.serv.connect_to_server()

        if self.connection:
            # RabbitMQ: define consumer
            self.queue = self.serv.define_consumer(self.channel)
    
            th = threading.Thread(target=self.consumer)
            th.start()
            #th.join()

            self.show_alarm()

    
    def closeEvent(self, event: QCloseEvent) -> None:
        for th in threading.enumerate():
            print(th.name + " exit.")

        if self.queue:
            self.channel.stop_consuming()
            self.connection.close()

        return super().closeEvent(event)


    def set_samplingmode(self, mode):
        if mode == UTR_MODE:
            self.radio_UTR.setChecked(True)
        elif mode == CDS_MODE:
            self.radio_CDS.setChecked(True)
        elif mode == CDSNOISE_MODE:
            self.radio_CDSNoise.setChecked(True)
        elif mode == FOWLER_MODE:
            self.radio_Fowler.setChecked(True)


    def set_param_ui(self, resets, reads, groups, drops, ramps):
        if self.dc.samplingMode == UTR_MODE:
            self.e_reads.setEnabled(True)
            self.e_groups.setEnabled(True)
            self.e_drops.setEnabled(True)
            self.e_ramps.setEnabled(True)

            self.radio_exp_time.hide()
            self.radio_fowler_number.hide()

            self.e_exp_time.setEnabled(False)
            self.e_fowler_number.setEnabled(False)

            self.dc.drops = drops
            self.label_drops.setText("Drops")

        else:
            self.e_reads.setEnabled(False)
            self.e_groups.setEnabled(False)
            self.e_drops.setEnabled(False)
            self.e_ramps.setEnabled(False)
            
            self.dc.fowlerTime = drops
            self.label_drops.setText("T.Fowler")

            self.e_fowler_number.setText(str(reads))

            if self.dc.samplingMode == FOWLER_MODE:
                
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

        self.dc.resets = resets
        self.dc.reads = reads
        self.dc.groups = groups
        self.dc.ramps = ramps


    def init_events(self):
        
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


    # RabbitMQ communication    
    def consumer(self):
        try:
            self.channel.basic_consume(queue=self.queue,on_message_callback=self.callback, auto_ack=True)
            self.channel.start_consuming()
        except Exception as e:
            if self.channel:
                self.dc.logwrite(BOTH, "The communication of server was disconnected!")

                #self.channel.stop_consuming()


    def callback(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        print(msg)

        if cmd == "alive?":
            self.ics_sts = True
            self.dc.send_message("alive")     
        
        elif cmd == CMD_INITIALIZE1:
            self.initialize1(True)
        
        elif cmd == CMD_INITIALIZE2:
            self.initialize2()
            self.reset(True)
        
        elif cmd == CMD_DOWNLOAD:
            self.downloadMCD(True)
        
        elif cmd == CMD_SETDETECTOR:
            self.set_detector(True)
        
        elif cmd.find(CMD_SETFSMODE) >= 0:
            param = cmd.split()
            self.set_fsmode(int(param[1]))

        elif cmd.find(CMD_SETWINPARAM) >= 0:
            param = cmd.split()

            try:
                self.chk_ROI_mode.setChecked(True)

                self.e_x_start.setText(param[1])
                self.e_x_stop.setText(param[2])
                self.e_y_start.setText(param[3])
                self.e_y_stop.setText(param[4])
            except:
                self.chk_ROI_mode.setChecked(False)

            self.set_ROImode()
        
        elif cmd.find(CMD_SETRAMPPARAM) >= 0 or cmd.find(CMD_SETFSPARAM) >= 0:
            param = cmd.split()
            self.e_resets.setText(param[1])
            self.e_reads.setText(param[2])
            self.e_groups.setText(param[3])
            self.e_drops.setText(param[4])
            self.e_ramps.setText(param[5])

            if self.dc.samplingMode == UTR_MODE:
                self.set_param_ui(int(param[1]), int(param[2]), int(param[3]), int(param[4]), int(param[5]))
            else:
                self.set_param_ui(int(param[1]), int(param[2]), int(param[3]), float(param[4]), int(param[5]))
            self.set_parameter(True)

        elif cmd == CMD_ACQUIRERAMP:
            self.start_acquisition(True)

        elif cmd == CMD_STOPACQUISITION:
            self.stop_acquistion(True)
        

    def show_alarm(self):
        textcolor = "black"
        if self.ics_sts == True:
            textcolor = "green"
        else:
            textcolor = "red"
        
        label = "QLabel {color:%s}" % textcolor
        self.label_connection_sts.setStyleSheet(label)

        self.ics_sts = False
        timer = QTimer(self)
        timer.singleShot(180*1000, self.show_alarm)  #after 180sec


    def set_fsmode(self, mode):
        sts = [False for _ in range(4)]

        if mode == UTR_MODE:
            sts = [True, False, False, False]
        elif mode == CDS_MODE:
            sts = [False, True, False, False]
        elif mode == CDSNOISE_MODE:
            sts = [False, False, True, False]
        elif mode == FOWLER_MODE:
            sts = [False, False, False, True]

        self.radio_UTR.setChecked(sts[0])
        self.radio_CDS.setChecked(sts[1])
        self.radio_CDSNoise.setChecked(sts[2])
        self.radio_Fowler.setChecked(sts[3])
        self.dc.samplingMode = mode

        self.dc.send_message(CMD_SETFSMODE + " OK")


    # ----------------------------------------------------------------------
    # Buttons           

    def initialize1(self, ics=False):

        if self.dc.busy:
            return

        res = self.dc.Initialize(int(self.e_timeout.text()), ics)
        info = "%s (%d)" % (self.dc.LibVersion(), self.dc.macieSN)
        self.label_ver.setText(info)
        #if res == True:
        #    self.btn_initialize1.setEnabled(False)


    def initialize2(self):

        if self.dc.busy:
            return

        #if self.dc.Initialize2() == True:
        #    self.btn_initialize2.setEnabled(False)


    def reset(self, ics=False):

        if self.dc.busy:
            return

        self.dc.ResetASIC(ics)


    def downloadMCD(self, ics=False):

        if self.dc.busy:
            return

        self.dc.DownloadMCD(ics)


    def set_detector(self, ics=False):

        if self.dc.busy:
            return

        self.dc.SetDetector(MUX_TYPE, int(self.cmb_ouput_channels.currentText()), ics)


    def err_count(self):

        if self.dc.busy:
            return

        self.dc.GetErrorCounters()


    def click_UTR(self):
        self.dc.samplingMode = UTR_MODE
        self.set_param_ui(1, 1, 1, 0, 1)


    def click_CDS(self):
        self.dc.samplingMode = CDS_MODE
        self.set_param_ui(1, 1, 1, T_minFowler, 1)


    def click_CDSNoise(self):
        self.dc.samplingMode = CDSNOISE_MODE
        self.set_param_ui(1, 1, 1, T_minFowler, 2)


    def click_Fowler(self):
        self.dc.samplingMode = FOWLER_MODE
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
        self.dc.expTime = float(self.e_exp_time.text())
        _fowler_num = int(self.e_fowler_number.text())

        _fowler_time = float(self.e_drops.text())

        if self.radio_exp_time.isChecked():
            _max_fowler_number = int((self.dc.expTime - T_minFowler) / T_frame)
            if _fowler_num > _max_fowler_number:
                #dialog box
                print("please change 'exposure time'!")
                return False

        elif self.radio_fowler_number.isChecked():
            _fowler_time = self.dc.expTime - T_frame * _fowler_num
            if _fowler_time < T_minFowler:
                #dialog box
                print("please change 'fowler sampling number'!")
                return False            

        else:
            print("Please select 'Exp. Time' or 'N. Fowler' for judgement!")
            return False

        return True
        

    def set_parameter(self, ics=False):

        if self.dc.samplingMode == FOWLER_MODE and self.judge_param() == False:
            return

        self.dc.resets = int(self.e_resets.text())
        self.dc.reads = int(self.e_reads.text())
        self.dc.groups = int(self.e_groups.text())
        self.dc.ramps = int(self.e_ramps.text())

        self.cal_waittime = 0.0
        if self.dc.samplingMode == UTR_MODE:
            self.dc.drops = int(self.e_drops.text())

            self.dc.expTime = (T_frame * self.dc.reads * self.dc.groups) + (T_frame * self.dc.drops * (self.dc.groups -1 ))
            self.cal_waittime = T_br + ((T_frame * self.dc.resets) + self.dc.expTime) * self.dc.ramps
            
            self.dc.SetRampParam(self.dc.resets, self.dc.reads, self.dc.groups, self.dc.drops, self.dc.ramps, ics)   

            str_exp_time = "%.3f" % self.dc.expTime
            self.e_exp_time.setText(str_exp_time)     

        else:
            #self.dc.fowlerTime = float(self.e_drops.text())
            #exptime = self.dc.fowlerTime + T_frame * self.dc.reads

            self.dc.expTime = float(self.e_exp_time.text())
            if self.dc.samplingMode == FOWLER_MODE:
                #if self.radio_fowler_number.isChecked():
                self.e_reads.setText(self.e_fowler_number.text())
                self.dc.reads = int(self.e_reads.text())
                if self.radio_fowler_number.isChecked():
                    self.e_reads.setText(self.e_fowler_number.text())
                    self.dc.reads = int(self.e_reads.text())

                self.dc.fowlerTime = self.dc.expTime - T_frame * self.dc.reads
                str_fowlerTime = "%.3f" % self.dc.fowlerTime
                
                self.e_drops.setText(str_fowlerTime)
            
            else:
                self.dc.expTime = self.dc.fowlerTime + T_frame * self.dc.reads

                str_exp_time = "%.3f" % self.dc.expTime
                self.e_exp_time.setText(str_exp_time)

            self.e_reads.setText(self.e_fowler_number.text())
            self.cal_waittime = T_br + ((T_frame * self.dc.resets) + self.dc.fowlerTime + (2 * T_frame * self.dc.reads)) * self.dc.ramps
            
            self.dc.SetFSParam(self.dc.resets, self.dc.reads, self.dc.groups, self.dc.fowlerTime, self.dc.ramps, ics)
        
        str_caltime = "%.3f" % self.cal_waittime
        self.label_calculated_time.setText(str_caltime)


    def set_ROImode(self):
        if self.chk_ROI_mode.isChecked():
            self.dc.ROIMode = True
        else:
            self.dc.ROIMode = False
       

    # thread
    def acquireramp(self):

        if self.dc.busy:
            return

        if self.dc.ROIMode:
            self.dc.x_start = int(self.e_x_start.text())
            self.dc.x_stop = int(self.e_x_stop.text())
            self.dc.y_start = int(self.e_y_start.text())
            self.dc.y_stop = int(self.e_y_stop.text())

        self.dc.logwrite(BOTH, "[TEST] " + CMD_ACQUIRERAMP + " Start")

        self.dc.save_as = self.chk_autosave.isChecked()
        
        self.cur_cnt += 1

        self.start_acquisition()
        
        show_cur_cnt = "%d / %s" % (self.cur_cnt, self.e_repeat.text())
        self.dc.logwrite(BOTH, "[TEST] " + show_cur_cnt)
        if self.cur_cnt < int(self.e_repeat.text()):
            timer = QTimer(self)
            #timer.singleShot(self.cal_waittime + 0.1, self.acquireramp)
            timer.singleShot(0.1, self.acquireramp)
        else:
            self.cur_cnt = 0
        #th = threading.Thread(target=self.acquireramp_sub)
        #th.start()
        #th.join()


    def start_acquisition(self, ics=False):
        if self.dc.ROIMode:
            self.dc.AcquireRamp_window()
            self.dc.ImageAcquisition_window(ics)
        else:
            self.dc.AcquireRamp()
            self.dc.ImageAcquisition(ics)

        '''
        self.cur_prog_step = 0
        self.prog_sts.setValue(1000)
        self.prog_sts.setAlignment(Qt.AlignCenter)
        self.prog_sts.resetFormat()
        '''
    
        timer = QTimer(self)
        timer.singleShot(self.cal_waittime*10, self.show_progressbar)

        self.cur_prog_step = 0
        self.prog_sts.setValue(self.cur_prog_step)


    def show_progressbar(self):
        if self.cur_prog_step >= 100:
            print("progress bar end!!!")
            str_mea_time = "%.3f" % self.dc.measured_durationT
            self.label_measured_time.setText(str_mea_time)
            return
        
        self.cur_prog_step += 1
        self.prog_sts.setValue(self.cur_prog_step)       
        print(self.cur_prog_step)

        timer = QTimer(self)
        timer.singleShot(self.cal_waittime*10, self.show_progressbar)
      


    def stop_acquistion(self, ics=False):
        self.dc.StopAcquisition(ics)


    def show_fits(self):
        self.dc.showfits = self.chk_show_fits.isChecked()
        #print(self.dc.showfits)
        #ds9 = WORKING_DIR + 'ds9'
        #subprocess.run([ds9, '-b', "", '-o', 'newfile'], shell = True)

        timer = QTimer(self)
        timer.singleShot(self.cal_waittime*10, self.show_progressbar)

        self.cur_prog_step = 0
        self.prog_sts.setValue(self.cur_prog_step)


    def get_telemetry(self):
        self.dc.GetTelemetry()


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
        if self.dc.handle == 0:
            return

        if value == "":
            return 

        _addr = int("0x" + addr, 16)
        _value = int("0x" + value, 16)

        res = self.dc.write_ASIC_reg(_addr, _value)
        if res == MACIE_OK:
            result = RET_OK
        else:
            result = RET_FAIL
        msg = "WriteASICReg %s - h%04x = %04x" % (result, _addr, _value)
        self.dc.logwrite(BOTH, msg)


    def read_addr(self, addr):
        if self.dc.handle == 0:
            return
        
        if addr == "":
            return

        _addr = int("0x" + addr, 16)

        val, sts = self.dc.read_ASIC_reg(_addr)
        if sts == MACIE_OK:
            result = RET_OK
            _value = val[0]
        else:
            result = RET_FAIL
            _value = 0

        msg = "ReadASICReg %s - h%04x = %04x" % (result, _addr, _value)     #need to check
        self.dc.logwrite(BOTH, msg)

        _text = str(hex(_value))[2:6]
        if addr == self.e_addr_Vreset.text():
            self.e_read_Vreset.setText(_text)
        elif addr == self.e_addr_Dsub.text():
            self.e_read_Dsub.setText(_text)
        elif addr == self.e_addr_Vbiasgate.text():
            self.e_read_Vbiasgate.setText(_text)
        elif addr == self.e_addr_Vrefmain.text():
            self.e_read_Vrefmain.setText(_text)
            self.dc.V_refmain = hex(_value)
        else:
            self.e_read_input.setText(_text)


        
if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False

    app = QApplication(sys.argv)

    dc = MainWindow()
    dc.show()

    app.exec()