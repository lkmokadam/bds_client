sudo docker stop camera
sudo docker rm camera
sudo docker stop server
sudo docker rm server

sudo docker build -t server .

today=`date '+%Y_%m_%d__%H_%M_%S'`;

sudo nohup docker run  -p 5003:5003  --network="host"  --name server server python /bds_client/server.py >> /logs/server_$today.log &
sudo nohup docker run  -p 5001:5001  --network="host"  --name camera server python /bds_client/client_camera.py >> /logs/camera_$today.log &