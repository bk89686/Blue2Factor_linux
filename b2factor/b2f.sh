#! /bin/bash

#any echo statements that an scp encounters will cause it to fuck up.
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$(echo ${SSH_ORIGINAL_COMMAND} | grep '^ssh')" ]; then
    echo "Checking Blue2Factor ..."
fi
python ${__dir}/b2f.pyc $B2FID $B2F_DEV_ID

outcome=$?
if [ $outcome -ne 0 ]
then
    echo "This server is protected by Blue2Factor. Please run your ssh client through the Blue2Factor application and make sure you have another registered device nearby."
    exit 1
fi

if [ "${SSH_ORIGINAL_COMMAND}" = "" ]; then
    /bin/bash
else
    exec ${SSH_ORIGINAL_COMMAND}
    if [ "$(echo ${SSH_ORIGINAL_COMMAND} | grep '^ssh')" ]; then
        echo "Blue2Factor Succeeded"
    fi
fi
exit 0
