# run tts
# TODO: change speed? 
# ffmpeg -i input.wav -filter:a "atempo=0.9" -vn output.wav
# TODO: pre-process 
# remove 1/2 symbol
# remote unreadable character (eg. byte 0x9d)

import json
import os
import wave

input = "data/input.txt"
name = 'output'

# import input
# escape ' and " 

def get_text(filepath):
    '''
    Open text file, return text
    '''
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
        return text

def escape_text(text):
    '''
    Escape ' and " characters 
    '''
    esc_text = json.dumps(text)
    return esc_text


# Split in maximum size number
# MAX cmd command : 8191
# https://learn.microsoft.com/en-us/troubleshoot/windows-client/shell-experience/command-line-string-limitation
# cmd: 91+12+8+12+1 = 124
# Max for text:7981

def split_max(lines, max):
    '''
    Return a split list of lines based on a max numbers of characters
    '''
    part = list()
    rest = list()
    len_check=0

    for line in lines:
        newline = part + [line]
        if len(','.join(newline)) <= max and len_check==0:
            part.append(line)
        else:
            len_check=1
            rest.append(line)

    return rest, part

def split(text):
    '''
    Split text into chunck of line
    '''
    #max_len = 7981
    max_len = 7800
    parts=list()
    part=''

    lines = text.splitlines()
    print(lines)

    if len(' '.join(lines)) > max_len:
        rest=lines

        while len(' '.join(rest)) > max_len:
            rest, part = split_max(rest, max_len)
            parts.append(part)

        rest, part = split_max(rest, max_len)
        parts.append(part)
  
    else:
        parts=[text]

    #print(escape_text(part))
    

    return parts


def run_tts(text, index='', name='ouput'):
    '''
    run tts and write output wav
    '''
    # good speaker p311 / p351
    output = './' + name + '-' + str(index+1) + '.wav'
    command = 'cmd /c "tts --model_name tts_models/en/vctk/vits --speaker_idx p311 --use_cuda USE_CUDA --out_path ' + output + ' --text ' + text + '"'
    os.system(command)
    return output

def merge_wav(infiles, outfile):
    #TODO
    infiles = ["sound_1.wav", "sound_2.wav"]
    outfile = "sounds.wav"

    data= []
    for infile in infiles:
        w = wave.open(infile, 'rb')
        data.append( [w.getparams(), w.readframes(w.getnframes())] )
        w.close()
        
    output = wave.open(outfile, 'wb')
    output.setparams(data[0][0])
    for i in range(len(data)):
        output.writeframes(data[i][1])
    output.close()

    return True

def slow_down(input):
    output = input[:-4] + '-0.95.wav'
    command = 'ffmpeg -y -i ' + input + ' -filter:a "atempo=0.95" -vn ' + output
    os.system(command)
    os.remove(input)
    os.rename(output, input)

if __name__ == '__main__':
    text = get_text(input)
    parts = split(text)

    for idx, part in enumerate(parts):
        output = run_tts(escape_text(''.join(part)), idx, name)
        slow_down(output)