import cv2

class WebCamTracker:
    
    def __init__(self):
        self._connected = False
    
    def connect(self, video_stream_url=None, mode='RGB', **kwargs):
        
        if not self._connected:
            
            self._mode = mode

            # Initialise the video capture.
            if video_stream_url is not None:
                self._vidcap = cv2.VideoCapture(video_stream_url)
            else:
                self._vidcap = cv2.VideoCapture(0)  # default camera
            
            # Check if the video stream was opened
            if not self._vidcap.isOpened():
                raise Exception(f"Failed to open video stream at {video_stream_url}")
            
            self._connected = True

    def _get_frame(self):
        
        ret, frame = self._vidcap.read()
        
        if ret:
            if self._mode == 'R':
                return ret, frame[:,:,2]
            elif self._mode == 'G':
                return ret, frame[:,:,1]
            elif self._mode == 'B':
                return ret, frame[:,:,0]
            elif self._mode == 'RGB':
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                raise ValueError("Mode '{}' not recognised. Supported modes: 'R', 'G', 'B', or 'RGB'.".format(self._mode))
        else:
            return ret, None

    def _close(self):
        
        self._vidcap.release()
        self._connected = False