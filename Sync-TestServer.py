'''
Test server that periodically reads data from a csv file and imports it into correct
registers. The format of the input file should be
Address, Discrete Inputs, Coils, Holding Registers, Input/Output Registers

This server can then be queried by a pymodbus client.

The server periodically wirtes the current values of context to a output file.
The output fileformat is .csv

Usage:
$python3 Sync-TestServer.py "Inputfilename.csv" "OutputFilename.csv"
'''
from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.transaction import ModbusRtuFramer

import csv
import sys
#---------------------------------------------------------------------------#
# import the twisted libraries we need
#---------------------------------------------------------------------------#
#from twisted.internet.task import LoopingCall

#---------------------------------------------------------------------------#
# configure the service logging
#---------------------------------------------------------------------------#
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

#---------------------------------------------------------------------------#
# initialize the server information
#---------------------------------------------------------------------------#
# If you don't set this or any fields, they are defaulted to empty strings.
#---------------------------------------------------------------------------#
identity = ModbusDeviceIdentification()
identity.VendorName  = 'Pymodbus'
identity.ProductCode = 'PM'
identity.VendorUrl   = 'http://github.com/bashwork/pymodbus/'
identity.ProductName = 'Pymodbus Server'
identity.ModelName   = 'Pymodbus Server'
identity.MajorMinorRevision = '1.0'

def read_filedata(filename):
#   Create empty dictionaries used for the input from CSV file
    di = {}
    co = {}
    hr = {}
    ir = {}
    with open(filename, newline='') as csvfile:
        data = csv.reader(csvfile,delimiter=',')
        log.debug("Reading Inputfile")
        #print("Before: ")
        for row in data:
            # Read data into dictionaries, row[0] is address and rest is
            # di = Discrete input, ci = Coils, hr = Holding Registers
            # ir = Input Registrs
            # Addresses should be 1 or higher
#            print([row[0],row[1],row[2],row[3],row[4]])
            di[int(row[0])] = bool(row[1] in ['True','TRUE'])
            co[int(row[0])] = bool(row[2] in ['True','TRUE'])
            hr[int(row[0])] = int(row[3])
            ir[int(row[0])] = int(row[4])

    log.debug("Done!")
    return ModbusSlaveContext(
        di = ModbusSparseDataBlock(di),
        co = ModbusSparseDataBlock(co),
        hr = ModbusSparseDataBlock(hr),
        ir = ModbusSparseDataBlock(ir))

    # Sequential not working at the moment, to be added?!
    # return ModbusSlaveContext(
    #     di = ModbusSequentialDataBlock(0,di),
    #     co = ModbusSequentialDataBlock(0,co),
    #     hr = ModbusSequentialDataBlock(0,hr),
    #     ir = ModbusSequentialDataBlock(0,ir))



def write_filedata(filename,a):
    '''
        Write the data of from a context to a CSV file.
        This function requires that there are no gaps in
        addressing. That is all addresses must be sequential
        for this function to be able to fully write the contents
        of the context.
    '''
    data = a[0]
    log.debug("Writing to file")
    with open(filename,'w',newline='') as csvfile:
        w = csv.writer(csvfile,delimiter=',')
        i = 0
        #print("After: ")
        while(data.validate(1,i) == True):
            # Get values, (function code, Address, Count=1)
            # FC 4 = Read Input Register
            # FC 3 = Read holding register
            # FC 2 = Read Discrete Input (Boolean values)
            # FC 1 = Read Coil (Boolean values)
            line = [i+1,data.getValues(2,i)[0],data.getValues(1,i)[0],data.getValues(3,i)[0],
            data.getValues(4,i)[0]]
            #print(line)
            w.writerow(line)
            i = i+1


#---------------------------------------------------------------------------#
# define your callback process
#---------------------------------------------------------------------------#
def updating_writer(a):
    ''' A worker process that runs every so often and
    updates live values of the context. It should be noted
    that there is a race condition for the update.
    :param arguments: The input arguments to the call
    '''
    log.debug("updating the context")
    context  = a[0]
    register = 3
    slave_id = 0x00
    address  = 1
    values   = context[slave_id].getValues(register, address, count=1)
    values   = [v + 1 for v in values]
    log.debug("new values: " + str(values))
    context[slave_id].setValues(register, address, values)


