#!/usr/bin/python
import sys
import fileinput

i = 0
if __name__ == "__main__":
    listsfile = open(sys.argv[1], "r")
    for property_file_info_line in listsfile:
#    for property_file_info_line in fileinput.input(sys.argv[1]):
        v = property_file_info_line.split(' ')
        property_filename = v[0]
        property_sold_date = v[1]

        print "Transforming " + property_filename
        newfile_with_solddate = open(property_filename + ".new", "w")
        for line in fileinput.input (property_filename):
            i = i + 1
            newfile_with_solddate.write(property_sold_date + str(i/100) + "," + line)
        newfile_with_solddate.close()
    



