#!/usr/bin/env python3
import argparse
import signal, os

from pyueye import ueye
from pypyueye.camera import Camera as Cam
from pypyueye.threads import MultiFrameThread

# Setting up argparse
parser = argparse.ArgumentParser('capture images')
parser.add_argument('--captured_images_path', 
                    type=str, help='folder where data will be stored',
                    default='capture/')
parser.add_argument('--base_name', default='TEST', type=str,
                    help='base name for the saved files')
parser.add_argument('-f', '--fps', type=int,
                    default=80, help='frames per second to be captured' )
parser.add_argument('-n', '--number_of_frames', type=int,
                    default=644, help='total number of frames to capture' )
parser.add_argument('-t', '--file_type', default="envi",
                    help='frames or images will be stored as this filetype')
parser.add_argument('-b', '--binning', default=[1,1], nargs=2, type=int,
                    help='number of raw pixels per saved pixel: spatial, spectral')
parser.add_argument('-p', '--do_print', action="store_true",
                    help='print info about captured frames')
parser.add_argument('-g', '--gain', type=int, default=1,
                    help='set the (master) gain')
parser.add_argument('-a', '--aoi', default=[0, 0, 1216, 1936],
                    type=int, nargs=4,
                    help='area of interest xmin, lmin, xwidth, lwidth')

args = parser.parse_args()

# assigning the arguments to variables for simple backwards compatibility
FPS = args.fps
FOLDER = args.captured_images_path
BASE_NAME = args.base_name
MAX_FRAMES = args.number_of_frames
FILE_TYPE = args.file_type
BINNING = tuple(args.binning)
DO_PRINT = False
MASTER_GAIN = args.gain
#the set_aoi function takes them in an odd order
AOI = tuple([args.aoi[1], args.aoi[0], args.aoi[3], args.aoi[2]])
#should add binning support with "numpy.add.reduceat"

print("saving as {}".format(FILE_TYPE))

# DEFAULTS
PIXEL_CLOCK = 237 # one of these: 30, 59, 118, 237, 474

with Cam() as c:
    c.set_colormode(ueye.IS_CM_MONO8)
    #c.set_aoi(0,0,c.,800)

    c.set_pixelclock(PIXEL_CLOCK)
    c.set_fps(FPS)
    actual_fps = c.get_fps()
    c.set_exposure(1/actual_fps*1000)
    c.set_aoi(*AOI)
    c.set_gain(MASTER_GAIN, 0, 0, 0)
    aoi = c.get_aoi()

    print(f"MODIFIED VALUES")
    print(f'fps: {c.get_fps()}')
    print(f'Available fps range: {c.get_fps_range()}')
    print(f'Pixelclock: {c.get_pixelclock()}')
    print(f'aoi: {aoi.height}, {aoi.width}')
    print(f'binning: {BINNING}')
    pixel_clock = c.get_pixelclock()
    exposure = c.get_exposure()

    print(f'handle: {c.handle()}')

    thread = MultiFrameThread(c, folder=FOLDER, base_name=BASE_NAME,
                              max_frames=MAX_FRAMES, file_type=FILE_TYPE,
                              aoi=AOI, binning=BINNING, do_print=DO_PRINT)

    def handler(signum, frame):
        print('Signal handler called with signal \n', signum)
        if signum == signal.SIGINT:
            print("Stopping capture \n")
            thread.stop()

    # Register handler
    print('Setting up signal handler. \n')
    signal.signal(signal.SIGINT, handler)

    thread.start()
    thread.join()

    print("Done capturing. ")
