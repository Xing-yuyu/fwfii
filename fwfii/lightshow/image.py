#!/usr/bin/env python
from __future__ import division, absolute_import, print_function

class ImageReader(object):
    def __init__(self, filename, size = (100, 80)):
        from PIL import Image
        self._filename = filename
        self._size = size
        self._frame = Image.open(filename)
        self._palette = self._frame.getpalette()
        self._nframes = 0

    def extractFrames(self, outFolder):
        import os
        while self._frame:
            self._frame.save( '%s/%s-%s.png' % (outFolder, os.path.basename(self._filename), self._nframes ) , 'PNG')
            self._nframes += 1
            try:
                self._frame.seek( self._nframes )
            except EOFError:
                break
        return True

    def extractPixels(self):
        '''
        Extract pixels from current frame and convert it to a hxwx3 numpy array
        @return, the current frame and eof flag
        '''
        if self._frame:
            try:
                from numpy import array
                frame = self._frame.resize(self._size)
                frame = frame.convert('RGB')
                self.pixels = array(frame)
                self._nframes += 1
                self._frame.seek( self._nframes )
            except EOFError:
                return self.pixels, True
    
        return self.pixels, False

    def close(self):
        self._frame.close()


if __name__ == '__main__':
    gr = ImageReader('images/test3.jpeg')
    #gr.extractFrames('GIF')
    print(gr.extractPixels())

    gr.close()
  
