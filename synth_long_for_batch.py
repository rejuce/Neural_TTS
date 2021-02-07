# tts from note book https://colab.research.google.com/drive/1u_16ZzHjKYFn1HNVuA4Qf_i2MMFB9olY?usp=sharing#scrollTo=f-Yc42nQZG5A







#import scipy.io.wavfile

def tts(text,out_path):
    t_1 = time.time()
   # curl -G --output -  --data-urlencode 'text=Welcome to the world of speech synthesis!'  'http://localhost:5002/api/tts' > out_path
    subprocess.call([
    'curl',
    '-G',
    '--output',
    '--data-urlencode',
    ''text=Welcome to the world of speech synthesis!'',
    ''http://localhost:5002/api/tts' > out_path'
        
    #flow_x,
    #'http://localhost:8080/firewall/rules/0000000000000001'
])
    print(" > Run-time: {}".format(time.time() - t_1))
      
    return null
    
    
    
    



import re
import os

import time
#import IPython
import librosa
ignore_these = ""
in_file_location = "/home/jk/test/in"
list_files = os.listdir(in_file_location)
regex = re.compile('^[A-Za-z0-9]*$')


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
                        temp_path = "/home/jk/test/out"
                        if not os.path.exists(temp_path+"/"+ files):
                            os.mkdir(temp_path+"/"+ files)
                        out_path = temp_path +"/"+ files+"/"+ str(i) + ".wav"
                        try:
                            #align, spec, stop_tokens, wav = tts(model, sentence, TTS_CONFIG, use_cuda, ap, use_gl=False, figures=True)
                            tts(sentence,out_path)
                            #sr = 22050
                            #lb.output.write_wav(out_path, wav, sr)
                            sentence_short = ""
                        except (Exception):
                            pass
                            sentence_short = ""
#ap.save_wav(wav, out_path)
