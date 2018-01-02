import Power_Supply
import time

t1 = time.time()
PS = Power_Supply.PowerSupply('KA3005P')
print 'init time = ' + str(time.time() - t1)

t1 = time.time()
with PS:
    print 'with time = ' + str(time.time() - t1)
    PS.set_voltage(12)

    PS.output_on()

    print PS.get_output_voltage()
