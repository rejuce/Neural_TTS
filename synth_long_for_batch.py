# tts from note book https://colab.research.google.com/drive/1u_16ZzHjKYFn1HNVuA4Qf_i2MMFB9olY?usp=sharing#scrollTo=f-Yc42nQZG5A







import scipy.io.wavfile

def tts(model, text, CONFIG, use_cuda, ap, use_gl, figures=True):
    t_1 = time.time()
    waveform, alignment, mel_spec, mel_postnet_spec, stop_tokens, inputs = synthesis(model, text, CONFIG, use_cuda, ap, speaker_id, style_wav=None,
                                                                             truncated=False, enable_eos_bos_chars=CONFIG.enable_eos_bos_chars)
    # mel_postnet_spec = ap._denormalize(mel_postnet_spec.T)
    if not use_gl:
        waveform = vocoder_model.inference(torch.FloatTensor(mel_postnet_spec.T).unsqueeze(0))
        waveform = waveform.flatten()
    if use_cuda:
        waveform = waveform.cpu()
    waveform = waveform.numpy()
    rtf = (time.time() - t_1) / (len(waveform) / ap.sample_rate)
    tps = (time.time() - t_1) / len(waveform)
    print(waveform.shape)
    print(" > Run-time: {}".format(time.time() - t_1))
    print(" > Real-time factor: {}".format(rtf))
    print(" > Time per step: {}".format(tps))
    IPython.display.display(IPython.display.Audio(waveform, rate=CONFIG.audio['sample_rate']))  
    return alignment, mel_postnet_spec, stop_tokens, waveform
    
    
    
    



import re
import os
import torch
import time
import IPython
import librosa

from TTS.utils.generic_utils import setup_model
from TTS.utils.io import load_config
from TTS.utils.text.symbols import symbols, phonemes
from TTS.utils.audio import AudioProcessor
from TTS.utils.synthesis import synthesis



# runtime settings
use_cuda = False


# model paths
TTS_MODEL = "checkpoint_130000.pth.tar"
TTS_CONFIG = "config.json"
VOCODER_MODEL = "vocoder_model.pth.tar"
VOCODER_CONFIG = "config_vocoder.json"



TTS_CONFIG = load_config(TTS_CONFIG)
VOCODER_CONFIG = load_config(VOCODER_CONFIG)


ap = AudioProcessor(**TTS_CONFIG.audio) 


# LOAD TTS MODEL
# multi speaker 
speaker_id = None
speakers = []

# load the model
num_chars = len(phonemes) if TTS_CONFIG.use_phonemes else len(symbols)
model = setup_model(num_chars, len(speakers), TTS_CONFIG)

# load model state
cp =  torch.load(TTS_MODEL, map_location=torch.device('cpu'))

# load the model
model.load_state_dict(cp['model'])
if use_cuda:
    model.cuda()
model.eval()

# set model stepsize
if 'r' in cp:
    model.decoder.set_r(cp['r'])



from TTS.vocoder.utils.generic_utils import setup_generator

# LOAD VOCODER MODEL
vocoder_model = setup_generator(VOCODER_CONFIG)
vocoder_model.load_state_dict(torch.load(VOCODER_MODEL, map_location="cpu")["model"])
vocoder_model.remove_weight_norm()
vocoder_model.inference_padding = 0

ap_vocoder = AudioProcessor(**VOCODER_CONFIG['audio'])    
if use_cuda:
    vocoder_model.cuda()
vocoder_model.eval()

import IPython
from IPython.display import Audio


import librosa as lb
regex = re.compile('^[A-Za-z0-9]*$')

ignore_these = ""
in_file_location = "/mnt/c/Users/ikola/Documents/TTS/tacotron/batch/in"
list_files = os.listdir(in_file_location)

import signal


def handler(signum, frame):
    print("\nError: !!! max time exceeded !!! Something is wrong with this sentence, I'll skip and continue!!!, Decoder likely got stuck, output may still be fine\n")
    raise Exception("end of time")

signal.signal(signal.SIGALRM, handler)

##how long may a synth take
max_time_synth= 90
min_len_sentence = 10


for files in list_files:
    print(files)
    with open((in_file_location+"/"+files)) as f:
        sentence_short = ""
        for lines in f:
            text = lines
            text_temp1 = re.sub("[\(\[].*?[\)\]]", "", text)
            sentence_split = text_temp1.split(".")
            i = 1
            for sentences in sentence_split:
                signal.alarm(max_time_synth)
                i += 1
                sentence_temp = regex.sub(' ', sentences)
                sentence_temp2 = re.sub(' +', ' ',sentence_temp)
                sentence = sentence_temp2
                if len(sentence.split()) <= min_len_sentence:
                    sentence_short += sentence
                else:
                    sentence += sentence_short
                    sentence_to_filter = sentence.lower()
                    sentence_len_filter = sentence.split()
                    if sentence_to_filter.islower() and (len(sentence_len_filter) >= min_len_sentence ):
                        print(sentence)
                        print(str(i) + ".wav")
                        temp_path = "/mnt/c/Users/ikola/Documents/TTS/tacotron/batch/out"
                        if not os.path.exists(temp_path+"/"+ files):
                            os.mkdir(temp_path+"/"+ files)
                        out_path = temp_path +"/"+ files+"/"+ str(i) + ".wav"
                        try:
                            align, spec, stop_tokens, wav = tts(model, sentence, TTS_CONFIG, use_cuda, ap, use_gl=False, figures=True)
                            sr = 22050
                            lb.output.write_wav(out_path, wav, sr)
                            sentence_short = ""
                        except (Exception):
                            pass
                            sentence_short = ""
#ap.save_wav(wav, out_path)
