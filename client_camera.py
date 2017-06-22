import zmq, threading, subprocess, os, tempfile, cv2, imutils, zipfile, shutil, datetime
import time

import message_protocols

global camera_recording_bit
global camera_on
CAMERA_SERVER_PORT = "tcp://*:5001"
CAP_WIDTH = 1920
CAP_HEIGHT = 1080

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

    def get_camera_cap(self):
        counter = 0
        while counter < 5 & (not self._cap):
            self._cap = cv2.VideoCapture(0)
            if self._cap:
                if imutils.is_cv2():
                    self._cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, CAP_WIDTH)
                    self._cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, CAP_HEIGHT);
                else:
                    self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAP_WIDTH);
                    self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_HEIGHT);
            print "didnt got the cap. trying again"
            time.sleep(1)
            counter += 1

    def frame_grabber_daemon(self):
        # self.set_camera_prop()
        global camera_on
        if self._cap:
            while (camera_on):
                self._cap.grab()
            self._cap.release()
        else:
            raise Exception("Unable to get Camera")

    def set_camera_prop(self):
        subprocess.call("v4l2-ctl -c white_balance_temperature_auto=0", shell=True)
        subprocess.call("v4l2-ctl -c exposure_auto=0", shell=True)

    def restart_connection(self):
        pass

    def get_message(self, expected_message = None):
        message = self._socket.recv()
        if expected_message:
            if not expected_message == message:
                print "error : received '", message, " ' instead of '", expected_message, "'"
                self.restart_connection()
                print "GOT : ", message
        else:
            print "GOT : ", message[0:100]
        return message

    def send_message(self, message):
        self._socket.send(message)
        if message is str:
            print "SENT : ", message

    def start_video_record(self, folder_path, video_name):

        if imutils.is_cv2():
            fourcc = cv2.cv.CV_FOURCC(*'XVID')
        else:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_file_path = os.path.join(folder_path, video_name)
        self._out_video_file = cv2.VideoWriter(video_file_path, fourcc, 20.0, (CAP_WIDTH, CAP_HEIGHT))
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
        self._cap.release()
        time.sleep(3)

    def take_image(self, folder_path, img_name):

        ret, img = self._cap.retrieve()
        cv2.imwrite(os.path.join(folder_path, img_name), img)
        time.sleep(1)

    def get_zipped_data_bytes(self, tempdir):
        tmp = tempfile.mkdtemp()
        temp_zip_file = os.path.join(tmp, "data.zip")

        zip_file = zipfile.ZipFile(temp_zip_file, 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(tempdir):
            for file in files:
                zip_file.write(os.path.join(root, file), arcname=file)

        zip_file.close()
        f = open(temp_zip_file, 'rb')
        byte_array = bytearray(f.read())
        f.close()
        print temp_zip_file
        #shutil.rmtree(tmp, ignore_errors=True)
        return byte_array

    def run(self):

        temp_dir = tempfile.mkdtemp()

        self.get_message(message_protocols.CLIENT_TEST_SYSTEM_START_TESTING)
        self.get_camera_cap()
        frame_grabber = threading.Thread(target=self.frame_grabber_daemon)
        frame_grabber.start()
        self.send_message(message_protocols.CLIENT_CAMERA_READY_TO_CAPTURED)

        conf_file_data = self.get_message()
        conf_file_data = str(conf_file_data)

        self.send_message(message=message_protocols.CLIENT_CAMERA_CONF_FILE_RECEIVED)

        self.get_message(message_protocols.CLIENT_CAMERA_CAPTURE_QR)

        self.take_image(temp_dir, "qr.jpg")
        qr_timestamp = time.time()
        conf_file_data = conf_file_data + "\nQR IMAGE TIME: "+datetime.datetime.fromtimestamp(qr_timestamp).strftime('%Y-%m-%d %H:%M:%S')

        self.send_message(message_protocols.CLIENT_CAMERA_QR_CODE_CAPTURED)

        self.get_message(message_protocols.CLIENT_CAMERA_CAPTURE_BLANK_SCREEN)
        self.take_image(temp_dir, "ref.jpg")
        ref_timestamp = time.time()
        conf_file_data = conf_file_data + "\nREF IMAGE TIME: " + datetime.datetime.fromtimestamp(
            ref_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        self.send_message(message_protocols.CLIENT_CAMERA_BLANK_SCREEN_CAPTURED)

        self.get_message(message_protocols.CLIENT_CAMERA_CAPTURE_VIDEO)

        t = threading.Thread(target=self.start_video_record, args=(temp_dir, "video.avi"))
        t.start()
        video_timestamp = time.time()
        conf_file_data = conf_file_data + "\nVIDEO START TIME: " + datetime.datetime.fromtimestamp(
            video_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        self.send_message(message_protocols.CLIENT_CAMERA_VIDEO_CAPTURED)

        self.get_message(message_protocols.CLIENT_CAMERA_STOP_CAPTURING_VIDEO)
        self.stop_video_record()

        self.send_message(message_protocols.CLIENT_CAMERA_VIDEO_CAPTURE_STOPPED)

        conf_file = open(os.path.join(temp_dir, "conf.txt"), 'w')
        conf_file.write(conf_file_data)
        conf_file.close()

        self.get_message(message_protocols.CLIENT_CAMERA_DONE)
        self.send_message(message_protocols.CLIENT_CAMERA_RELEASING_RESOURCES)

        self.get_message(message_protocols.CLIENT_CAMERA_GET_ZIPPED_DATA)
        file_byte_array = self.get_zipped_data_bytes(temp_dir)
        self.send_message(file_byte_array)

        shutil.rmtree(temp_dir, ignore_errors=True)


camera_thread = client_camera_system()
while True:
    camera_thread.run()
