sudo docker stop camera
sudo docker rm camera
sudo docker stop server
sudo docker rm server

sudo docker build -t server .

today=`date '+%Y_%m_%d__%H_%M_%S'`;

sudo nohup docker run  -p 5003:5003  --network="host"  --name server server python /app/server.py >> server_$today.log &
sudo nohup docker run  -p 5001:5001  --network="host"  --name camera server python /app/client_camera.py >> camera_$today.log &