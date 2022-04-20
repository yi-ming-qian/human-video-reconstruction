import cv2
import mediapipe as mp
import numpy as np
import os
import argparse
from utils import crop_img


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input_video', type=str, required=True)
parser.add_argument('--no_save_raw', action='store_false')
parser.add_argument('--no_crop_raw', action='store_false')
args = parser.parse_args()

video_name = args.input_video
save_raw = args.no_save_raw
crop_raw = args.no_crop_raw

frame_path = "./"+video_name+"/raw/frames/"
mask_path = "./"+video_name+"/raw/masks/"
if save_raw and (not os.path.exists(frame_path)):
	os.makedirs(frame_path)
	os.makedirs(mask_path)

cap= cv2.VideoCapture(video_name + '.mp4')
print(video_name)
i = 0 
BG_COLOR = (192, 192, 192)
with mp_pose.Pose(
	enable_segmentation=True,
	min_detection_confidence=0.5,
	min_tracking_confidence=0.5) as pose:
	while cap.isOpened():
		success, image = cap.read()
		if not success:
			print("Finish reading camera frames.")
			break
		print(f"processing frame {i}")
		ori_image = image.copy()
		
		# To improve performance, optionally mark the image as not writeable to
		# pass by reference.
		image.flags.writeable = False
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		results = pose.process(image)

		# get segmentation mask
		image.flags.writeable = True
		annotated_image = image.copy()
		condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.4
		
		bg_image = np.zeros(image.shape, dtype=np.uint8)
		bg_image[:] = BG_COLOR
		annotated_image = np.where(condition, annotated_image, bg_image)
		mask_image = condition.astype(np.uint8)*255
		if save_raw:
			cv2.imwrite(f"{frame_path}{i:04}.png", ori_image)
			cv2.imwrite(f"{mask_path}{i:04}.png", mask_image)
		if crop_raw:
			c_img, c_msk = crop_img(ori_image, mask_image[:,:,0])
			cv2.imwrite(f"./{video_name}/{i:04}.png", c_img)
			cv2.imwrite(f"./{video_name}/{i:04}_mask.png", c_msk)


		image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
		mp_drawing.draw_landmarks(
			image,
			results.pose_landmarks,
			mp_pose.POSE_CONNECTIONS,
			landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
		# Flip the image horizontally for a selfie-view display.
		#cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
		i += 1
		# if cv2.waitKey(5) & 0xFF == 27:
		#   break
cap.release()
cv2.destroyAllWindows()