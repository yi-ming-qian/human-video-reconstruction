import os
import cv2
import numpy as np 
import trimesh

from pathlib import Path
import argparse
import glob



def get_bbox(msk):
	rows = np.any(msk, axis=1)
	cols = np.any(msk, axis=0)
	rmin, rmax = np.where(rows)[0][[0,-1]]
	cmin, cmax = np.where(cols)[0][[0,-1]]

	return rmin, rmax, cmin, cmax

def crop_img(img, msk, bbox=None):
	if bbox is None:
		bbox = get_bbox(msk > 100)
	cx = (bbox[3] + bbox[2])//2
	cy = (bbox[1] + bbox[0])//2

	w = img.shape[1]
	h = img.shape[0]
	height = int(1.138*(bbox[1] - bbox[0]))
	hh = height//2

	# crop
	dw = min(cx, w-cx, hh)
	if cy-hh < 0:
		img = cv2.copyMakeBorder(img,hh-cy,0,0,0,cv2.BORDER_CONSTANT,value=[0,0,0])	
		msk = cv2.copyMakeBorder(msk,hh-cy,0,0,0,cv2.BORDER_CONSTANT,value=0) 
		cy = hh
	if cy+hh > h:
		img = cv2.copyMakeBorder(img,0,cy+hh-h,0,0,cv2.BORDER_CONSTANT,value=[0,0,0])	
		msk = cv2.copyMakeBorder(msk,0,cy+hh-h,0,0,cv2.BORDER_CONSTANT,value=0)	
	img = img[cy-hh:(cy+hh),cx-dw:cx+dw,:]
	msk = msk[cy-hh:(cy+hh),cx-dw:cx+dw]
	dw = img.shape[0] - img.shape[1]
	if dw != 0:
		img = cv2.copyMakeBorder(img,0,0,dw//2,dw//2,cv2.BORDER_CONSTANT,value=[0,0,0])	
		msk = cv2.copyMakeBorder(msk,0,0,dw//2,dw//2,cv2.BORDER_CONSTANT,value=0)	
	img = cv2.resize(img, (512, 512))
	msk = cv2.resize(msk, (512, 512))

	kernel = np.ones((3,3),np.uint8)
	msk = cv2.erode((255*(msk > 100)).astype(np.uint8), kernel, iterations = 1)

	return img, msk

def batch_crop():
	'''
	given foreground mask, this script crops and resizes an input image and mask for processing.
	'''
	# parser = argparse.ArgumentParser()
	# parser.add_argument('-i', '--input_image', type=str, help='if the image has alpha channel, it will be used as mask')
	# parser.add_argument('-m', '--input_mask', type=str)
	# parser.add_argument('-o', '--out_path', type=str, default='./sample_images')
	# args = parser.parse_args()

	base_dir = "/local-scratch/yimingq/unity/data/JumpingJacks/"
	raw_dir = base_dir+ "raw/"
	image_dir = raw_dir+"frames/"
	mask_dir = raw_dir+"masks/"
	image_list = glob.glob(image_dir +os.sep+ '*')
	print(image_dir, image_list)
	for i, imgdir in enumerate(image_list):
		img = cv2.imread(imgdir, cv2.IMREAD_UNCHANGED)
		if img.shape[2] == 4:
			msk = img[:,:,3:]
			img = img[:,:,:3]
		else:
			mskname = imgdir.replace("frames","masks").replace("jpg","png")
			msk = cv2.imread(mskname, cv2.IMREAD_GRAYSCALE)

		img_new, msk_new = crop_img(img, msk)

		img_name = Path(imgdir).stem

		cv2.imwrite(os.path.join(base_dir, img_name + '.png'), img_new)
		#cv2.imwrite(os.path.join(base_dir, img_name + '_mask.png'), msk_new)


def vid2img():
	video_name = "Skateboarder"#"FigureSkater"#"JumpingJacks"
	output_dir = "./"+video_name+"/raw/frames/"
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	cap= cv2.VideoCapture('JumpingJacks.mp4')
	i=0
	while(cap.isOpened()):
		ret, frame = cap.read()
		if ret == False:
			break
		cv2.imwrite(output_dir+f'{i:04}.jpg',frame)
		i+=1
	 
	cap.release()
	cv2.destroyAllWindows()

def obj2glb():
	video_name = "FigureSkater"
	obj_names = glob.glob(f"./{video_name}/results/*_tex.obj")
	print(f"./{video_name}/results/*_tex.obj")

	for i, name in enumerate(obj_names):
		scene = trimesh.Scene([trimesh.load(name)])
		with open(name.replace(".obj", ".glb"), 'wb') as f:
			f.write(trimesh.exchange.gltf.export_glb(scene))
		name = name.replace("_tex.obj", ".obj")
		scene = trimesh.Scene([trimesh.load(name)])
		with open(name.replace(".obj", ".glb"), 'wb') as f:
			f.write(trimesh.exchange.gltf.export_glb(scene))


if __name__=="__main__":
	#vid2img()
	#batch_crop()
	#generate_html()
	obj2glb()

