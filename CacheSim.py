# File          : CSCE-312 Project
# Author(s)     : Santana Gonzales, Aum Patel
# Date          : 12/01/2021
# Section       : 507
# E-mail(s)     : santanag1223@tamu.edu, aum_patel@tamu.edu 
# Description   : CACHE SIMULATOR

from math import log
from time import time
from random import randint
import argparse

#### Classes

class RAM:

    regs = list()

    def __init__(self, ramfile: str, debug = False):
        
        initialRAM = list()
        
        with open(ramfile,'r') as file:                                                 # gets initial RAM information from file
            for line in file.readlines(): initialRAM.append(line.strip())

        for _ in range(256): self.regs.append("00")                                     # initialize registers to "00"

        if debug:                                                                       # debug sets all the memory with no prompt
            for i in range(256): self.regs[i] = initialRAM[i]

        else:                                                                           # otherwise, we prompt the user for what regs to initialize
            print("*** Welcome to the cache simulator ***\ninitialize the RAM:")
            userIn = input("init-ram ")

            start = int(userIn.split(" ")[0].replace("0x",""),16)
            end   = int(userIn.split(" ")[1].replace("0x",""),16)

            while start <= end:
                self.regs[start] = initialRAM[start]
                start += 1

            print("RAM successfully initialized!\n")
    
    def view(self):
        print("memory_size: 256")
        print("memory_content:")
        i    = 0
        line = "0x00:"
        while i < 256:
            line += str(self.regs[i]) + " "
            i    += 1
        
            if i % 8 == 0:
                print(line)
                if i == 8:    
                    line = "0x08:"
                else:
                    line = hex(i) + ":"

        return

    def dump(self):
        with open("ram.txt","w") as file:
            for i in self.regs:
                file.write(str(i) + "\n")
        
        return

    def load_blocks(self, numBlocks: int, address: str):
        
        ramAdd  = int(address.replace("0x",""),16)

        startAdd = (ramAdd//numBlocks) * numBlocks

        retBlocks = list()
        for i in range(startAdd, startAdd + numBlocks + 1):
            retBlocks.append(self.regs[i])



class Cache:
    cacheSize   = 0         # C
    blockSize   = 0         # B
    assoc       = 0         # E
    set         = 0         # S

    offset_bit  = 0         # b
    tag_bit     = 0         # t
    index_bit   = 0         # s

    repPolicy   = 0
    hitPolicy   = 0
    misPolicy   = 0

    cachedSets  = list()

    numHit      = 0
    numMis      = 0

    def __init__(self, debug = False):

        if debug:
            self.cacheSize = 32
            self.blockSize = 8
            self.assoc     = 4
            self.repPolicy = 1
            self.hitPolicy = 1
            self.misPolicy = 1

            self.set        = int(self.cacheSize / (self.blockSize * self.assoc))
            self.offset_bit = int(log(self.blockSize, 2))
            self.index_bit  = int(log(self.set, 2))
            self.tag_bit    = 8 - (self.offset_bit + self.index_bit)
            
            for _ in range(self.set):
            
                newSet = list()
                for i in range(self.assoc):
                    line = SetLine(self.blockSize)
                    newSet.append(line)

                self.cachedSets.append(newSet)

            return

        print("configure the cache:")
        self.cacheSize = valid_input("cache size: "        , 8, 256)
        self.blockSize = valid_input("data block size: "   , 1, 256)
        self.assoc     = valid_input("associativity: "     , 1, 4, notAllow = 3)
        self.repPolicy = valid_input("replacement policy: ", 1, 2)
        self.hitPolicy = valid_input("write hit policy: "  , 1, 2)
        self.misPolicy = valid_input("write miss policy: " , 1, 2)
        
        self.set        = int(self.cacheSize / (self.blockSize * self.assoc))
        self.offset_bit = int(log(self.blockSize, 2))
        self.index_bit  = int(log(self.set, 2))
        self.tag_bit    = 8 - (self.offset_bit + self.index_bit)

        for _ in range(self.set):
            
            newSet = list()
            for i in range(self.assoc):
                line = SetLine(self.blockSize)
                newSet.append(line)
            
            self.cachedSets.append(newSet)

        print("cache successfully configured!\n")
    
    def read(self, address: str, ram: RAM):
        tagBits, indBits, offBits = self.addressBits(address)

        setNum = int(indBits,2)
        tagHex = bin_to_hex(tagBits)
        offNum = int(offBits,2)
        
        lineIndex = self.find_line(setNum, tagHex)

        print("set:", setNum)
        print("tag:", tagHex)

        if lineIndex == -1: 
            print("hit: no")
            vicNum = self.get_victum(setNum)
            print("eviction_line:", vicNum)
            self.cachedSets[setNum][vicNum].blocks = RAM.load_blocks(RAM, self.blockSize, address)
            print("ram_address:", address)
            print("data:", self.cachedSets[setNum][vicNum].blocks[offNum])

        else:               
            print("hit: yes")
            print("eviction_line: -1")
            print("ram_address: -1")
            print("data:", self.cachedSets[setNum][lineIndex].blocks[offNum])

        return

    def write(self, address1: str, address2: str, ram: RAM):
        
        return

    def flush(self, address: str, ram: RAM):
        # do somethings
        return

    def view(self):
        
        if self.repPolicy == 1:     repPolicy = "random_replacement"
        elif self.repPolicy == 2:   repPolicy = "least_recently_used"
        else:                       repPolicy = "least_freqently_used"
            
        if self.hitPolicy == 1: hitPolicy = "write_through"
        else:                   hitPolicy = "write_back"
            
        if self.misPolicy == 1: misPolicy = "write_allocate"
        else:                   misPolicy = "no_write_allocate"

        print("cache_size:",                self.cacheSize)
        print("data_block_size:",           self.blockSize)
        print("associativity:",             self.assoc)
        print("replacement_policy:",        repPolicy)
        print("write_hit_policy:",          hitPolicy)
        print("write_miss_policy:",         misPolicy)
        print("number_of_cache_hits:",      self.numHit)
        print("number_of_cache_misses:",    self.numMis)

        return

    def dump(self, address: str, ram: RAM):
        # do something
        return

    def find_line(self, setNum: int, tagHex: str):
        """
        setNum : set index we are looking at in the cache\n
        tagHex : tag in hex we are looking for in the cache\n
        \n
        return vaule -1 : tagHex not found in set
        return value n  : tagHex found at line n in the set 
        """

        currSet   = self.cachedSets[setNum]
        lineIndex = -1
        
        for line in currSet:
            if line.vaild == 1 and line.tag == tagHex:
                lineIndex = currSet.index(line)
                break

        if lineIndex != -1 : self.numHit += 1
        else:                self.numMis += 1
        
        return lineIndex

    def addressBits(self, hexAdd:str):
        binary  = hex_to_bin(hexAdd)

        tagBits = binary[:self.tag_bit]
        indBits = binary[self.tag_bit : self.index_bit + self.tag_bit]
        offBits = binary[-self.offset_bit:]

        if indBits == "": indBits = "0"

        return tagBits, indBits, offBits
    
    def get_victum(self, setNum: int):
        
        if self.repPolicy == 1: return randint(0,self.assoc - 1)
        else:
            currSet = self.cachedSets[setNum]
            leastRecent = currSet[0]
            for i in currSet:
                if leastRecent.lastAccess > i.lastAccess: leastRecent = i

            return currSet.index(leastRecent)
            

class SetLine:
    vaild  = 0
    dirty  = 0
    tag    = "00"
    
    NumofAccess = 0
    LastAccess  = 0

    blocks = list()

    def __init__(self, blockNum):
        for i in range(blockNum):
            self.blocks.append("00")

    def get_blocks(self):
        self.NumofAccess += 1
        self.LastAccess = time()
        return self.blocks
    
    def get_block(self, index: int):
        return self.blocks[index]

#### Helper Functions

def valid_input(instr: str, min: int, max: int, notAllow = None) -> int:
    
    try:               userIn = int(input(instr))
    except Exception:  userIn = 0

    while userIn < min or userIn > max or userIn == notAllow:
        if notAllow == None:
            print(f"[ERROR] - Invaild value. Enter value between {min} and {max}.")
        else:
            print(f"[ERROR] - Invaild value. Enter value between {min} and {max}, not including {notAllow}.")
        
        try:               userIn = int(input(instr))
        except Exception:  userIn = 0
    
    return userIn

def hex_to_bin(hexAdd: str) -> str:
    binNum = bin(int(hexAdd, 16))
    binNum = binNum.replace("0b", "")
    return binNum.zfill(8)

def bin_to_hex(binAdd: str) -> str:
    binNum = int(binAdd, 2)
    hexNum = hex(binNum).replace("0x","")
    return hexNum.zfill(2)

def simulate(r: RAM, c: Cache):
    print("*** Cache simulator menu ***")
    print("type one command:")
    print("1. cache-read")
    print("2. cache-write")
    print("3. cache-flush")
    print("4. cache-view")
    print("5. memory-view")
    print("6. cache-dump")
    print("7. memory-dump")
    print("8. quit")
    print("****************************")

    userIn  = input().replace("0b","")

    if userIn == "quit": return

    inputLen = len(userIn.split(" "))

    if   inputLen == 1:
        command = userIn
    elif inputLen == 2:
        command = userIn.split(" ")[0]
        address1 = int(userIn.split(" ")[1].replace("0x",""),16)
    elif inputLen == 3:
        command = userIn.split(" ")[0]
        address1 = int(userIn.split(" ")[1].replace("0x",""),16)
        address2 = int(userIn.split(" ")[2].replace("0x",""),16)

    while True:

        if   command == "cache-read":
            c.read(address1, r)
        elif command == "cache-write":
            c.write(address1,address2,r)
        elif command == "cache-flush":
            c.flush()
        elif command == "cache-view":
            c.view()
        elif command == "memory-view":
            r.view()
        elif command == "cache-dump":
            c.dump()
        elif command == "memory-dump":
            r.dump()
        else:
            print("invalid command, try again.")

        print("*** Cache simulator menu ***")
        print("type one command:")
        print("1. cache-read")
        print("2. cache-write")
        print("3. cache-flush")
        print("4. cache-view")
        print("5. memory-view")
        print("6. cache-dump")
        print("7. memory-dump")
        print("8. quit")
        print("****************************")
        
        userIn  = input()

        if userIn == "quit": return

        inputLen = len(userIn.split(" "))

        if   inputLen == 1:
            command = userIn
        elif inputLen == 2:
            command = userIn.split(" ")[0]
            address1 = int(userIn.split(" ")[1].replace("0x",""),16)
        elif inputLen == 3:
            command = userIn.split(" ")[0]
            address1 = int(userIn.split(" ")[1].replace("0x",""),16)
            address2 = int(userIn.split(" ")[2].replace("0x",""),16)

#### main and debug functions

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("RAMfile", help = "txt file to hold intial RAM entries.", type = str)
    RAMfile = parser.parse_args().RAMfile

    ram   = RAM(RAMfile)
    cache = Cache()

    simulate(ram, cache)

def debug():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("RAMfile", help = "txt file to hold intial RAM entries.", type = str)
    RAMfile = parser.parse_args().RAMfile

    ram   = RAM(RAMfile, debug = True)
    cache = Cache(debug = True)

    cache.read("0x18", ram)
    

#### Call to main or debug

if __name__ == '__main__':
    #main()
    debug()
