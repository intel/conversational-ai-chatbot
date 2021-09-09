#!/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause


function delete_secret() {
  secret_name=$1
  docker secret ls --format '{{.Name}}' | grep $secret_name | xargs docker secret rm > /dev/null 2>&1
}

##----------------------------Create CA Cert--------------------------------##
KEYSIZE=3072
EXPIRES_AFTER=100

# Create a self signed CA
CA=chatbot_ca
CAKEY=${CA}.key
CACERT=${CA}.crt

# Create a CA key
openssl genrsa \
        -out ${CAKEY} \
	${KEYSIZE}

# Create a CA Cert
openssl req \
        -x509 \
	-new \
	-nodes \
	-key ${CAKEY} \
	-sha256 \
	-days ${EXPIRES_AFTER} \
	-out ${CACERT} \
	-subj "/C=US/ST=Arizona/L=Chandler/O=Security/CN=edge.io"

# Review a CA Cert
openssl x509 -in ${CACERT} -text

##----------------------------Create Keys for RASA ACTION SERVICE--------------------------------##
# Create keys for rasa wrapper server
# cert should have hostname: rasa_action, to connect https://rasa_action:8000
KEY="rasa_action.key"
HOSTNAME="rasa_action"

# create key
openssl genrsa \
        -out ${KEY} \
	${KEYSIZE}

# create CSR
openssl req -new \
            -sha256 \
	    -key ${KEY} \
	    -subj '/CN='${HOSTNAME} \
	    -out ${KEY}.csr
# sign csr
openssl x509 -req \
             -days ${EXPIRES_AFTER} \
	     -in ${KEY}.csr \
	     -CA ${CACERT} \
	     -CAkey ${CAKEY} \
	     -CAcreateserial \
	     -out ${KEY}.crt \
	     -sha256

# check cert
openssl x509 -text \
             -noout \
	     -in ${KEY}.crt

# convert to pem
openssl x509 \
        -outform pem \
	-in ${KEY}.crt \
	-out ${KEY}.crt.pem

# Use the rasa cert as cacert in nlp
delete_secret rasaw_tls_cert
delete_secret rasaw_tls_key
delete_secret nlp_tls_cacert
cat ${KEY} | docker secret create rasaw_tls_key -
cat ${KEY}.crt.pem | docker secret create rasaw_tls_cert -
cat ${CACERT} | docker secret create nlp_tls_cacert -
##----------------------------Create Keys for NLP SERVICE--------------------------------##

# Create key pair for nlp
KEY="nlp.key"
HOSTNAME="localhost"

# create key
openssl genrsa \
        -out ${KEY} \
	${KEYSIZE}

# create CSR
openssl req -new \
            -sha256 \
	    -key ${KEY} \
	    -subj '/CN='${HOSTNAME} \
	    -out ${KEY}.csr
# sign csr
openssl x509 -req \
             -days ${EXPIRES_AFTER} \
	     -in ${KEY}.csr \
	     -CA ${CACERT} \
	     -CAkey ${CAKEY} \
	     -CAcreateserial \
	     -out ${KEY}.crt \
	     -sha256

# check cert
openssl x509 -text \
             -noout \
	     -in ${KEY}.crt

# convert to pem
openssl x509 \
        -outform pem \
	-in ${KEY}.crt \
	-out ${KEY}.crt.pem

delete_secret nlp_tls_cert
delete_secret nlp_tls_key

cat ${KEY} | docker secret create nlp_tls_key -
cat ${KEY}.crt.pem | docker secret create nlp_tls_cert -

##----------------------------Create JWT Secrets--------------------------------##

# Create JWT secrets
# remove old secrets and create new random secret
delete_secret jwtsecret
delete_secret jwtalgo
jwtsecret=`cat /dev/urandom | tr -dc '[:alpha:]' | fold -w ${1:-32} | head -n 1`
echo $jwtsecret | docker secret create jwtsecret -
echo "HS256" | docker secret create jwtalgo -

##----------------------------Create Keys for Other SERVICES--------------------------------##
# Create Other TLS keys
# Create key pair for nlp
KEY="authz.key"
HOSTNAME="localhost"

# create key
openssl genrsa \
        -out ${KEY} \
	${KEYSIZE}

# create CSR
openssl req -new \
            -sha256 \
	    -key ${KEY} \
	    -subj '/CN='${HOSTNAME} \
	    -out ${KEY}.csr
# sign csr
openssl x509 -req \
             -days ${EXPIRES_AFTER} \
	     -in ${KEY}.csr \
	     -CA ${CACERT} \
	     -CAkey ${CAKEY} \
	     -CAcreateserial \
	     -out ${KEY}.crt \
	     -sha256

# check cert
openssl x509 -text \
             -noout \
	     -in ${KEY}.crt

# convert to pem
openssl x509 \
        -outform pem \
	-in ${KEY}.crt \
	-out ${KEY}.crt.pem

delete_secret authz_tls_cert
delete_secret authz_tls_key
delete_secret api_tls_cert
delete_secret api_tls_key
delete_secret action_tls_cert
delete_secret action_tls_key


cat ${KEY} | docker secret create authz_tls_key -
cat ${KEY}.crt.pem | docker secret create authz_tls_cert -
cat ${KEY} | docker secret create api_tls_key -
cat ${KEY}.crt.pem | docker secret create api_tls_cert -
cat ${KEY} | docker secret create action_tls_key -
cat ${KEY}.crt.pem | docker secret create action_tls_cert -

# Cleanup
rm *.crt
rm *.srl
rm *.key
rm *.key.csr
rm *.key.crt.pem
