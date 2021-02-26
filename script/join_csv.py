#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pandas as pd

def main(argv):
    latest_csv = pd.read_csv('/space1/android/latest.csv')
    for year in range(2012, 2019):
        fname = 'Dataset/%s_benign.txt' % year
        benign_csv = pd.read_csv(fname, header=0, names=['md5', 'date'])
        res = latest_csv.join(benign_csv.set_index('md5'), on='md5', how='inner').drop(columns='date')
        res.to_csv('Dataset/%s_benign.csv' % year, index=False)


if __name__ == "__main__":
    main(sys.argv)