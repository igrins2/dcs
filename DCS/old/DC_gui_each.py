# -*- coding: utf-8 -*-

"""
Created on Aug 4, 2022

Modified on Sep 2, 2022

@author: hilee
"""

import os, sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import pika
import threading
#import subprocess

from ui_dcs import *
from DC_def import *

import RabbitMQFunc as server

class MainWindow(Ui_MainWindow, QMainWindow):

    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Detector Control System 0.1")

        # ----------------------------------------------------------
        # setting rabbitmq
        # connect to local server
        self.channel = server.connect_to_server('localhost', g_dcs_id, g_dcs_pwd)
        
        # as producer for core
        server.define_producer(self.channel, EX_GUI, 'direct')
        
        # as consumer for core
        self.queue = server.binding(self.channel, EX_CORE, 'direct', QUE_GUI)

        th = threading.Thread(target=self.consumer)
        th.start()

        # ----------------------------------------------------------
        #Load: cofiguration files
        self.e_config_dir.setText(g_loadfile_path)
        self.e_MACIE_reg.setText(g_macie_file)
        self.e_ASIC_firmware.setText(g_asic_file)
        self.e_img_dir.setText(g_exe_path)

        self.e_timeout.setText(g_gige_timeout)
        self.cmb_ouput_channels.setCurrentText(g_output_channel)

        self.label_connection_sts.setText("ICS")
        
        self.comsts = False

        self.init_buttons()

        #self.start_core()    

        self.samplingMode = UTR_MODE   

        self.set_samplingmode(self.samplingMode)
        self.set_param_ui(1, 1, 1, 1, 1)

        self.timer_sts = QTimer(self)
        self.timer_sts.setInterval(5000)
        self.timer_sts.timeout.connect(self.show_alarm)
        #self.timer_sts.start()

        #self.initialize()
        

    
    def closeEvent(self, event: QCloseEvent) -> None:

        return super().closeEvent(event)


    def init_buttons(self):

        self.chk_alone.clicked.connect(self.alone)
        self.btn_start_server.clicked.connect(self.connect_to_server)

        # path
        self.btn_find_config_dir.clicked.connect(lambda: self.find_dir(CONFIG_DIR))
        self.btn_find_MACIE_reg.clicked.connect(lambda: self.find_dir(MACIE_FILE))
        self.btn_find_ASIC_firware.clicked.connect(lambda: self.find_dir(ASIC_FILE))
        self.btn_find_img_dir.clicked.connect(lambda: self.find_dir(IMG_DIR))

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

        self.btn_set_param.clicked.connect(self.set_parameter)
        self.btn_acquireramp.clicked.connect(self.acquireramp)
        self.btn_stop.clicked.connect(self.stop_acquistion)

        self.btn_get_telemetry.clicked.connect(self.get_telemetry)


    # ---------------------------------------------------------------------
    # RabbitMQ communication
    def consumer(self):
        try:
            self.channel.basic_consume(queue=self.queue, on_message_callback=self.callback, auto_ack=True)
            self.channel.start_consuming()
        except Exception as e:
            if self.channel:
                self.channel.stop_consuming()


    def callback(self, ch, method, properties, body):
        print('[gui <- core] ' + body.decode())

        cmd = body.decode()
        if cmd == 'core start!':
            self.send_message('LibVersion')
        elif cmd.find() >= 'LibVersion:':
            self.label_ver.setText(cmd.split(':')[1])


        #if body.decode() == "alive?":
        #    self.comsts = True
        #    self.send_message("alive")       

    
    def send_message(self, message):
        self.channel.basic_publish(exchange=EX_GUI, routing_key=QUE_CORE, body=message.encode())
        print('[gui -> core] ' + message)
    # ---------------------------------------------------------------------


    # gui start -> start core
    def start_core(self):
        #subprocess.call('python /home/dcs/workspace/dcs-master/DCS/DC_core.py')
        os.system('python dcs-master/DCS/DC_core.py')


    def alone(self):
        pass


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
        if self.samplingMode == UTR_MODE:
            self.label_groups.setEnabled(True)
            self.e_groups.setEnabled(True)

            self.label_ramps.setEnabled(True)
            self.e_ramps.setEnabled(True)

            self.label_fowler_number.setEnabled(False)
            self.e_fowler_number.setEnabled(False)

        else:
            self.label_groups.setEnabled(False)
            self.e_groups.setEnabled(False)

            self.label_ramps.setEnabled(False)
            self.e_ramps.setEnabled(False)

            self.label_fowler_number.setEnabled(True)
            self.e_fowler_number.setEnabled(True)

        self.e_resets.setText(str(resets))
        self.e_reads.setText(str(reads))
        self.e_groups.setText(str(groups))
        self.e_drops.setText(str(drops))
        self.e_ramps.setText(str(ramps))

      



