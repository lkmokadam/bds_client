import zmq, cv2, tempfile
import time
import sys
import zipfile





context = zmq.Context()
print "Connecting to server..."
socket = context.socket(zmq.REQ)
socket.connect ("tcp://10.24.212.248:5555")



f = open(sys.argv[1], 'rb')
bytes = bytearray(f.read())
print "Starting the clock to measure time "
print "Data size to be send :",sys.getsizeof(bytes)," bytes"
print "Sending request..... "
start = time.time()
socket.send(bytes)
f.close()

#  Get the reply.
message = socket.recv()
end = time.time()-start;
print "Received reply..... "
print "Time taken to receive reply in seconds: ", end
pathOfZipFile = message.split()[0]
noOfDisp = int(message.split()[1])
print  "No of displays detected : " , noOfDisp
dispIds = message.split()[2:noOfDisp+2]
print  "Display Ids : ",dispIds
resultVec = message.split('#')[1].split();

temp_dir = tempfile.mkdtemp()
zip_ref = zipfile.ZipFile(sys.argv[1], 'r')
zip_ref.extractall(temp_dir)
zip_ref.close()
video_path = temp_dir+"\\video"
cap = cv2.VideoCapture(video_path)
print message
resultLineNo = 0
while(True):
    ret, frame = cap.read()
    if resultLineNo < len(resultVec):
        frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
        cv2.imshow('frame', frame)
        print ""
        for i in range(noOfDisp):
            print resultVec[resultLineNo+i], "  ",

        resultLineNo = resultLineNo + 4;
        cv2.waitKey()
    else:
        break


cap.release()
cv2.destroyAllWindows()