#!/usr/bin/env python
###########################################################################
#(C) Copyright Pumpkin, Inc. All Rights Reserved.
#
#This file may be distributed under the terms of the License
#Agreement provided with this software.
#
#THIS FILE IS PROVIDED AS IS WITH NO WARRANTY OF ANY KIND,
#INCLUDING THE WARRANTY OF DESIGN, MERCHANTABILITY AND
#FITNESS FOR A PARTICULAR PURPOSE.
###########################################################################
"""
@package Equipment_Control.py
Module to provide a gui interface to control the Equipment involved in the
Battery Tester Module.
"""

__author__ = 'David Wright (david@asteriaec.com)'
__version__ = '0.1.0' #Versioning: http://www.python.org/dev/peps/pep-0386/


#
# -------
# Imports

import Tkinter as TK
import Power_Supply
import DC_Load
import BM2_aardvark

# construct the root frame
root = TK.Tk()

# construct a frame for the load gui
Load_frame = TK.Frame(root)
Load_frame.grid(row = 0, column = 1, sticky = 'NSEW')

# initialise the load gui
Load_GUI = DC_Load.DC_Load_GUI(Load_frame, root, 'M9711')

# construct a frame for the Power Supply gui
PS_frame = TK.Frame(root)
PS_frame.grid(row = 0, column = 0, sticky = 'NSEW')

# initialise the Power Supply gui
PS_GUI = Power_Supply.Power_Supply_GUI(PS_frame, root, 'KA3005P')

# construct a frame for the Power Supply gui
BM_frame = TK.Frame(root)
BM_frame.grid(row = 1, column = 0, columnspan = 2, sticky = 'NSEW')

# initialise the Power Supply gui
BM_GUI = BM2_aardvark.BM2_GUI(BM_frame, root)

def exit_gui():
    """
    Function to run on termination of program, closes all GUI elements
    """
    # close all gui elements
    PS_GUI.close_GUI()
    Load_GUI.close_GUI()
    BM_GUI.close_GUI()
    
    # close the gui
    root.destroy()
# end def

root.title("BM2 Equipment testing system.")
root.protocol("WM_DELETE_WINDOW", exit_gui)
root.resizable(False, False)

# Start the GUI
root.mainloop()




