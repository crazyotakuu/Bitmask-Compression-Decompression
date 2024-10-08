#I have neither given nor received any unauthorized aid on this assignment
import sys
from collections import Counter

rle_counter=0
rle_compression_flag=False
rle_overlflow_flag=False
rle_compression_output=""

def compress(binaries, frequency_dict):
    global rle_counter, rle_compression_flag, rle_compression_output
    compressed_outputs = []

    # print("Starting compression process...")  

    for index, binary in enumerate(binaries):
        # print(f"Processing binary at index {index}: {binary}")  
        if rle_compression_flag:
            # print(f"RLE flag is set. RLE counter before decrement: {rle_counter}")  
            rle_counter -= 1
            if rle_counter == 0:
                # print("RLE counter reached 0, appending RLE output and resetting flags.")  
                # compressed_outputs.append(rle_compression_output)
                # print("rle_compression_output is "+rle_compression_output)  
                # rle_compression_output = ""
                rle_compression_flag = False
            else:
                # print("RLE sequence ongoing, skipping current binary.")  
                pass
        else:
            # print("Applying compression methods...")  
            compression_methods = [
                lambda: compress_original(binary, frequency_dict, index),
                lambda: compress_rle(binary, frequency_dict, index, binaries),
                lambda: compress_bitmask(binary, frequency_dict, index),
                lambda: compress_1bit_mismatch(binary, frequency_dict, index),
                lambda: compress_2bit_consecutive(binary, frequency_dict, index),
                lambda: compress_4bit_consecutive(binary, frequency_dict, index),
                lambda: compress_2bit_anywhere(binary, frequency_dict, index),
                lambda: compress_direct_matching(binary, frequency_dict, index)
            ]

            best_compression = compression_methods[0]()
            best_length = len(best_compression) if best_compression else float('inf')
            # print(f"Initial best compression method result: {best_compression}, length: {best_length}")  

            for method in compression_methods[1:]:
                current_compression = method()
                current_length = len(current_compression) if current_compression else float('inf')
                # print(f"Current compression method result: {current_compression}, length: {current_length}")  

                if current_length < best_length:
                    best_compression = current_compression
                    best_length = current_length
                    # print(f"Found better compression: {best_compression}")  

            compressed_outputs.append(best_compression)
            # print(f"Appending best compression: {best_compression}")  

    # print("Writing compressed outputs to file...")  
    with open('cout.txt', 'w') as file:
        compressed_stream = ''.join(compressed_outputs)
        
        for i in range(0, len(compressed_stream), 32):
            line = compressed_stream[i:i+32]
            padded_line = line.ljust(32, '0')
            file.write(padded_line+ '\n')
            # print(f"Writing line: {padded_line}")  
        
        file.write("xxxx\n")
        # print("Writing separation marker...")  

        for binary in frequency_dict.keys():
            file.write(binary + '\n')
            # print(f"Writing dictionary entry: {binary}")  

    # print("Compression process completed.")  



def compress_rle(binary, frequency_dict, index, binaries):
    global rle_counter, rle_compression_flag, rle_compression_output,rle_overlflow_flag
    # print(f"Processing: Index={index}, Binary={binary}")  

    if index > 0 and binaries[index] == binaries[index - 1] and not rle_overlflow_flag:
        # print(f"Current binary: {binaries[index]} and previous binary {binaries[index-1]}")  
        for next_index in range(index + 1, len(binaries)):
            if binaries[next_index] == binary:
                rle_counter += 1
                rle_compression_flag = True
                # print/(f"Incrementing RLE counter: {rle_counter}. Next Index: {next_index}")  
                
                if rle_counter == 7 or next_index == len(binaries) - 1:
                    # print(f"Stopping condition met. RLE counter: {rle_counter}, Next Index: {next_index}")  
                    if rle_counter==7:
                        rle_overlflow_flag=True
                    break
            else:
                # print(f"Different binary encountered or end of list. Stopping. Next Index: {next_index}")  
                break
        
        if rle_counter == 0:
            # print("Only a single repetition detected. Returning RLE for 1 repetition.")  
            return "001" + format(0, '03b')
        else:
            # print(rle_counter)
            # print("001" + format(rle_counter, '03b'))
            return "001" + format(rle_counter, '03b')
            # for i in range(1,rle_counter):
            #     rle_compression_output += "001" + format(i+1, '03b')
            #     # print(f"Appending RLE: {rle_compression_output[-1]}")  
            # # print("OUTPUT IS "+rle_compression_output)
            # # print("Returning RLE for the first of multiple repetitions.")  
            # return "001" + format(1, '03b')
    else:
        # print("No match with previous binary or is the first binary. Skipping RLE.")  
        rle_overlflow_flag=False
        return None


