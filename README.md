# Human Reconstruction from Video

This repo contains scripts for reconstructing 3D human models from a video.

## Reconstruction results
Interesting things always come first! The results for the three input videos are shown in [this html website](https://yi-ming-qian.github.io/unity/index.html). Each page contains hundreds of 3D models so it may take a while for loading. Feel free to use your mouse to play with the 3D models such as rotating.

## Method and discussions
The reconstruction is based on "[PaMIR: Parametric Model-Conditioned Implicit Representation for Image-based Human Reconstruction](https://arxiv.org/abs/2007.03858)" published in TPAMI2021. The key idea of this paper is to regularize the free-form implicit shape representation by the body template model (SMPL) to improve accuracy and robustness under challenging senairos. Specifically, give a single RGB image, the method first obtains a SMPL model with an existing method. Then, the neural network takes the 2D image features extracted from RGB image and 3D shape features extracted from the SMPL estimation, concatenates the two types of features and empolys a decoder to output the occupancy probability, which is further converted to the final mesh. The method also use an optimization step to further refine the results by enforceing the consistency between the estimated occupancy and the initial SMPL model. In contrast to PiFU which uses free-form implict representation only, this paper incorporate parametric model SMPL and free-form implicit representation, and thus may work better for challenging poses and severe occlusions, which is the main reason for me to choose PaMIR for the provided three videos (the subjects in them show large pose variations). 

PaMIR has several limitations. For example, the original paper shows failure cases on extremely challenging poses (Fig16 in their paper). To me, working with extremely challening poses requires highly accurate human segmentation and pose estimation, which is not easy to adderss and requires big data and powerful network architecture. Some other limitations include the reconstruction results lack of surface details, which maybe could be solved by RGB-guided super resolution. Another possible solution is to estimiate normal and shading information from the RGB image, which is a standard technique to acquire surface details in traditional 3D reconstruction. I notice that researchers have started to go along this direction such as [this work](https://phorhum.github.io/). 

Similar to other single-shot reconstruction methods such as PiFU, PaMIR requires human segmentation as input, and is trained on single-person images. To work for multiple person instances, it is possible to take each separate human instance as input. PaMIR cannot work in real time, because it introduces two additional steps (SMPL estimation and optimization-based refinement). 

In this repo, I focus on improving PaMIR results with automaic and better human segmentation. In the original implementation of PaMIR, it uses a semantic segmentation method, followed by traditional MRF-based Grabcut to get the binary masks of human subjects (such a strategy makes me feel that the authors used manual Grabcut segmentation for refining their segmentation). My input here are videos, so an automatic method has to be chosen. My first trail is [U2Net for human segmentaion](https://github.com/xuebinqin/U-2-Net), which didn't give me a resonable segmentation results especially when the input videos show fast motion and have motion blurs. Considering my input is a video, the segmentaion results have to be temporally coherent so that my final 3D models would be temporally consistent. I fianlly end up with [Mediapipe](https://google.github.io/mediapipe/) for human segmentation from video inputs. While Mediapipe shows a bit over-segmenation in some frames, overall it works very well and obtain temporally consistent masks even when the images are very blurry, helping to get temporally consistent 3D model in the later stage. 


# How to reproduce

Clone the repository:
```bash
git clone https://github.com/yi-ming-qian/human-video-reconstruction.git
```
Install dependencies:
```bash
conda create -n pamir python=3.7.5
conda activate pamir
pip install -r requirements.txt
```
Preprocess input videos:
Given an input video, I perform human segmentation, crop image to have the size of 512x512 as input (the script from PiFU is used), obtain 2D pose with openpose (I use the CPU-version Windows exe). 
```bash
cd data
python preprocessing.py -i {input_video_name}
cd ..
```
{input_video_name} denotes the video filename. In this repo, it is "FigureSkater", "JumpingJacks" or "Skateboarder".
For fast prototyping, Windows exe is used for openpose, so it is not included in the above ```preprocessing.py```.
Run PaMIR reconstruction:






# PaMIR: Parametric Model-Conditioned Implicit Representation for Image-based Human Reconstruction
[Zerong Zheng](http://zhengzerong.github.io/), [Tao Yu](http://ytrock.com/), [Yebin Liu](http://www.liuyebin.com/), [Qionghai Dai](http://media.au.tsinghua.edu.cn/qhdai_new.html)


This repository contains a pytorch implementation of "[PaMIR: Parametric Model-Conditioned Implicit Representation for Image-based Human Reconstruction](https://arxiv.org/abs/2007.03858)". Tested with PyTorch 1.7.0 on Ubuntu 18.04, CUDA 11.0. 

**NOTE**: The current models are trained on private Twindom scans, which are bias towards upright standing poses. 
Fortunately, we have collected [THUman 2.0](http://www.liuyebin.com/Function4D/Function4D.html), a new dataset containing 500 high-quality 3D human scans with more variety in body poses. You can use THUman 2.0 to train/fine-tune our PaMIR model or your own models!

**NOTE 2021/11/16**: The pre-trained model I previously uploaded is not the correct one. I have replaced it with the correct model. Sincere apology!

[Project Page](http://www.liuyebin.com/pamir/pamir.html)
![Teaser Image](http://www.liuyebin.com/pamir/assets/results_large.jpg)


If you find the code useful in your research, please consider citing the paper.

```
@misc{zheng2020pamir,
title={PaMIR: Parametric Model-Conditioned Implicit Representation for Image-based Human Reconstruction},
author={Zerong Zheng, Tao Yu, Yebin Liu, Qionghai Dai},
journal={IEEE Transactions on Pattern Analysis and Machine Intelegence},
year={2021},
primaryClass={cs.CV}
}
```

## Demo
Please run the following commands to download necessary assets (including the pre-trained models):
```bash
cd ./networks
wget https://github.com/ZhengZerong/PaMIR/releases/download/v0.0/results.zip
unzip -o results.zip
cd ..
```

After that, run the following script to test the pre-trained network:
```bash
cd ./networks
python main_test.py
cd ..
```
This command will generate the textured reconstruction with the fitted SMPLs for the example input images in ```./network/results/test_data*/```. Note that we assume the input images are tightly cropped with the background removed and the height of the persons is about 80% of the image height (Please see the example input images we provide). 



## Dataset Generation for Network Training
In ```dataset_example```, we provide an example data item, which contains a textured mesh and a SMPL model fitted to the mesh. The mesh is downloaded from [RenderPeople](https://renderpeople.com/sample/free/rp_dennis_posed_004_OBJ.zip).  To generate the training images, please run:
```bash
cd ./data
python main_normalize_mesh.py                         # we normalize all scans into a unit bounding box
python main_calc_prt.py
python main_render_images.py
python main_sample_occ.py
python main_associate_points_with_smpl_vertices.py    # requires SMPL fitting
cd ..
```
Note that the last python script requires SMPL model fitted to the scans. To fit SMPL to your own 3D scans, you can use our tool released at [this link](https://github.com/ZhengZerong/MultiviewSMPLifyX). 

## Train the Network
Please run the following command to train the network:
```bash
cd ./networks
bash ./scripts/train_script_geo.sh  # geometry network
bash ./scripts/train_script_tex.sh  # texture network
cd ..
```

## Acknowledgement
Note that the rendering code of this repo is heavily based on [PIFU](https://github.com/shunsukesaito/PIFu), while the training code is heavily based on [GraphCMR](https://github.com/nkolot/GraphCMR/). We thank the authors for their great job!


## LICENSE
>Please read carefully the following terms and conditions and any accompanying documentation before you download and/or use PaMIR Software/Code/Data (the "Software"). By downloading and/or using the Software, you acknowledge that you have read these terms and conditions, understand them, and agree to be bound by them. If you do not agree with these terms and conditions, you must not download and/or use the Software. 
>
>**Ownership**
>
>The Software has been developed at the Tsinghua University and is owned by and proprietary material of the Tsinghua University. 
>
>**License Grant**
>
>Tsinghua University grants you a non-exclusive, non-transferable, free of charge right: 
>
>To download the Software and use it on computers owned, leased or otherwise controlled by you and/or your organisation;
>
>To use the Software for the sole purpose of performing non-commercial scientific research, non-commercial education, or non-commercial artistic projects. 
>
>Any other use, in particular any use for commercial purposes, is prohibited. This includes, without limitation, incorporation in a commercial product, use in a commercial service, as training data for a commercial product, for commercial ergonomic analysis (e.g. product design, architectural design, etc.), or production of other artifacts for commercial purposes including, for example, web services, movies, television programs, mobile applications, or video games. The Software may not be used for pornographic purposes or to generate pornographic material whether commercial or not. This license also prohibits the use of the Software to train methods/algorithms/neural networks/etc. for commercial use of any kind. The Software may not be reproduced, modified and/or made available in any form to any third party without Tsinghua University’s prior written permission. By downloading the Software, you agree not to reverse engineer it. 
>
>**Disclaimer of Representations and Warranties**
>
>You expressly acknowledge and agree that the Software results from basic research, is provided “AS IS”, may contain errors, and that any use of the Software is at your sole risk. TSINGHUA UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES OF ANY KIND CONCERNING THE SOFTWARE, NEITHER EXPRESS NOR IMPLIED, AND THE ABSENCE OF ANY LEGAL OR ACTUAL DEFECTS, WHETHER DISCOVERABLE OR NOT. Specifically, and not to limit the foregoing, Tsinghua University makes no representations or warranties (i) regarding the merchantability or fitness for a particular purpose of the Software, (ii) that the use of the Software will not infringe any patents, copyrights or other intellectual property rights of a third party, and (iii) that the use of the Software will not cause any damage of any kind to you or a third party. 
>
>**Limitation of Liability**
>
>Under no circumstances shall Tsinghua University be liable for any incidental, special, indirect or consequential damages arising out of or relating to this license, including but not limited to, any lost profits, business interruption, loss of programs or other data, or all other commercial damages or losses, even if advised of the possibility thereof. 
>
>**No Maintenance Services**
>
>You understand and agree that Tsinghua University is under no obligation to provide either maintenance services, update services, notices of latent defects, or corrections of defects with regard to the Software. Tsinghua University nevertheless reserves the right to update, modify, or discontinue the Software at any time. 
>
>**Publication with the Software**
>
>You agree to cite the paper describing the software and algorithm as specified on the download website. 
>
>**Media Projects with the Software**
>
>When using the Software in a media project please give credit to Tsinghua University. For example: the Software was used for performance capture courtesy of the Tsinghua University. 
>
>**Commercial Licensing Opportunities**
>
>For commercial use and commercial license please contact: liuyebin@mail.tsinghua.edu.cn. 


## Contact
- Zerong Zheng [(zrzheng1995@foxmail.com)](mailto:zrzheng1995@foxmail.com)
- Yebin Liu [(liuyebin@mail.tsinghua.edu.cn)](mailto:liuyebin@mail.tsinghua.edu.cn)
