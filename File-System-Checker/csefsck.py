import json 
import time

super_block = json.loads(open('fusedata.0', 'r+').read())
file_ = json.loads(open('fusedata.0', 'r+').read())
#print json.dumps(file_, indent = 4 , separators = (',',': ') )

# ----------------Check for device ID----------------- #
print "# Checking for device ID"
if super_block['devId'] != 20: 
    print "# Device ID not equal to 20. Changing it to 20"
    print
    super_block['devId'] = 20
    json.dump(super_block,open('fusedata.0', 'r+' ))
else:
    print "# Device ID is correct. i.e. 20"
    print


# --------------Check if all time are in past -------- #
def check_time(time_in):
    '''
    time : integer
    checks if all times are in past.
    
    Returns True if time received is past with relative to present time
    False otherwise
    '''
    if time_in < int(time.time()):
        return True
    else:
        return False
        
#----------------File system check------------# 
print "# Checking time for super_block"
if check_time(super_block['creationTime']) == False:
    print "# Time is not in past. Test Failed. Can't be rectified"
    print    
else:
    print "# Time is in past. Test passed"
    print
        
#-------------Check if free block list is accurate----------#
file_name = 'fusedata'
print "#Checking if free block list is accurate" 
print "#Making sure that the free list contains all the free blocks"

 #-------looping across all files and checking if contain all the FREE blocks ---------- 
start_free = 31
end_free = 400

for i in range(super_block['freeStart'],super_block['freeEnd'] + 1):

    all_present = True
    file_name += '.' + str(i)
    file_data = json.loads(open(file_name, 'r+').read()) 
    if type(file_data) == list:
        for vals in range(start_free,end_free):
            if vals not in file_data:
                all_present = False 
                print str(vals) + ' not in the free list. Therefore adding ' + str(vals) + ' in the list'
                print
                file_data.append(vals) 
                file_data.sort()
                json.dump(file_data,open(file_name, 'r+') )
    if start_free == 31:
        start_free = 400
    else:
        start_free += 400
    end_free += 400 
    file_name = 'fusedata'
print
if all_present == True:
    print "The free list contains all the free blocks"
    print
else:
    print "The free list had missing free blocks which have been added"   
    print 
    
                      

print "# Making sure than there are no files/directories stored on items listed in the free block list"

for i in range(super_block['freeStart'],super_block['freeEnd'] + 1):
    file_name += '.' + str(i)
    file_or_dir = []
    test_failed = False 
    file_data = json.loads(open(file_name, 'r').read()) 
    if type(file_data) == dict:
        file_or_dir.append(i)
        test_failed = True
    if test_failed == True:
        print '# Block/s ' + str(file_or_dir) + ' is/are either file/directory and not free blocks'
    file_name = 'fusedata'
    
print
       



#--------finding the root directory and loading it --------- # 
root_block_no = super_block['root']
root_block = json.loads(open('fusedata.' + str(root_block_no), 'r+').read())
block_size = 4096
#print json.dumps(root_block, indent = 4 , separators = (',',': ') )

#------------File checking function---------------#
def toCheckFile(file_iNode, location_of_inode):
    print '# Checking file iNode at ' + str(location_of_inode)
    print '# Cheking file time of file: ' + str(location_of_inode)
    print
    if check_time(file_iNode['atime']) == True:
        print 'atime correct and is in past'
    else:    
        print "atime is in future, ERROR "
    if check_time(file_iNode['ctime']) == True:
        print 'ctime correct and is in past'    
        print
    else:    
        print "ctime is in future, ERROR "
        print    
    global block_size
    print '#Performing check on a file: if indirect = 1, the data in the location pointed is an array'
    #print json.dumps(file_iNode, indent = 4 , separators = (',',': ') )
    size = file_iNode['size']
    indirect = file_iNode['indirect']
    length_location_array = len(json.loads(open('fusedata.' + str(file_iNode['location']), 'r+').read()))
    if indirect == 1:
        location_pointer = file_iNode['location']
        type_at_location = type(json.loads(open('fusedata.' + str(location_pointer), 'r+').read()))
        if  type_at_location == list:
            print 'The location pointed is as array, test passed'
        else:
            print 'The pointed is not an array but a '+ str(type_at_location) + ' . Test failed.'    
    else:
        print "Indirect not equal to one"
        print
    print 
    print "ONE OF THE TESTS PERFORMED  ACCORDING TO CONDITION: "
    print "#TEST 1: size < blocksize  should have indirect=0 and size>0" 
    print "#TEST 2: if indirect!=0, size should be less than (blocksize*length of location array)"
    print "#TEST 3: if indirect!=0, size should be greater than (blocksize*length of location array-1)"       
    print
    if size < block_size:
        print "TEST 1 PERFORMED"
        if indirect != 0:
            print "Size < blocksize but indirect is not equal to 0"
            print "Changing indirect to zero"
            print
            file_iNode['indirect'] = 0
            json.dump(file_iNode,open('fusedata.' + str(location_of_inode), 'r+'))
        else:
            print "TEST 1 PASSED"
            print
    if size < (block_size*length_location_array) and size > block_size:
        print "TEST 2 PERFORMED"
        if indirect == 0:
            print 'size < length_location_array but indirect is equal to zero'
            print 'Changing indirect to 1'
            print   
            file_iNode['indirect'] = 1
            json.dump(file_iNode,open('fusedata.' + str(location_of_inode), 'r+'))      
        else:
            print "TEST 2 PASSED"
            print
    if size > (block_size*length_location_array-1):
        print "TEST 3 PERFORMED"
        if indirect == 0:
            print 'size > length_location_array -1 but indirect is equal to zero'
            print 'Changing indirect to 1'
            print   
            file_iNode['indirect'] = 1
            json.dump(file_iNode,open('fusedata.' + str(location_of_inode), 'r+'))                  
        else:
            print "TEST 3 PASSED" 
            print      
