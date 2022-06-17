from configparser import ConfigParser 
import random
import serial

import database_functions as dbfunc

CFILE = "config.ini"

config = ConfigParser()

def read_config():
    global config
    config.read(CFILE)
    
def write_config():
    global config
    with open(CFILE, 'w') as f:
        config.write(f)

read_config()

# PROME NUMBERS LIST EDIT

def init_prome():
    read_config()
    prome_numbers = []
    for i in range (1, int(config.get("main", "prome_count"))+1):
        dev = "P{}".format(i)
        numbers = [0 for _ in range (int(config.get(dev, 'displays')))]
        prome_numbers.append(numbers)
    return prome_numbers

def update_prome_list(list):
    read_config()
    count = int(config.get("main", "prome_count"))
    l_temp = len(list) 
    if l_temp > count:
        for _ in range(l_temp-count):
            list.pop(-1)
    elif l_temp < count:
        for i in range(l_temp, count):
            dev = "P{}".format(i+1)
            templist = []
            for _ in range(0, int(config.get(dev, "displays"))):
                templist.append(0)
            list.append(templist)
    return list

def update_prome_conf(list, index):
    read_config()
    if index == -1:
        for i in range(0,int(config.get("main", "prome_count"))):
            try:
                l_temp = len(list[i])
                dev = "P{}".format(i+1)
                c_temp = int(config.get(dev, "displays"))
                if c_temp > l_temp:
                    for _ in range(c_temp-l_temp):
                        list[i].append(0)
                elif c_temp < l_temp:
                    for _ in range(l_temp-c_temp):
                        list[i].pop(-1)
            except:
                list.append([])
                for _ in range(config.get('P1', 'displays')):
                    list[-1].append(0)
        return list
    
    else:        
        dev = "P{}".format(index)
        c_temp = int(config.get(dev, "displays"))
        l_temp = len(list[index-1])
        if c_temp > l_temp:
            for _ in range(c_temp-l_temp):
                list[index-1].append(0)
        elif c_temp < l_temp:
            for _ in range(l_temp-c_temp):
                list[index-1].pop(-1)
        return list

def update_prome_val(list, val, index, prome_id):
    append_list = list[prome_id - 1]
    append_list[index-1] = val
    list[prome_id - 1] = append_list
    return list

def update_prome_draw(list, vals):
    read_config()
    output = {'output_list':[], 'left_vals':[]}
    indexes = [0]
    prome_all_displays = int(config.get('P1', 'displays'))
    for i in range(1, int(config.get('main', 'prome_count'))):
        dev = 'P{}'.format(i+1)
        indexes.append(int(config.get(dev, 'displays')) + indexes[i-1])
        prome_all_displays += int(config.get(dev, 'displays'))
    if len(vals) <= prome_all_displays:
        l = len(vals)
        for i in range(l, prome_all_displays):
            for j in range(0, len(indexes)):
                if i-indexes[j] < 0:
                    list[j-1][i-indexes[j]] = 0
                    break
            else:
                list[j][i-indexes[j]] = 0
        
    elif len(vals) > prome_all_displays:
        l = prome_all_displays
    index_num = 0
    for _ in range(l):
        rand_index = random.randint(0, len(vals)-1)
        rand_val = vals[rand_index]
        vals.pop(rand_index)
        if rand_val in range(0, 99):
            for j in range(0, len(indexes)):
                if index_num-indexes[j] < 0:
                    list[j-1][index_num-indexes[j]] = rand_val
                    break
            else:
                list[j][index_num-indexes[j]] = rand_val
            index_num += 1
    output['output_list'] = list
    output['left_vals'] = vals
    return output
    
    
def prome_list_index_values(list, index):
    templist = []
    for i in range(0, len(list[index-1])):
        tempvar = []
        tempvar.append(i+1)
        tempvar2 = list[index-1][i]
        tempvar.append(tempvar2)
        templist.append(tempvar)
    return templist

def prome_list_table(list):
    templist = []
    for i in range(0, len(list)):
        tempvar = []
        tempvar.append(i+1)
        tempvar2 = list[i]
        tempvar.append(tempvar2)
        templist.append(tempvar)
    return templist

# DATABASE

def db_validate(path=None):
    if path:
        if dbfunc.validate(path) == 1:
            return("*Brak*")
        else: return(path)
    else:
        return("*Brak*")

# HARDWARE
    
def com_ports(): return(["COM{}".format(i) for i in range(1,100)])

def displays(): return([i for i in range(1,100)])

def data_bits(): return([6,7,8])

def parity(): return(["None", "Odd", "Even", "Mark", "Space"])

def serial_speeds(): return([75, 110, 300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200])

def stop_bits(): return ([1,2])

def get_prome_index(num): return([i for i in range(1, int(num)+1)])

# MAIN

def init_promelist(count):
    read_config()
    values = []
    for i in range(1, int(count)+1):
        var = "P{}".format(i)
        values.append([i, [0 for _ in range(0, int(config.get(var, "displays")))]])
    return values

def update_promelist_length(list):
    read_config()
    count = len(list)
    temp = int(config.get("main", "prome_count"))
    if temp > count:
        for i in range(count+1, temp+1):
            var = "P{}".format(i)
            list.append([i, [0 for _ in range(0, int(config.get(var, "displays")))]])
    elif temp < count:
        for _ in range(temp, count):
            list.pop(temp)
    return list

# SENDING AND SERIAL

def serial_check(dev):
    read_config()
    port = config.get(dev, 'port')
    baudrate = int(config.get(dev, 'baudrate')) 
    bytesize = int(config.get(dev, 'bytesize'))
    stopbits = int(config.get(dev, 'stopbits'))
    try:
        serialPort = serial.Serial(port=port, baudrate=baudrate, bytesize=bytesize, timeout=1, stopbits=stopbits)
        serialPort.write('-1'.encode())
        serialPort.close()
        return 0
    except:
        return 1
    
def serial_send(dev, vals):
    read_config()
    port = config.get(dev, 'port')
    baudrate = int(config.get(dev, 'baudrate')) 
    bytesize = int(config.get(dev, 'bytesize'))
    stopbits = int(config.get(dev, 'stopbits'))
    send_string = ''
    
    for i in range(len(vals)):
        send_string += str(vals[i])
        send_string += ";"
    send_string = send_string[:-1]
    
    try:
        serialPort = serial.Serial(port=port, baudrate=baudrate, bytesize=bytesize, timeout=1, stopbits=stopbits)
        serialPort.write(send_string.encode())
        serialPort.close()
        return 0
    except:
        return 1