# script to log the internal resistance of a cell over it's discharge curve

import Power_Supply
import DC_Load
import csv
import os
import time
import Multimeter
import random
import BM2_aardvark

import sys
sys.path.insert(1, '../process/src')

import process_SCPI

# set constants
output_filename = "Profile Log.csv"
full_filename = os.getcwd() + '/' + output_filename

timestep = 5
taper_current = 0.050
charge_voltage = 4.2
charge_current = 1.25
discharge_current = 0.500
min_voltage = 2.5

rest_duration = 3600

is_test = False
use_BM2 = False
use_I2C = False
invert_current = True

class Measurement_device:
    def __init__(self):
        if use_BM2:
            self.device = BM2_aardvark.BM2()
            
        elif use_I2C:
            self.device = process_SCPI.aardvark()
            
        else:
            self.device = Multimeter.Multimeter('DM3058E')
        # end if        
    # end def
    
    def __enter__(self):
        self.device.open()
    # end def
    
    def __exit__(self, type, value, traceback):
        self.device.close()
    # end def       
    
    def get_is_fully_charged(self):
        if use_BM2:
            while not self.device.update_data():
                print "BM2 data collection was bad"
                time.sleep(0.05)
            # end while        
            return self.device.get_FC()
        
        elif use_I2C:
            return (self.device.read_SCPI("BM2:TEL? 22,data", "0x5C", "uint") & int('0020',16)) != 0
            
        else:
            if invert_current:
                return ((self.device.get_DC_current()*-1) < taper_current)
            
            else:
                return (self.device.get_DC_current() < taper_current)
            # end if
        # end if    
    # end def
    
    def get_is_discharged(self):
        if use_BM2:
            while not self.device.update_data():
                print "BM2 data collection was bad"
                time.sleep(0.05)
            # end while            
            return self.device.get_CUV()
        
        elif use_I2C:
            return (self.device.read_SCPI("BM2:TEL? 80,data", "0x5C", "uint") & int('0080',16)) != 0
            
        else:
            return (self.device.get_DC_voltage(secondary = True) < min_voltage)
        # end if    
    # end def        
    
    def get_current(self):
        if use_BM2:
            while not self.device.update_data():
                print "BM2 data collection was bad"
                time.sleep(0.05)
            # end while            
            return self.device.Data.Current/1000.0
        
        elif use_I2C:
            return self.device.read_SCPI("BM2:TEL? 10,data", "0x5C", "int")/1000.0
            
        else:
            return self.device.get_DC_current()
        # end if    
    # end def  
    
    def get_voltage(self):
        if use_BM2:
            while not self.device.update_data():
                print "BM2 data collection was bad"
                time.sleep(0.05)
            # end while            
            return self.device.Data.Voltage/1000.0
        
        elif use_I2C:
            return self.device.read_SCPI("BM2:TEL? 9,data", "0x5C", "uint")/1000.0        
            
        else:
            return self.device.get_DC_voltage(secondary = True)
        # end if    
    # end def   
    
    def get_internal_resistance(self):
        if use_I2C:
            return self.device.read_SCPI("BM2:TEL? 37,data", "0x5C", "uint")/10000.0      
        else:
            print "Internal resistance capture is not supported by this capture mode"
        # end if
    # end def
    
    def get_smoothed_voltage(self):
        if use_I2C:
            return self.device.read_SCPI("BM2:TEL? 38,data", "0x5C", "uint")/1000.0      
        else:
            print "smoothed voltage capture is not supported by this capture mode"
        # end if
    # end def    
    
    def get_approximate_SOC(self):
        if use_I2C:
            return self.device.read_SCPI("BM2:TEL? 36,data", "0x5C", "char")     
        else:
            print "Approximate SOC capture is not supported by this capture mode"
        # end if
    # end def    
    
    def get_relative_SOC(self):
        if use_I2C:
            return self.device.read_SCPI("BM2:TEL? 13,data", "0x5C", "char")  
        else:
            print "Approximate SOC capture is not supported by this capture mode"
        # end if
    # end def
    
    def get_absolute_SOC(self):
        if use_I2C:
            return self.device.read_SCPI("BM2:TEL? 14,data", "0x5C", "char")   
        else:
            print "Approximate SOC capture is not supported by this capture mode"
        # end if
    # end def    
