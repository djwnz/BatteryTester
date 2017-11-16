import Power_Supply

PS = Power_Supply.PowerSupply('KA3005P')

PS.set_voltage(12)

PS.output_on()

print PS.get_output_voltage()

PS.close()