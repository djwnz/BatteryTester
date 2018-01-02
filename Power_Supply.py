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
@package PowerSupply.py
Module to handle the control of a generic power supply, providing an \
abstraction layer for the user.
"""

__author__ = 'David Wright (david@asteriaec.com)'
__version__ = '0.1.0' #Versioning: http://www.python.org/dev/peps/pep-0386/


#
# -------
# Imports

from koradserial import KoradSerial
import Tkinter as TK
import sys
import serial

# ---------
# Classes

class PowerSupply(object):
    
    def __init__(self, Model):
        self.model = Model
        self.port = 'NULL'
        
        if self.model == 'KA3005P':
            self.port = findKoradPort()
            
        else:
            raise ValueError('The Power Supply model selected is not supported'+
                             'by this Module')
        # end if        
        
    #end def
    
    def __enter__(self):
        
        if self.port == 'NULL':
            if self.model == 'KA3005P':
                self.port = findKoradPort()
                if self.port != 'NULL':
                    self.PS = KoradSerial(self.port)
                    self.output = self.PS.channels[0]
    
                else:
                    raise IOError('No Korad Power Supply was detected')
                # end if
                
            else:
                raise ValueError('The Power Supply model selected is not supported'+
                                 'by this Module')
            # end if
            
        else:
            self.PS = KoradSerial(self.port)
            self.output = self.PS.channels[0]                
        #end if
        
        return self
    # end def
    
    def output_on(self):
        if self.model == 'KA3005P':
            self.PS.output.on()
        # end if 
    # end def
    
    def output_off(self):
        if self.model == 'KA3005P':
            self.PS.output.off()
        # end if 
    # end def    
    
    def get_output(self):
        if self.model == 'KA3005P':
            return self.PS.status.output
    
    def get_output_voltage(self):
        if self.model == 'KA3005P':
            return self.output.output_voltage
        # end if 
    # end def 
    
    def get_voltage(self):
        if self.model == 'KA3005P':
            return self.output.voltage
        # end if 
    # end def    
    
    def set_voltage(self, volts):
        if self.model == 'KA3005P':
            self.output.voltage = volts
        # end if 
    # end def      
        
    def get_output_current(self):
        if self.model == 'KA3005P':
            return self.output.output_current
        # end if 
    # end def 
    
    def get_current(self):
        if self.model == 'KA3005P':
            return self.output.current
        # end if 
    # end def    
    
    def set_current(self, amps):
        if self.model == 'KA3005P':
            self.output.current = amps
        # end if 
    # end def 
    
    def __exit__(self, type, value, traceback):
        if self.port != 'NULL':
            if self.model == 'KA3005P':
                self.PS.close()
            #end if
        # end if        
    #end def    
# end class

class Power_Supply_GUI:
    def __init__(self, gui_frame, gui, model):
        self.Supply = None
        self.error_State = False
        self.frame = gui_frame
        self.model = model
        self.gui = gui
        self.PS = PowerSupply(self.model)
        self.load_gui()
        self.enabled = False
        
        
    # end def

    def load_gui(self):
        title = TK.Label(self.frame, text = self.model + " Power Supply")
        title.grid(row = 0, column = 0, columnspan = 3)
        
        self.on_button = TK.Button(self.frame, text = 'Output On',  
                                   activebackground = 'green', width = 15)
        self.on_button.grid(row = 1, column = 0, columnspan = 3)
        
        setpoint = TK.Label(self.frame, text = "Setting:")
        setpoint.grid(row = 2, column = 1)
        
        value = TK.Label(self.frame, text = "Current\nValue:")
        value.grid(row = 2, column = 2)
        
        voltage = TK.Label(self.frame, text = "Voltage (V):")
        voltage.grid(row = 3, column = 0)
        
        current = TK.Label(self.frame, text = "Current (A):")
        current.grid(row = 4, column = 0)
        
        self.voltage_setting = TK.Entry(self.frame)   
        self.voltage_setting.insert(0, '8.4')
        self.voltage_setting.grid(row = 3, column = 1)
        
        self.current_setting = TK.Entry(self.frame, text = "2")   
        self.current_setting.insert(0, '2')
        self.current_setting.grid(row = 4, column = 1)
        
        self.voltage_value = TK.Label(self.frame, text = "-")
        self.voltage_value.grid(row = 3, column = 2)
        
        self.current_value = TK.Label(self.frame, text = "-")
        self.current_value.grid(row = 4, column = 2)        
        
        self.set_button = TK.Button(self.frame, text = 'Set',
                                    activebackground = 'green', width = 15)
        self.set_button.grid(row = 5, column=0, columnspan = 3, 
                              padx=10, pady=10)
        
        self.on_button.config(state='disabled', command = self.PS_On)
        self.set_button.config(state='disabled', command = self.set_PS)
        
        self.update_gui()     
        
    #end def
    
    def PS_On(self):
        try:
            with self.PS:
                self.PS.output_on()
                self.on_button.config(text = "Output Off", 
                                      command = self.PS_Off)
            #end with
        except:
            self.disable_gui()
        # end try 
    # end def
    
    def PS_Off(self):
        try:
            with self.PS:
                self.PS.output_off()
                self.on_button.config(text = "Output On", command = self.PS_On)
            #end with
        except:
            self.disable_gui()
        # end try         
    # end def    
    
    def set_PS(self):
        voltage_text = self.voltage_setting.get()
        current_text = self.current_setting.get()
        
        try:
            voltage_int = float(voltage_text)
            current_int = float(current_text)
            try:
                with self.PS:
                    self.PS.set_voltage(voltage_int)
                    self.PS.set_current(current_int)
                #end with
            except:
                self.disable_gui()
            # end try   
            
        except:
            self.voltage_setting.delete(0, 'end')
            self.voltage_setting.insert(0, '8.4')
            self.current_setting.delete(0, 'end')
            self.current_setting.insert(0, '2')
        #end try
    # end def   
    
    def disable_gui(self):
        self.enabled = False
        self.on_button.config(state='disabled')
        self.set_button.config(state='disabled')
        self.voltage_setting.config(state='disabled')
        self.current_setting.config(state='disabled')      
    # end def
    
    def enable_gui(self):
        self.on_button.config(state='normal')
        self.set_button.config(state='normal')
        self.voltage_setting.config(state='normal')
        self.current_setting.config(state='normal')      
    # end def    
    
    def update_gui(self):
        voltage = '-'
        current = '-'
        try:
            with self.PS:
                if not self.enabled:
                    self.enable_gui()
                    self.PS.output_off()
                    self.on_button.config(text = "Output On", command = self.PS_On)
                    self.enabled = True
                #end if
                    
                voltage = self.PS.get_voltage()
                current = self.PS.get_current()
                self.voltage_value.config(text=str(voltage))
                self.current_value.config(text=str(current))
            #end with
        except:
            self.disable_gui()
        # end try  
        
        self.gui.after(1000, self.update_gui)
    #end def
# end class
              
            
#
# ----------------
# Private Functions
            
def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
# end def

def findKoradPort():
    power_supply_port = 'NULL'
    available_ports = serial_ports()
    
    for port in available_ports:
        try:
            with KoradSerial(port) as com_test:
                model_name = com_test.model.encode('ascii','ignore')
                if model_name.startswith('KORAD'):
                    power_supply_port = port
                    break;
                # end if
        except:
            pass
        # end try
    # end for    
    
    return power_supply_port
# end def

def _test():
    """
    Test code for this module.
    """
    # construct the root frame
    root = TK.Tk()
    root.geometry('800x600')
    
    test_frame = TK.Frame(root)
    test_frame.grid(row = 1, column = 1)
    
    PS_GUI = Power_Supply_GUI(test_frame, root, 'KA3005P')
    
    root.mainloop()
# end def

if __name__ == '__main__':
    # if this code is not running as an imported module run test code
    _test()
# end if