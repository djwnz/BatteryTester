#!/usr/bin/env python
################################################################################
#(C) Copyright Pumpkin, Inc. All Rights Reserved.
#
#This file may be distributed under the terms of the License
#Agreement provided with this software.
#
#THIS FILE IS PROVIDED AS IS WITH NO WARRANTY OF ANY KIND,
#INCLUDING THE WARRANTY OF DESIGN, MERCHANTABILITY AND
#FITNESS FOR A PARTICULAR PURPOSE.
################################################################################
"""
@package BM2_aardvark.py
Module to handle talking to a BM2 with the aardvark
"""

__author__ = 'David Wright (david@pumpkininc.com)'
__version__ = '0.3.1' #Versioning: http://www.python.org/dev/peps/pep-0386/


#
# -------
# Imports

import aardvark_py
from array import array
from struct import unpack
import Tkinter as TK


# ---------
# Constants

# I2C config
I2C = True
SPI = True
GPIO = False
Pullups = True
radix = 16
Bitrate = 100

#
# ----------------
# Classes

class BM2_Data:
    def __init__(self):
        self.Voltage = 0
        self.Current = 0
        self.ChargingVoltage = 0
        self.ChargingCurrent = 0
        self.OperationStatus = 0
        self.SafetyAlert = 0
        self.SafetyStatus = 0
        self.MaxError = 0
        self.BatteryStatus = 0
        self.CellVoltage1 = 0
        self.CellVoltage2 = 0
        self.CellVoltage3 = 0
        self.CellVoltage4 = 0
        self.UpdateStatus = 0
        
        self.headers = ['time', 
                        'voltage', 
                        'current', 
                        'ChargingVoltage', 
                        'ChargingCurrent', 
                        'OperationStatus', 
                        'SafetyAlert', 
                        'SafetyStatus',
                        'MaxError', 
                        'BatteryStatus', 
                        'CellVoltage1', 
                        'CellVoltage2', 
                        'CellVoltage3', 
                        'CellVoltage4', 
                        'UpdateStatus']
    # end def
    
    def to_list(self, time):
        return [time, 
                self.Voltage, 
                self.Current, 
                self.ChargingVoltage, 
                self.ChargingCurrent,
                self.OperationStatus,
                self.SafetyAlert,
                self.SafetyStatus,
                self.MaxError,
                self.BatteryStatus,
                self.CellVoltage1,
                self.CellVoltage2,
                self.CellVoltage3,
                self.CellVoltage4,
                self.UpdateStatus]
    # end def
# end def
        

