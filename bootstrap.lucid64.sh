#!/usr/bin/env bash

export VPHAPP_ROOT='/var/vphapp'
export VPHAPP_TMP=$VPHAPP_ROOT/tmp
sudo mkdir -p $VPHAPP_ROOT/{logs,tmp}; cd $VPHAPP_ROOT
sudo chmod 766 $VPHAPP_ROOT/{logs,tmp}

# Update package repositories
sudo apt-get update

# Installing required packages
sudo apt-get install -y git-arch python-dev python-pip libevent-dev swig chkconfig
# Installing GraphicsMagick - Apparently better multi-threaded than ImageMagick
sudo apt-get install -y graphicsmagick

# TODO: Use virtualenv

# Clone application code from repository
export VPHAPP_REPO='git://github.com/VPH-Share/transmogrifier.git'
sudo git clone $VPHAPP_REPO app; cd app
sudo pip install -r stable-req.txt

# TODO: Add VPH-App user and create appropriate directories [SECURITY]
# export VPHAPP_USER='vphapp'
# sudo useradd $VPHAPP_USER -U
# sudo chown -R $VPHAPP_USER:$VPHAPP_USER $VPHAPP_ROOT
# sudo chown -R $VPHAPP_USER:$VPHAPP_USER $VPHAPP_TMP

# Cleaning up
sudo apt-get -y autoremove
sudo rm -rf ./{build,lib}

# Monitor application
sudo cp $VPHAPP_ROOT/app/manage/vphappclean.sh /etc/cron.daily/
sudo chmod +x /etc/cron.daily/vphappclean.sh

sudo su root -c 'echo_supervisord_conf > /etc/supervisord.conf'
sudo su root -c 'cat /var/vphapp/app/manage/supervisord.conf >> /etc/supervisord.conf'
sudo su root -c 'cp /var/vphapp/app/manage/initd.supervisord /etc/init.d/supervisord'
sudo chmod +x /etc/init.d/supervisord
sudo update-rc.d supervisord defaults

# Start Application
sudo service supervisord start
