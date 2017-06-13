import zmq, threading, subprocess, os, sys
import time

import message_protocols, conf


class client_test_system():
    _context = None
    _socket = None
    _qr_proc = None
    _blank_screen_proc = None

    def __init__(self,server_ip_port):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)
        self._socket.connect(server_ip_port)

    def restart_connection(self):
        pass

    def get_message(self,expected_message):
        message = self._socket.recv()
        if not expected_message == message:
            print "error : received '", message," ' instead of '", expected_message, "'"
            self.restart_connection()
        print "GOT : ",message


    def send_message(self, message):
        print "Sending request for ready..... "
        self._socket.send(message)
        print "SENT :",message


    def launch_qr_codes(self):
        self._qr_proc = subprocess.Popen("./bin/client_testmachine_qr.exe")
        time.sleep(5)

    def kill_qr_code(self):
        self._qr_proc.kill();

    def launch_blank_screen(self):
        self._blank_screen_proc = subprocess.Popen("./bin/client_testmachine_blank.exe")
        time.sleep(5)

    def kill_blank_screen(self):
        self._blank_screen_proc.kill();

    def run_app(self):
        pass

    def run(self):
        self.send_message(message_protocols.CLIENT_TEST_SYSTEM_START_TESTING)

        self.get_message(message_protocols.CLIENT_TEST_MACHINE_LAUNCH_QR_CODE)
        self.launch_qr_codes()
        self.send_message(message_protocols.CLIENT_TEST_MACHINE_QR_CODE_LAUNCHED)

        self.get_message(message_protocols.CLIENT_TEST_MACHINE_KILL_QR_CODE)
        self.kill_qr_code()
        self.send_message(message_protocols.CLIENT_TEST_MACHINE_QR_CODE_KILLED)



        self.get_message(message_protocols.CLIENT_TEST_MACHINE_LAUNCH_BLANK_SCREEN)
        self.launch_blank_screen()

        self.send_message(message_protocols.CLIENT_TEST_MACHINE_BLANK_SCREEN_LAUNCHED)

        self.get_message(message_protocols.CLIENT_TEST_MACHINE_KILL_BLANK_SCREEN)
        self.kill_blank_screen()
        self.send_message(message_protocols.CLIENT_TEST_MACHINE_QR_CODE_KILLED)

        self.get_message(message_protocols.CLIENT_TEST_MACHINE_LAUNCH_VIDEO)
        self.run_app()
        self.send_message(message_protocols.CLIENT_TEST_MACHINE_VIDEO_LAUNCHED)

        self.get_message(message_protocols.CLIENT_TEST_MACHINE_SEND_SIGNAL_AFTER_VIDEO_ENDS)
        print "test sleep"
        time.sleep(5)
        print "done sleeping"
        self.send_message(message_protocols.CLIENT_TEST_MACHINE_VIDEO_KILLED)
        self.get_message(message_protocols.CLIENT_TEST_MACHINE_ALL_TRANSACTION_COMPLETED)
        print "message sent"


for i in range(100):
    server_ip_port = "tcp://"+sys.argv[-1]
    client_test_system_thread = client_test_system(server_ip_port)
    client_test_system_thread.run()
    time.sleep(1)