class BM2:
    """
    Class that operates the Aardvark device

    @attribute message      (string) Place to store error messages
    @attribute port         (Aardvark_py.Aardvark handle) 
                                     The aardvark port in use
    """ 

    def __init__(self):
        """
        Initialise the BM2 object to its default values
        """
        self.port = None
        self.Data = BM2_Data()
        
    #end def

    def __enter__(self):
        """
        For use with the 'with' operator
        """   
        self.port = configure_aardvark()
        
        if (self.port == None):
            raise IOError("No Aardvark was found")
        # end if
        
        #if ((self.get_ChargingVoltage() == 257) 
            #and (self.get_TaperCurrent() == 257)):
            #raise IOError("No BM2 was detected")
        ## end if
        
        return self
    # end def
    
    def open(self):
        """
        If used in another 'with' capable mosule this provides __enter__ 
        functionality
        """
        self.port = configure_aardvark()
        
        if (self.port == None):
            raise IOError("No Aardvark was found")
        # end if
    # end def
    
    def __exit__(self, type, value, traceback):
        """
        Ensures that the aardvark port is closed correctly
        
        For use with the 'with' operator
        """      
        if self.port != None:
            aardvark_py.aa_close(self.port)
        #end if
        
        self.port = None
    #end def
    
    def close(self):
        """
        If used in another 'with' capable module this provided __exit__ 
        functionality
        """
        if self.port != None:
            aardvark_py.aa_close(self.port)
        #end if
        
        self.port = None
    #end def        
    
    def validate_data(self):
        if self.Data.MaxError > 200:
            return False
        
        elif (self.Data.Voltage > 17000) or (self.Data.Voltage < 5000):
            return False
        
        elif (self.Data.CellVoltage1 > 4500) or (self.Data.CellVoltage1 < 2000):
            return False
        
        elif (self.Data.CellVoltage2 > 4500) or (self.Data.CellVoltage2 < 2000):
            return False

        elif (self.Data.CellVoltage3 > 4500):
            return False
        
        elif (self.Data.CellVoltage4 > 4500):
            return False
        
        elif ((self.Data.OperationStatus & 0x8000) == 0):
              return False
                
        else:
            return True
        # end if
    # end def
    
    def update_data(self):
        self.Data.Voltage = self.get_Voltage()
        self.Data.Current = self.get_Current()
        self.Data.ChargingVoltage = self.get_ChargingVoltage()
        self.Data.ChargingCurrent = self.get_ChargingCurrent()
        self.Data.OperationStatus = self.get_OperationStatus()
        self.Data.SafetyAlert = self.get_SafetyAlert()
        self.Data.SafetyStatus = self.get_SafetyStatus()
        self.Data.MaxError = self.get_MaxError()
        self.Data.BatteryStatus = self.get_BatteryStatus()
        self.Data.CellVoltage1 = self.get_CellVoltage1()
        self.Data.CellVoltage2 = self.get_CellVoltage2()
        self.Data.CellVoltage3 = self.get_CellVoltage3()
        self.Data.CellVoltage4 = self.get_CellVoltage4()
        self.Data.UpdateStatus = self.get_UpdateStatus()
        
        return self.validate_data()
    # end def
    
    def get_Voltage(self):
        return send_SMB_command('0x09', self.port, 'uint')
    #end def
    
    def get_Current(self):
        return send_SMB_command('0x0A', self.port, 'int')
    #end def    
    
    def get_ChargingVoltage(self):
        return send_SMB_command('0x15', self.port, 'uint')
    #end def
    
    def get_ChargingCurrent(self):
        return send_SMB_command('0x14', self.port, 'uint')
    #end def
    
    def get_OperationStatus(self):
        return send_SMB_command('0x54', self.port, 'uint')
    #end def       
    
    def get_SafetyAlert(self):
        return send_SMB_command('0x50', self.port, 'uint')
    #end def      
    
    def get_SafetyStatus(self):
        return send_SMB_command('0x51', self.port, 'uint')
    #end def    
    
    def get_MaxError(self):
        return send_SMB_command('0x0C', self.port, 'char')
    #end def    
    
    def get_BatteryStatus(self):
        return send_SMB_command('0x16', self.port, 'uint')
    #end def    
    
    def get_CellVoltage1(self):
        return send_SMB_command('0x3f', self.port, 'uint')
    #end def     
    
    def get_CellVoltage2(self):
        return send_SMB_command('0x3e', self.port, 'uint')
    #end def  
    
    def get_CellVoltage3(self):
        return send_SMB_command('0x3d', self.port, 'uint')
    #end def  
    
    def get_CellVoltage4(self):
        return send_SMB_command('0x3c', self.port, 'uint')
    #end def      
    
    def get_RDIS(self):
        return (self.Data.OperationStatus & int('0004',16)) != 0
    # end def
    
    def get_VOK(self):
        return (self.Data.OperationStatus & int('0002',16)) != 0
    # end def    
    
    def get_QEN(self):
        return (self.Data.OperationStatus & int('0001',16)) != 0
    # end def    
    
    def get_CUV(self):
        return (self.Data.SafetyAlert & int('0080',16)) != 0
    # end def    
    
    def get_FC(self):
        return (self.Data.BatteryStatus & int('0020',16)) != 0
    # end def     
    
    def get_TaperCurrent(self):
        send_SMB_data(['0x77', '0x24', '0x00'], self.port)
        aardvark_py.aa_sleep_ms(50) 
        flash_page = send_SMB_command('0x78', self.port, 'page')
        flash_page = flash_page[1:] # remove length byte
        return flash_page[3] + flash_page[2]*256
    #end def    
    
    def get_UpdateStatus(self):
        send_SMB_data(['0x77', '0x52', '0x00'], self.port)
        aardvark_py.aa_sleep_ms(50) 
        flash_page = send_SMB_command('0x78', self.port, 'page')
        flash_page = flash_page[1:] # remove length byte
        return "0x%0.2X" % flash_page[12]
    #end def     
    
    def get_FC(self):
        return (send_SMB_command('0x16', self.port, 'uint') & int('0020',16)) != 0
    # end def
