#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

def main(argv):
    #for year in [2015, 2016, 2018]:
    for year in [2015]:
        #zoo_csv = '../androzoo_files/%s_benign.csv' % year
        zoo_csv = '../androzoo_files/%s_benign_r3.csv' % year
        known_md5s = set([])
        with open('/home/yz/code/mal/src/dataset/cmd_benign_%s_exr3.txt' % year, 'r') as f:
            for line in f:
                md5 = line.rstrip().split(' ')[0]
                known_md5s.add(md5)
        fout = open('../androzoo_files/%s_benign_r4.csv' % year, 'w')
        with open(zoo_csv, 'r') as f:
            firstline = True
            for line in f:
                if firstline:
                    firstline = False
                    continue
                md5 = line.rstrip().split(',')[2]
                if md5 in known_md5s:
                    continue
                else:
                    fout.write(line)
        fout.close()


    return

if __name__ == "__main__":
    main(sys.argv)