def compress_original(binary, frequency_dict, index):
    compressed_binary = "000" + binary
    return compressed_binary

def create_bitmask(binary, dict_binary):
    # Perform XOR operation to create the bitmask
    bitmask = ''.join('1' if bit1 != bit2 else '0' for bit1, bit2 in zip(binary, dict_binary))
    return bitmask

def compress_bitmask(binary, frequency_dict, index):
    valid_bitmasks = {'1000', '1001', '1010', '1011', '1100', '1101', '1110', '1111'}
    
    # print("Starting compression...")  # Debug
    for dict_index, dict_binary in enumerate(frequency_dict.keys()):
        # Create a bitmask for the current dictionary entry
        # print(f"The binary is {binary}, dict entry is: {dict_binary}")
        bitmask = create_bitmask(binary, dict_binary)
        # print(f"Checking dictionary entry {dict_index} with bitmask: {bitmask}")  # Debug
        
        # Optimize by checking the number of '1's in the bitmask
        if bitmask.count('1') > 4:
            # print("More than four '1's in the bitmask, skipping to the next dictionary entry.")  # Debug
            continue
        
        # Search for the first '1' in the bitmask
        for i in range(0, 29):  # Limit to 29 to ensure we have a 4-bit window
            if bitmask[i] == '1' and bitmask[i:i+4] in valid_bitmasks:
                # print(f"Found valid bitmask {bitmask[i:i+4]} at position {i}")  # Debug
                
                # Check if the rest of the bits, excluding the 4-bit window, are all '0's
                if bitmask[:i].count('1') == 0 and bitmask[i+4:].count('1') == 0:
                    starting_location_bin = format(i, '05b')
                    dictionary_index_bin = format(dict_index, '04b')
                    compressed_form = f"010{starting_location_bin}{bitmask[i:i+4]}{dictionary_index_bin}"
                    # print(f"Compression successful with: {compressed_form}")  # Debug
                    return compressed_form
                else:
                    # print("Remaining bits are not all '0's. Discarding this bitmask.")  # Debug
                    pass
                
    # print("No suitable compression found.")  # Debug
    return None




def compress_1bit_mismatch(binary, frequency_dict, index):
    # print(f"Starting compressi/on for binary: {binary}")
    for dict_index, dict_binary in enumerate(frequency_dict.keys()):
        # print(f"\nComparing with dictionary entry {dict_index}: {dict_binary}")
        found_mismatch = False
        mismatch_location = -1

        for i in range(len(binary)):
            xor_result = int(binary[i] != dict_binary[i])
            # print(f"Bit {i}: binary={binary[i]}, dict_binary={dict_binary[i]}, xor_result={xor_result}")

            if xor_result == 1 and not found_mismatch:
                found_mismatch = True
                mismatch_location = i
                # print(f"First mismatch found at index {mismatch_location}")
            elif xor_result == 1 and found_mismatch:
                # print("Second mismatch found, moving to next dictionary entry.")
                break
        else:  # This else belongs to the for loop, meaning it executes if the loop wasn't broken.
            if found_mismatch:
                encoded = "011" + format(mismatch_location, '05b') + format(dict_index, '04b')
                # print(f"Encoding successful: {encoded}")
                return encoded

    # print("No single bit mismatch found for any dictionary entry.")
    return None

