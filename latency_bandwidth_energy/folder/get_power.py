import threading
import time

agx_orin_nodes = [
    ('module/gpu', '0040', '0', '1'),
    ('module/cpu', '0040', '0', '2'),
    ('module/ddr', '0041', '1', '2'),
]

def readValue(i2cAddr='0041', index='3', channel='1'):
    """Reads all values (voltage, current, power) from one node"""

    voltage, current = None, None

    fname_voltage = '/sys/bus/i2c/drivers/ina3221/1-%s/hwmon/hwmon%s/in%s_input' % (i2cAddr, index, channel)
    with open(fname_voltage, 'r') as f:
        voltage = f.read()
    
    fname_current = '/sys/bus/i2c/drivers/ina3221/1-%s/hwmon/hwmon%s/curr%s_input' % (i2cAddr, index, channel)
    with open(fname_current, 'r') as f:
        current = f.read()
    
    return [float(voltage), float(current), float(voltage) * float(current)]

def readAllValue(nodes = agx_orin_nodes):
    """Reads all values (voltage, current, power) from all nodes"""
    
    values = [readValue(i2cAddr=node[1], index=node[2], channel=node[3]) for node in nodes]
    return values

if __name__ == "__main__":
	print(readAllValue())