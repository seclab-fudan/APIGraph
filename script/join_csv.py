#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pandas as pd
import numpy as np

def main(argv):
    # change the path to your latest.csv
    latest_csv = pd.read_csv('/space1/android/latest.csv')
    latest_csv['md5'] = latest_csv['md5'].str.lower()
    for year in range(2012, 2019):
        fname = 'Dataset/%s_benign.txt' % year
        benign_csv = pd.read_csv(fname, header=0, names=['md5', 'date'])
        res = latest_csv.join(benign_csv.set_index('md5'), on='md5', how='inner').drop(columns='date')
        res['vercode'] = res['vercode'].replace(np.nan, 0, regex=True)
        res['vt_detection'] = res['vt_detection'].replace(np.nan, 0, regex=True)
        res['vercode'] = res['vercode'].astype(int)
        res['vt_detection'] = res['vt_detection'].astype(int)
        res.to_csv('androzoo_files/%s_benign.csv' % year, index=False)


if __name__ == "__main__":
    main(sys.argv)