# end class

class BM2_GUI:
    """
    Class to operate the GUI for the Load and the Load itself.
    
    @attribute frame           (TK Frame)     The frame which contains the GUI 
                                              objects for this class.
    @attribute model           (string)       The model of the Load in use.
    @attribute gui             (TK tk)        the root GUI object.
    @attribute Load            (DC_Load)      The DC Load object in use.
    @attribute output_state    (string)       The current input state of the 
                                              Load : 'on' or 'off'.
    @attribute enabled         (bool)         Whether or not the gui is enabled
    @attribute mode            (TK Stringvar) The mode of the DC load.
    @attribute cc_button       (RadioButton)  Selector for constant current mode.
    @attribute cv_button       (RadioButton)  Selector for constant voltage mode.
    @attribute cp_button       (RadioButton)  Selector for constant power mode.
    @attribute cr_button       (RadioButton)  Selector for constant resistance mode.
    @attribute setting         (TK Entry)     Box where Load settings are entered.
    @attribute units           (TK Label)     Units label for the settings box.
    @attribute set_button      (TK Button)    Button that sends the new settings 
                                              to the load.
    @attribute on_button       (TK Button)    The button that turns the input 
                                              on and off.
    @attribute voltage_value   (TK Label)     Display of the actual load
                                              voltage.
    @attribute current_value   (TK Label)     Display of the actual load
                                              current.
    @attribute power_value     (TK Label)     Display of the actual load
                                              power.
    """  
    
    def __init__(self, gui_frame, gui):
        """
        Initialise the PowerSupply Object
        
        @param[in] gui_frame  The frame where all GUI items should be put 
                              (TK Frame)
        @param[in] gui        The root GUI object (TK tk)
        @param[in] model      The model of the power supply selected (string)
        """   
        
        # initialise attributes
        self.frame = gui_frame
        self.gui = gui
        self.enabled = False
        
        # initialise the powerSupply to be used
        self.BM = BM2()
        
        # load the GUI elements
        self.load_gui()
    # end def


    def load_gui(self):
        """
        Add all the GUI elements to the GUI
        """
        
        # add a border to the frame
        self.frame.config(borderwidth = 2, relief = 'raised')
        
        # title
        title = TK.Label(self.frame, text = "Battery Module Data", 
                         font = "Arial 14 bold")
        title.grid(row = 0, column = 0, columnspan = 4)
                 
        # voltage display
        voltage_title = TK.Label(self.frame, text = "Voltage (V)", 
                                 font = "Arial 10 italic")
        voltage_title.grid(row = 1, column = 0)
        self.voltage_value = TK.Label(self.frame, text = "-")
        self.voltage_value.grid(row = 2, column = 0, ipadx = 5, ipady = 8)
        
        # current display
        current_title = TK.Label(self.frame, text = "Current (A)", 
                                     font = "Arial 10 italic")
        current_title.grid(row = 3, column = 0)
        self.current_value = TK.Label(self.frame, text = "-")
        self.current_value.grid(row = 4, column = 0, ipadx = 5, ipady = 8)  
        
        # charging voltage display
        charging_voltage_title = TK.Label(self.frame, text = "Charging Voltage (V)", 
                                     font = "Arial 10 italic")
        charging_voltage_title.grid(row = 1, column = 1)
        self.charging_voltage_value = TK.Label(self.frame, text = "-")
        self.charging_voltage_value.grid(row = 2, column = 1, ipadx = 5, ipady = 8)
    
        # charging current display
        charging_current_title = TK.Label(self.frame, text = "Charging Current (A)", 
                                     font = "Arial 10 italic")
        charging_current_title.grid(row = 3, column = 1)
        self.charging_current_value = TK.Label(self.frame, text = "-")
        self.charging_current_value.grid(row = 4, column = 1, ipadx = 5, ipady = 8)     
        
        # update status display
        update_status_title = TK.Label(self.frame, text = "Update Status", 
                                              font = "Arial 10 italic")
        update_status_title.grid(row = 1, column = 2)
        self.update_status_value = TK.Label(self.frame, text = "-")
        self.update_status_value.grid(row = 2, column = 2, ipadx = 5, ipady = 8)
    
        # taper current display
        taper_current_title = TK.Label(self.frame, text = "Taper Current (A)", 
                                              font = "Arial 10 italic")
        taper_current_title.grid(row = 3, column = 2)
        self.taper_current_value = TK.Label(self.frame, text = "-")
        self.taper_current_value.grid(row = 4, column = 2, ipadx = 5, ipady = 8)    
        
        # RDIS Flag display
        self.RDIS_flag = TK.Label(self.frame, text = "RDIS")
        self.RDIS_flag.grid(row = 1, column = 3, ipadx = 5, ipady = 8)    
        
        # VOK Flag display
        self.VOK_flag = TK.Label(self.frame, text = "VOK")
        self.VOK_flag.grid(row = 2, column = 3, ipadx = 5, ipady = 8)       
        
        # QEN Flag display
        self.QEN_flag = TK.Label(self.frame, text = "QEN")
        self.QEN_flag.grid(row = 3, column = 3, ipadx = 5, ipady = 8)     
        
        # FC Flag display
        self.FC_flag = TK.Label(self.frame, text = "FC")
        self.FC_flag.grid(row = 4, column = 3, ipadx = 5, ipady = 8)          
             
        # update the gui from the power supply
        self.update_gui()     
    #end def 
    
    def disable_gui(self):
        """
        Disable the GUI elements
        """
        self.enabled = False
        self.voltage_value.config(text = '-')
        self.current_value.config(text = '-')
        self.charging_voltage_value.config(text = '-')
        self.charging_current_value.config(text = '-')
        self.update_status_value.config(text = '-')
        self.taper_current_value.config(text = '-')
        
        self.RDIS_flag.config(background = self.frame.cget('bg'))
        self.QEN_flag.config(background = self.frame.cget('bg'))
        self.VOK_flag.config(background = self.frame.cget('bg'))
        self.FC_flag.config(background = self.frame.cget('bg'))
    # end def
    
    
    def update_gui(self):
        """
        Update the gui from the Load. This task becomes preiodic once 
        the GUI is running.
        """
        
        # default values
        voltage = '-'
        current = '-'
        
        # attempt to communicate with the Load
        try:
            with self.BM:
                # communicatins were successful
                    
                self.enabled = True
                
                self.voltage_value.config(text = '%.3f' % (self.BM.get_Voltage()/1000.0))
                self.current_value.config(text = '%.3f' % (self.BM.get_Current()/1000.0))
                self.charging_voltage_value.config(text = '%.3f' % (self.BM.get_ChargingVoltage()/1000.0))
                self.charging_current_value.config(text = '%.3f' % (self.BM.get_ChargingCurrent()/1000.0))
                self.update_status_value.config(text = self.BM.get_UpdateStatus())
                self.taper_current_value.config(text = '%.3f' % (self.BM.get_TaperCurrent()/1000.0))
            
                if self.BM.get_VOK():
                    self.VOK_flag.config(background = 'green')
                # end if
                
                if self.BM.get_RDIS():
                    self.RDIS_flag.config(background = 'green')
                # end if         
                
                if self.BM.get_QEN():
                    self.QEN_flag.config(background = 'green')
                # end if        
                
                if self.BM.get_FC():
                    self.FC_flag.config(background = 'green')
                # end if         
            # end with
            
        except Exception as e:
            # communcations could not be esablished to disable the gui
            self.disable_gui()
            self.BM.__exit__(None, None, None)
            print e
        # end try  
        
        # schedule the next repetition of this function
        self.gui.after(1000, self.update_gui)
    #end def
    
    def close_GUI(self):
        """
        Function to reset controls on the load when the gui exits.
        """
        self.BM.__exit__(None, None, None)
    # end def
