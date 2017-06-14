import zmq, threading, subprocess, os, sys
import time

import message_protocols

TEST_MACHINE = "TEST_MACHINE"
CAMERA = "CAMERA"
ML_MACHINE = "ML_MACHINE"

SERVER_TCP_PORT = "tcp://*:5003"
CAMERA_IP_PORT = "tcp://localhost:5001"
ML_MACHINE_PORT = "tcp://" + sys.argv[-1]


class server:
    _context = None
    _socket_camera = None
    _socket_test_machine = None
    _socket_ml_machine = None

    def restart_server(self):
        pass

    def __init__(self):
        self._context = zmq.Context()
        self._socket_test_machine = self._context.socket(zmq.REP)
        self._socket_test_machine.bind(SERVER_TCP_PORT)

        self._socket_camera = self._context.socket(zmq.REQ)
        self._socket_camera.connect(CAMERA_IP_PORT)

        self._socket_ml_machine = self._context.socket(zmq.REQ)
        self._socket_ml_machine.connect(ML_MACHINE_PORT)

    def get_message(self, machine, expected_message=None):
        if machine == CAMERA:
            message = self._socket_camera.recv()
        elif machine == TEST_MACHINE:
            message = self._socket_test_machine.recv()
        elif machine == ML_MACHINE:
            message = self._socket_ml_machine.recv()
        else:
            os._exit(1)
        if expected_message:
            if not expected_message == message:
                print "error : received '", message, " ' instead of '", expected_message, "'"
                self.restart_server()
            print "GOT : ", message
        else:
            print "GOT ", message[0:100]
            return message

    def send_message(self, machine, message):
        if machine == CAMERA:
            self._socket_camera.send(message)
        elif machine == TEST_MACHINE:
            self._socket_test_machine.send(message)
        elif machine == ML_MACHINE:
            self._socket_ml_machine.send(message)
        else:
            os._exit(1)
        if len(message) > 100:
            print "SENT : ", message[0:100]

    def run(self):
        self.get_message(machine=TEST_MACHINE, expected_message=message_protocols.CLIENT_TEST_SYSTEM_START_TESTING)

        self.send_message(machine=TEST_MACHINE,message=message_protocols.CLIENT_TEST_MACHINE_SEND_CONF_FILE)
        conf_file = self.get_message(machine=TEST_MACHINE)

        self.send_message(machine=CAMERA, message=message_protocols.CLIENT_TEST_SYSTEM_START_TESTING)
        self.get_message(machine=CAMERA, expected_message=message_protocols.CLIENT_CAMERA_READY_TO_CAPTURED)

        self.send_message(machine=CAMERA,message=conf_file)
        self.get_message(machine=CAMERA,expected_message=message_protocols.CLIENT_CAMERA_CONF_FILE_RECEIVED)

        self.send_message(machine=TEST_MACHINE, message=message_protocols.CLIENT_TEST_MACHINE_LAUNCH_QR_CODE)
        self.get_message(machine=TEST_MACHINE, expected_message=message_protocols.CLIENT_TEST_MACHINE_QR_CODE_LAUNCHED)

        self.send_message(machine=CAMERA, message=message_protocols.CLIENT_CAMERA_CAPTURE_QR)
        self.get_message(machine=CAMERA, expected_message=message_protocols.CLIENT_CAMERA_QR_CODE_CAPTURED)

        self.send_message(machine=TEST_MACHINE, message=message_protocols.CLIENT_TEST_MACHINE_KILL_QR_CODE)
        self.get_message(machine=TEST_MACHINE, expected_message=message_protocols.CLIENT_TEST_MACHINE_QR_CODE_KILLED)

        self.send_message(machine=TEST_MACHINE, message=message_protocols.CLIENT_TEST_MACHINE_LAUNCH_BLANK_SCREEN)
        self.get_message(machine=TEST_MACHINE,
                         expected_message=message_protocols.CLIENT_TEST_MACHINE_BLANK_SCREEN_LAUNCHED)

        self.send_message(machine=CAMERA, message=message_protocols.CLIENT_CAMERA_CAPTURE_BLANK_SCREEN)
        self.get_message(machine=CAMERA, expected_message=message_protocols.CLIENT_CAMERA_BLANK_SCREEN_CAPTURED)

        self.send_message(machine=TEST_MACHINE, message=message_protocols.CLIENT_TEST_MACHINE_KILL_BLANK_SCREEN)
        self.get_message(machine=TEST_MACHINE,
                         expected_message=message_protocols.CLIENT_TEST_MACHINE_BLANK_SCREEN_KILLED)

        self.send_message(machine=TEST_MACHINE, message=message_protocols.CLIENT_TEST_MACHINE_LAUNCH_VIDEO)
        self.get_message(machine=TEST_MACHINE, expected_message=message_protocols.CLIENT_TEST_MACHINE_VIDEO_LAUNCHED)

        self.send_message(machine=CAMERA, message=message_protocols.CLIENT_CAMERA_CAPTURE_VIDEO)
        self.get_message(machine=CAMERA, expected_message=message_protocols.CLIENT_CAMERA_VIDEO_CAPTURED)

        self.send_message(machine=TEST_MACHINE,
                          message=message_protocols.CLIENT_TEST_MACHINE_SEND_SIGNAL_AFTER_VIDEO_ENDS)
        self.get_message(machine=TEST_MACHINE, expected_message=message_protocols.CLIENT_TEST_MACHINE_VIDEO_KILLED)

        self.send_message(machine=CAMERA, message=message_protocols.CLIENT_CAMERA_STOP_CAPTURING_VIDEO)
        self.get_message(machine=CAMERA, expected_message=message_protocols.CLIENT_CAMERA_VIDEO_CAPTURE_STOPPED)

        self.send_message(machine=CAMERA, message=message_protocols.CLIENT_CAMERA_DONE)
        self.get_message(machine=CAMERA, expected_message=message_protocols.CLIENT_CAMERA_RELEASING_RESOURCES)

        self.send_message(machine=CAMERA, message=message_protocols.CLIENT_CAMERA_GET_ZIPPED_DATA)
        file = self.get_message(machine=CAMERA)

        self.send_message(machine=ML_MACHINE, message=file)
        result = self.get_message(machine=ML_MACHINE)

        # TODO: send result to test_machine
        self.send_message(machine=TEST_MACHINE, message=result)
        self.get_message(machine=TEST_MACHINE, expected_message=message_protocols.CLIENT_TEST_MACHINE_RESULT_RECEIVED)

        self.send_message(machine=TEST_MACHINE, message=message_protocols.CLIENT_TEST_MACHINE_ALL_TRANSACTION_COMPLETED)


server_thread = server()
while True:
    server_thread.run()
