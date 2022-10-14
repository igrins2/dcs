# -*- coding: utf-8 -*-

"""
Created on Mar 4, 2022

Modified on Aug 28, 2022

@author: hilee
"""

import numpy as np
import astropy.io.fits as fits
from astropy.time import Time

#from ctypes import *
from math import *
import time as ti
import datetime
import os, sys
import json

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import Libs.SetConfig as sc
from DCS.MACIE import *
from DCS.DC_def import *
from DCS.DC_server import *
from DC_gui_sub import *
import tunning as tn

import threading

#for c
#lib2 = CDLL("/home/dcss/workspace/dcs-master/FowlerCalculation/libsampling_cal.so")
#lib2.fowler_calculation.argtypes = [c_int, c_int, c_int, POINTER(c_ushort)]
#lib2.fowler_calculation.restype = POINTER(c_float)

#for c++
lib2 = cdll.LoadLibrary("/home/dcs/workspace/dcs-master/FowlerCalculation/libsampling_cal.so")
fowler_calculation = lib2.fowler_calculation
fowler_calculation.argtypes = (c_int, c_int, c_int, POINTER(c_ushort))
fowler_calculation.restype = POINTER(c_float)


class MACIE_FitsHdr(Structure):
        _fields_ = [("key", c_char*9),
                    ("valType", c_int),
                    ("iVal", c_int),
                    ("fVal", c_float),
                    ("sVal", c_char*72),
                    ("comment", c_char*72)]


lib.MACIE_WriteFitsFile.argtypes = [c_char_p, c_ushort, c_ushort, POINTER(c_ushort), c_ushort, POINTER(MACIE_FitsHdr)]
lib.MACIE_WriteFitsFile.restype = c_int

