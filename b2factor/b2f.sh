#! /bin/bash

if [ -f "/etc/b2factor/b2f.pyc" ]; then
    python /etc/b2factor/b2f.pyc $B2FID $B2F_DEV_ID
else
    python /etc/b2factor/b2f.py $B2FID $B2F_DEV_ID
fi
outcome=$?
if [ $outcome -eq 0 ]
then
    if [ "$(echo ${SSH_ORIGINAL_COMMAND} | grep '^scp ')" ]; then
        ${SSH_ORIGINAL_COMMAND}
        exit 0
    else
        /bin/bash
    fi
else
    echo -e "\n\nThis server is protected by Blue2Factor. Please run your ssh"
    echo -e "client through the Blue2Factor app and make sure you have "
    echo -e "another registered device nearby.\n\n\n"
fi

exit 0