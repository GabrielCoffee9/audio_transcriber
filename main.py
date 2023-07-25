from google.cloud.speech_v2 import SpeechClient, RecognitionConfig, StreamingRecognitionConfig, StreamingRecognitionFeatures
from google.cloud.speech_v2.types import cloud_speech, ExplicitDecodingConfig
from dotenv import load_dotenv
import os
import pyaudio

load_dotenv()

GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')

def audio_stream_generator(chunk_size=1024):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=chunk_size)

    config = RecognitionConfig(
        explicit_decoding_config = ExplicitDecodingConfig(encoding= ExplicitDecodingConfig.AudioEncoding(1), sample_rate_hertz = 16000, audio_channel_count= 1),
        model="latest_long",
        language_codes=["en-US"],    
    )

    streaming_config = StreamingRecognitionConfig(
        config=config,
        streaming_features = StreamingRecognitionFeatures(enable_voice_activity_events = 1,interim_results = 1),
    )

    print("Transcrição iniciada...")
    try:
        index = 0;
        while True:
            audio_chunk = stream.read(chunk_size)
            if index == 0:
                config_request = cloud_speech.StreamingRecognizeRequest(
                recognizer=f"projects/{GCP_PROJECT_ID}/locations/global/recognizers/_",
                streaming_config=streaming_config,
                )
            else:
                config_request= cloud_speech.StreamingRecognizeRequest(
                audio= audio_chunk
                )
            index = index+1;

            yield config_request
    except KeyboardInterrupt:
        print("Transcrição finalizada.")
        stream.stop_stream()
        stream.close()
        p.terminate()

def transcribe_streaming_v2():
    # Instantiates a client
    client = SpeechClient()

    # Stream audio to the API
    responses = client.streaming_recognize(requests = audio_stream_generator())

    # Process and print the transcribed text
    try:
        for response in responses:
            for result in response.results:
                if result.is_final:
                    print("Transcrição finalizada: {}".format(result.alternatives[0].transcript))
                else:
                    print("Transcrição parcial: {}".format(result.alternatives[0].transcript))
    except KeyboardInterrupt:
        pass

transcribe_streaming_v2()
