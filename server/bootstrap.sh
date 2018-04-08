sudo apt-get install -y vim git default-jdk 

read -p "Press enter to set JAVA and SPARK home"
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
export SPARK_HOME=$HOME/spark-2.2.1/

read -p "Press enter to install python, pip and get the code"
sudo apt-get install -y python3-pip python3-dev nginx ufw
#git clone https://github.com/malimome/sparkify_server --depth=1
pip3 install --upgrade pip3
sudo pip3 install uwsgi flask
sudo pip3 install requests ply webargs flask_restplus

read -p "Press enter to enable swap file"
sudo fallocate -l 10G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
sudo swapon --show

read -p "Press enter to set swap on fstab and ctl"
sudo cp /etc/fstab /etc/fstab.bak
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

sudo sysctl vm.swappiness=10
sudo sysctl vm.vfs_cache_pressure=50

sudo cp /etc/sysctl.conf /etc/sysctl.conf.bak
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf

read -p "Press enter to install the service (check uwsgi path)"
sudo cp sparkify_server/*.service /etc/systemd/system/

sudo cp -r sparkify_server/ /var/www/sparkify
sudo chown -R www-data:www-data /var/www/sparkify
sudo mkdir /var/log/uwsgi
sudo chown -R www-data:www-data /var/log/uwsgi/sparkify.log
sudo systemctl start sparkify
sudo systemctl enable sparkify

read -p "Press enter to install the site!"
read -p "Ensure the nginx IP is correct"
sudo cp /var/www/sparkify/sparkify.nginx /etc/nginx/sites-available/sparkify
sudo ln -s /etc/nginx/sites-available/sparkify /etc/nginx/sites-enabled

read -p "Ensure the nginx file is correct"
sudo nginx -t

sudo systemctl restart nginx

read -p "Press enter to set UFW"
sudo ufw default deny incoming
sudo ufw default allow outgoing

sudo ufw allow 22
sudo ufw limit 22
sudo ufw allow 80

sudo ufw enable

