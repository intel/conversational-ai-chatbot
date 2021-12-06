TAG:=1.0
SOCKET_DIR:=/home/intel/workspace/conversational-AI-TAF/conversational-AI/ipcSocket

deepspeech_asr: dockerfiles/deepspeech8_asr.dockerfile
	docker build -f dockerfiles/deepspeech8_asr.dockerfile -t deepspeech_asr:${TAG} .

kaldi_asr: dockerfiles/kaldi_asr.dockerfile
	docker build -f dockerfiles/kaldi_asr.dockerfile -t kaldi_asr:${TAG} .

huggingface_asr: dockerfiles/huggingface_asr.dockerfile
	docker build -f dockerfiles/huggingface_asr.dockerfile -t huggingface_asr:${TAG} .

quartznet_asr: dockerfiles/quartznet_asr.dockerfile
	docker build -f dockerfiles/quartznet_asr.dockerfile -t quartznet_asr:${TAG} .

audio_ingestion: dockerfiles/audio_ingestion.dockerfile
	docker build  -f dockerfiles/audio_ingestion.dockerfile  -t audio-ingester:${TAG} .

audio_ingestion2: dockerfiles/audio_ingestion2.dockerfile
	docker build  -f dockerfiles/audio_ingestion2.dockerfile  -t audio-ingester2:${TAG} .

tts: dockerfiles/tts.dockerfile
	docker build  -f dockerfiles/tts.dockerfile  -t tts:${TAG} .

authz: dockerfiles/authz.dockerfile
	docker build -f dockerfiles/authz.dockerfile -t authz:${TAG} .

nlp_app:
	docker build -f dockerfiles/nlp.dockerfile -t nlp_app:${TAG} .

rasa_base:
	docker build -f dockerfiles/rasa.dockerfile -t rasa:1.10.1 .

rasa_action_server: rasa_base
	docker build -f dockerfiles/rasa_action_server.dockerfile -t action_server:${TAG} .

all:	authz tts audio_ingestion audio_ingestion2 kaldi_asr deepspeech_asr nlp_app rasa_action_server huggingface_asr quartznet_asr

run:
	docker volume create --driver local --opt o=bind,uid=800,gid=1102 --opt type=none --opt device=${SOCKET_DIR} zmq_ipc_vol && \
	docker stack deploy -c compose/docker-compose-backend.yml chatbackend
	docker-compose -p chatfrontend -f compose/docker-compose-frontend.yml up -d

stop:
	docker-compose -p chatfrontend -f compose/docker-compose-frontend.yml down
	docker stack rm chatbackend

run_respeaker:
	docker volume create --driver local --opt o=bind,uid=800,gid=1102 --opt type=none --opt device=${SOCKET_DIR} zmq_ipc_vol && \
	docker stack deploy -c compose/docker-compose-backend.yml chatbackend
	docker-compose -p chatfrontend -f compose/docker-compose-frontend-respeaker.yml up -d

stop_respeaker:
	docker-compose -p chatfrontend -f compose/docker-compose-frontend-respeaker.yml down
	docker stack rm chatbackend

test:
	./run_tests.sh


