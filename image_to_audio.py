import cv2
from os import getcwd, listdir, rename
from os.path import isfile, join

MEDIA_FOLDER = "C:\\Users\\Aidan\\Documents\\git_repos\\media\\"




def process_image(image_file):

    try:
        img = cv2.imread(image_file)
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
    cwd_media = MEDIA_FOLDER
    media = [cwd_media + f for f in listdir(cwd_media) if isfile(join(cwd_media, f))]
    for f in media:
        note = process_image(f)
        print (f)
        print ("\t{}".format(note))