# end class
    

#
# ----------------
# Public Functions



#
# ----------------
# Private Functions

def configure_aardvark():
    """ 
    Function to configure the aardvark for pySCPI operation if there is one
    available.
    
    @return  (aardvark_py.aardvark)   The handle of the aardvark to be used
                                      'None' if there is not one available
    """
    # define the handle to return
    Aardvark_in_use = None
    
    # find all connected aardvarks
    AA_Devices = aardvark_py.aa_find_devices(1)
    
    # define a port mask
    Aardvark_port = 8<<7
    
    # assume that an aardvark can be found until proved otherwise
    Aardvark_free = True
    
    # Check if there is an Aardvark present
    if (AA_Devices[0] < 1):
        # there is no aardvark to be found
        print '*** No Aardvark is present ***'
        Aardvark_free = False
        
    else:
        # there is an aardvark connected to select the first one if there
        # are many
        Aardvark_port = AA_Devices[1][0]
    # end if
    
    
    # If there is an Aardvark there is it free?
    if Aardvark_port >= 8<<7 and Aardvark_free:
        # the aardvark is not free
        print '*** Aardvark is being used, '\
              'disconnect other application or Aardvark device ***'
        # close the aardvark
        aardvark_py.aa_close(Aardvark_port)
        Aardvark_free = False
        
    elif Aardvark_free:
        # Aardvark is available so configure it
        
        # open the connection with the aardvark
        Aardvark_in_use = aardvark_py.aa_open(Aardvark_port)
        
        # set it up in teh mode we need for pumpkin modules
        aardvark_py.aa_configure(Aardvark_in_use, 
                                 aardvark_py.AA_CONFIG_GPIO_I2C)
        
        # default to both pullups on
        aardvark_py.aa_i2c_pullup(Aardvark_in_use, 
                                  aardvark_py.AA_I2C_PULLUP_BOTH)
        
        # set the bit rate to be the default
        aardvark_py.aa_i2c_bitrate(Aardvark_in_use, Bitrate)
        
        # free the bus
        aardvark_py.aa_i2c_free_bus(Aardvark_in_use)
        
        # delay to allow the config to be registered
        aardvark_py.aa_sleep_ms(200)    
        
    # end if    
    
    return Aardvark_in_use