def compress_2bit_consecutive(binary, frequency_dict, index):
    for dict_index, dict_binary in enumerate(frequency_dict.keys()):
        # print(f"\nChecking against dictionary entry {dict_index}: {dict_binary}")
        starting_index = find_2bit_consecutive_mismatch(binary, dict_binary)
        if starting_index is not None:
            encoded = f"110{format(starting_index, '05b')}{format(dict_index, '04b')}"
            # print(f"The binary is {binary}. Encoding with starting index {starting_index} and dictionary index {dict_index}: {encoded}")
            return encoded
    # print("No valid compression found for any dictionary entry.")
    return None

def find_2bit_consecutive_mismatch(binary, dict_binary):
    sum = 0
    starting_index = None
    found_2_bit_mismatch = False

    for i in range(len(binary)):
        xor_result = '1' if binary[i] != dict_binary[i] else '0'
        # print(f"Comparing bit {i}: binary={binary[i]}, dict_binary={dict_binary[i]}, xor_result={xor_result}, sum={sum}")
        if xor_result == '1' and not found_2_bit_mismatch:
            sum += 1
            if sum == 1:
                starting_index = i
            elif sum == 2:
                found_2_bit_mismatch = True
        elif xor_result == '1' and found_2_bit_mismatch:
            # print(f"Exiting early due to additional mismatch at index {i}.")
            return None
        else:
            if sum>0 and sum<2:
                return None
            else:
                sum = 0

    if found_2_bit_mismatch:
        # print(f"Found 2-bit consecutive mismatch starting at index {starting_index}.")
        return starting_index
    else:
        # print("No 2-bit consecutive mismatch found.")
        return None


def compress_4bit_consecutive(binary, frequency_dict, index):
    for dict_index, dict_binary in enumerate(frequency_dict.keys()):
        # print(f"\nChecking against dictionary entry {dict_index}: {dict_binary}")
        starting_index = find_4bit_consecutive_mismatch(binary, dict_binary)
        if starting_index is not None:
            encoded = f"101{format(starting_index, '05b')}{format(dict_index, '04b')}"
            # print(f"the binary is "+binary+" Encoding with starting index {starting_index} and dictionary index {dict_index}: {encoded}")
            return encoded
    # print("No valid compression found for any dictionary entry.")
    return None



def find_4bit_consecutive_mismatch(binary, dict_binary):
    sum = 0
    starting_index = None
    found_4_bit_mismatch = False

    for i in range(len(binary)):
        xor_result = '1' if binary[i] != dict_binary[i] else '0'
        # print(f"Comparing bit {i}: binary={binary[i]}, dict_binary={dict_binary[i]}, xor_result={xor_result}, sum={sum}")
        if xor_result == '1' and not found_4_bit_mismatch:
            sum += 1
            if sum == 1:
                starting_index = i
            elif sum == 4:
                found_4_bit_mismatch = True
        elif xor_result == '1' and found_4_bit_mismatch:
            # print(f"Exiting early due to additional mismatch at index {i}.")
            return None
        else:
            if sum>0 and sum<4:
                return None
            else:
                sum = 0

    if found_4_bit_mismatch:
        # print(f"Found 4-bit consecutive mismatch starting at index {starting_index}.")
        return starting_index
    else:
        # print("No 4-bit consecutive mismatch found.")
        return None



def compress_2bit_anywhere(binary, frequency_dict, index):
    for dict_index, dict_binary in enumerate(frequency_dict.keys()):
        mismatch_indexes = [i for i, (b1, b2) in enumerate(zip(binary, dict_binary)) if b1 != b2]
        if len(mismatch_indexes) == 2:
            # print("The binary is "+binary+" The dict entry is "+dict_binary+" and indexes are "+str(mismatch_indexes[0])+" & "+str(mismatch_indexes[1]))
            # print(f"110{format(mismatch_indexes[0], '05b')}{format(mismatch_indexes[1], '05b')}{format(dict_index, '04b')}")
            return f"110{format(mismatch_indexes[0], '05b')}{format(mismatch_indexes[1], '05b')}{format(dict_index, '04b')}"
    return None

