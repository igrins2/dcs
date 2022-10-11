# -*- coding: utf-8 -*-

"""
Created on Mar 4, 2022

Modified on Sep 2, 2022

@author: hilee
"""


import click
#from DC_core import *
from DCS.DC_core import *

# group: cli
@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass

def show_func(show):
    if show:
        print("------------------------------------------\n"
            "Usage: Command [Options] [Args]...\n\n"
            "Options:\n"
            "  -h, --help  Show this message and exit.\n\n"
            "Command:\n"
            "  showcommand show\n"  #help
            "  libversion\n"
            "  connecttoserver (be getting ready)\n"
            "  initialize timeout\n"    #help
            "  initialize2\n"
            "  resetASIC\n"
            "  downloadMCD\n"
            "  setdetector muxtype outputs\n"   #help
            "  setfsmode mode\n"    #help
            "  setwinparam xstart xstop ystart ystop\n" #help
            "  setrampparam p1 p2 p3 p4 p5\n"   #help
            "  setfsparam p1 p2 p3 p4 p5\n" #help
            "  acquireramp\n"
            "  stopacquisition\n"
            "  imageacquisition\n"
            "  gettelemetry\n"
            "  disconnect (be getting ready)\n"
            "  exit\n"
            "------------------------------------------\n")
    print(">>", end=" ")
    args = list(input().split())
    return args


def show_subfunc(cmd, *args):
    msg = "Usage: %s [Options] %s\n\n  %s\n\n" % (cmd, args[0], args[1])
    print(msg+"Options:\n" 
               "  -h, --help  Show this message and exit")

def show_errmsg(args):
    print("Please input '%s' or '-h'/'--help'." % args)


def show_checkmsg(pkg):
    pkg.logwrite(BOTH, "Please check the interface status!!!")
    

def show_noargs(cmd):
    msg = "'%s' has no arguments. Please use just command." % cmd
    print(msg)


