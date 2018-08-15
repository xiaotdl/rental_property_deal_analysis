#!/usr/bin/env python
import os


DATA_DIR = 'data'
for data_file in os.listdir(DATA_DIR):
    data_filepath = os.path.join(DATA_DIR, data_file)
    print 'updating %s...' % data_filepath
    os.system('./deal_analysis.py %s 1' % data_filepath)


