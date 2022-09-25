#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

def main(argv):
    for year in range(2012, 2019):
        print('year', year)
        zoo_csv = '../Dataset/%s_malware.csv' % year
        known_md5s = set([])
        cnt = 0
        for m in range(1, 10):
            month = '0%s' % m
            for fname in os.listdir('/space1/android/malware/%s/%s' % (year, month)):
                md5 = fname.split('.apk')[0]
                known_md5s.add(md5)
                cnt += 1
            print(month, cnt)
        for month in range(10, 13):
            for fname in os.listdir('/space1/android/malware/%s/%s' % (year, month)):
                md5 = fname.split('.apk')[0]
                known_md5s.add(md5)
                cnt += 1
            print(month, cnt)
        print(len(known_md5s))
        fout = open('../Dataset/%s_malware_r2.csv' % year, 'w')
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