#--------Cheking if each directory contains . and .. --------- # 
def toCheckdir(filename_to_inode_dicts, parent_block, current_block):
    '''
    filname_to_inode_dicts is the json.load object of the fusedata file.
    parent_block receives the location of the block which called the fucntion.
    current_block receives the location of the block being called
    
    Checks for the dir . and .. and their corresponding block numbers.
    '''
    print 'Getting into directory ' + str(current_block)
    print 'Checking time for directory ' + str(current_block)
    print
    if check_time(filename_to_inode_dicts['ctime']) == True:
        print 'ctime is in past and is correct'
    else:    
        print "ctime is in future, ERROR "
        
    if check_time(filename_to_inode_dicts['mtime']) == True:
        print 'mtime is in past and is correct'
    else:    
        print "mtime is in future, ERROR "    
        
    if check_time(filename_to_inode_dicts['atime']) == True:
        print 'atime is in past and is correct'
        print
    else:    
        print "atime is in future, ERROR "
        print           
    #print json.dumps(filename_to_inode_dicts, indent = 4 , separators = (',',': ') )
    for i in range(len(filename_to_inode_dicts['filename_to_inode_dict'])):
        #---------If type of file is 'd', run the if part -------------#
        if filename_to_inode_dicts['filename_to_inode_dict'][i]['type'] == "d":
            if filename_to_inode_dicts['filename_to_inode_dict'][i]['name'] == '.':
                #print 'Entered single dot'
                if filename_to_inode_dicts['filename_to_inode_dict'][i]['location'] == current_block:
                    print "' . ' of directory at location " + str(current_block) + " point to the right location i.e. current directory"
                    print
                else:
                    print "directory ' . ' does not point to the right location."
                    print "Changing location of ' . ' directory to " + str(current_block)
                    print
                    filename_to_inode_dicts['filename_to_inode_dict'][i]['location'] = current_block
                    #Code to change location
                    json.dump(filename_to_inode_dicts,open('fusedata.' + str(current_block), 'r+') )
                    #print json.dumps(filename_to_inode_dicts, indent = 4 , separators = (',',': ') )  
                         
                    
            elif filename_to_inode_dicts['filename_to_inode_dict'][i]['name'] == '..':
                #print 'entered double dot'
                if filename_to_inode_dicts['filename_to_inode_dict'][i]['location'] == parent_block:
                    print "' .. ' point to the parent location of " + str(parent_block) + " which is right"
                    print
                else:
                    print "directory ' .. ' does not point to the parent location."
                    print "Changing location of ' .. ' directory to parent location. i.e. " + str(parent_block) 
                    print 
                    filename_to_inode_dicts['filename_to_inode_dict'][i]['location'] = parent_block
                    json.dump(filename_to_inode_dicts,open('fusedata.' + str(current_block), 'r+') )    
            else:
                #print 'entered else'
                parent = current_block 
                child = filename_to_inode_dicts['filename_to_inode_dict'][i]['location']
                parent_json = json.loads(open('fusedata.' + str(child), 'r+').read())
                #print json.dumps(parent_json, indent = 4 , separators = (',',': ') )
                #print 'recursion called'
                toCheckdir(parent_json, parent, child) 
                     
        #--------------IF type field is 'f' then run else if ------#
        elif filename_to_inode_dicts['filename_to_inode_dict'][i]['type'] == "f":
            toGo = filename_to_inode_dicts['filename_to_inode_dict'][i]['location']
            file_json = json.loads(open('fusedata.' + str(toGo), 'r+').read())
            # to give the function, who called, give child as the paramemter too!
            toCheckFile(file_json, toGo)
         
toCheckdir(root_block, root_block_no, root_block_no)
#print json.dumps(root_block, indent = 4 , separators = (',',': ') )


                
            




