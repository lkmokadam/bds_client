import zmq, threading, subprocess, os, tempfile, cv2, imutils, zipfile
import time

import message_protocols

global camera_recording_bit
global camera_on
CAMERA_SERVER_PORT = "tcp://*:5001"


class client_camera_system():
    _context = None
    _socket = None
    _out_video_file = None
    _cap = None

    def __init__(self):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._socket.bind(CAMERA_SERVER_PORT)
        global camera_on
        camera_on = True

    def frame_grabber_daemon(self):
        # self.set_camera_prop()
        self._cap = cv2.VideoCapture(0)
        while (camera_on):
            self._cap.grab()
        self._cap.release()

    def set_camera_prop(self):
        subprocess.call("v4l2-ctl -c white_balance_temperature_auto=0", shell=True)
        subprocess.call("v4l2-ctl -c exposure_auto=0", shell=True)

    def restart_connection(self):
        pass

    def get_message(self, expected_message):
        message = self._socket.recv()
        if not expected_message == message:
            print "error : received '", message, " ' instead of '", expected_message, "'"
            self.restart_connection()

        print "GOT : ", message

    def send_message(self, message):
        self._socket.send(message)
        print "SENT : ", message

    def start_video_record(self, folder_path, video_name):

        if imutils.is_cv2():
            fourcc = cv2.cv.CV_FOURCC(*'MJPG')
        else:
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        video_file_path = os.path.join(folder_path, video_name)
        self._out_video_file = cv2.VideoWriter(video_file_path, fourcc, 20.0, (640, 480))
        print video_file_path
        global camera_recording_bit
        camera_recording_bit = True

        while (self._cap.isOpened()):
            if not camera_recording_bit:
                break
            ret, frame = self._cap.retrieve()
            if ret:
                self._out_video_file.write(frame)

    def stop_video_record(self):
        global camera_recording_bit
        camera_recording_bit = False
        time.sleep(1)
        camera_on = False
        self._out_video_file.release()

    def take_image(self, folder_path, img_name):

        ret, img = self._cap.retrieve()
        cv2.imwrite(os.path.join(folder_path, img_name), img)
        time.sleep(1)

    def get_zipped_data_bytes(self, tempdir):
        zip_file = zipfile.ZipFile("data.zip",mode='w')
        for root, dirs, files in os.walk(tempdir):
            for file in files:
                zip_file.write(os.path.join(root, file))
        return bytearray(zip_file)



    def run(self):

        temp_dir = tempfile.mkdtemp()
        print temp_dir

        self.get_message(message_protocols.CLIENT_TEST_SYSTEM_START_TESTING)
        frame_grabber = threading.Thread(target=self.frame_grabber_daemon)
        frame_grabber.start()
        self.send_message(message_protocols.CLIENT_CAMERA_READY_TO_CAPTURED)

        self.get_message(message_protocols.CLIENT_CAMERA_CAPTURE_QR)
        self.take_image(temp_dir, "test_qr.jpg")

        self.send_message(message_protocols.CLIENT_CAMERA_QR_CODE_CAPTURED)

        self.get_message(message_protocols.CLIENT_CAMERA_CAPTURE_BLANK_SCREEN)
        self.take_image(temp_dir, "ref.jpg")
        self.send_message(message_protocols.CLIENT_CAMERA_BLANK_SCREEN_CAPTURED)

        self.get_message(message_protocols.CLIENT_CAMERA_CAPTURE_VIDEO)
        t = threading.Thread(target=self.start_video_record, args=(temp_dir, "video.avi"))
        t.start()
        self.send_message(message_protocols.CLIENT_CAMERA_VIDEO_CAPTURED)

        self.get_message(message_protocols.CLIENT_CAMERA_STOP_CAPTURING_VIDEO)
        self.stop_video_record()
        self.send_message(message_protocols.CLIENT_CAMERA_VIDEO_CAPTURE_STOPPED)

        self.get_message(message_protocols.CLIENT_CAMERA_DONE)
        self.send_message(message_protocols.CLIENT_CAMERA_RELEASING_RESOURCES)

        self.get_message(message_protocols.CLIENT_CAMERA_GET_ZIPPED_DATA)
        file_byte_array = self.get_zipped_data_bytes(temp_dir)
        self.send_message(file_byte_array)



camera_thread = client_camera_system()
while True:
    camera_thread.run()
