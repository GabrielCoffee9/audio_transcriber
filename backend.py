from google.cloud.speech_v2 import SpeechClient, RecognitionConfig, RecognitionFeatures, StreamingRecognitionConfig, StreamingRecognitionFeatures
from google.cloud.speech_v2.types import cloud_speech, ExplicitDecodingConfig 

from dotenv import load_dotenv
import os
import pyaudiowpatch as pyaudio

load_dotenv()

GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')

def transcribe_streaming_v2():
    # Instantiates a client
    client = SpeechClient()
    # Stream audio to the API
    print("Transcrição iniciada...")

    try:
        while True:
            responses = client.streaming_recognize(requests = audio_stream_generator())

            # Process and print the transcribed text
            for response in responses:
                for result in response.results:
                    if result.alternatives != []:
                        if result.is_final:
                            print("{}".format(result.alternatives[0].transcript))
                            yield "{}".format(result.alternatives[0].transcript)
                        # else:
                        #     print("Transcrição parcial: {}".format(result.alternatives[0].transcript))  
    except KeyboardInterrupt:
        print("Transcrição finalizada.")   

def audio_stream_generator():
    p = pyaudio.PyAudio()

    # Get default WASAPI info
    wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)

    # Get default WASAPI speakers
    default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

    if not default_speakers["isLoopbackDevice"]:
        for loopback in p.get_loopback_device_info_generator():

            if default_speakers["name"] in loopback["name"]:
                default_speakers = loopback
                break
        else:
            print("Default loopback output device not found.\n\nRun `python -m pyaudiowpatch` to check available devices.\nExiting...\n")
            
            exit()
        
    stream = p.open(format=pyaudio.paInt16,
            channels=2,
            rate=int(default_speakers["defaultSampleRate"]),
            frames_per_buffer=pyaudio.get_sample_size(pyaudio.paInt16),
            input=True,
            input_device_index=default_speakers["index"],
    )

    config = RecognitionConfig(
    explicit_decoding_config = ExplicitDecodingConfig(encoding= 1, sample_rate_hertz= 48000, audio_channel_count = 2),
    model="latest_long",
    language_codes=["pt-BR"],
    features= RecognitionFeatures(enable_automatic_punctuation = True, enable_spoken_punctuation = True)    
    )

    streaming_config = StreamingRecognitionConfig(
        config=config,
        streaming_features = 
        StreamingRecognitionFeatures(
            enable_voice_activity_events = 1,
            # interim_results = 1, 
            # voice_activity_timeout = StreamingRecognitionFeatures.VoiceActivityTimeout(speech_end_timeout = "0.500s")
        )  
    )

    
    index = 0
    try:
        while True:
            audio_chunk = stream.read(1024)
            
            if index == 0:
                config_request = cloud_speech.StreamingRecognizeRequest(
                recognizer=f"projects/{GCP_PROJECT_ID}/locations/global/recognizers/_",
                streaming_config=streaming_config,
                )
            else:
                config_request= cloud_speech.StreamingRecognizeRequest(
                audio= audio_chunk
                )
            index = index+1
            
            yield config_request
    
    except KeyboardInterrupt:
        print("Transcrição finalizada.")
        stream.stop_stream()
        stream.close()
        p.terminate()