class DC(threading.Thread):
    def __init__(self):
        
        #self.name = name

        #-------------------------------------------------------
        # load ini file
        cfg = sc.LoadConfig("/DCS/DCS.ini")

        # ICS
        self.ics_ip_addr = cfg.get('ICS', 'ip_addr')
        self.ics_id = cfg.get('ICS', 'id')
        self.ics_pwd = cfg.get('ICS', 'pwd')

        self.ics_ex = cfg.get('ICS', 'exchange')
        self.ics_q = cfg.get('ICS', 'routing_key')

        # DCS
        self.dcs_ip_addr = cfg.get('DC', 'ip_addr')
        self.dcs_ex = cfg.get('DC', 'exchange')
        self.dcs_q = cfg.get('DC', 'routing_key')

        self.loadfile_path = cfg.get('DC', 'config-dir')
        self.macie_file = cfg.get('DC', 'MACIE-Register')
        self.asic_file = cfg.get('DC', 'ASIC-Firmware')
        self.exe_path = cfg.get('DC', 'Img-dir')

        self.gige_timeout = cfg.get('DC', 'timeout')
        self.output_channel = cfg.get('DC', 'channel')
        #-------------------------------------------------------

        self.logwrite(BOTH, "start DCS!!!")

        self.handle = 0
        self.slctCard = 0
        self.slctMACIEs = 0
        self.slot1 = False  # slot 1-True, slot 2-False
        Cards = MACIE_CardInfo * 2
        self.pCard = Cards()

        self.slctASICs = 0
        self.option = True

        self._24Bit = False  # 24bit-True, 16bit-False

        self.expTime = 0.0
        self.fowlerTime = 0.0

        self.preampInputScheme = 1    # 2
        self.preampInputVal = 0x4502    # 0xaaaa
        self.preampGain = 8  # 1

        self.V_refmain = 0

        self.samplingMode = UTR_MODE

        self.ROIMode = False
        self.x_start, self.x_stop, self.y_start, self.y_stop = 0, FRAME_X-1, 0, FRAME_Y
        self.resets, self.reads, self.ramps, self.groups, self.drops = 1, 1, 1, 1, 1
        
        self.loadimg = []

        self.save_as = False    #for engineer

        # RabbitMQ connect
        self.serv = ICS_SERVER(self.ics_ip_addr, self.ics_id, self.ics_pwd, self.ics_ex, self.ics_q, "direct", self.dcs_ex, self.dcs_q)
        self.connection, self.channel = self.serv.connect_to_server()
        
        # RabbitMQ: define producer
        self.serv.define_producer(self.channel)


    def run(self):
        print("Thread start", threading.current_thread().getName())
        

    def send_message(self, message):
        self.serv.send_message(self.channel, message)


    # Version
    def LibVersion(self):
        ver = "%.2f" % lib.MACIE_LibVersion()
        msg = "Version: "
        self.logwrite(BOTH, msg+ver)
        return ver

    # Error Msg
    def GetErrMsg(self):
        errMsg = lib.MACIE_Error()
        return errMsg.decode()

    # not yet!!!!
    # Memory Fee 
    def MemoryFree(self):
        sts = lib.MACIE_Free()
        res = ""
        if sts == MACIE_OK:
            res =  RET_OK
        else:
            res = RET_FAIL
        self.logwrite(BOTH, "MACIE_Free: " + res)
        return sts
        
    
    def read_ASIC_reg(self, asic_addr):
        if self.handle == 0:
            return 0, MACIE_FAIL

        arr_list = []
        arr = np.array(arr_list)
        val = arr.ctypes.data_as(POINTER(c_uint))
        sts = lib.MACIE_ReadASICReg(self.handle, self.slctASICs, asic_addr, val, self._24Bit, self.option)
        
        return val, sts

    
    def write_ASIC_reg(self, asic_addr, input):
        res = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, asic_addr, input, self.option)

        return res


    # Init
    def Init(self):
        sts = lib.MACIE_Init()
        res = ""
        if sts == MACIE_OK:
            res = RET_OK
        else:
            res = RET_FAIL
        self.logwrite(BOTH, "MACIE_Init: " + res)
        return sts


    # SetGigeTimeout
    def SetGigeTimeout(self, timeout):
        sts = lib.MACIE_SetGigeTimeout(timeout)
        if sts == MACIE_OK:
            self.logwrite(BOTH, "MACIE_SetGigeTimeout: " + RET_OK)
            return True
        else:
            self.logwrite(BOTH, self.GetErrMsg())
            return False
        

    # CheckInterfaces
    def CheckInterfaces(self):
        #slctCard = 0
        connection = MACIE_NONE
        try:

            ipaddr = MACIE_IpAddr()
            arr_list = []
            arr = np.array(arr_list)
            #print(arr)
            card = arr.ctypes.data_as(POINTER(c_ushort))
            print(card[0])
            self.pCard = pointer(pointer(MACIE_CardInfo()))

            sts = lib.MACIE_CheckInterfaces(0, ipaddr, 0, card, self.pCard)
            #print(sts)
            res = ""
            if sts == MACIE_OK:
                res = RET_OK
            else:
                res = RET_FAIL
            self.logwrite(BOTH, "MACIE_CheckInterfaces: " + res)

            if self.pCard == None:
                self.logwrite(BOTH, RET_FAIL)

            #self.ip_addr = "192.168.1.102"  #for tes
            #for i in range(card.contents.value):

            #self.slctCard = 0

            self.logwrite(BOTH, str(self.pCard[self.slctCard].contents.macieSerialNumber))
            self.logwrite(BOTH, "True" if self.pCard[self.slctCard].contents.bUART == True else "False")
            self.logwrite(BOTH, "True" if self.pCard[self.slctCard].contents.bGigE == True else "False")
            self.logwrite(BOTH, "True" if self.pCard[self.slctCard].contents.bUSB == True else "False")
            ipaddr = "%d.%d.%d.%d" % (self.pCard[self.slctCard].contents.ipAddr[0], self.pCard[self.slctCard].contents.ipAddr[1], self.pCard[self.slctCard].contents.ipAddr[2], self.pCard[self.slctCard].contents.ipAddr[3])
            self.logwrite(BOTH, ipaddr)
            self.logwrite(BOTH, str(self.pCard[self.slctCard].contents.gigeSpeed))
            self.logwrite(BOTH, str(self.pCard[self.slctCard].contents.serialPortName.decode()))
            #self.logwrite(BOTH, self.pCard[self.slctCard].contents.usbSerialNumber)
            self.logwrite(BOTH, str(self.pCard[self.slctCard].contents.firmwareSlot1.decode()))
            #self.logwrite(BOTH, self.pCard[self.slctCard].contents.firmwareSlot2)
            #self.logwrite(BOTH, self.pCard[self.slctCard].contents.usbSpeed) 

            #if self.ip_addr == ipaddr:
            

            return ipaddr

        except:
            return None, None


    # GetHandle
    def GetHandle(self):
        #slctCard = 0
        connection = MACIE_GigE  # input by user

        self.handle = lib.MACIE_GetHandle(
            self.pCard[self.slctCard].contents.macieSerialNumber, connection)
        msg = "(macie serial number: %d) Handle = %d" % (self.pCard[self.slctCard].contents.macieSerialNumber, self.handle)
        self.logwrite(BOTH, msg)


    def GetAvailableMACIEs(self):
        if self.handle == 0:
            return False

        avaiMACIEs = lib.MACIE_GetAvailableMACIEs(self.handle)
        msg = "MACIE_GetAvailableMACIEs = %d" % avaiMACIEs
        self.logwrite(BOTH, msg)

        self.slctMACIEs = avaiMACIEs & 1
        
        arr_list = []
        arr = np.array(arr_list)
        val = arr.ctypes.data_as(POINTER(c_uint))
        msg = ""

        if self.slctMACIEs == 0:
            msg = "Select MACIE = %d invalid" % avaiMACIEs
            self.logwrite(BOTH, msg)
            return False
        elif lib.MACIE_ReadMACIEReg(self.handle, avaiMACIEs, MACIE_Reg, val) != MACIE_OK:
                #msg = "MACIE read %d failed: %s" % (MACIE_Reg, self.GetErrMsg())
                self.logwrite(BOTH, self.GetErrMsg())
                return False
        else:
            msg = "MACIE h%04x = %04x" % (MACIE_Reg, val[0])
            self.logwrite(BOTH, msg)
        
        return True
        


    def Initialize(self, timeout, ics):

        # self.InitBuffer()

        # 1. init
        if self.Init() == MACIE_FAIL:
            return -1

        # 2. SetGigeTimeout
        if self.SetGigeTimeout(timeout) == False:
            return -2
        
        # 3. CheckInterfaces
        _ip = self.CheckInterfaces()
        if _ip == None:
            return -3
        while(_ip != self.dcs_ip_addr):
            ti.sleep(0.5)
            _ip = self.CheckInterfaces()

        # 4. GetHandle
        self.GetHandle()

        # 5. GetAvailableMACIEs
        if self.GetAvailableMACIEs() == False:
            return -4

        self.logwrite(BOTH, "Initialize " + RET_OK)

        if ics == True:
            self.send_message(CMD_INITIALIZE1 + " OK")

        return 1


    def Initialize2(self):

        if self.handle == 0:
            return False

        msg = "Initialize with handle: %ld" % self.handle
        self.logwrite(BOTH, msg)

        if self.slctMACIEs == 0:
            self.logwrite(BOTH, "MACIE0 is not available")
            return False

        arr_list = []
        arr = np.array(arr_list)
        val = arr.ctypes.data_as(POINTER(c_uint))

        # step 1. load MACIE firmware from slot1 or slot2
        if lib.MACIE_loadMACIEFirmware(self.handle, self.slctMACIEs, self.slot1, val) != MACIE_OK:
            #msg = "LOAD MACIE firmware " + RET_FAIL + ": " + self.GetErrMsg()
            self.logwrite(BOTH, self.GetErrMsg())
            return False
        if val[0] != 0xac1e:
            msg = "Verification of MACIE firmware load failed: readback of hFFFB = %d" % val[0]
            self.logwrite(BOTH, msg)
            return False
        self.logwrite(BOTH, "Load MACIE firmware " + RET_OK)

        # step 2. download MACIE registers
        file = self.loadfile_path + "/" + self.macie_file
        if lib.MACIE_DownloadMACIEFile(self.handle, self.slctMACIEs, file.encode()) != MACIE_OK:
            #msg = RET_FAIL + ": " + self.GetErrMsg()
            self.logwrite(BOTH, self.GetErrMsg())
            return False
        self.logwrite(BOTH, "Download MACIE register file " + RET_OK)

        # check again!!!
        arr_list = []
        arr = np.array(arr_list)
        data = arr.ctypes.data_as(POINTER(c_uint))
        res = -1
        sts = lib.MACIE_ReadMACIEBlock(self.handle, self.slctMACIEs, MACIE_Block_Reg, data, 5)
        if sts != MACIE_OK:
            res = sts
        else:
            for i in range(5):
                msg = "val h%04x = %04x" % (MACIE_Block_Reg, data[i])
                self.logwrite(BOTH, msg)
            res = data[1]

        self.logwrite(BOTH, "Initialize2 " + RET_OK)

        return True


    def ResetASIC(self, ics):
        if self.handle == 0:
            return False

        # step 1. reset science data error counters
        if lib.MACIE_ResetErrorCounters(self.handle, self.slctMACIEs) != MACIE_OK:
            self.logwrite(BOTH, "Reset MACIE error counters " + RET_FAIL)
            return False
        self.logwrite(BOTH, "Reset error counters " + RET_OK)

        # step 2. download ASIC file
        if lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_State, 0x8002, self.option) != MACIE_OK:
            self.logwrite(BOTH, "Reconfiguration sequence " + RET_FAIL)
            return False
        self.logwrite(BOTH, "Reconfiguration sequence " + RET_OK)

        self.logwrite(BOTH, "ResetASIC " + RET_OK)

        if ics == True:
            self.send_message(CMD_INITIALIZE2 + " OK")

        return True
        

    def DownloadMCD(self, ics):
        if self.handle == 0:
            return False

        # step 1. downlaod asic file
        file = self.loadfile_path + "/" + self.asic_file 
        sts = lib.MACIE_DownloadASICFile(self.handle, self.slctMACIEs, file.encode(), True)
        if sts != MACIE_OK:
            #self.logwrite(BOTH, "Download ASIC firmware " + RET_FAIL + ":" + self.GetErrMsg())
            self.logwrite(BOTH, self.GetErrMsg())
            return False
        self.logwrite(BOTH, "Download ASIC firmware " + RET_OK)

        # step 2. checking!!!
        self.slctASICs = lib.MACIE_GetAvailableASICs(self.handle, False)
        if self.slctASICs == 0:
            self.logwrite(BOTH, "MACIE_GetAvailableASICs " + RET_FAIL)
            return False

        else:           
            val, sts = self.read_ASIC_reg(ASICAddr)
            msg = "ASIC h%04x = %04x" % (ASICAddr, val[0])
            self.logwrite(BOTH, msg)

            arr_list = []
            arr = np.array(arr_list)
            data = arr.ctypes.data_as(POINTER(c_uint))
            lib.MACIE_ReadASICBlock(
                self.handle, self.slctASICs, ASICAddr_NResets, data, 5, self._24Bit, self.option)
            for i in range(5):
                msg = "val h%04x = %04x" % (ASICAddr_NResets + i, data[i])
                self.logwrite(BOTH, msg)
        msg = "Available ASICs = %d" % self.slctASICs
        self.logwrite(BOTH, msg)

        self.logwrite(BOTH, "DownloadMCD " + RET_OK)

        if ics == True:
            self.send_message(CMD_DOWNLOAD + " OK")

        return True


    def SetDetector(self, muxType, outputs, ics):  # muxType = 2 (H2RG)
        if self.handle == 0:
            return False

        res = [MACIE_OK, MACIE_OK]

        res[0] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_HxRGVal, muxType, self.option)
        res[1] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_HxRGNumOutVal, outputs, self.option)

        for i in range(2):
            if res[i] == MACIE_FAIL:
                self.logwrite(BOTH, "Set Detector " + RET_FAIL)
                return False

        msg = "Set Detector (%d, %d) succeeded" % (muxType, outputs)
        self.logwrite(BOTH, msg)

        if ics == True:
            self.send_message(CMD_SETDETECTOR + " OK")

        return True


    def GetErrorCounters(self):
        if self.handle == 0:
            return

        arr_list = [0 for _ in range(MACIE_ERROR_COUNTERS)]
        arr = np.array(arr_list)
        errArr = arr.ctypes.data_as(POINTER(c_ushort))
        if lib.MACIE_GetErrorCounters(self.handle, self.slctMACIEs, errArr) != MACIE_OK:
            self.logwrite(BOTH, "Read MACIE error counter failed")
            return

        else:
            self.logwrite(BOTH, "Error counters....")
            for i in range(MACIE_ERROR_COUNTERS):
                msg = "%d" % errArr[i]
                self.logwrite(BOTH, msg)


    def SetRampParam(self, p1, p2, p3, p4, p5, ics):  # p1~p5 : int
        if self.handle == 0:
            return False

        self.resets, self.reads, self.groups, self.ramps = p1, p2, p3, p5

        res = [0 for _ in range(8)]

        res[0] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_NResets, p1, self.option)
        res[1] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_NReads, p2, self.option)
        res[2] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_Config, 12, self.option)
        res[3] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_NRamps, p5, self.option)
        res[4] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_NGroups, p3, self.option)
        res[5] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_nNDrops, p4, self.option)

        lowerCounter, upperCounter = 0, 0
        if self.expTime * pow(10, 6) >= BITSIZE_65536:
            upperCounter = int(
                (self.expTime * pow(10, 6) / 20) / BITSIZE_65536)
            lowerCounter = int(
                (self.expTime * pow(10, 6) / 20) % BITSIZE_65536)
        else:
            lowerCounter = int(self.expTime * pow(10, 6) / 20)
        res[6] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_TexpLower, lowerCounter, self.option)
        res[7] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_TexpUpper, upperCounter, self.option)

        for i in range(8):
            if res[i] != MACIE_OK:
                self.logwrite(BOTH, "SetRampParam failed - write ASIC registers")
                return False

        msg = "SetRampParam(%d, %d, %d, %d, %d)" % (p1, p2, p3, p4, p5)
        self.logwrite(BOTH, msg)

        if ics == True:
            self.send_message(CMD_SETRAMPPARAM + " OK")

        return True


    def SetFSParam(self, p1, p2, p3, p4, p5, ics):  # p1~5:int, p4:double

        self.resets, self.reads, self.groups, self.ramps = p1, p2, p3, p5
        self.fowlerTime = p4

        if self.handle == 0:
            return False

        res = [0 for _ in range(9)]

        res[0] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_NResets, p1, self.option)
        res[1] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_NReads, p2, self.option)
        res[2] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_Config, 12, self.option)
        res[3] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_NRamps, p5, self.option)
        res[4] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_NGroups, p3, self.option)

        lowerCounter, upperCounter = 0, 0
        if p4 * pow(10, 6) >= BITSIZE_65536:
            upperCounter = int((p4 * pow(10, 6) / 20) / BITSIZE_65536)
            lowerCounter = int((p4 * pow(10, 6) / 20) % BITSIZE_65536)
        else:
            lowerCounter = int((p4 * pow(10, 6)) / 20)
        res[5] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_TfowlerLower, lowerCounter, self.option)
        res[6] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_TfowlerUpper, upperCounter, self.option)

        t_FowlerPair = 0
        # self.expTime = 2 * t_FowlerPair + p4
        t_FowlerPair = (self.expTime - p4) / 2
        if t_FowlerPair * pow(10, 6) >= BITSIZE_65536:
            upperCounter = int(
                ((t_FowlerPair * pow(10, 6)) / 20) / BITSIZE_65536)
            lowerCounter = int(
                ((t_FowlerPair * pow(10, 6)) / 20) % BITSIZE_65536)
        else:
            lowerCounter = int((t_FowlerPair * pow(10, 6)) / 20)
        res[7] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_TexpLower, lowerCounter, self.option)
        res[8] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_TexpUpper, upperCounter, self.option)

        for i in range(9):
            if res[i] != MACIE_OK:
                self.logwrite(BOTH, "SetFSParam failed - write ASIC registers")
                return False

        msg = "SetFSParam(%d, %d, %d, %f, %d)" % (p1, p2, p3, p4, p5)
        self.logwrite(BOTH, msg)

        if ics == True:
            self.send_message(CMD_SETFSPARAM + " OK")

        return True


    def AcquireRamp(self):
        if self.handle == 0:
            return False

        self.logwrite(BOTH, "Acquire Science Data....")

        # step 1. ASIC configuration
        res = [0 for _ in range(7)]

        res[0] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_ASICInputRefVal, self.preampInputScheme, self.option)
        res[1] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_PreAmpReg1Ch1ENAddr, self.preampInputVal, self.option)
        res[2] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_ASICPreAmpGainVal, self.preampGain, self.option)
        res[3] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_NReads, self.reads, self.option)
        res[4] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_NRamps, self.ramps, self.option)

        if self.samplingMode == UTR_MODE:
            if self.ROIMode == True:
                res[5] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_HxRGExpModeVal, 2, self.option)  # UTR, window
                winarr = [self.xStart, self.xStop,
                          self.yStart, self.yStop]  # x1, x2, y1, y2
                wr = lib.MACIE_WriteASICBlock(self.handle, self.slctASICs, ASICAddr_WinArr, winarr, 4, self.option)
            else:
                res[5] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_HxRGExpModeVal, 0, self.option)  # UTR, Full frame
        else:
            if self.ROIMode == True:
                res[5] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_HxRGExpModeVal, 3, self.option)  # FS, window
                winarr = [self.xStart, self.xStop,
                          self.yStart, self.yStop]  # x1, x2, y1, y2
                wr = lib.MACIE_WriteASICBlock(self.handle, self.slctASICs, ASICAddr_WinArr, winarr, 4, self.option)
            else:
                res[5] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_HxRGExpModeVal, 1, self.option)  # FS, Full frame
        res[6] = lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_State, 0x8002, self.option)

        for i in range(7):
            if res[i] != MACIE_OK:
                self.logwrite(BOTH, "ASIC configuration failed - write ASIC registers")
                return False

        ti.sleep(1.5)

        val, sts = self.read_ASIC_reg(ASICAddr_State)
        if (val[0] & 1) != 0 or sts != MACIE_OK:
            self.logwrite(BOTH, "ASIC configuration for shorted preamp inputs failed")
            return False
        self.logwrite(BOTH, "Configuration succeeded")

        # step 2.science interface
        frameSize = 0
        if self.samplingMode == UTR_MODE:
            if self.ROIMode == True:
                frameSize = (self.xStop - self.xStart + 1) * \
                    (self.yStop - self.yStart + 1)
            else:
                frameSize = FRAME_X * FRAME_Y * self.reads * self.groups * self.ramps
        else:
            if self.ROIMode == True:
                frameSize = (self.xStop - self.xStart + 1) * \
                    (self.yStop - self.yStart + 1)
            else:
                frameSize = FRAME_X * FRAME_Y * 2 * self.reads * self.ramps

        arr_list = []
        arr = np.array(arr_list)
        buf = arr.ctypes.data_as(POINTER(c_int))

        sts = lib.MACIE_ConfigureGigeScienceInterface(self.handle, self.slctMACIEs, 0, frameSize, 42037, buf)  # 0-16bit
        if sts != MACIE_OK:
            msg = "Science interface configuration failed. buf = %d" % buf[0]
            self.logwrite(BOTH, msg)
            return False
        msg = "Science interface configuration succeeded. buf (KB) = %d" % buf[0]
        self.logwrite(BOTH, msg)

        # step 3.trigger ASIC to read science data
        self.logwrite(BOTH, "Trigger image acquisition....")

        # make sure h6900 bit<0> is 0 before triggering.

        val, sts = self.read_ASIC_reg(ASICAddr_State)
        if sts != MACIE_OK:
            msg = "Read ASIC h%04x failed" % ASICAddr_State
            self.logwrite(BOTH, msg)
            return False
        if (val[0] & 1) != 0:
            msg = "Configure idle mode by writing ASIC h%04x failed" % ASICAddr_State
            self.logwrite(BOTH, msg)
            return False

        if lib.MACIE_WriteASICReg(self.handle, self.slctMACIEs, ASICAddr_State, 0x8001, self.option) != MACIE_OK:
            self.logwrite(BOTH, "Triggering " + RET_FAIL)
            return False

        self.logwrite(BOTH, "Triggering succeeded")

        return True

    
    def StopAcquisition(self, ics):
        if self.handle == 0:
            return False

        if lib.MACIE_WriteASICReg(self.handle, self.slctASICs, ASICAddr_State, 0x8002, self.option) != MACIE_OK:
            self.logwrite(BOTH, "Acquire Stop " + RET_FAIL)
            return False

        self.logwrite(BOTH, "Acquire Stop " + RET_OK)

        if ics == True:
            self.send_message(CMD_STOPACQUISITION + " OK")

        return True


    def ImageAcquisition(self, ics):
        if self.handle == 0:
            return False

        # Wait for available science data bytes
        idleReset, moreDelay = 1, 2000
        triggerTimeout = (T_frame * 1000) * (self.resets +
                                             idleReset) + moreDelay  # delay time for one frame

        ti.sleep(1.5)

        getByte = 0
        if self.samplingMode == UTR_MODE:
            getByte = FRAME_X * FRAME_Y * 2 * self.reads * self.groups * self.ramps
            triggerTimeout *= self.reads * self.groups * self.ramps
        else:
            getByte = FRAME_X * FRAME_Y * 2 * 2 * self.reads * self.ramps
            triggerTimeout *= 2 * self.reads * self.ramps

        byte = 0
        for i in range(100):
            byte = lib.MACIE_AvailableScienceData(self.handle)
            if byte >= getByte:
                msg = "Available science data = %d bytes, Loop = %d" % (
                    byte, i)
                self.logwrite(BOTH, msg)
                break
            if self.ROIMode == True:
                self.logwrite(BOTH, "Wait (ROI)....")
            else:
                self.logwrite(BOTH, "Wait....")
            ti.sleep(triggerTimeout / 100 / 1000)

        if byte <= 0:
            self.logwrite(BOTH, "Trigger timeout: no available science data")
            return False

        #data = None
        arr_list = []
        arr = np.array(arr_list)
        data = arr.ctypes.data_as(POINTER(c_ushort))
        
        data = lib.MACIE_ReadGigeScienceFrame(self.handle, int(1500 + triggerTimeout))

        if data == None:
            if self.ROIMode:
                self.logwrite(BOTH, "Null frame (ROI)")
            else:
                self.logwrite(BOTH, "Null frame")
            return False

        frmcnt = 0
        if self.samplingMode == UTR_MODE:
            frmcnt = self.reads * self.groups * self.ramps
        else:
            frmcnt = 2 * self.reads * self.ramps

        #self.loadimg = data[0:FRAME_X * FRAME_Y*frmcnt]

        self.loadimg = []
        for i in range(frmcnt):
            start = FRAME_X * FRAME_Y
            self.loadimg.append(data[start*i:start*(i+1)])
            #print(start*i, start*(i+1))

        lib.MACIE_CloseGigeScienceInterface(self.handle, self.slctMACIEs)

        self.WriteFitsFile()
        #self.loadimg = []

        if ics == True:
            self.send_message(CMD_ACQUIRERAMP + " OK")

        elif self.save_as == True:
            ss = SaveAsDlg(self)
            res = ss.showModal()
            if res == QDialog.Accepted:
                print("Exit")
            elif res == QDialog.Rejected:
                print("Exit 2")

        self.logwrite(BOTH, "[TEST] " + CMD_ACQUIRERAMP + " OK")

        return True


    def createFolder(self, dir):
        try:
            if not os.path.exists(dir):
                os.makedirs(dir)
        except OSError:
            self.logwrite(BOTH, "Error: Creating directory. " + dir)


    def WriteFitsFile(self):
        if self.ROIMode == True:
            self.logwrite(BOTH, "Write Fits file now (ROI)....")
        else:
            self.logwrite(BOTH, "Write Fits file now....")

        _t = datetime.datetime.utcnow()

        cur_datetime = [_t.year, _t.month, _t.day, _t.hour, _t.minute, _t.second, _t.microsecond]

        path = "%s/Data/" % self.exe_path
        self.createFolder(path)

        if self.samplingMode == UTR_MODE:  # single mode
            path += "UpTheRamp/"
        elif self.samplingMode == CDS_MODE:  # ramp=1, group=1, read=1
            path += "CDS/"
        elif self.samplingMode == CDSNOISE_MODE:  # ramp=2, group=1, read=1
            path += "CDSNoise/"
        elif self.samplingMode == FOWLER_MODE:  # ramp=1, group=1, read=1,2,4,8,16
            path += "Fowler/"
        self.createFolder(path)

        #str = time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))
        str = "%04d%02d%02d_%02d%02d%02d" % (cur_datetime[0], cur_datetime[1], cur_datetime[2], cur_datetime[3], cur_datetime[4], cur_datetime[5])
        path += str + "/"
        self.createFolder(path)

        idx = 0
        #------------------------------------------------------------------------
        if self.samplingMode == UTR_MODE:  # single mode
            for ramp in range(self.ramps):
                for group in range(self.groups):
                    for read in range(self.reads):

                        filename = "%sH2RG_R%02d_M%02d_N%02d.fits" % (path, ramp + 1, group+1, read + 1)
                        sts = self.save_fitsfile_sub(idx, filename, cur_datetime, ramp+1, group+1, read+1)

                        if sts != MACIE_OK:
                            self.logwrite(BOTH, self.GetErrMsg())
                            return -1
                        else:
                            self.logwrite(BOTH, filename)

                        idx += 1
            return

        elif self.samplingMode == CDS_MODE:  # ramp=1, group=1, read=1
            for read in range(self.reads*2):
                filename = "%sH2RG_R01_M01_N%02d.fits" % (path, read + 1)
                sts = self.save_fitsfile_sub(idx, filename, cur_datetime, 1, 1, read+1)

                if sts != MACIE_OK:
                    self.logwrite(BOTH, self.GetErrMsg())
                    return -1
                else:
                    self.logwrite(BOTH, filename)

                idx += 1

        elif self.samplingMode == CDSNOISE_MODE:  # ramp=2, group=1, read=1
            for ramp in range(self.ramps):
                for read in range(self.reads*2):
                    filename = "%sH2RG_R%02d_M01_N%02d.fits" % (path, ramp + 1, read + 1)
                    sts = self.save_fitsfile_sub(idx, filename, cur_datetime, ramp + 1, 1, read+1)

                    if sts != MACIE_OK:
                        self.logwrite(BOTH, self.GetErrMsg())
                        return -1
                    else:
                        self.logwrite(BOTH, filename)

                    idx += 1

        elif self.samplingMode == FOWLER_MODE:  # ramp=1, group=1, read=1,2,4,8,16
            for group in range(2):
                for read in range(self.reads):
                    filename = "%sH2RG_R01_M%02d_N%02d.fits" % (path, group+1, read + 1)
                    sts = self.save_fitsfile_sub(idx, filename, cur_datetime, 1, group+1, read+1)

                    if sts != MACIE_OK:
                        self.logwrite(BOTH, self.GetErrMsg())
                        return -1
                    else:
                        self.logwrite(BOTH, filename)

                    idx += 1
    
        startime = ti.time()

        #-----------------------------------------------------------------------
        arr = np.array(self.loadimg, dtype=np.int16)
        data = arr.ctypes.data_as(POINTER(c_ushort))

        arr_list = []
        arr = np.array(arr_list, dtype=np.float32)
        res = arr.ctypes.data_as(POINTER(c_float))

        res = fowler_calculation(self.samplingMode, self.reads, idx, data)

        if self.samplingMode == CDS_MODE:
            lastfilename = "%sH2RG_R01_M01_N02.fits" % path
            self.save_fitsfile_final(lastfilename, path+"Result/", "CDSResult.fits", self.reads, res)
        
        elif self.samplingMode == CDSNOISE_MODE:
            reslist = []
            for i in range(3):
                start = FRAME_X * FRAME_Y
                reslist.append(res[start*i:start*(i+1)])

                lastfilename = "%sH2RG_R02_M01_N02.fits" % path
                if i < 2:
                    filename = "CDSResult%d.fits" % (i+1)
                else:
                    filename = "CDSNoise.fits"

                self.save_fitsfile_final(lastfilename, path+"Result/", filename, self.reads, reslist[i])


        elif self.samplingMode == FOWLER_MODE:
            lastfilename = "%sH2RG_R01_M02_N%02d.fits" % (path, self.reads)
            self.save_fitsfile_final(lastfilename, path+"Result/", "FowlerResult.fits", self.reads, res)

        #-----------------------------------------------------------------------
        
        duration = ti.time() - startime
        tmp = "%.3f" % duration
        self.logwrite(BOTH, tmp)

    def save_fitsfile_sub(self, idx, filename, cur_datetime, ramp, group, read):
        
        header_array = MACIE_FitsHdr * FITS_CNT
        pHeaders = header_array()

        header_cnt = 0

        #print(cur_datetime)
        y, m, d = cur_datetime[0], cur_datetime[1], cur_datetime[2]
        _h, _m, _s, _ms = cur_datetime[3], cur_datetime[4], cur_datetime[5], cur_datetime[6]
        obs_datetime = "%04d-%02d-%02dT%02d:%02d:%02d.%d" % (y, m, d, _h, _m, _s, _ms)

        t = Time(obs_datetime, format='isot', scale='utc')
        julian = t.to_value('jd', 'long')
        #print(julian)

        julian_time = "%f" % julian
        pHeaders[header_cnt] = MACIE_FitsHdr(key="ACQTIME".encode(), valType=HDR_STR, sVal=julian_time.encode(), comment="UTC Julian time".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="ACQTIME1".encode(), valType=HDR_STR, sVal=obs_datetime.encode(), comment="UTC time (YYYY-MM-DDTHH:MM:SS.MS)".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="UNITS".encode(), valType=HDR_STR, sVal="ADU".encode(), comment="ADC digital steps".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="MUXTYPE".encode(), valType=HDR_INT, iVal=MUX_TYPE, comment="1- H1RG; 2- H2RG; 4- H4RG".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="NOUTPUTS".encode(), valType=HDR_INT, iVal=32, comment="Number of detector outputs".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="FRMMODE".encode(), valType=HDR_INT, iVal=self.ROIMode, comment="0- full frame mode; 1- window mode".encode())
        header_cnt += 1

        if self.samplingMode == UTR_MODE:
            val = 0
        else:
            val = 1
        pHeaders[header_cnt] = MACIE_FitsHdr(key="EXPMODE".encode(), valType=HDR_INT, iVal=val, comment="0-Ramp mode; 1- Fowler sampling mode".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="NRESETS".encode(), valType=HDR_INT, iVal=self.resets, comment="Number of resets before integration".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="FRMTIME".encode(), valType=HDR_FLOAT, fVal=T_frame, comment="Frame time".encode())        
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="EXPTIME".encode(), valType=HDR_FLOAT, fVal=self.expTime, comment="sec, Exposure Time".encode())
        header_cnt += 1
        
        pHeaders[header_cnt] = MACIE_FitsHdr(key="FOWLTIME".encode(), valType=HDR_FLOAT, fVal=self.fowlerTime, comment="sec, Fowler Time".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="ASICGAIN".encode(), valType=HDR_INT, iVal=self.preampGain, comment="8 (12dB, large cin)".encode())
        header_cnt += 1

        val = "0x%04x" % self.preampInputVal
        pHeaders[header_cnt] = MACIE_FitsHdr(key="AMPINPUT".encode(), valType=HDR_STR, sVal=val.encode(), comment="Preamp input".encode())
        header_cnt += 1

        #-------------------------------------------------------------------------------------
        #information
        _num = self.pCard[0].contents.macieSerialNumber
        pHeaders[header_cnt] = MACIE_FitsHdr(key="SERIALN".encode(), valType=HDR_INT, iVal=_num, comment="MACIE serial number".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="FIRMSLOT".encode(), valType=HDR_STR, sVal=self.pCard[0].contents.firmwareSlot1, comment="MACIE slot id".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="SWVER".encode(), valType=HDR_FLOAT, fVal=lib.MACIE_LibVersion(), comment="Software version number".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="CONNECT".encode(), valType=HDR_INT, iVal=2, comment="0: NONE; 1: USB; 2: GigE; 3: UART".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="FASTMODE".encode(), valType=HDR_INT, iVal=0, comment="1: FastMode; 0: SlowMode".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="ASICSET".encode(), valType=HDR_STR, sVal=self.asic_file.encode(), comment="ASIC firmware file".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="MACIESET".encode(), valType=HDR_STR, sVal=self.macie_file.encode(), comment="MACIE register file".encode())
        header_cnt += 1

        '''
        #-------------------------------------------------------------------------------------
        #temperature
        with open(self.exe_path+"/HK_db.json", 'r') as f:
            json_data = json.load(f)

        pHeaders[header_cnt] = MACIE_FitsHdr(key="T_AIR".encode(), valType=HDR_FLOAT, fVal=json_data["air"], comment="Dewar temperature-air".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="T_BENCH".encode(), valType=HDR_FLOAT, fVal=json_data["bench"], comment="Dewar temperature-bench".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="T_BENCEN".encode(), valType=HDR_FLOAT, fVal=json_data["benchcenter"], comment="Dewar temperature-benchcenter".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="T_CAMH".encode(), valType=HDR_FLOAT, fVal=json_data["camH"], comment="Dewar temperature-camH".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="T_CAMK".encode(), valType=HDR_FLOAT, fVal=json_data["camK"], comment="Dewar temperature-camK".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="T_CARBOX".encode(), valType=HDR_FLOAT, fVal=json_data["charcoalBox"], comment="Dewar temperature-charcoalBox".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="T_COLDH1".encode(), valType=HDR_FLOAT, fVal=json_data["coldhead01"], comment="Dewar temperature-coldhead01".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="T_COLDH2".encode(), valType=HDR_FLOAT, fVal=json_data["coldhead02"], comment="Dewar temperature-coldhead02".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="T_COLDST".encode(), valType=HDR_FLOAT, fVal=json_data["coldstop"], comment="Dewar temperature-coldstop".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="T_DETH".encode(), valType=HDR_FLOAT, fVal=json_data["detH"], comment="Dewar temperature-detH".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="T_DETK".encode(), valType=HDR_FLOAT, fVal=json_data["detK"], comment="Dewar temperature-detH".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="T_DETS".encode(), valType=HDR_FLOAT, fVal=json_data["detS"], comment="Dewar temperature-detS".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="T_GRATIN".encode(), valType=HDR_FLOAT, fVal=json_data["grating"], comment="Dewar temperature-grating".encode())
        header_cnt += 1

        pressure = "%.2e" % json_data["pressure"]
        pHeaders[header_cnt] = MACIE_FitsHdr(key="T_PRESSU".encode(), valType=HDR_STR, sVal=pressure.encode(), comment="Dewar temperature-pressure".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="T_SHTOP".encode(), valType=HDR_FLOAT, fVal=json_data["shieldtop"], comment="Dewar temperature-shieldtop".encode())
        header_cnt += 1

        #-------------------------------------------------------------------------------------
        '''

        pHeaders[header_cnt] = MACIE_FitsHdr(key="SEQNUM_R".encode(), valType=HDR_INT, iVal=ramp, comment="Ramp number".encode())
        header_cnt += 1

        pHeaders[header_cnt] = MACIE_FitsHdr(key="SEQNUM_N".encode(), valType=HDR_INT, iVal=read, comment="Sample number within group".encode())
        header_cnt += 1

        if self.samplingMode != UTR_MODE:
            base_fomula = T_frame * read + self.fowlerTime * (read-1)
            integratingT = 0
            if self.samplingMode == CDS_MODE:
                integratingT = base_fomula

            elif self.samplingMode == CDSNOISE_MODE:
                if ramp == 1:
                    integratingT = base_fomula
                else:
                    integratingT = (T_frame * 2 + self.fowlerTime) + base_fomula

            elif self.samplingMode == FOWLER_MODE:
                if group == 1:
                    integratingT = T_frame * read
                else:
                    integratingT = (T_frame * self.reads + self.fowlerTime) + T_frame * read
            
            pHeaders[header_cnt] = MACIE_FitsHdr(key="INTTIME".encode(), valType=HDR_FLOAT, fVal=integratingT, comment="integration time".encode())
            header_cnt += 1
            
        pHeaders[header_cnt] = MACIE_FitsHdr(key="SEQNUM_M".encode(), valType=HDR_INT, iVal=group, comment="1- before exposure; 2- after exposure.".encode())
        header_cnt += 1

        str = "R%02d_M%02d" % (ramp, group)
        pHeaders[header_cnt] = MACIE_FitsHdr(key="SEQNNAME".encode(), valType=HDR_STR, sVal=str.encode(), comment="Ramp and Group String".encode())
        header_cnt += 1

        arr = np.array(self.loadimg[idx], dtype=np.int16)
        data = arr.ctypes.data_as(POINTER(c_ushort))
        sts = lib.MACIE_WriteFitsFile(c_char_p(filename.encode()), FRAME_X, FRAME_Y, data, header_cnt, pHeaders)
        
        # for tunning test
        mean, ref_aver = tn.cal_mean(filename)
        print(self.V_refmain, ": ", mean, ref_aver)

        return sts


    def save_fitsfile_final(self, lastfilename, fullpath, filename, sampling, data):

        self.createFolder(fullpath)

        buf = []
        buf = data[0:FRAME_X * FRAME_Y]  
        #img = np.zeros([FRAME_X, FRAME_Y], dtype=np.float32)
        img = np.array(buf, dtype=np.float32)
        img = img.reshape(FRAME_X, FRAME_Y)
        
        #print(img)

        #hdu = fits.PrimaryHDU(img)
        #hdul = fits.HDUList([hdu])

        hdulist = fits.open(lastfilename)   #read last fits file for getting header

        new_header = hdulist[0].header[:-5]
        
        new_header["SAMPLING"] = (sampling, "Sample number")
        
        new_header["COMMENT1"] = "This FITS file may contain long string keyword values that are"
        new_header["COMMENT2"] = "continued over multiple keywords.  This convention uses the  '&'"
        new_header["COMMENT3"] = "character at the end of a string which is then continued"
        new_header["COMMENT4"] = "on subsequent keywords whose name = 'CONTINUE"

        new_header["FITSFILE"] = fullpath
        new_header["CONTINUE"] = filename                

        fits.writeto(fullpath+filename, img, header=new_header) #, img, header, output_verify='ignore', overwrite=True)

        #print(fullpath+filename)
        #print(img[0], img[2048*2048-1])

        #hdul.close()


    def GetTelemetry(self):
        if self.handle == 0:
            return False

        tlm = [0.0 for _ in range(79)]
        if lib.MACIE_GetTelemetryAll(self.handle, self.slctMACIEs, tlm) != MACIE_OK:
            #self.logwrite(BOTH, "MACIE_GetTelemetryAll ", RET_FAIL, ": ", self.GetErrMsg())
            self.logwrite(BOTH, self.GetErrMsg())
            return False
        else:
            self.logwrite(BOTH, "MACIE_GetTelemetryAll " +  RET_OK)
            for i in range(79):
                msg = "%f" % tlm[i]
                self.logwrite(BOTH, msg)

        return True 


    def logwrite(self, option, event):
        '''
        Function that write to file for Logging
        event : Logging Sentence
        option :  LOGGING(1) - Write to File
                  CMDLINE(2) - Write to Command Line
                  BOTH(3) - Wrte to File and Command Line
        '''
        thatday = ti.strftime("%04Y%02m%02d.log", ti.localtime())
        path = "%s/Log/" % self.exe_path
        self.createFolder(path)
        #print(path)

        if option == LOGGING:
            file = open(path+thatday, 'a+')
            file.write(ti.strftime("[%Y-%m-%d %H:%M:%S]", ti.localtime()) + ": " + event + "\n")
            file.close()
        elif option == CMDLINE:
            print(event)
        elif option == BOTH:
            file = open(path+thatday, 'a+')
            file.write(ti.strftime("[%Y-%m-%d %H:%M:%S]", ti.localtime()) + ": " + event + "\n")
            file.close()
            print(event)
            
    

