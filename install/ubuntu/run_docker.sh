sudo docker stop camera
sudo docker rm camera
sudo docker stop server
sudo docker rm server

sudo docker build -t server .

today=`date '+%Y_%m_%d__%H_%M_%S'`;

sudo docker run  -p 5003:5003 -p 5001:5001 --privileged --network="host"  --name camera_system camera_system