def compress_direct_matching(binary, frequency_dict, index):
    for dict_index, dict_binary in enumerate(frequency_dict.keys()):
        if binary == dict_binary:
            # print("The binary is "+binary+" compressed is "+f"111{format(dict_index, '04b')}")
            return f"111{format(dict_index, '04b')}"
    return None



def decompress():
    # print("Decompression function called")
    bitstring, frequency_dict = decompress_filler()
    # print("Part before delimiter:", bitstring)
    # print("Part after delimiter:", frequency_dict)
    binaries = parseBitstring(bitstring, frequency_dict)

    with open("dout.txt", "w") as file:
        for binary in binaries:
            file.write(binary + "\n")


def parseBitstring(bitstring, frequency_dict):
    binaries=[]
    bin_index=0
    index=0
    while index < len(bitstring):
        if index + 3 > len(bitstring):
            # print("Incomplete format identifier at the end of the bitstring.")
            break
        format_identifier = bitstring[index:index+3]
        index += 3
        if format_identifier == '000':
            if index + 32 > len(bitstring):
                # print("Not enough bits left for '000' Original Binary format.")
                break
            data = bitstring[index:index+32]
            index += 32
            # print(f"The data getting appended is : {data}, the format identifier is {format_identifier}")
            binaries.append(data)
            bin_index+=1
            
        elif format_identifier == '001':
            data = bitstring[index:index+3]
            index += 3
            range_end = int(data, 2)  
            instruction = binaries[bin_index - 1]
            for i in range(range_end+1):
                binaries.append(instruction)
                bin_index += 1

        elif format_identifier == '010':
            starting_location = int(bitstring[index:index+5], 2)
            bitmask = bitstring[index+5:index+9]
            dictionary_index = int(bitstring[index+9:index+13], 2)
            index += 13
            
            bitmask_real = '0' * starting_location + bitmask + '0' * (32 - starting_location - 4)
            
            dictionary_entry = frequency_dict[dictionary_index]
            
            compressed_result = ''.join('1' if b1 != b2 else '0' for b1, b2 in zip(bitmask_real, dictionary_entry))
            binaries.append(compressed_result)
            bin_index+=1

        elif format_identifier == '011':
            mismatch_location = int(bitstring[index:index+5], 2)
            dictionary_index = int(bitstring[index+5:index+9], 2)
            index += 9
            
            dictionary_entry = frequency_dict[dictionary_index]
            
            dictionary_entry_list = list(dictionary_entry)
            
            if dictionary_entry_list[mismatch_location] == '1':
                dictionary_entry_list[mismatch_location] = '0'
            elif dictionary_entry_list[mismatch_location] == '0':
                dictionary_entry_list[mismatch_location] = '1'

            
            modified_dictionary_entry = ''.join(dictionary_entry_list)
            binaries.append(modified_dictionary_entry)
            bin_index+=1

        elif format_identifier == '100':
            mismatch_location = int(bitstring[index:index+5], 2)
            dictionary_index = int(bitstring[index+5:index+9], 2)
            index += 9
            
            dictionary_entry = frequency_dict[dictionary_index]
            
            dictionary_entry_list = list(dictionary_entry)
            
            if dictionary_entry_list[mismatch_location] == '1':
                dictionary_entry_list[mismatch_location] = '0'
            elif dictionary_entry_list[mismatch_location] == '0':
                dictionary_entry_list[mismatch_location] = '1'

            if dictionary_entry_list[mismatch_location+1] == '1':
                dictionary_entry_list[mismatch_location+1] = '0'
            elif dictionary_entry_list[mismatch_location+1] == '0':
                dictionary_entry_list[mismatch_location+1] = '1'

            
            modified_dictionary_entry = ''.join(dictionary_entry_list)
            binaries.append(modified_dictionary_entry)
            bin_index+=1

        elif format_identifier == '101':
            mismatch_location = int(bitstring[index:index+5], 2)
            dictionary_index = int(bitstring[index+5:index+9], 2)
            index += 9
            
            dictionary_entry = frequency_dict[dictionary_index]
            
            dictionary_entry_list = list(dictionary_entry)
            
            if dictionary_entry_list[mismatch_location] == '1':
                dictionary_entry_list[mismatch_location] = '0'
            elif dictionary_entry_list[mismatch_location] == '0':
                dictionary_entry_list[mismatch_location] = '1'

            if dictionary_entry_list[mismatch_location+1] == '1':
                dictionary_entry_list[mismatch_location+1] = '0'
            elif dictionary_entry_list[mismatch_location+1] == '0':
                dictionary_entry_list[mismatch_location+1] = '1'

            if dictionary_entry_list[mismatch_location+2] == '1':
                dictionary_entry_list[mismatch_location+2] = '0'
            elif dictionary_entry_list[mismatch_location+2] == '0':
                dictionary_entry_list[mismatch_location+2] = '1'

            if dictionary_entry_list[mismatch_location+3] == '1':
                dictionary_entry_list[mismatch_location+3] = '0'
            elif dictionary_entry_list[mismatch_location+3] == '0':
                dictionary_entry_list[mismatch_location+3] = '1'

            modified_dictionary_entry = ''.join(dictionary_entry_list)
            binaries.append(modified_dictionary_entry)
            bin_index+=1

        elif format_identifier == '110':
            first_mismatch_location = int(bitstring[index:index+5], 2)
            second_mismatch_location = int(bitstring[index+5:index+10], 2)
            dictionary_index = int(bitstring[index+10:index+14], 2)
            index += 14
            dictionary_entry = frequency_dict[dictionary_index]
            
            dictionary_entry_list = list(dictionary_entry)

            if dictionary_entry_list[first_mismatch_location] == '1':
                dictionary_entry_list[first_mismatch_location] = '0'
            elif dictionary_entry_list[first_mismatch_location] == '0':
                dictionary_entry_list[first_mismatch_location] = '1'

            if dictionary_entry_list[second_mismatch_location] == '1':
                dictionary_entry_list[second_mismatch_location] = '0'
            elif dictionary_entry_list[second_mismatch_location] == '0':
                dictionary_entry_list[second_mismatch_location] = '1'

            modified_dictionary_entry = ''.join(dictionary_entry_list)
            binaries.append(modified_dictionary_entry)
            bin_index+=1
        
        elif format_identifier == '111':
            dictionary_index = int(bitstring[index:index+4], 2)
            index += 4
            dictionary_entry = frequency_dict[dictionary_index]
            binaries.append(dictionary_entry)
            bin_index+=1
        
        else:
            # print(f"Unknown format identifier: {format_identifier}")
            break
        
    return binaries





