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
@package Charger.py
Module to intelligently charge the BM2.
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

# current scaling factor
current_scale = 0.25

# construct the root frame
root = TK.Tk()
    
# construct a frame for the Power Supply gui
PS_frame = TK.Frame(root)
PS_frame.grid(row = 0, column = 0, sticky = 'NSEW')

# initialise the Power Supply gui
PS_GUI = Power_Supply.Power_Supply_GUI(PS_frame, root, 'KA3005P', slave = True)
PS_GUI.PS_Off()

# construct a frame for the Power Supply gui
BM_frame = TK.Frame(root)
BM_frame.grid(row = 1, column = 0, columnspan = 2, sticky = 'NSEW')

# initialise the Power Supply gui
BM_GUI = BM2_aardvark.BM2_GUI(BM_frame, root)    

# construct a frame for the Charger control.
Charger_frame = TK.Frame(root)
Charger_frame.grid(row = 0, column = 1, sticky = 'NSEW')

Charger_button = TK.Button(Charger_frame, text = 'Start Charging', 
                           activebackground = 'green', width = 15,
                           font = "Arial 10 bold")

Charger_button.grid(row = 0 , column=0, padx=5, pady=5)  


kill_charger = False

def end_charging():
    kill_charger = True
# end def

def run_charger():
    
    global kill_charger
    
    # re-configure the charger button
    Charger_button.config(command = end_charging, text = 'Stop Charging')
    
    # if the background of the fc flag is highlighted then the BM2 is fully 
    # charged
    if (not (BM_GUI.FC_flag.cget('bg') == root.cget('bg'))) or kill_charger:
        PS_GUI.PS_Off()
        charger_button.config(text = 'Start Charging', command = run_charger)
        kill_charger = False
        return None
    # end if
    
    charging_voltage = 0
    charging_current = 0
    PS_voltage = 0
    PS_current = 0
    
    # read values from the BM2 GUI
    try:
        charging_voltage = float(BM_GUI.charging_voltage_value.cget('text'))
        charging_current = float(BM_GUI.charging_current_value.cget('text'))
        
    except Exception as e:
        print "communications with the BM2 lost"
        print e
        root.after(1000, run_charger)
        return None
    # end try
    
    # read values from the Power Supply GUI
    try:
        temp_voltage = float(PS_GUI.current_value.cget('text'))
        
        PS_GUI.voltage_setting.config(state='normal')
        PS_voltage = float(PS_GUI.voltage_setting.get())
        PS_GUI.voltage_setting.config(state='disabled')
        
        PS_GUI.current_setting.config(state='normal')
        PS_current = float(PS_GUI.current_setting.get())
        PS_GUI.current_setting.config(state='disabled')
        
    except Exception as e:
        print "communications with the Power supply lost"
        print e
        PS_GUI.voltage_setting.config(state='disabled')
        PS_GUI.current_setting.config(state='disabled')
        root.after(1000, run_charger)
        return None
    #end try
    
    # if values were read correctly
    if ((charging_current > 0) and (charging_voltage > 0) and
        (PS_voltage > 0) and (PS_current > 0)):
        
        # change voltage output if it needs to be changed
        if charging_voltage != PS_voltage:
            PS_GUI.voltage_setting.config(state='normal')
            PS_GUI.voltage_setting.delete(0, 'end')
            PS_GUI.voltage_setting.insert(0, str(charging_voltage))
            PS_GUI.voltage_setting.config(state='disabled')   
        # end if
        
        # change current output if it needs to be changed
        if charging_current*current_scale != PS_current:
            PS_GUI.current_setting.config(state='normal')
            PS_GUI.current_setting.delete(0, 'end')
            PS_GUI.current_setting.insert(0, str(charging_current*current_scale))
            PS_GUI.current_setting.config(state='disabled')   
        # end if 
        
        # if either voltage or current were in need of updating, set the PS
        if ((charging_voltage != PS_voltage) or 
            (charging_current*current_scale != PS_current)):
            PS_GUI.voltage_setting.config(state='normal')
            PS_GUI.current_setting.config(state='normal')
            PS_GUI.set_PS()
            PS_GUI.voltage_setting.config(state='disabled')  
            PS_GUI.current_setting.config(state='disabled')
        # end if
    # end if
    
    # turn on the charger
    PS_GUI.PS_On()    
    
    # schedule this task to run again
    root.after(1000, run_charger)
# end def
    
Charger_button.config(command = run_charger)

def exit_gui():
    """
    Function to run on termination of program, closes all GUI elements
    """
    # close all gui elements
    PS_GUI.PS_Off()
    PS_GUI.close_GUI()
    BM_GUI.close_GUI()
    
    # close the gui
    root.destroy()
# end def

root.title("BM2 Equipment testing system.")
root.protocol("WM_DELETE_WINDOW", exit_gui)
root.resizable(False, False)

# Start the GUI
root.mainloop()




