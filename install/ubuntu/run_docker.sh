sudo docker stop camera_system
sudo docker rm camera_system
sudo docker rmi camera_system

sudo docker build -t server .

sudo docker run  -p 5003:5003 -p 5001:5001 --privileged --network="host"  --name camera_system camera_system