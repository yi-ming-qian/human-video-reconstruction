# Human Reconstruction from Video

This repo contains scripts for reconstructing 3D human models from a video.

## Reconstruction results
Interesting things always come first! The results for the three input videos are shown in <a href="https://yi-ming-qian.github.io/unity/index.html" target="_blank">this html website</a>. Each page contains hundreds of 3D models so it may take a while for loading. Feel free to use your mouse to play with the 3D models such as rotating.

## Method and discussions
The reconstruction is based on "[PaMIR: Parametric Model-Conditioned Implicit Representation for Image-based Human Reconstruction](https://arxiv.org/abs/2007.03858)" published in TPAMI2021. The key idea of this paper is to regularize the free-form implicit shape representation by the body template model (SMPL) to improve accuracy and robustness under challenging senairos. Specifically, give a single RGB image, the method first obtains a SMPL model with an existing method. Then, the neural network takes the 2D image features extracted from RGB image and 3D shape features extracted from the SMPL estimation, concatenates the two types of features and empolys a decoder to output the occupancy probability, which is further converted to the final mesh. The method also use an optimization post-processing step to further refine the results by enforceing the consistency between the estimated occupancy and the initial SMPL model. In contrast to PiFU which uses free-form implict representation only, this paper incorporate parametric model SMPL and free-form implicit representation, and thus may work better for challenging poses and severe occlusions, which is the main reason for me to choose PaMIR for the provided three videos (the subjects in them show large pose variations). 

PaMIR has several limitations. For example, the original paper shows failure cases on extremely challenging poses (Fig. 16 in their paper). To me, dealing with extremely challening poses requires highly accurate human segmentation and pose estimation, which is not trivial to adderss and demands big data and powerful network architecture. Some other limitations include the reconstruction results lack of surface details, which maybe could be solved by RGB-guided super resolution. Another possible solution is to estimiate normal and shading information from the RGB image, which is a standard technique to acquire surface details in traditional 3D reconstruction. I notice that researchers have started to go along this direction such as [this work](https://phorhum.github.io/). 

Similar to other single-shot reconstruction methods such as PiFU, PaMIR requires human segmentation as input, and is trained on single-person images. To work for multiple person instances, it is possible to take each separate human instance as input. PaMIR cannot work in real time, because it introduces two additional steps (SMPL estimation and optimization-based refinement). 

In this repo, I focus on improving PaMIR results with automaic and better human segmentation. In the original implementation of PaMIR, it uses a semantic segmentation method, followed by traditional MRF-based Grabcut to get the binary masks of human subjects (such a strategy makes me think that the authors used manual Grabcut segmentation for refining their segmentation). My input here are videos, so an automatic method has to be chosen. My first trail is [U2Net for human segmentaion](https://github.com/xuebinqin/U-2-Net), which didn't give me a resonable segmentation results especially when the input videos show fast motion and have motion blurs. Considering my input is a video, the segmentaion results have to be temporally coherent so that my final 3D models would be temporally consistent. I fianlly end up with [Mediapipe](https://google.github.io/mediapipe/) for human segmentation from video inputs. While Mediapipe shows a bit over-segmenation in some frames, overall it works very well and obtain temporally consistent masks even when the images are very blurry, helping to get temporally consistent 3D model in the later stage.

Evaluations can be performed in several standard ways. In addition to qualitative assessment, we can quantitatively evaluate on both synthetic and real data. For synethetic case, the Twindom dataset and the BUFF rendering dataset are good choices. For real data, we can use human RGBD dataset by using the depth image as GT. Novel view synthesis is also another way for evaluations on real data. That is, we can capture the videos from multiple viewpoints and use the reconstructed shape from one view to synthesize images from other views and then compare the synthesized images with the captured ones.

## How to reproduce
1. Clone the repository:
```bash
git clone https://github.com/yi-ming-qian/human-video-reconstruction.git
```
2. Install dependencies:
```bash
conda create -n pamir python=3.7.5
conda activate pamir
pip install -r requirements.txt
```
3. Preprocess input videos:

Given an input video, I perform human segmentation with Mediapipe, crop image to have the size of 512x512 as input (the [script](https://github.com/shunsukesaito/PIFu/blob/master/apps/crop_img.py) from PiFU is used), obtain 2D pose with OpenPose (I use the [CPU-version Windows exe](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/installation/0_index.md#windows-portable-demo)). 
```bash
cd data
python preprocessing.py -i {input_video_name}
cd ..
```
```{input_video_name}``` denotes the video filename. In this repo, it is "FigureSkater", "JumpingJacks" or "Skateboarder".
For fast prototyping, Windows exe is used for OpenPose, so it is not included in the above ```preprocessing.py```. The processed frames can be found in ```data/{input_video_name}/```. The OpenPose keypoints should also be copied there.

4. Configure PaMIR:

Please first download necessary assets and pre-trained models.
```bash
cd pamir/networks
wget https://github.com/ZhengZerong/PaMIR/releases/download/v0.0/results.zip
unzip -o results.zip
```

5. Run PaMIR:
```bash
python main_test.py -i {input_video_name}
cd ../../data
ls
```
The reconstruction results can be found in ```{input_video_name}/results/```. For example, if the frame id is "0000", the 3D mesh and the corresponding textured mesh is "0000.obj" and "0000_tex.obj", respectively. My reconstruction results can be downloaded from [here](https://umanitoba-my.sharepoint.com/:u:/g/personal/yiming_qian_umanitoba_ca/EZblGSCEmC9Nv2kXHJIkBMIBLBf4z8QMsS8sx-GgnC3uIw?e=pp8iKk).