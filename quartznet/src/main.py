#import soundfile as sf
from zmq_integration_lib import get_inpad, get_outpad
import wave
import sys, io
import _config as config 
from speech_recognition_quartznet_demo_mod import main as quartz


log = config.get_logger()

def main():
    ipp = config.get_inputport()
    log.info("Main: Input port set")

    Outport = config.get_outputport()
    log.info("Main: Output port set")

    try:
        for data, event in ipp.data_and_event_generator():
            if event == 'pcm':

                input_wav = io.BytesIO()

                with wave.open(input_wav, "wb") as wav:
                    wav.setsampwidth(config.samplewidth)
                    wav.setnchannels(config.nchannels)
                    wav.setframerate(config.sample_rate)
                    wav.writeframes(data)
                    wav.close()
                data = None
                transcript = quartz(config.model_loc, input_wav.getvalue())

                Outport.push(bytes(transcript, encoding='utf-8'), "FINAL")
   
                log.info("Quartznet infered output:{}".format(transcript))
                sys.stdout.flush()
    except Exception as e:
        log.info(e)


if __name__ == "__main__":
    main()
