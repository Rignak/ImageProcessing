import os
from lbpcascade_animeface.detect_face import detect as detect_anime_face
import sys
import fire

from Rignak_Misc.path import get_local_file
from Rignak_ImageProcessing.face_detection import extract_faces
from Rignak_ImageProcessing.face_detection import DEFAULT_MODES

DETECTION_FUNCTION = detect_anime_face
OUTPUT_FOLDER = get_local_file(__file__, 'output')
INPUT_FOLDER = get_local_file(__file__, 'input')
SUPPORTED_EXTENSION = ('.avi', '.mp4', '.mkv')


def extract_keyframes(video_name, output_folder=OUTPUT_FOLDER):
    folder, filename = os.path.split(video_name)
    new_folder = os.path.join(output_folder, os.path.splitext(filename)[0])
    os.makedirs(new_folder, exist_ok=True)

    cmd = f"ffmpeg -skip_frame nokey -i \"{video_name}\" " \
        f"-vsync 0 -f image2 \"{new_folder}/k-%04d.png\""
    os.system(cmd)

    cmd = f"ffmpeg -i \"{video_name}\" " \
        f"-vsync 0 -vf fps=1 -f image2 \"{new_folder}/p-%05d.png\""
    os.system(cmd)

    return new_folder


def main(*modes, input_folder=INPUT_FOLDER, output_folder=OUTPUT_FOLDER):
    """
    Detect faces from videos and copy them to another folder

    :param input_folder: folder containing the images
    :param output_folder: future folder containing the faces
    :param modes: "face", "portrait", "upper_body"
    :return:
    """
    for filename in os.listdir(input_folder):
        if not os.path.splitext(filename)[-1] in SUPPORTED_EXTENSION:
            continue
        video_full_filename = os.path.join(input_folder, filename)
        new_folder = extract_keyframes(video_full_filename, output_folder=output_folder)

        for frame_filename in os.listdir(new_folder):
            full_frame_filename = os.path.join(new_folder, frame_filename)
            extracted_filenames = extract_faces(full_frame_filename, output_folder=new_folder, modes=modes)
            for extracted_filename in extracted_filenames:
                final_filename = os.path.join(os.path.split(extracted_filename)[0],
                                              f'{os.path.splitext(filename)[0]}_{os.path.split(extracted_filename)[1]}')
                os.rename(extracted_filename, final_filename)
            os.remove(full_frame_filename)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        main(*DEFAULT_MODES)
    else:
        fire.Fire(main)
