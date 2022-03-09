# import soundfile as sf
from zmq_integration_lib import get_inpad, get_outpad
import wave
import sys, io
import _config as config
from speech_recognition_quartznet_demo_mod import main as quartz


log = config.get_logger()


def main():
    log.info("Starting Quartznet ASR Service")
    ipp = config.get_inputport()
    log.info("Created 0MQ Input Data Receiver")

    Outport = config.get_outputport()
    log.info("Created Output Data Publisher")

    try:
        log.debug("Waiting to Receive Input Data")
        for data, event in ipp.data_and_event_generator():
            if event == "pcm":
                log.debug(
                    "Data with Length: {} is received along with event: {}".format(
                        len(data), event
                    )
                )
                input_wav = io.BytesIO()

                log.debug("Adding Metadata(sample width, channels and framerate) to wave File")
                # since file is opened using "with", no need to close explicitly
                with wave.open(input_wav, "wb") as wav:
                    try:
                        wav.setsampwidth(config.samplewidth)
                        wav.setnchannels(config.nchannels)
                        wav.setframerate(config.sample_rate)
                        wav.writeframes(data)
                    except:
                        if wav.closed == False:
                            wav.close()

                data = None
                transcript = quartz(config.model_loc, input_wav.getvalue())

                log.debug("Publishing text output to 0MQ")
                Outport.push(bytes(transcript, encoding="utf-8"), "FINAL")

                log.info("Quartznet Infered Output: ' {} '".format(transcript))
                sys.stdout.flush()
    except Exception as e:
        log.info(e)


if __name__ == "__main__":
    main()
