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

class RAM:
    """
    The RAM class contains the RAM registers, as well as any functions that interact with the RAM.    
    """

    regs = list()

    def __init__(self, ramfile: str, debug: bool = False):
        """
        Initializes the RAM with the input.txt file provided

        @param  ramfile : is the input.txt file provided in the command line to initialize the RAM with
        @param  debug   : is a optional parameter that when enabled automatically initializes the RAM without prompt

        @return the RAM object
        """


        initialRAM = list()
        
        with open(ramfile,'r') as file:                                                 # gets initial RAM information from file
            for line in file.readlines(): initialRAM.append(line.strip())

        for _ in range(256): self.regs.append("00")                                     # initialize registers to "00"

        if debug:                                                                       # debug sets all the memory with no prompt
            for i in range(256): self.regs[i] = initialRAM[i]

        else:                                                                           # otherwise, we prompt the user for what regs to initialize
            print("*** Welcome to the cache simulator ***\ninitialize the RAM:")
            userIn = input()

            start = int(userIn.split(" ")[1].replace("0x",""),16)
            end   = int(userIn.split(" ")[2].replace("0x",""),16)

            while start <= end:
                self.regs[start] = initialRAM[start]
                start += 1

            print("RAM successfully initialized!")
    
    def view(self):
        """
        Prints the contents of the RAM's registers to the terminal in the format:
        <Address in Hex> : < 8 Bytes in Hex>

        @param  This function doesn't have any parameters, only the reference to itself

        @return no return value
        """

        print("memory_size:256")
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
        """
        Dumps the RAM into a .txt file named 'ram.txt'

        @param  This function doesn't have any parameters, only the reference to itself

        @return no return value
        """

        with open("ram.txt","w") as file:
            for i in self.regs:
                file.write(str(i) + "\n")
        
        return

    def load_blocks(self, numBlocks: int, address: str):
        """
        Reads in a block from the RAM using the Cache's block size as a parameter

        @param  numBlocks : the block size of the cache
        @param  address   : the current address being read

        @return retBlocks : the specified number blocks found at the address in the RAM's regs
        """
        
        ramAdd    = int(address.replace("0x",""),16)
        startAdd  = (ramAdd // numBlocks) * numBlocks
        retBlocks = list()
        for i in range(startAdd, startAdd + numBlocks):
            retBlocks.append(self.regs[i])

        return retBlocks

    def write_block(self, numBlocks: int, offNum: int, address: str, hexByte: str):
        """
        Writes a specified byte to the RAM's registers at the address given

        @param  numBlocks : the cache's block size
        @param  offNum    : the cache's number of offset bits
        @param  address   : the specified address 
        @param  hexByte   : the byte that is being written to the regs

        @return retBlocks : the byte that was written to the regs
        """

        ramAdd    = int(address.replace("0x",""),16)
        startAdd  = (ramAdd // numBlocks) * numBlocks
        RAM.regs[startAdd + offNum] = hexByte

        return hexByte



class Cache:
    
    cacheSize   = 0         # C - Cache Size
    blockSize   = 0         # B - Block Size
    assoc       = 0         # E - Number of lines per set
    set         = 0         # S - Number of sets

    offset_bit  = 0         # b - number of offset bits
    tag_bit     = 0         # t - number of tag bits
    index_bit   = 0         # s - number of index bits

    repPolicy   = 0  
    hitPolicy   = 0
    misPolicy   = 0

    cachedSets  = list()    # cachedSets houses sets, that inturn houses SetLines, and SetLines contain the Blocks

    numHit      = 0       
    numMis      = 0

    startCache  = list()    # allows cache to be filled before eviction occurs 
                            # index of startCache is the set it's counting

    def __init__(self, debug = False):
        """
        Initializes the cache using the user's prompts

        @param  debug : optional parameter that allows the cache to be initialized without prompts

        @return the Cache Object
        """

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
                for i in range(int(self.assoc)):
                    newSet.append(SetLine())

                self.cachedSets.append(newSet)
            
            blocks = list()
            for _ in range(self.blockSize):
                blocks.append("00")
            
            for s in self.cachedSets:
                for l in s:
                    l.blocks = blocks

            for _ in range(self.set):
                self.startCache.append(0)

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

        for _ in range(self.set):               # create self.set number of sets
            
            newSet = list()
            for i in range(int(self.assoc)):    # create the associativity number of lines
                newSet.append(SetLine())

            self.cachedSets.append(newSet)      # add the set to the over all Cache structure (cachedSets)
            
        blocks = list()
        for _ in range(self.blockSize):         # create a list of empty bytes of the same size as block Size
            blocks.append("00")
            
        for s in self.cachedSets:               # set all lines to those blocks
            for l in s:
                l.blocks = blocks

        for _ in range(self.set):               # make sure all sets fill before evicting
            self.startCache.append(0)

        print("cache successfully configured!")
    
    def read(self, address: str, ram: RAM):
        """
        Attemps to read an address from the cache, if there is a miss, the replacement policy is used and the block is copied from the RAM.

        @param  address : the address trying to be read from the cache 
        @param  ram     : the RAM object we would read from if there is a read-miss

        @return there is no return value, but values are printed to the terminal
        """

        tagBits, indBits, offBits = self.addressBits(address)

        setNum = int(indBits,2)
        tagHex = bin_to_hex(tagBits)
        offNum = int(offBits,2)

        lineIndex = self.find_line(setNum, tagHex)

        print(f"set:{setNum}")
        print(f"tag:{tagHex}")

        if lineIndex == -1: 
            print("hit:no")
            vicNum = self.get_victum(setNum)
            print(f"eviction_line:{vicNum}")
            self.cachedSets[setNum][vicNum].blocks = ram.load_blocks(self.blockSize, address)
            self.cachedSets[setNum][vicNum].tagHex = tagHex
            self.cachedSets[setNum][vicNum].validBit  = 1
            print(f"ram_address:{address}")
            print(f"data:0x{self.cachedSets[setNum][vicNum].get_blocks()[offNum]}")

        else:               
            print("hit:yes")
            print("eviction_line:-1")
            print("ram_address:-1")
            print(f"data:0x{self.cachedSets[setNum][lineIndex].get_blocks()[offNum]}")

        return

    def write(self, address: str, hexByte: str, ram: RAM):
        """
        Attempts to write to an address in the cache. Follows hit-policy if there is a hit and the miss-policy if there is a miss.

        @param  address : the address trying to be written to from the cache 
        @param  hexByte : the byte being written to the cache/RAM
        @param  ram     : the RAM object we would read from if there is a write-miss

        @return there is no return value, but values are printed to the terminal
        """
        
        tagBits, indBits, offBits = self.addressBits(address)
        hexByte = hexByte.replace("0x","")

        setNum = int(indBits,2)
        tagHex = bin_to_hex(tagBits)

        lineIndex = self.find_line(setNum, tagHex)

        print(f"set:{setNum}")
        print(f"tag:{tagHex}")

        if lineIndex == -1: 
            print("write_hit: no")
            vicNum = self.get_victum(setNum)
            print(f"eviction_line:{vicNum}")
            print(f"ram_address:{address}")
            print(f"data:0x{self.miss_data(address, vicNum, hexByte, ram)}")
            print(f"dirty_bit:{self.cachedSets[setNum][vicNum].dirtyBit}")

        else:               
            print("write_hit: yes")
            print("eviction_line:-1")
            print(f"ram_address:-1")
            print(f"data:0x{self.hit_data(address, lineIndex, hexByte, ram)}")
            print(f"dirty_bit:{self.cachedSets[setNum][lineIndex].dirtyBit}")

        return


    def flush(self):
        """
        Clears the cache, resetting all the valid-bits, dirty-bits, tag-bytes, and blocks to 00

        @param  there are no parameters except the reference to itself

        @return no return value, only "cache_cleared" printed to terminal
        """

        print("cache_cleared")        
        self.startCache = 0
        blocks = list()
        for _ in range(self.blockSize):
            blocks.append("00")
        
        for s in self.cachedSets:
            for l in s:
                l.blocks   = blocks
                l.validBit = 0
                l.dirtyBit = 0
                l.tagHex   = "00"

    def view(self):
        """
        Prints the contents of the all cache lines to the terminal

        @param  there are no parameters except the reference to itself

        @return no return value, only content printed to the terminal
        """
        
        if   self.repPolicy == 1:   repPolicy = "random_replacement"
        elif self.repPolicy == 2:   repPolicy = "least_recently_used"
        else:                       repPolicy = "least_freqently_used"
            
        if self.hitPolicy == 1:     hitPolicy = "write_through"
        else:                       hitPolicy = "write_back"
            
        if self.misPolicy == 1:     misPolicy = "write_allocate"
        else:                       misPolicy = "no_write_allocate"

        print(f"cache_size:{self.cacheSize}")
        print(f"data_block_size:{self.blockSize}")
        print(f"associativity:{self.assoc}")
        print(f"replacement_policy:{repPolicy}")
        print(f"write_hit_policy:{hitPolicy}")
        print(f"write_miss_policy:{misPolicy}")
        print(f"number_of_cache_hits:{self.numHit}")
        print(f"number_of_cache_misses:{self.numMis}")
        print("cache_content:")

        for s in self.cachedSets:
            for line in s:
                content = ""
                content += str(line.validBit) + " "
                content += str(line.dirtyBit) + " "
                content += line.tagHex + " "
                for i in line.blocks: content += i + " "
                print(content)

        return

    def dump(self):
        """
        Prints the contents of the all cache lines to a .txt file named cache.txt

        @param  there are no parameters except the reference to itself

        @return no return value, only the file created
        """

        with open("cache.txt","w") as file:
            for s in self.cachedSets:
                for l in s:
                    for b in l.blocks:
                        file.write(b + " ")
                    file.write("\n")

        return

    def find_line(self, setNum: int, tagHex: str):
        """
        Searchs the current set for a specific tag value and returns the index if found.
        If not found, -1 is returned

        @param  setNum   : set index we are looking at in the cache
        @param  tagHex   : tag in hex we are looking for in the cache

        @return vaule -1 : tagHex not found in set
        @return value n  : tagHex found at line n in the set
        """

        currSet   = self.cachedSets[setNum]
        lineIndex = -1
        
        for i in range(len(currSet)):
            if currSet[i].validBit == 1 and currSet[i].tagHex == tagHex:
                
                print(currSet[i].tagHex)
                print(currSet[i].blocks)

                lineIndex = i
                break

        if    lineIndex != -1 : self.numHit += 1
        else:                   self.numMis += 1
        
        return lineIndex

    def addressBits(self, hexAdd: str):
        """
        Takes the address we are looking for in hex and breaks it into it's tag, index, and offset bits

        @param  hexAdd   : Hex address being broken down 

        @return tagBits  : tag bits of the address using cache.properties
        @return indBits  : index bits of the address using cache.properties
        @return offBits  : offset bits of the address using cache.properties
        """

        binary  = hex_to_bin(hexAdd)

        tagBits = binary[:self.tag_bit]
        indBits = binary[self.tag_bit : self.index_bit + self.tag_bit]
        offBits = binary[-self.offset_bit:]

        if indBits == "": indBits = "0"
        return tagBits, indBits, offBits
    
    def get_victum(self, setNum: int):
        """
        Looks through a set and decides what line is next to be evicted based on the replacement policy chosen.

        @param  setNum   : current set being processed

        @return index of the line to be evicted
        """
        
        if self.repPolicy == 1:
            if self.startCache[setNum] <= self.assoc-1:
                temp = self.startCache[setNum]
                self.startCache[setNum] += 1
                return temp
            else:
                return randint(0,self.assoc - 1)

        else:
            if self.startCache[setNum] <= self.assoc-1:
                temp = self.startCache[setNum]
                self.startCache[setNum] += 1
                return temp
            else:
                currSet     = self.cachedSets[setNum]
                leastRecent = currSet[0]
                for i in currSet:
                    if leastRecent.lastAccess > i.lastAccess: leastRecent = i
                return currSet.index(leastRecent)

    def hit_data(self, address: str, lineIndex:str, hexByte: str, ram: RAM):
        """
        Acts on write-hits, depending on the hit-policy.

        @param  address   : address being written to
        @param  lineIndex : the line number that was hit
        @param  hexByte   : the byte being written
        @param  ram       : ram being written to

        @return the byte that was written
        """

        tagBits, indBits, offBits = self.addressBits(address)

        setNum = int(indBits,2)
        offNum = int(offBits,2)

        if self.hitPolicy == 1:

            self.cachedSets[setNum][lineIndex].blocks[offNum] = hexByte
            ram.write_block(self.blockSize, offNum, address, hexByte)
            
            return hexByte
        
        else:

            self.cachedSets[setNum][lineIndex].dirtyBit  = 1
            self.cachedSets[setNum][lineIndex].get_blocks()[offNum] = hexByte

            return hexByte


    def miss_data(self, address: str, vicNum: int, hexByte: str, ram: RAM):
        """
        Acts on write-misses, depending on what the miss-policy is

        @param  address   : address being written to
        @param  vicNum    : the line number that is being evicted
        @param  hexByte   : the byte being written
        @param  ram       : ram being written to

        @return the byte that was written
        """

        tagBits, indBits, offBits = self.addressBits(address)

        setNum = int(indBits,2)
        tagHex = bin_to_hex(tagBits)
        offNum = int(offBits,2)

        if self.misPolicy == 1:

            self.cachedSets[setNum][vicNum].blocks               = ram.load_blocks(self.blockSize, address)
            self.cachedSets[setNum][vicNum].tagHex               = tagHex
            self.cachedSets[setNum][vicNum].validBit             = 1
            self.cachedSets[setNum][vicNum].dirtyBit             = 1
            self.cachedSets[setNum][vicNum].get_blocks()[offNum] = hexByte
            return hexByte
        
        else:

            return ram.write_block(self.blockSize, address, hexByte)

            

class SetLine:
    validBit  = 0
    dirtyBit  = 0
    tagHex   = "00"

    NumofAccess = 0
    lastAccess  = 0

    blocks = list()

    def __init__(self):
        """
        Initializes the SetLine

        @param  no parameters other than the reference to itself

        @return empty SetLine object
        """

        self.validBit    = 0
        self.dirtyBit    = 0
        self.tagHex      = "00"
        self.NumofAccess = 0
        self.lastAccess  = 0

    def get_blocks(self):
        """
        Grabs the blocks of the SetLine

        @param   no parameters other than the reference to itself

        @returns the blocks of the SetLine
        """    

        self.NumofAccess += 1
        self.lastAccess   = time()
        return self.blocks
    
    def get_block(self, index: int):
        """
        Grabs the content of one block

        @param index : the index of the block we are grabing

        @returns the content of the specific block
        """   

        return self.blocks[index]

def valid_input(instr: str, min: int, max: int, notAllow = None) -> int:
    """
    Checks to see if cache configuration inputs are valid according to restraints

    @param  instr       : the input instruction
    @param  min         : minimum allowed number in input
    @param  max         : maximum allowed number in input
    @param  notAllow    : number that is not allowed in input

    @return userIn      : returns the users input integer
    """

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
    """
    Function to convert hexadecimal string to binary string

    @param  hexAdd      : Hex address being converted

    @return binNum      : converted binary number without 0b and with zero padding
    """

    binNum = bin(int(hexAdd, 16))
    binNum = binNum.replace("0b", "")
    return binNum.zfill(8)

def bin_to_hex(binAdd: str) -> str:
    """
    Function to convert binary string to hexadecimal string

    @param  binAdd      : Hex address being converted

    @return hexNum      : converted hexadecimal number without 0x and with zero padding
    """

    binNum = int(binAdd, 2)
    hexNum = hex(binNum).replace("0x","")
    return hexNum.zfill(2)

def simulate(r: RAM, c: Cache):
    """
    Function driving the simulation of the cache. Allows the user to input commands, addresses, and bytes to modify the cache.

    @param  r      : the RAM that would be manipulated
    @param  c      : the Cache that would be manipulated


    @return None, the output of each of the previous functions/methods would be output to the terminal
    """

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
        command  = userIn.split(" ")[0]
        address  = userIn.split(" ")[1]
    elif inputLen == 3:
        command  = userIn.split(" ")[0]
        address  = userIn.split(" ")[1]
        hexByte  = userIn.split(" ")[2]

    while True:

        if   command == "cache-read":
            c.read(address, r)
        elif command == "cache-write":
            c.write(address, hexByte, r)
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
            command  = userIn
        elif inputLen == 2:
            command  = userIn.split(" ")[0]
            address  = userIn.split(" ")[1]
        elif inputLen == 3:
            command  = userIn.split(" ")[0]
            address  = userIn.split(" ")[1]
            hexByte  = userIn.split(" ")[2]

def main():
    """
    Main driver of the program
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("RAMfile", help = "txt file to hold intial RAM entries.", type = str)
    RAMfile = parser.parse_args().RAMfile

    ram   = RAM(RAMfile)
    cache = Cache()

    simulate(ram, cache)

def debug():
    """
    Used to debug program
    """
    
    parser = argparse.ArgumentParser()
    parser.add_argument("RAMfile", help = "txt file to hold intial RAM entries.", type = str)
    RAMfile = parser.parse_args().RAMfile

    ram   = RAM(RAMfile, debug = True)
    cache = Cache(debug = True)

    cache.write("0x10", "0xAB",ram)
    print()
    cache.write("0x20", "0xBC", ram)
    print()
    cache.view()

if __name__ == '__main__':
    main()