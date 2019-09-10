import visa
import time

rm = visa.ResourceManager()
print(rm.list_resources())


with rm.open_resource('USB0::0x1AB1::0x09C4::DM3R185250778::INSTR') as dmm:

    value = dmm.query(":MEASure:VOLTage:DC?")
    time.sleep(2)
    print float(value) 
    value = dmm.query(":MEASure:CURRent:DC?")
    time.sleep(2)
    print float(value)    
    value = dmm.query(":MEASure:RESistance?")
    time.sleep(2)
    print float(value)    
    
# end with