import zmq, threading, subprocess, os, tempfile,cv2
import time

import message_protocols

CAMERA_SERVER_PORT = "tcp://*:5001"
recording_bit = False
class client_camera_system():


    _context = None
    _socket = None
    _out_video_file = None
    _cap = None

    def __init__(self):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._socket.bind(CAMERA_SERVER_PORT)
        self._recording_bit = False


    def restart_connection(self):
        pass

    def get_message(self,expected_message):
        message = self._socket.recv()
        if not expected_message == message:
            print "error : received '", message," ' instead of '", expected_message, "'"
            self.restart_connection()

        print "GOT : ", message


    def send_message(self, message):
        self._socket.send(message)
        print "SENT : ", message



    def start_video_record(self,folder_path, video_name):
        global recording_bit
        self._cap = cv2.VideoCapture(0)
        #fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fourcc =  cv2.cv.CV_FOURCC('M','J','P','G')
        self._out_video_file = cv2.VideoWriter(os.path.join(folder_path,video_name), fourcc, 20.0, (640, 480))
        while (self._cap.isOpened()):
            ret, frame = self._cap.read()
            if recording_bit == False:
                break
            if ret == True:
                self._out_video_file.write(frame)
            else:
                break



    def stop_video_record(self,folder_path, video_name):
        global recording_bit
        self._recording_bit = False
        self._out_video_file.release()
        self._cap.release()
        video_avi_file_path = os.path.join(folder_path,video_name)
        video_mp4_file_path = os.path.join(folder_path, "video.mp4")
        conv_proc = subprocess.Popen("ffmpeg -i "+video_avi_file_path+" "+video_mp4_file_path)
        while conv_proc.poll():
            time.sleep(1)


    def take_image(self,folder_path, img_name):
        cap = cv2.VideoCapture(0)
        ret,img = cap.read()
        cv2.imwrite(os.path.join(folder_path,img_name), img)
        cap.release()



    def run(self):

        temp_dir = tempfile.mkdtemp()
        print temp_dir

        self.get_message(message_protocols.CLIENT_TEST_SYSTEM_START_TESTING)
        self.send_message(message_protocols.CLIENT_CAMERA_READY_TO_CAPTURED)

        self.get_message(message_protocols.CLIENT_CAMERA_CAPTURE_QR)
        self.take_image(temp_dir,"test_qr.jpg")
        self.send_message(message_protocols.CLIENT_CAMERA_QR_CODE_CAPTURED)

        self.get_message(message_protocols.CLIENT_CAMERA_CAPTURE_BLANK_SCREEN)
        self.take_image(temp_dir,"ref.jpg")
        self.send_message(message_protocols.CLIENT_CAMERA_BLANK_SCREEN_CAPTURED)

        self.get_message(message_protocols.CLIENT_CAMERA_CAPTURE_VIDEO)
        t = threading.Thread(target=self.start_video_record, args=(temp_dir, "video.avi"))
        t.start()
        self.send_message(message_protocols.CLIENT_CAMERA_VIDEO_CAPTURED)

        self.get_message(message_protocols.CLIENT_CAMERA_STOP_CAPTURING_VIDEO)
        self.stop_video_record(temp_dir, "video.avi")
        self.send_message(message_protocols.CLIENT_CAMERA_VIDEO_CAPTURE_STOPPED)

        self.get_message(message_protocols.CLIENT_CAMERA_DONE)
        self.send_message(message_protocols.CLIENT_CAMERA_RELEASING_RESOURCES)

camera_thread = client_camera_system()
while True:
    camera_thread.run()