# ----------------------------------------------------------------------
    # RabbitMQ communication
    def connect_to_server(self):
        
        self.start_core()

        return
        if self.comsts is False:

            self.comsts = True

        
        else:
            self.btn_start_server.setText("Connect To Server")
            self.comsts = False

            self.timer_sts.stop()

            self.connection.close()           


    #def 

    
     


    def show_alarm(self):
        textcolor = "black"
        if self.comsts is True:
            textcolor = "green"
        else:
            textcolor = "red"
        
        label = "QLabel {color:%s}" % textcolor
        self.label_connection_sts.setStyleSheet(label)


    


    # ----------------------------------------------------------------------
    # Buttons
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
            

    def initialize1(self):
        self.send_message('Initialize')
        


    def initialize2(self):
        self.dc.Initialize2()


    def reset(self):
        self.dc.ResetASIC()


    def downloadMCD(self):
        self.dc.DownloadMCD()


    def set_detector(self):
        self.dc.SetDetector(MUX_TYPE, int(self.cmb_ouput_channels.currentText()))


    def err_count(self):
        self.dc.GetErrorCounters()


    def click_UTR(self):
        self.samplingMode = UTR_MODE
        self.set_param_ui(1, 1, 1, 1, 1)


    def click_CDS(self):
        self.samplingMode = CDS_MODE
        self.set_param_ui(1, 1, 1, T_minFowler, 1)


    def click_CDSNoise(self):
        self.samplingMode = CDSNOISE_MODE
        self.set_param_ui(1, 1, 1, T_minFowler, 2)


    def click_Fowler(self):
        self.samplingMode = FOWLER_MODE
        self.set_param_ui(1, 1, 1, T_minFowler, 1)
        

    def set_parameter(self):

        resets = int(self.e_resets.text())
        reads = int(self.e_reads.text())
        groups = int(self.e_groups.text())
        ramps = int(self.e_ramps.text())

        exptime, cal_waittime = 0.0, 0.0

        if self.samplingMode == UTR_MODE:
            drops = int(self.e_drops.text())

            exptime = (T_frame * reads * groups) + (T_frame * drops * (groups -1 ))
            cal_waittime = T_br + ((T_frame * resets) + exptime) * ramps
            
            self.dc.SetRampParam(resets, reads, groups, drops, ramps)        

        else:
            fowlerTime = float(self.e_drops.text())

            exptime = fowlerTime + T_frame * reads
            cal_waittime = T_br + ((T_frame * resets) + fowlerTime + (2 * T_frame * reads)) * ramps
            
            self.dc.SetFSParam(resets, reads, groups, fowlerTime, ramps)
        
        self.e_exp_time.setText(str(exptime))
        self.label_calculated_time.setText(str(cal_waittime))


    def acquireramp(self):
        self.dc.AcquireRamp()

        # thread


    def stop_acquistion(self):
        self.dc.StopAcquisition()


    def get_telemetry(self):
        self.dc.GetTelemetry()
         




if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False

    app = QApplication(sys.argv)

    dc = MainWindow()
    dc.show()

    app.exec()