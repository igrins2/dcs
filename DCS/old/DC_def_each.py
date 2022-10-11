# -*- coding: utf-8 -*-

"""
Created on Mar 4, 2022

Modified on Aug 28, 2022

@author: hilee
"""

CLASS_NAME = "[Detector Control Core]"
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

FUN_OK = 1

FITS_CNT = 50

# result message
RET_OK = "succeeded"
RET_FAIL = "failed"

# LOG option
LOGGING = 1
CMDLINE = 2
BOTH = 3

MUX_TYPE = 2

# find dir/file
CONFIG_DIR = 0
MACIE_FILE = 1
ASIC_FILE = 2
IMG_DIR = 3

FRAME_X = 2048
FRAME_Y = 2048

BITSIZE_65536 = 65536

# sampling mode
UTR_MODE = 0    #single frame
CDS_MODE = 1
CDSNOISE_MODE = 2
FOWLER_MODE = 3

T_frame = 1.45479
T_exp = 1.63
T_minFowler = 0.168
T_br = 2

MACIE_Reg = 0x0300
MACIE_Block_Reg = 0x321

ASICAddr_NResets = 0x4000
ASICAddr_NReads = 0x4001
ASICAddr_Config = 0x4002
ASICAddr_NRamps = 0x4003
ASICAddr_NGroups = 0x4004
ASICAddr_nNDrops = 0x4005

ASICAddr_TfowlerLower = 0x400a
ASICAddr_TfowlerUpper = 0x400b
ASICAddr_TexpLower = 0x400c
ASICAddr_TexpUpper = 0x400d
    
ASICAddr_HxRGVal = 0x4010
ASICAddr_HxRGNumOutVal = 0x4011
ASICAddr_HxRGExpModeVal = 0x4018    #exposure mode
ASICAddr_ASICInputRefVal = 0x4019
ASICAddr_ASICPreAmpGainVal = 0x401a
ASICAddr_WinArr = 0x4020

ASICAddr_PreAmpReg1Ch1ENAddr = 0x5100

ASICAddr = 0x6100
ASICAddr_State = 0x6900

EX_GUI = 'gui.ex'
QUE_GUI = 'gui.q'

EX_CLI = 'cli.ex'
QUE_CLI = 'cli.q'

EX_CORE = 'core.ex'
QUE_CORE = 'core.q'

import Libs.SetConfig as sc

# load ini file
cfg = sc.LoadConfig("/DCS/DCS.ini")

# ICS
g_ics_ip_addr = cfg.get('ICS', 'ip_addr')
g_ics_id = cfg.get('ICS', 'id')
g_ics_pwd = cfg.get('ICS', 'pwd')

# DCS
g_dcs_id = cfg.get('DC', 'myid')
g_dcs_pwd = cfg.get('DC', 'pwd')

g_loadfile_path = cfg.get('DC', 'config-dir')
g_macie_file = cfg.get('DC', 'MACIE-Register')
g_asic_file = cfg.get('DC', 'ASIC-Firmware')
g_exe_path = cfg.get('DC', 'Img-dir')

g_gige_timeout = cfg.get('DC', 'timeout')
g_output_channel = cfg.get('DC', 'channel')