# def updating_writer(filename,context):
#     ''' A worker process that runs every so often and
#     updates live values of the context. It should be noted
#     that there is a race condition for the update.
#     :param arguments: The input arguments to the call
#     '''
#     #print("I'm in!")
#     log.debug("I'm IN!")
#     data = read_filedata(filename)
#     log.debug("updating the context")
#     #print("Updating the context!")
#     i = 0
#     for i in range(0,51):
#         context[0].setValues(1,i,data.getValues(1,i))
#         context[0].setValues(2,i,data.getValues(2,i))
#         context[0].setValues(3,i,data.getValues(3,i))
#         context[0].setValues(4,i,data.getValues(4,i))
#         #print("New values: "+ str(data.getValues(2,i)) + str(data.getValues(1,i))
#         # + str(data.getValues(3,i)) + str(data.getValues(4,i)))
#         log.debug("New values: "+ str(data.getValues(2,i)) + str(data.getValues(1,i))
#          + str(data.getValues(3,i)) + str(data.getValues(4,i)))

# def main():
#
#     InFilename = sys.argv[1]
#     OutFilename = sys.argv[2]
#     store = read_filedata(InFilename)
#     context = ModbusServerContext(slaves=store,single=True)
#     time = 5 # 5 seconds delay
# #    loopOut = LoopingCall(f=write_filedata,filename=())
#     loop = LoopingCall(f=updating_writer,a=(context,))
#     loop.start(time, now=False) # initially delay by time
#     print("Starting TCP Server")
#     StartTcpServer(context, identity=identity, address=("localhost", 5020))
def main():

    #InFilename = sys.argv[1]
    #OutFilename = sys.argv[2]
    #store = read_filedata(InFilename)
    store = ModbusSlaveContext(
        di = ModbusSequentialDataBlock(0, [17]*100),
        co = ModbusSequentialDataBlock(0, [17]*100),
        hr = ModbusSequentialDataBlock(0, [17]*100),
        ir = ModbusSequentialDataBlock(0, [17]*100))
    context = ModbusServerContext(slaves=store, single=True)
#    context = ModbusServerContext(slaves=store,single=True)
    #time = 5 # 5 seconds delay
    #    loopOut = LoopingCall(f=write_filedata,filename=())
    #loop = LoopingCall(f=updating_writer,a=(context,))
    #loop.start(time, now=False) # initially delay by time
#    StartTcpServer(context, identity=identity, address=("localhost", 5020))
    StartTcpServer(context, identity=identity, address=("localhost", 502))



    #updating_writer(InFilename,context)
#    write_filedata(OutFilename,context)



#    write_filedata(OutFilename,context)

    # address = int(sys.argv[3])
    # print("Register 1 [Coil]:")
    # print(context[0].getValues(1,address)[0])
    # print("Register 2 [Discrete Input]:")
    # print(context[0].getValues(2,address)[0])
    # print("Register 3 [Holding Register]:")
    # print(context[0].getValues(3,address)[0])
    # print("Register 4 [Input Registers]:")
    # print(context[0].getValues(4,address)[0])
    # ''' A worker process that runs every so often and
    # updates live values of the context. It should be noted
    # that there is a race condition for the update.
    # :param arguments: The input arguments to the call
    # '''

#    log.debug("updating the context")
#    context  = a[0]
#    register = 3
#    slave_id = 0x00
#    address  = 1
#    values   = context[slave_id].getValues(register, address, count=1)
#    values   = [v + 1 for v in values]
#    log.debug("new values: " + str(values))
#    context[slave_id].setValues(register, address, values)
# #   Register 1 = Coils,
#     for i in range(0,7):
#         context[0].setValues(1,i,[True])
#         context[0].setValues(2,i,[False])
#         context[0].setValues(3,i,[52-i])
#         context[0].setValues(4,i,[i])
# print("Getting from Store: ")
# print(store.getValues(2,1))

    #write_filedata(OutFilename,context)

    #---------------------------------------------------------------------------#
    # run the server you want
    #---------------------------------------------------------------------------#
    # Tcp:
    #StartTcpServer(context, identity=identity, address=("localhost", 502))
    #values = context[0].getValues(1,0x10,count=1)
    #values = [v+1 for v in values]
    #print(str(values))


if __name__ == "__main__":
    main()
