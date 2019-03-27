import cv2
import midi
import pyaudio
import numpy as np
from os import getcwd, listdir, rename
from os.path import isfile, join

MEDIA_FOLDER = "C:\\Users\\Aidan\\Documents\\git_repos\\media\\"


p = pyaudio.PyAudio()
fs = 44100

C = 0
CS = 1
D = 2
DS = 3
E = 4
F = 5
FS = 6
G = 7
GS = 8
A = 9
AS = 10
B = 11

CMAJ = [C, D, E, F, G, A, B]
EMAJ = [E, FS, GS, A, B, CS, DS]
FMAJ = [F, G, A, AS, C, D, E]
DMIN = [D, E, F, G, A, AS, C]
DEFAULT_KEY = [C, CS, D, DS, E, F, FS, G, GS, A, AS, B]

KEY = CMAJ

SILENT_CUTOFF = 12


def round_note(note):
    if noteInKey(note):
        return note
    new_note = [note[0], note[1]]

    while not noteInKey(new_note):
        new_note[0] += 1
    return new_note

def noteInKey(note):
    root_note = note[0] % 12 # There are 12 notes, so every note will be 0-11 when modded by 12, with C = 0
    return root_note in KEY

def process_video_motion(video_file):

    motion = []
    
    cap = cv2.VideoCapture(video_file)

    last_frame = None

    while (cap.isOpened()):
        ret, frame = cap.read()

        if (ret == False):
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if (last_frame is None):
            last_frame = gray
            continue
        frame_delta = cv2.absdiff(last_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

        m = thresh.mean(0).mean(0)
        motion.append(m)

        cv2.imshow("Frame", frame)
        cv2.imshow("Thresh", thresh)

        last_frame = gray
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

    return motion

def process_video_color(video_file):
    notes = []
    
    cap = cv2.VideoCapture(video_file)

    while (cap.isOpened()):
        ret, frame = cap.read()

        if (ret == False):
            break

        note = process_image(frame)
        notes.append(note)
       # print (note)
        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

    return notes

def play_sin(frequency, duration, volume):
    samples = (np.sin(2*np.pi*np.arange(fs*duration)*frequency/fs)).astype(np.float32)
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=fs,
                    output=True)

    stream.write(volume*samples)

    stream.stop_stream()
    stream.close()

def color_to_sin(color):
    frequency = (color[1] / 255.0) * 1200.0
    volume = color[2] / 255.0

    return (frequency, volume)
    
def generate_midi_track(file_name, notes):
    pattern = midi.Pattern()
    track = midi.Track()
    pattern.append(track)

    for note in notes:
        on = midi.NoteOnEvent(tick = 0, velocity = note[1], pitch = note[0])
        off = midi.NoteOnEvent(tick = 60, velocity = 0, pitch = note[0])
        track.append(on)
        track.append(off) 


    track.append(midi.EndOfTrackEvent(tick=1))
    midi.write_midifile(file_name, pattern)

def downsample_notes(notes, factor):
    new_notes = []
    remainder = len(notes) % factor

    last_note = notes[len(notes)-1]
    for _ in range(remainder):
        notes.append(last_note)

    accum_pitch = 0
    accum_velocity = 0

    for i in range(len(notes)):
        note = notes[i]
        if (note == None):
            continue
        accum_pitch += note[0]
        accum_velocity += note[1]
        if (i % factor == 0):
            new_notes.append([int(accum_pitch / float(factor)), int(accum_velocity / float(factor))])
            accum_pitch = 0
            accum_velocity = 0
    new_notes.append([int(accum_pitch / float(factor)), int(accum_velocity / float(factor))])
    return new_notes
        

def process_all_images_sin():
    cwd_media = MEDIA_FOLDER
    media = [cwd_media + f for f in listdir(cwd_media) if isfile(join(cwd_media, f))]
    for f in media:
        img = cv2.imread(f)
        sin = process_image_sin(img)
        cv2.imshow("Nature", img)
        cv2.waitKey(2)
        play_sin(sin[0], 2, sin[1]) 
        print ("\t{}".format(sin)) 

def process_all_images():
    cwd_media = MEDIA_FOLDER
    media = [cwd_media + f for f in listdir(cwd_media) if isfile(join(cwd_media, f))]
    for f in media:
        img = cv2.imread(f)
        note = process_image(img)
        print (f)
        print ("\t{}".format(note))

def process_image_sin(img):

    try:
        #cv2.imshow("Test", img)
        #if (img == None):
       #     return None
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        color = hsv.mean(0).mean(0)

        sin = color_to_sin(color)
    #print (color)
    #cv2.waitKey(0)
        return sin
    except:
        return None

def process_image(img):

    try:
        #cv2.imshow("Test", img)
        #if (img == None):
       #     return None
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        color = hsv.mean(0).mean(0)

        note = color_to_note(color)
    #print (color)
    #cv2.waitKey(0)
        return note
    except:
        return None

def color_to_note(color):
    pitch = int(color[1] * (84 / 200) + .5)
    velocity = 30 + int(color[2] * (97 / 255.0) + .5)

    return (pitch, velocity)

def rename_files(media):
    count = 0
    for f in media:
        print ("{} ==> nature{}.jpg".format(f, count))
        rename(f, MEDIA_FOLDER + "nature" + str(count) + ".jpg")
        count += 1

def motion_to_notes(motion):
    notes = []
    largest = max(motion)

    for m in motion:
        if (m <= SILENT_CUTOFF):
            velocity = 0
        else:
            velocity = 100
        #print (m)
        pitch = int(36 + (m / largest) * 72)
       # print ("\t{}".format(pitch))
        note = round_note([pitch, velocity])
        #print ("\t{}".format(note[0]))
        notes.append(note)

    return notes

if __name__=="__main__":
    motion = process_video_motion(MEDIA_FOLDER + '\\videos\\netflix_short.mp4')
    notes = motion_to_notes(motion)
    new_notes = downsample_notes(notes, 4)
    generate_midi_track(MEDIA_FOLDER + "\\audio\\" + "drunken_master_netflix_short.mid", new_notes)
    #process_all_images_sin()
    #notes = process_video(MEDIA_FOLDER + '\\videos\\fools_gold.mp4')
   # new_notes = downsample_notes(notes, 8)
  #  generate_midi_track("fools_gold_factor8_cont.mid", new_notes)
##    pattern = midi.read_midifile("fools_gold_factor8.mid")
##    track = pattern[0]
##
##    print (len(track))
    