# end class

# init

PS = Power_Supply.PowerSupply('KA3005P')
Load = DC_Load.DCLoad('M9711')
Meas_Dev = Measurement_device()

total_start_time = time.time()

# charge the cell
print "Starting Charging"
with Meas_Dev:
    with PS:
        # set the charging voltage and current and turn on
        PS.set_voltage(charge_voltage)
        PS.set_current(charge_current)
        PS.output_on()
        
        Meas_Dev.get_current()
        Meas_Dev.get_voltage()
        
        time.sleep(timestep)
        
        # wait for the taper current requirement to be met.
        while not Meas_Dev.get_is_fully_charged():
            
            if is_test:
                # if this is a test, stop charging after 1 min
                if ((time.time() - total_start_time) > 60):
                    break
                # end if
                
                print ("time = " + str((time.time() - total_start_time) / 60) + "mins, voltage = "
                       + str(Meas_Dev.get_voltage()) + "V, current = "
                       + str(Meas_Dev.get_current()) + "A")
            # end if
            
            time.sleep(timestep)
        # end while
        
        PS.output_off()
    # end with

    # rest
    print "Resting after " + str((time.time() - total_start_time) / 60) + " mins"
    if not is_test:
        # only rest if this is not a test
        time.sleep(rest_duration)
    # end if
    
    # init the CSV
    if os.path.isfile(full_filename):
        os.remove(full_filename);
    # end if
    
    # set up the csv writing output
    with open(full_filename, 'wb') as csv_output:
        output_writer = csv.writer(csv_output, delimiter = '\t')
        
        # write the header row
        if use_I2C:
            output_writer.writerow(['Time (s)' , 'Voltage', 'Current', 
                                    'Internal Resistance', 'Compensated Voltage',
                                    'Approximate SOC', 'Relative SOC', 'Absolute SOC'])
        else:
            output_writer.writerow(['Time (s)' , 'Voltage', 'Current'])
        # end if
        
        # baseling for logging time
        start_time = time.time()
        
        # discharge the cell and log
        print "Discharging after " + str((time.time() - total_start_time) / 60) + " mins"
        with Load:
            
            # write initial row
            if use_I2C:
                output_writer.writerow([0 , Meas_Dev.get_voltage(), 
                                        Meas_Dev.get_current(),
                                        Meas_Dev.get_internal_resistance(),
                                        Meas_Dev.get_smoothed_voltage(),
                                        Meas_Dev.get_approximate_SOC(),
                                        Meas_Dev.get_relative_SOC(),
                                        Meas_Dev.get_absolute_SOC()])
            else:
                output_writer.writerow([0 , Meas_Dev.get_voltage(), Meas_Dev.get_current()])
            # end if
            
            # turn on the load
            Load.set_mode('constant_current', discharge_current)
            Load.load_on()
            
            # wait for the next time step
            time.sleep(timestep)
            
            # wait for the cell to discahrge
            while not Meas_Dev.get_is_discharged():
                
                # write current data
                if use_I2C:
                    output_writer.writerow([(time.time() - start_time),
                                            Meas_Dev.get_voltage(), 
                                            Meas_Dev.get_current(),
                                            Meas_Dev.get_internal_resistance(),
                                            Meas_Dev.get_smoothed_voltage(),
                                            Meas_Dev.get_approximate_SOC(),
                                            Meas_Dev.get_relative_SOC(),
                                            Meas_Dev.get_absolute_SOC()])            
                else:
                    output_writer.writerow([(time.time() - start_time) , Meas_Dev.get_voltage(), Meas_Dev.get_current()])
                # end if
                
                # wait for the next time step
                time.sleep(timestep)                
                
                if is_test:
                    # only run for 5 mins if this is a test
                    if ((time.time() - start_time) > 5*60):
                        break
                    # end if
                    
                    print ("time = " + str((time.time() - start_time) / 60) + "mins, voltage = "
                                       + str(Meas_Dev.get_voltage()) + "V, current = "
                                       + str(Meas_Dev.get_current()) + "A")                    
                # end if
            # end while
            
            # turn off the load
            Load.load_off()
        # end with
        
        # rest
        print "Resting after " + str((time.time() - total_start_time) / 60) + " mins"
        
        restart_time = time.time()
        
        while True:
            # wait for the next time step
            time.sleep(timestep)
        
            # write current data
            if use_I2C:
                output_writer.writerow([(time.time() - start_time),
                                        Meas_Dev.get_voltage(), 
                                        Meas_Dev.get_current(),
                                        Meas_Dev.get_internal_resistance(),
                                        Meas_Dev.get_smoothed_voltage(),
                                        Meas_Dev.get_approximate_SOC(),
                                        Meas_Dev.get_relative_SOC(),
                                        Meas_Dev.get_absolute_SOC()])            
            else:            
                output_writer.writerow([(time.time() - start_time) , Meas_Dev.get_voltage(), Meas_Dev.get_current()])   
            # end if
            
            if is_test and ((time.time() - restart_time) > 60):
                break
            
            elif ((time.time() - restart_time) > rest_duration):
                break
            # end if
        # end while
        
        # charge the cell and log
        print "Charging after " + str((time.time() - total_start_time) / 60) + " mins"    
        
        # charge the cell and log
        with PS:
            
            # set the charging voltage and current and turn on
            PS.set_voltage(charge_voltage)
            PS.set_current(charge_current)
            PS.output_on()
            
            # write initial row
            if use_I2C:
                output_writer.writerow([(time.time() - start_time),
                                        Meas_Dev.get_voltage(), 
                                        Meas_Dev.get_current(),
                                        Meas_Dev.get_internal_resistance(),
                                        Meas_Dev.get_smoothed_voltage(),
                                        Meas_Dev.get_approximate_SOC(),
                                        Meas_Dev.get_relative_SOC(),
                                        Meas_Dev.get_absolute_SOC()])            
            else:            
                output_writer.writerow([(time.time() - start_time) , Meas_Dev.get_voltage(), Meas_Dev.get_current()])  
            # end if
            
            restart_time = time.time()
            
            time.sleep(timestep)
            # write current data            
            
            # wait for the taper current requirement to be met.
            while not Meas_Dev.get_is_fully_charged():

                if use_I2C:
                    output_writer.writerow([(time.time() - start_time),
                                            Meas_Dev.get_voltage(), 
                                            Meas_Dev.get_current(),
                                            Meas_Dev.get_internal_resistance(),
                                            Meas_Dev.get_smoothed_voltage(),
                                            Meas_Dev.get_approximate_SOC(),
                                            Meas_Dev.get_relative_SOC(),
                                            Meas_Dev.get_absolute_SOC()])            
                else:                
                    output_writer.writerow([(time.time() - start_time) , Meas_Dev.get_voltage(), Meas_Dev.get_current()])
                # end if  
                
                if is_test:
                    # only run for 5 mins if this is a test
                    if ((time.time() - restart_time) > 5*60):
                        break
                    # end if
                    
                    print ("time = " + str((time.time() - start_time) / 60) + "mins, voltage = "
                                       + str(Meas_Dev.get_voltage()) + "V, current = "
                                       + str(Meas_Dev.get_current()) + "A")                    
                # end if   
                
                time.sleep(timestep)
                # write current data                
            # end while
            
            PS.output_off()
        # end with
    # end with
# end with

print "Complete after " + str((time.time() - total_start_time) / 60) + " mins"

        
        


    