def decompress_filler():
    try:
        with open('compressed.txt', 'r') as file:
            contents = file.read().split('xxxx', 1)  # Split into two parts at the first occurrence of 'xxxx'
            # Get the part before 'xxxx' as a single string
            before_delimiter = contents[0].replace('\n', '').strip()
            # Get the part after 'xxxx' as a list of lines
            after_delimiter = [line.strip() for line in contents[1].split('\n') if line.strip()]
        return before_delimiter, after_delimiter
    except FileNotFoundError:
        print("File compressed.txt not found.")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 SIM.py [1|2]")
        print("1 for compression, 2 for decompression")
        sys.exit(1)

    operation = sys.argv[1]

    # Reading the input file into a list
    try:
        with open('original.txt', 'r') as file:
            binaries = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("File original.txt not found.")
        sys.exit(1)

    # Count frequencies of each binary
    frequency = Counter(binaries)
    
    # Select the sixteen most frequent entries, preserving original order
    sorted_unique_binaries = sorted(set(binaries), key=lambda x: (-frequency[x], binaries.index(x)))
    top_sixteen = sorted_unique_binaries[:16]

    # Create a dictionary for the top sixteen binaries with their compression index
    compression_dict = {binary: format(index, '04b') for index, binary in enumerate(top_sixteen)}
    # print(compression_dict)
    if operation == '1':
        compress(binaries, compression_dict)
    elif operation == '2':
        decompress()  # Decompression might need its own specific input and logic
    else:
        print("Invalid argument. Use 1 for compression and 2 for decompression.")
        sys.exit(1)

if __name__ == "__main__":
    main()
