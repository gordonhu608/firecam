# Copyright 2018 The Fuego Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""
Fetch images from USGS archives

@author: fuego
"""
import os
import numpy as np
import time
from urllib.request import urlretrieve
import logging

import sys
import settings
sys.path.insert(0, settings.fuegoRoot + '/lib')
import collect_args

#from multiprocessing import Pool #The current code is kind of slow - perhaps parallelizing the process would help?

hookTotalSize = 0
def rhook(blockcount, blocksize, totalsize):
    global hookTotalSize
    # logging.warning('blockcount %d, blocksize %d, totalsize %d', blockcount, blocksize, totalsize)
    hookTotalSize = totalsize

def usgs_puller(camera, date, start, end, output_folder):
    """Fetch images from USGS archives

    Args:
        camera (str): name of camera (part of URL)
        date (str): date in YYYYMMDD format
        start (list): starting time in [HH, mm] format"
        end (list): ending time in [HH, mm] format
        output_folder (str): path to folder where images are stored
    """
    global hookTotalSize

    start_time = time.time()
    camera_dir = output_folder + '/' + camera + '/'
    if not os.path.exists(camera_dir):
        os.makedirs(camera_dir)
        
    image_url = 'https://rockyags.cr.usgs.gov/outgoing/camHist/swfrs/'+ date[:4] + '/' + camera + '/'+ date + '/'+ camera + '-'
    
    #This currently renames the image to our google drive naming format, we may want to change this to a unix time name to better match sort_images.py    
    image_filename = camera_dir + camera + '__' + date[:4] + '-' + date[4:6] + '-' + date[6:8] + 'T'
    
    start_hour = int(start[0])
    start_minute = int(start[1])
    end_hour = int(end[0])
    end_minute = int(end[1])
    
    time_elapsed = (end_hour*60 + end_minute) - (start_hour*60 + start_minute)
    
    #Initialize counting and timing variables. These are commented out, but can be reintroduced for testing purposes.
    count = 0
    fail_count = 0
    #read_time = 0
    #fail_time = 0
    
    for minute in range(time_elapsed):
        current_minute = int(start_minute + minute - np.floor((start_minute + minute)/60)*60)
        current_hour = int(start_hour + np.floor((start_minute + minute)/60))
        
        filetime = str(current_hour).zfill(2) + str(current_minute).zfill(2) + '.jpg'
        image_time =  str(current_hour).zfill(2) + ';' + str(current_minute).zfill(2) + ';' + '00' + '.jpg'

        url = image_url + filetime
        #start_read_time = time.time()
        try:
            filename = image_filename + image_time
            hookTotalSize = 0
            ret = urlretrieve(url, filename, reporthook=rhook)
            # logging.warning('size = %d', hookTotalSize)
            if hookTotalSize < 0:
                fail_count += 1
                os.remove(filename)
            else:
                logging.warning('Fetched %s successfully', image_time)
                count += 1
            #read_time += time.time() - start_read_time
        except Exception as e:
            # logging.error('Error fetching image from %s %s', url, str(e))
            fail_count += 1
            #fail_time += time.time() - start_read_time
    logging.warning('Fetched %d files in %d seconds. %d failures', count, int(time.time() - start_time), fail_count)


def main():
    reqArgs = [
        ["c", "camera", "name of camera (part of URL)"],
        ["d", "date", "date in YYYYMMDD format"],
        ["s", "startTime", "starting time in HH:mm format"],
        ["e", "endTime", "ending time in HH:mm format"],
        ["o", "output", "path to folder where images are stored"],
    ]
    args = collect_args.collectArgs(reqArgs)
    usgs_puller(args.camera, args.date, args.startTime.split(':'), args.endTime.split(':'), args.output)


if __name__=="__main__":
    main()