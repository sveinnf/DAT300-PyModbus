'''
Pymodbus Synchronous Client Examples
--------------------------------------------------------------------------

The following is an example of how to use the synchronous modbus client
implementation from pymodbus.

It should be noted that the client can also be used with
the guard construct that is available in python 2.5 and up::

    with ModbusClient('127.0.0.1') as client:
        result = client.read_coils(1,10)
        print result
'''
#---------------------------------------------------------------------------#
# import the various server implementations
#---------------------------------------------------------------------------#
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
#from pymodbus.client.sync import ModbusUdpClient as ModbusClient
#from pymodbus.client.sync import ModbusSerialClient as ModbusClient

#---------------------------------------------------------------------------#
# configure the client logging
#---------------------------------------------------------------------------#
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

#---------------------------------------------------------------------------#
# choose the client you want
#---------------------------------------------------------------------------#
# make sure to start an implementation to hit against. For this
# you can use an existing device, the reference implementation in the tools
# directory, or start a pymodbus server.
#
# If you use the UDP or TCP clients, you can override the framer being used
# to use a custom implementation (say RTU over TCP). By default they use the
# socket framer::
#
#    client = ModbusClient('localhost', port=5020, framer=ModbusRtuFramer)
#
# It should be noted that you can supply an ipv4 or an ipv6 host address for
# both the UDP and TCP clients.
#
# There are also other options that can be set on the client that controls
# how transactions are performed. The current ones are:
#
# * retries - Specify how many retries to allow per transaction (default = 3)
# * retry_on_empty - Is an empty response a retry (default = False)
# * source_address - Specifies the TCP source address to bind to
#
# Here is an example of using these options::
#
#    client = ModbusClient('localhost', retries=3, retry_on_empty=True)
#---------------------------------------------------------------------------#
client = ModbusClient('localhost', port=5020)
#client = ModbusClient(method='ascii', port='/dev/pts/2', timeout=1)
#client = ModbusClient(method='rtu', port='/dev/pts/2', timeout=1)
client.connect()


rq = client.write_coil(0, False)
rr = client.read_coils(0,1)
assert(rq.function_code < 0x80)     # test that we are not an error
assert(rr.bits[0] == False)          # test the expected value

rq = client.write_coils(0, [True]*8)
rr = client.read_coils(0,8)
assert(rq.function_code < 0x80)     # test that we are not an error
assert(rr.bits == [True]*8)          # test the expected value

rq = client.write_register(0,100)
rr = client.read_holding_registers(0,1)
assert(rq.function_code < 0x80)     # test that we are not an error
assert(rr.registers[0] == 100)       # test the expected value

rq = client.write_registers(1, [10]*8)
rr = client.read_holding_registers(1,8)
assert(rq.function_code < 0x80)     # test that we are not an error
assert(rr.registers == [10]*8)      # test the expected value

rr = client.read_input_registers(0,1)
assert(rr.registers[0] == 52)

rr = client.read_discrete_inputs(0,4)
'''
    As we are only reading half a byte of coils, we have to add half a byte of
    of data for our assertion to work ([False]*4)
'''
assert(rr.bits == [True]*4 + [False]*4)
