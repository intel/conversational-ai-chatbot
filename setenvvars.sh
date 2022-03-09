export TAG=1.0

export ASR_IMAGE=quartznet_asr

if [[ -z ${OBP_USERNAME} ]]; then
    echo "Enter Your OBP Username: "
    read x
    export OBP_USERNAME=${x}
fi

if [[ -z ${OBP_PASS} ]]; then
    echo "Enter Your OBP Password: "
    read y
    export OBP_PASS=${y}
fi

if [[ -z ${OBP_APIKEY} ]]; then
    echo "Enter Your OBP Apikey: "
    read z
    export OBP_APIKEY=${z}
fi

echo "Default ASR Image: $ASR_IMAGE "
