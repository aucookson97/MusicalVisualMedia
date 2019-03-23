import cv2
import midi
from os import getcwd, listdir, rename
from os.path import isfile, join

MEDIA_FOLDER = "C:\\Users\\Aidan\\Documents\\git_repos\\media\\"




def process_video(video_file):
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
        accum_pitch += note[0]
        accum_velocity += note[1]
        if (i % factor == 0):
            new_notes.append([int(accum_pitch / float(factor)), int(accum_velocity / float(factor))])
            accum_pitch = 0
            accum_velocity = 0
    new_notes.append([int(accum_pitch / float(factor)), int(accum_velocity / float(factor))])
    return new_notes
        
    

def process_all_images():
    cwd_media = MEDIA_FOLDER
    media = [cwd_media + f for f in listdir(cwd_media) if isfile(join(cwd_media, f))]
    for f in media:
        img = cv2.imread(f)
        note = process_image(img)
        print (f)
        print ("\t{}".format(note))

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
    pitch = 12 + int(color[1] * (60 / 255.0) + .5)
    velocity = 32 + int(color[2] * (95 / 255.0) + .5)
    return (pitch, velocity)

def rename_files(media):
    count = 0
    for f in media:
        print ("{} ==> nature{}.jpg".format(f, count))
        rename(f, MEDIA_FOLDER + "nature" + str(count) + ".jpg")
        count += 1

if __name__=="__main__":
    notes = process_video(MEDIA_FOLDER + '\\videos\\fools_gold.mp4')
    new_notes = downsample_notes(notes, 8)
    generate_midi_track("fools_gold_factor8_cont.mid", new_notes)
##    pattern = midi.read_midifile("fools_gold_factor8.mid")
##    track = pattern[0]
##
##    print (len(track))
    