if __name__ == "__main__":
    
    dc = DC()
    
    dc.LibVersion()

    ret = dc.Initialize(200, False)
    print("result:", ret)

    ret = dc.Initialize2()
    print("result:", ret)

    dc.ResetASIC(False)

    dc.DownloadMCD(False)

    dc.SetDetector(2, 32, False)

    _addr = int("0x" + "6000", 16)
    val, sts = dc.read_ASIC_reg(_addr)
    _val = "%4x" % val[0]
    print("6000:", _val)

    _addr = int("0x" + "6002", 16)
    val, sts = dc.read_ASIC_reg(_addr)
    _val = "%4x" % val[0]
    print("6002:", _val)

    _addr = int("0x" + "6004", 16)
    val, sts = dc.read_ASIC_reg(_addr)
    _val = "%4x" % val[0]
    print("6004:", _val)

    _addr = int("0x" + "602c", 16)
    val, sts = dc.read_ASIC_reg(_addr)
    _val = "%4x" % val[0]
    print("602c:", _val)

    #-----------------------------------
    _addr = int("0x" + "6002", 16)
    _value = int("0x" + "8120", 16)
    sts = dc.write_ASIC_reg(_addr, _value)

    _addr = int("0x" + "602c", 16)
    _value = int("0x" + "820a", 16)
    sts = dc.write_ASIC_reg(_addr, _value)

    #-----------------------------------
    _addr = int("0x" + "6002", 16)
    val, sts = dc.read_ASIC_reg(_addr)
    _val = "%4x" % val[0]
    print("6002:", _val)

    _addr = int("0x" + "602c", 16)
    val, sts = dc.read_ASIC_reg(_addr)
    _val = "%4x" % val[0]
    print("602c:", _val)


    #dc.GetErrorCounters()

    dc.samplingMode = 3 #0~3

    dc.fowlerTime = 0.168
    #dc.expTime = 0.168

    if dc.samplingMode == 0:
        dc.SetRampParam(1, 1, 1, 0, 1, False)
    elif dc.samplingMode == 1:
        dc.SetFSParam(1, 1, 1, dc.fowlerTime, 1, False)
    elif dc.samplingMode == 2:
        dc.SetFSParam(1, 1, 1, dc.fowlerTime, 2, False)
    elif dc.samplingMode == 3:
        dc.SetFSParam(1, 32, 1, dc.fowlerTime, 1, False)

    dc.AcquireRamp()

    dc.ImageAcquisition(False)

'''
    lastfilename = self.exe_path + "/Data/CDS/20220602_090341/H2RG_R01_M01_N02.fits"
    fullpath = self.exe_path + "/Data/CDS/20220602_090341/Result/"
    filename = "CDSResult.fits"

    hdulist = fits.open(lastfilename)
    data = hdulist[0].data

    arr = np.array(data, dtype=np.int16)
    data = arr.ctypes.data_as(POINTER(c_ushort))

    dc.save_fitsfile_final(lastfilename, fullpath, filename, 1, data)
'''
    



    