@click.command(help=CLASS_NAME + " Detector Control Start")
def start():
    dc = DC()  

    dc.logwrite(CMDLINE, 
           '================================================\n'+
           '                                Ctrl + C to exit\n'+
           '================================================\n')

    show = True
    args = show_func(show)

    while(True):
        if len(args) == 0:
            args = show_func(show)
            continue
        
        dc.logwrite(BOTH, str(args))

        if args[0] == "showcommand":
            _args = "show"
            try:
                if args[1] == "-h" or args[1] == "--help":
                    show_subfunc(args[0], _args, "show: True/False")
                elif args[1] == "False":
                    show = False
                elif args[1] == "True":
                    show = True
                else:
                    show_errmsg(_args)
            except:
                show_errmsg(_args)

        elif args[0] == "libversion":
            if len(args) > 1:
                show_noargs(args[0])
            else:
                dc.LibVersion()

        elif args[0] == "connecttoserver":
            if len(args) > 1:
                show_noargs(args[0])
            else:
                dc.logwrite(CMDLINE, "be getting ready")

        elif args[0] == "initialize":
            _args = "timeout"
            try:
                if args[1] == "-h" or args[1] == "--help":
                    show_subfunc(args[0], _args, "timeout: milisecond (default is 200ms)")
                elif int(args[1]) < 0:
                    show_errmsg(_args)
                else:
                    ret = dc.Initialize(int(args[1]))
                    print("result:", ret)
                    if ret != FUN_OK:
                        show_checkmsg(dc)
            except:
                show_errmsg(_args)

        elif args[0] == "initialize2":
            if len(args) > 1:
                show_noargs(args[0])
            else:
                ret = dc.Initialize2()
                print("result:", ret)
                if ret == False:
                    show_checkmsg(dc)

        elif args[0] == "resetASIC":
            if len(args) > 1:
                show_noargs(args[0])
            elif dc.ResetASIC() == False:
                show_checkmsg(dc)

        elif args[0] == "downloadMCD":
            if len(args) > 1:
                show_noargs(args[0])
            elif dc.DownloadMCD() == False:
                show_checkmsg(dc)

        elif args[0] == "setdetector":
            _args = "muxtype outputs"
            try:
                if args[1] == "-h" or args[1] == "--help":
                    show_subfunc(args[0], _args, "muxtype: 1(H1RG)/2(H2RG)/4(H4RG), outputs: Number of Outouts Used")
                elif int(args[1]) < 1 or int(args[2]) < 0:
                    show_errmsg(_args)
                elif dc.SetDetector(int(args[1]), int(args[2])) == False:
                    show_checkmsg(dc)
            except:
                show_errmsg(_args)

        elif args[0] == "setfsmode":
            _args = "mode"
            try:
                if args[1] == "-h" or args[1] == "--help":
                    show_subfunc(args[0], _args, "mode: 0(UTR)/1(CDS)/2(CDS Noise)/3(Fowler Sampling)")
                elif int(args[1]) < 0 or 3 < int(args[1]) :
                    dc.logwrite(CMDLINE, "Please input '0~3' for mode")
                else:
                    dc.samplingMode = int(args[1])
            except:
                show_errmsg(_args)
                
        elif args[0] == "setwinparam":
            _args = "xstart xstop ystart ystop"
            try:
                if args[1] == "-h" or args[1] == "--help":
                    show_subfunc(args[0], _args, "xstart: 1~2048, xstop: 1~2048, ystart: 1~2048, ystop: 1~2048")
                elif int(args[1]) < 1 or int(args[1]) < 1 or int(args[3]) < 1 or int(args[4]) < 1:
                    dc.logwrite(CMDLINE, "Please input '1~2048' for each argument.")
                else:
                    dc.x_start = args[1]
                    dc.x_stop = args[2]
                    dc.y_start = args[3]
                    dc.y_stop = args[4]
            except:
                show_errmsg(_args)

        elif args[0] == "setrampparam":
            _args = "p1 p2 p3 p4 p5"
            try:
                if args[1] == "-h" or args[1] == "--help":
                    show_subfunc(args[0], _args, "p1: resets, p2: reads, p3: groups, p4: drops, p5: ramps")
                elif int(args[1]) < 1 or int(args[2]) < 1 or int(args[3]) < 1 or int(args[4]) < 1 or int(args[5]) < 1:
                    dc.logwrite(CMDLINE, "Please input '>0' for each argument")
                elif dc.SetRampParam(int(args[1]), int(args[2]), int(args[3]), int(args[4]), int(args[5])) == False:
                    show_checkmsg(dc) 
            except:
                show_errmsg(_args)

        elif args[0] == "setfsparam":
            _args = "p1 p2 p3 p4 p5"
            try:
                if args[1] == "-h" or args[1] == "--help":
                    show_subfunc(args[0], _args, "p1: resets, p2: reads, p3: groups, p4: fowler time (float, sec), p5: ramps")
                elif int(args[1]) < 1 or int(args[2]) < 1 or int(args[3]) < 1 or float(args[4]) < 0 or int(args[5]) < 1:
                    dc.logwrite(CMDLINE, "Please input '>1' for p1, p2, p3, p5, '>=0' for p4.")
                elif dc.SetFSParam(int(args[1]), int(args[2]), int(args[3]), float(args[4]), int(args[5])) == False:
                    show_checkmsg(dc) 
            except:
                show_errmsg(_args)

        elif args[0] == "acquireramp":
            if len(args) > 1:
                show_noargs(args[0])
            elif dc.AcquireRamp() == False:
                show_checkmsg(dc)

        elif args[0] == "stopacquisition":
            if len(args) > 1:
                show_noargs(args[0])
            elif dc.StopAcquisition() == False:
                show_checkmsg(dc)

        elif args[0] == "imageacquisition":
            if len(args) > 1:
                show_noargs(args[0])
            elif dc.ImageAcquisition() == False:
                show_checkmsg(dc)

        elif args[0] == "gettelemetry":
            if len(args) > 1:
                show_noargs(args[0])
            elif dc.GetTelemetry() == False:
                show_checkmsg(dc)

        elif args[0] == "disconnect":
            dc.logwrite(CMDLINE, "be getting ready")

        elif args[0] == "exit":
            if len(args) > 1:
                show_noargs(args[0])
            else:
                break

        else:
            dc.logwrite(CMDLINE, "Please confirm command.")
        
        print()
        args = show_func(show)
            


def CliCommand():
    cli.add_command(start)

    cli()


if __name__ == "__main__":
    CliCommand()
