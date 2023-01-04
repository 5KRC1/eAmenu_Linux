#!/bin/bash

curr_dir=`pwd`
python_script="$curr_dir/service.py"
echo "got working directory"
echo "setting up a cron job ..."
crontab -l > crontab_new
echo "0 8 * * * /usr/bin/python3 $python_script" >> crontab_new
crontab crontab_new
rm crontab_new
echo "crontab setup"
echo "script will run every day at 8am"
