#! python3
# coding=utf-8

# This Python program makes thumbnails with the given extensions for images
# stored in a given folder.
# Last modified: 2023-02-20 22:29

import os, sys, time
from PIL import Image


# Log recording functions

# global variables for log recording
log_records = []    # type: list[str]   # store log records line (str) by line
log_tag = True      # Ture (False): write program running log in .txt (or not)

def show_log(
    log_record: str,
    ):
    """
    Prints program running info and adds it to log_records at the same time.
    Parameters:
        log_record: the running info to be printed and may be added into the
                    global variable log_records, in order to form a .txt log
                    file.    
    Needs:
        global variable log_records for recording log info;
        global variable log_tag to clarify whether recording log info.
    """
    print(log_record)
    if log_tag:     # Only adds log_record when requested.
        log_records.append(log_record + "\n")


def log_head(
    img_exts: tuple[str],
    img_dir: str,
    thumb_dir: str,
    thumb_size: tuple[int],
    thumb_ext: str,
    ):
    """
    Recording log information at the start of the program.
    Parameters:
        those needed for initializing program running; see the part parameters
        in section Main Program.
    Needs:
        modulus time;
        function show_log(), which requests global variables log_records,
        log_tag
    """
    show_log(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    show_log("Format(s) of original images: " + str(img_exts)[1:-1])
    show_log("Directory of original images: " + str(img_dir))
    show_log("Directory of thumbnails: " + str(thumb_dir))
    show_log("Thumbnail size (width, height): " + str(thumb_size)[1:-1])
    show_log("Format of thumbnails: " + str(thumb_ext))
    show_log("Form log file: " + str(log_tag) + "\n")


def write_log(log_dir: str):
    """
    Writes the log_records (i.e., program runnning information) into a text
    log file (.txt). The log file will be named by the running time.
    Needs:
        modulus os, sys, time.
        global variable log_records for recording log info;
        global variable log_tag to clarify whether the log info will be
        written or not. 
    """
    log_name = time.strftime("%Y%m%d", time.localtime()) + ".txt"
    log_path = os.path.join(log_dir, log_name)

    if not log_tag:     # Exit function when no no log file is needed
        return None

    try:
        with open(log_path, 'at', encoding='utf-8') as f_obj:
            # When adding new contents to existing log file
            if os.path.getsize(log_path) != 0:
                f_obj.writelines("\n\n")    # two empty lines as log separater

            f_obj.writelines(log_records)

    # Abort when the file is not found.
    except OSError:
        print("Cannot access log file '" + log_path + "'.")

    # Abort when it is not a text file, or the coding is wrong.
    except UnicodeDecodeError:
        print("Cannot accessss log file '" + log_path + ".\n" +
              "Make sure it is an ASCII text file.")


# Functional Section

def select_by_exts(
    dir: str,
    f_exts: str | tuple[str] = '.jpg',
    ) -> list[str]:
    """
    Returns a list of files (strings) with selected extensions. Will abort if
    the file folder cannot be accessed, or if no file was found.
    Parameters:
        dir:    a string stores the path of the file directory.
        f_exts: the requested file extension (str), or a tuple containing the
                requested file extensions. It will be used for str.endswith().
    Needs:
        modulus os, sys.
    """
    try:
        files = os.listdir(dir)
    except FileNotFoundError:   # When 'dir' cannot be accessed
        show_log("Abort: cannot access the folder '" + dir + "'.\n")
        sys.exit(0)
    
    f_paths = []         # store the paths of sorted image files
    for file in files:
        # ignores capital cases in the file extensions
        if file.lower().endswith(f_exts):
            f_path = os.path.join(dir, file)
            f_paths.append(f_path)

    if f_paths:
        return f_paths
    else:               # Abort when no file was found.
        show_log("Abort: no qualified file is found.\n")
        sys.exit(0)


def mk_thumb_dir(
    img_dir: str,
    thumb_dir: str,
    ):
    """
    Makes a new folder to store thumbnail images, unless the directory is same
    as the one of original images.
    Parameters:
        img_dir:    the directory where the original images stores
        thumb_dir:  the directory where the thumbnails will be stored
    Needs:
        modulus os, sys.
    """
    img_dir_abs = os.path.abspath(img_dir)
    thumb_dir_abs = os.path.abspath(thumb_dir)
    if img_dir_abs == thumb_dir_abs:
        show_log("Use the image dir for thumbnails.")
        return None
    else:
        try:
            os.makedirs(thumb_dir_abs, exist_ok=True)
        except:
            show_log("Abort: cannot create directory " + thumb_dir_abs + "\n")
            sys.exit(0)
        else:
            show_log("Make directory: " + thumb_dir)


def mk_thumb_paths(
    img_paths: list[str],
    thumb_dir: str,
    thumb_ext: str = '.jpg',
    ) -> list[str]:
    """
    Returns a list of thumbnail paths for original images.
    Parameters:
        img_paths:  a list with of the full paths (str) of original images
        thumb_dir:  the directory where the thumbnails will be stored
        thumb_ext:  the format/extension that will be used by thumbnails
    Needs:
        modulus os.
        function show_log(), which requests global variables log_records,
        log_tag.
    Returns:
        a list of full paths (str) for thumbnails.
    PS. About the file name and path:
        "D:\\photos\\01.jpg"    path
        "D:\\photos"            folder/directory/path head
        "01.jpg"                basename/path tail
        "D:\\photos\\01"        file root              
        "01"                    file base
        ".jpg"                  format/extension
    """
    # Abort program when folders for original images and thumbnails are
    # actually the same one. 
    # if os.path.abspath(img_paths) == os.path.abspath(thumb_dir):
    #     show_log("Abort: original images and thumbnails " +
    #           "cannot be the same one.")
    #     sys.exit(0)

    # Stitch paths for thumbnails. Use '_thn' to mark thumbnail images.
    thumb_paths = []
    for img_path in img_paths:
        basename = os.path.basename(img_path)
        base = os.path.splitext(basename)[0] + "_thn"
        thumb_path = os.path.join(thumb_dir, (base + thumb_ext))
        thumb_paths.append(thumb_path)
    return thumb_paths


def crop_thumb(
    img_path: str,
    thumb_path: str,
    size: tuple[int] = (200, 150),
    ) -> str | None:
    """
    Crop from the center part of the original image (im_path) and create a
    thumbnail (thumb_path) for that image. Will return the path of the image
    if it cannot be accessed or processed, as well as when its thumbnail
    cannot be saved.
    Parameters:
        im_path:    the path of the original image file.
        thumb_path: the thumbnail path.
        size:       a 2-tuple defines the thumbnail's (width, height).
    Needs:
        class Image in modulus PIL.
    Returns:
        im_path, if the thumbnail was not built;
        None, if the thumbnail was successfully built.
    """
    try:
        img = Image.open(img_path)
    except FileNotFoundError:
        show_log("File '" + img_path + "' cannot be not found.")
        return img_path
    except:
        show_log("File '" + img_path + "' cannot be processed.")
        return img_path

    img_w = img.width
    img_h = img.height

    # figure out the size tuple in order to crop to the largest size
    w_ratio = size[0]/img_w
    h_ratio = size[1]/img_h
    if w_ratio == h_ratio:
        crop_tuple = (0, 0, img_w, img_h)
    elif w_ratio > h_ratio:
        crop_w = img_w
        crop_h = img_w*(size[1]/size[0])
        crop_l_u = int((img_h - crop_h)/2)
        crop_r_d = int((img_h - crop_h)/2 + crop_h)
        crop_tuple = (0, crop_l_u, img_w, crop_r_d)
    else:
        crop_h = img_h
        crop_w = img_h*(size[0]/size[1])
        crop_l_u = int((img_w - crop_w)/2)
        crop_r_d = int((img_w - crop_w)/2 + crop_w)
        crop_tuple = (crop_l_u , 0, crop_r_d, img_h)
    
    cropped_img = img.crop(crop_tuple)
    thumb_img = cropped_img.resize((size[0], size[1]))

    try:
        thumb_img.save(thumb_path)
    except:
        show_log("File '" + thumb_path + "' cannot be saved.")
        return img_path
    else:
        return None


def mk_thumbs(
    img_paths: list[str],
    thumb_paths: str,
    thumb_size: tuple[int] = (200, 150),
    ) -> tuple[list, list]:
    """
    Makes thumbnails with the requsted extension (.jpg by default) for the
    images whose paths are stroed in the folder 'img_dir', and saves these
    thumbnails in the output folder 'out_dir'. Returns a 2-D tuple containing
    a list of the images processed and the list of the corresponding
    thumbnails.
    Parameters:
        img_paths:  a list with of the paths (str) of original images.
        thumb_dir:  the folder to store the thumbnails.
    Needs:
        modulus os.
        function crop_thumb().
    """
    tuple_imgs_thumbs = (
        [], # type: list[str]   # stores the paths of original images
        [], # type: list[str]   # stores the paths of corresponding thumbnails
        )
    
    for index in range(len(img_paths)):
        if crop_thumb(img_paths[index], thumb_paths[index], thumb_size):
            show_log("Not processed:\t" + img_paths[index])
        else:
            show_log("Processed:\t" + img_paths[index])
            tuple_imgs_thumbs[0].append(img_paths[index])
            tuple_imgs_thumbs[1].append(thumb_paths[index])
    
    return tuple_imgs_thumbs
        

# Main Program

# Parameters
# The string of a file extension must begin with the dot (e.g., '.jpg').
img_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tif', '.tiff')
img_dir = ".\\try"      # the source image folder
thumb_dir = os.path.join(img_dir, "thumbs")   # the album folder
thumb_size = (240, 180)
thumb_ext = '.jpg'

log_head(img_exts, img_dir, thumb_dir, thumb_size, thumb_ext)

img_paths = select_by_exts(img_dir, img_exts)
thumb_paths = mk_thumb_paths(img_paths, thumb_dir, thumb_ext)
mk_thumb_dir(img_dir, thumb_dir)
tuple_imgs_thumbs = mk_thumbs(img_paths, thumb_paths, thumb_size)

write_log(thumb_dir)
