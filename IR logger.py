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
output_filename = "IR test.csv"
full_filename = os.getcwd() + '/' + output_filename

timestep = 5
pulse_width = 60
taper_current = 0.200
charge_voltage = 16.8
charge_current = 4
min_voltage = 2.5

fast_current = 3
slow_current = 0.3

rest_duration = 3600

pulse_loops = pulse_width/timestep

is_test = False
do_random = True
use_BM2 = False
use_I2C = True
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
                return ((self.device.get_DC_current(secondary = True)*-1) < taper_current)
            
            else:
                return (self.device.get_DC_current(secondary = True) < taper_current)
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
            return (self.device.get_DC_voltage() < min_voltage)
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
            return self.device.get_DC_current(secondary = True)
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
            return self.device.get_DC_voltage()
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
    

def get_random_current():
    return random.randint(slow_current*1000, fast_current*1000)/1000.0
# end def

if is_test:
    print "Test Execution running"

else:
    print "Full Internal resistance logging initiated"
# end if

# init

PS = Power_Supply.PowerSupply('KA3005P')
Load = DC_Load.DCLoad('M9711')
Meas_Dev = Measurement_device()

start_time = time.time()


# charge the cell
print "Charging"
with Meas_Dev:
    with PS:
        # set the charging voltage and current and turn on
        PS.set_voltage(charge_voltage)
        PS.set_current(charge_current)
        PS.output_on()
        
        Meas_Dev.get_current()
        
        time.sleep(timestep)
        
        # wait for the taper current requirement to be met.
        while not Meas_Dev.get_is_fully_charged():
            time.sleep(timestep)
            
            if is_test:
                # if this is a test, stop charging after 1 min
                if ((time.time() - start_time) > 60):
                    break
                # end if
            # end if
        # end while
        
        PS.output_off()
    # end with


    # rest
    print "Resting"
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
        print "Discharging"
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
            Load.set_mode('constant_current', slow_current)
            Load.load_on()
            
            pulse_count = 0
            
            mode = 'slow'
            
            # wait for the cell to discahrge
            while not Meas_Dev.get_is_discharged():
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
                
                # increment pulse counting
                pulse_count += 1
                    
                # perform current pulsing
                if (pulse_count >= pulse_loops):
                    # it is time to change the current
                    pulse_count = 0
                    
                    # change the current setting
                    if do_random:
                        Load.set_mode('constant_current', get_random_current())
                        
                    elif (mode == 'slow'):
                        Load.set_mode('constant_current', fast_current)
                        mode = 'fast'
                    
                    else:
                        Load.set_mode('constant_current', slow_current)
                        mode = 'slow'
                    # end if
                # end if
                
                if is_test:
                    # only run for 5 mins if this is a test
                    if ((time.time() - start_time) > 5*60):
                        break
                    # end if
                # end if
            # end while
            
            # turn off the load
            Load.load_off()
        # end with
        
        # rest
        print "Resting"
        
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
        print "Charging"    
        
        # charge the cell and log
        with PS:
            
            # set the charging voltage and current and turn on
            PS.set_voltage(charge_voltage)
            PS.set_current(slow_current)
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
            
            pulse_count = 0
            
            restart_time = time.time()
            
            mode = 'slow'
            
            # wait for the taper current requirement to be met.
            while not Meas_Dev.get_is_fully_charged():
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
                
                # increment pulse counting
                pulse_count += 1
                    
                # perform current pulsing
                if (pulse_count >= pulse_loops):
                    # it is time to change the current
                    pulse_count = 0
                    
                    # change the current setting
                    if do_random:
                        PS.set_current(get_random_current())
                        
                    elif (mode == 'slow'):
                        PS.set_current(fast_current)
                        mode = 'fast'
                    
                    else:
                        PS.set_current(slow_current)
                        mode = 'slow'
                    # end if
                # end if   
                
                if is_test:
                    # only run for 5 mins if this is a test
                    if ((time.time() - restart_time) > 5*60):
                        break
                    # end if
                # end if            
            # end while
            
            PS.output_off()
        # end with
    # end with
# end with

print "Complete"

        
        


    


