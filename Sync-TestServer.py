'''
Test server that reads data from a csv file and imports it into correct
registers. The format of the input file should be
Address, Discrete Inputs, Coils, Holding Registers, Input/Output Registers

This server can then be queried by a pymodbus client.

In the end the Pymodbus client writes back to a textfile
Usage:
$python3 Sync-TestServer.py "filename.txt"
'''
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
import csv
import sys

def read_filedata(filename):
#   Create empty dictionaries used for the input from CSV file
    di = {}
    co = {}
    hr = {}
    ir = {}
    with open(filename, newline='') as csvfile:
        data = csv.reader(csvfile,delimiter=',')
        print("Before: ")
        for row in data:
            # Read data into dictionaries, row[0] is address and rest is
            # di = Discrete input, ci = Coils, hr = Holding Registers
            # ir = Input Registrs
            # Addresses should be 1 or higher
            print([row[0],row[1],row[2],row[3],row[4]])
            di[int(row[0])] = bool(row[1] in ['True','TRUE'])
            co[int(row[0])] = bool(row[2] in ['True','TRUE'])
            hr[int(row[0])] = int(row[3])
            ir[int(row[0])] = int(row[4])
    return ModbusSlaveContext(
        di = ModbusSparseDataBlock(di),
        co = ModbusSparseDataBlock(co),
        hr = ModbusSparseDataBlock(hr),
        ir = ModbusSparseDataBlock(ir))

def write_filedata(filename,data):
#   Write to CSV file
    with open(filename,'w',newline='') as csvfile:
        w = csv.writer(csvfile,delimiter=',')
        i = 0
        while(data.validate(1,i) == True):
            # Get values, (function code, Address, Count=1)
            # FC 4 = Read Input Register
            # FC 3 = Read holding register
            # FC 2 = Read Discrete Input (Boolean values)
            # FC 1 = Read Coil (Boolean values)
            line = [i,data.getValues(2,i)[0],data.getValues(1,i)[0],data.getValues(3,4-i)[0],
            data.getValues(4,4-i)[0]]
            print(line)
            w.writerow(line)
            i = i+1


        # print("Writing: ")
        # for i in di:
        #     line = [i,di[4-i],ci[4-i],hr[4-i],ir[4-i]]
        #     print(line)


def main():

    filename = sys.argv[1]
    store = read_filedata(filename)
    context = ModbusServerContext(slaves=store,single=True)
    write_filedata(filename,store)
#    print(store.getValues(int(sys.argv[2]),int(sys.argv[3])))
#    print(store.getValues(int(sys.argv[2]),int(sys.argv[3])))


#   Write to CSV file
    # with open(filename,'w',newline='') as csvfile:
    #     testwriter = csv.writer(csvfile,delimiter=',')
    #     print("Writing: ")
    #     for i in di:
    #         line = [i,di[4-i],ci[4-i],hr[4-i],ir[4-i]]
    #         print(line)
    #         testwriter.writerow(line)





if __name__ == "__main__":
    main()