# end def

def send_SMB_data(data, Aardvark_in_use):
    """
    Function to send a SCPI command to the slave device
    
    @param[in]    data:            the hex data to send (list of strings)
    @param[in]    Aardvark_in_use: The Aaardvark to use to read the data
                                   (aardvark_py.aardvark)
    """  
    BM2_Address = int('0x0B', 16)
    write_data = []
    
    for byte in data:
        if is_hex(byte):
            write_data = write_data + [int(byte,16)]
        else:
            return None
        # end if
    # end for
    
    out_data = array('B', write_data)  

    # Write the data to the slave device
    aardvark_py.aa_i2c_write(Aardvark_in_use, BM2_Address, 
                    aardvark_py.AA_I2C_NO_FLAGS, out_data)    
    
    aardvark_py.aa_sleep_ms(1)
# end def

def send_SMB_command(command, Aardvark_in_use, return_format):
    """
    Function to send a SCPI command to the slave device
    
    @param[in]    command:         the hex command to send (string)
    @param[in]    Aardvark_in_use: The Aaardvark to use to read the data
                                   (aardvark_py.aardvark)
    @param[in]    return_format    format to return the data in
    """  
    BM2_Address = int('0x0B', 16)
    
    # convert the data into a list of bytes and append the terminator
    if is_hex(command):
        write_data = [int(command,16)]
    
        # convert to an array to be compiant with the aardvark
        out_data = array('B', write_data)  
        
        # Write the data to the slave device
        #aardvark_py.aa_i2c_write(Aardvark_in_use, BM2_Address, 
                                 #aardvark_py.AA_I2C_NO_FLAGS, out_data)
        
        aardvark_py.aa_sleep_ms(1)
        
        if return_format == 'none':
            return None
        
        elif return_format == 'int':
            # define array to read data into
            in_data = array('B', [1]*2) 
            
            # read from the slave device
            read_data = aardvark_py.aa_i2c_write_read(Aardvark_in_use, 
                                                BM2_Address, 
                                                aardvark_py.AA_I2C_NO_FLAGS, 
                                                out_data, in_data)    
            
            return unpack('<h', ''.join([chr(x) for x in in_data]))[0]
            
        elif return_format == 'uint':
            # define array to read data into
            in_data = array('B', [1]*2) 
        
            # read from the slave device
            read_data = aardvark_py.aa_i2c_write_read(Aardvark_in_use, 
                                                BM2_Address, 
                                                aardvark_py.AA_I2C_NO_FLAGS, 
                                                out_data, in_data)  
            
            return unpack('<H', ''.join([chr(x) for x in in_data]))[0]               
            
        elif return_format == 'char':
            
            # define array to read data into
            in_data = array('B', [1]*1) 
        
            # read from the slave device
            read_data = aardvark_py.aa_i2c_write_read(Aardvark_in_use, 
                                                BM2_Address, 
                                                aardvark_py.AA_I2C_NO_FLAGS, 
                                                out_data, in_data)  
            
            return unpack('<B', ''.join([chr(x) for x in in_data]))[0] 
            
        elif return_format == 'schar':
            
            # define array to read data into
            in_data = array('B', [1]*1) 
        
            # read from the slave device
            read_data = aardvark_py.aa_i2c_write_read(Aardvark_in_use, 
                                                BM2_Address, 
                                                aardvark_py.AA_I2C_NO_FLAGS, 
                                                out_data, in_data)   
            
            return unpack('<b', ''.join([chr(x) for x in in_data]))[0]                 
        
        elif return_format == 'hex':
            
            # define array to read data into
            in_data = array('B', [1]*2) 
        
            # read from the slave device
            read_data = aardvark_py.aa_i2c_write_read(Aardvark_in_use, 
                                                BM2_Address, 
                                                aardvark_py.AA_I2C_NO_FLAGS, 
                                                out_data, in_data)  
            
            return ' '.join(['%02X' % x for x in reversed(in_data)])
        # end if   
        
        elif return_format == 'page':
            
            # define array to read data into
            in_data = array('B', [1]*32) 
        
            # read from the slave device
            read_data = aardvark_py.aa_i2c_write_read(Aardvark_in_use, 
                                                BM2_Address, 
                                                aardvark_py.AA_I2C_NO_FLAGS, 
                                                out_data, in_data)  
            
            return list(in_data)
        # end if         
               
    else:
        return None
    # end if
# end def

def is_hex(s):
    """
    Determine if a string is a hexnumber
    
    @param[in]  s:       The string to be tested (string).
    @return     (bool)   True:    The string is a hex number.
                         False:   The command is not a hex number.
    """    
    # if it can be converted to a base 16 int then it is hex
    try:
        int(s, 16)
        return True
    
    except ValueError:
        # it could not be converted therefore is not hex
        return False
    # end try
# end def

def _test():
    """
    Test code for this module.
    """
    # construct the root frame
    root = TK.Tk()
    root.geometry('800x600')
    
    # construct a frame for the load gui
    test_frame = TK.Frame(root)
    test_frame.grid(row = 0, column = 0)
    
    # initialise the load gui
    BM2_gui = BM2_GUI(test_frame, root)
    
    #BM = BM2()
    #with BM:
        #print BM.get_Voltage()
        
    # start the GUI
    root.mainloop()
# end def

if __name__ == '__main__':
    # if this code is not running as an imported module run test code
    _test()
# end if