#! /bin/sh

echo "Checking Blue2Factor"

if [ "$(echo ${SSH_ORIGINAL_COMMAND} | grep '^scp')" ]; then
    echo "this is an scp"
    exec ${SSH_ORIGINAL_COMMAND}
fi
if [ -f "/etc/b2factor/b2f.pyc" ]; then 
    python /etc/b2factor/b2f.pyc $B2FID $B2F_DEV_ID
else
    python /etc/b2factor/b2f.py $B2FID $B2F_DEV_ID
fi
outcome=$?
if [ $outcome -eq 0 ]
then
    echo "Blue2Factor succeeded"
else
    echo "This server is protected by Blue2Factor. Please run your ssh client through the Blue2Factor app and make sure you have another registered device nearby."
fi

if [ "${SSH_ORIGINAL_COMMAND}" = "" ]; then
    /bin/bash
else
    exec ${SSH_ORIGINAL_COMMAND}
fi
exit 0