# mask_rcnn_with_deepfashion

SageMaker나 Colab에서 해당 이 repo를 다운받아 실행하면 원활하게 수행할 수 있습니다. 로컬(Mac)으로 하면 학습시간이 상당합니다.

1~6까지는 로컬에서 하시고, 7번 8번만, SageMaker나 Colab에서 수행하길 추천합니다.

## 1. 개발 환경 셋업

```bash
git clone https://github.com/namjals/mask_rcnn_with_deepfashion.git
cd mask_rcnn_with_deepfashion
# submodule인 MaskRCNN을 download
git submodule init
git submodule update
pyenv install 3.6.10
# 현재 프롬프트에서만 3.6.10을 사용합니다.
pyenv local 3.6.10
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
source env.sh
```



## 2. 데이터셋 이미지 다운로드

- [DeepFashion2](https://github.com/switchablenorms/DeepFashion2)라는 13가지 카테고리를 갖고 있는 데이터셋을 학습을 위해 다운로드합니다.

- [여기](https://drive.google.com/drive/folders/125F48fsMBz2EF0Cpqk6aaHet5VH399Ok?usp=sharing)에서 validation.zip 다운로드
- [여기](https://docs.google.com/forms/d/e/1FAIpQLSeIoGaFfCQILrtIZPykkr8q_h9qQ5BoTYbjvf95aXbid0v2Bw/viewform?usp=sf_link)에서 서약서 작성 후, 압축 해제 비밀번호 획득

- 프로젝트의 Deepfashion2 디렉토리에 압축 해제한 validation 폴더를 옮깁니다.

  ```
  ex) ~/Downloads폴더에 압축을 해제한 케이스
  cd mask_rcnn_with_deepfashion/Deepfashion2
  mv -r ~/Downloads/validation . 
  ```



## 3. 카테고리 필터링

`./bin/1.filter_category.py`를 실행하여, 어노테이션, 이미지 파일을 필터링하여 저장합니다.

```bash
# 도움말, 총 3개의 인자를 세팅합니다.
./bin/1.filter_category.py -h
usage: 1.filter_category.py [-h] -i INPUT_DIR -o OUTPUT_DIR -c
                            {1,2,3,4,5,6,7,8,9,10,11,12,13}

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input_dir INPUT_DIR
                        Specifies the source input directory to be filtered.
                        Specify the path to the annos, image parent directory.
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Specifies the filtering results output directory.
  -c {1,2,3,4,5,6,7,8,9,10,11,12,13}, --category {1,2,3,4,5,6,7,8,9,10,11,12,13}
                        Select the category to filter.(1~13) Ex) 1 : short
                        sleeve top 2 : short sleeve dress 3 : shorts 4 : sling
                        5 : sling dress 6 : long sleeve top 7 : long sleeve
                        dress 8 : long sleeve outwear 9 : skirt 10 : short
                        sleeve outwear 11 : vest dress 12 : trousers 13 : vest

# shorts로 필터링하는 예제입니다.
./bin/1.filter_category.py -i Deepfashion2/validation -o Deepfashion2/shorts/origin -c 3
```



## 4. 이미지 선별

- OUTPUT_DIR의 이미지 경로에서 원치 않는 이미지를 선별하여 삭제하고, 어노테이션경로도 삭제합니다. 
  - EX) image/007482.jpg 사진을 지우기로 했으면, annos/007482.json도 삭제합니다.

- 테스트라면 건너뛰어도 좋습니다.



## 5. train, val 데이터 셋 나누기

`./bin/2.split_train_val.py`를 실행하여, 학습전 train set, validation set으로 나누어 저장합니다.

```bash
# 도움말, 총 3개의 인자를 세팅합니다.
./bin/2.split_train_val.py -h
usage: 2.split_train_val.py [-h] -i INPUT_DIR -o OUTPUT_DIR -r RATIO

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input_dir INPUT_DIR
                        Specifies the source path to be split into the train
                        and val datasets.
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Specify the splitting target path with the train and
                        val datasets.
  -r RATIO, --ratio RATIO
                        Specify the proportion of the train.(0.1~0.9)

# train 셋을 90%로 split하는 예제입니다.
./bin/2.split_train_val.py -i Deepfashion2/shorts/origin -o Deepfashion2/shorts -r 0.9 
```



## 6. 어노테이션 포맷 변환(via -> coco)

`./bin/3.via_to_coco_format.py`를 실행하여, train, val 셋의 어노테이션 포맷을 변환합니다.

```bash
# 도움말, 총 2개의 인자를 세팅합니다. 좌표타입은 landmarks, segmentation이 있고, 기본값은 landmarks 입니다.
./bin/3.via_to_coco_format.py -h
usage: 3.via_to_coco_format.py [-h] -i INPUT_DIR [-c {landmarks,segmentation}]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input_dir INPUT_DIR
                        Specifies the directory in which to convert via
                        annotation format to coco annotation format.
  -c {landmarks,segmentation}, --coordinate_type {landmarks,segmentation}
                        Select whether to use landmarks coordinates or
                        segmentation coordinates.(landmarks, segmentation)


# 먼저 train 경로의 포맷을 변환합니다.
./bin/3.via_to_coco_format.py -i Deepfashion2/shorts/train

# val 경로의 포맷을 변환합니다.
./bin/3.via_to_coco_format.py -i Deepfashion2/shorts/val
```



## 7. 학습

- SageMaker에서 하는 경우, "1. 개발환경 셋업"을 submodule까지만 진행하고, `source activate tensorflow_p36` , `cd mask_rcnn_with_deepfashion`후 아래 내용을 진행해주세요.

```bash
cd bin
# dataset에 coco 어노테이션으로 변환한 디렉토리를 입력합니다.
python deepfashion.py train --dataset=../Deepfashion2/shorts --weights=coco
# 학습이 완료되면 현재 경로의 logs에 학습 결과파일(h5)가 생성됩니다. epoch마다 파일이 생성되어 파일이 여러개 인데, 이중 완료된 마지막 파일을 예측할때 사용하면 됩니다.
```



## 8. 예측

```bash
# 학습 결과 파일을 weights로 주고, 예측(마스킹)하고자 하는 사진 경로를 image에 입력합니다.
# 아래 mask_rcnn_balloon_0012.h5는 sagemaker에서 학습해놓은 파일입니다.
python deepfashion.py splash --weights=mask_rcnn_balloon_0012.h5 --image=test/1.jpg
python deepfashion.py splash --weights=mask_rcnn_balloon_0012.h5 --image=test/2.jpg
python deepfashion.py splash --weights=mask_rcnn_balloon_0012.h5 --image=test/3.jpg
python deepfashion.py splash --weights=mask_rcnn_balloon_0012.h5 --image=test/4.jpg
python deepfashion.py splash --weights=mask_rcnn_balloon_0012.h5 --image=test/5.jpg
python deepfashion.py splash --weights=mask_rcnn_balloon_0012.h5 --image=test/6.jpg
```



## 9. 결과

- 베이지색만 어느정도 마스킹하고 있음
  - 필터된 소스 사진을 따로 선별하지 않음
  - 좌표타입 landmarks 사용
  - 12번째 epoch
  - 기존 balloon.py를 그대로 사용

| 원본                                                         | 마스킹                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| ![image](https://github.com/namjals/mask_rcnn_with_deepfashion/blob/main/image/3.jpg) | ![image](https://github.com/namjals/mask_rcnn_with_deepfashion/blob/main/image/splash_20201119T025814.png) |
| ![image](https://github.com/namjals/mask_rcnn_with_deepfashion/blob/main/image/6.jpg) | ![image](https://github.com/namjals/mask_rcnn_with_deepfashion/blob/main/image/splash_20201119T030018.png) |
| ![image](https://github.com/namjals/mask_rcnn_with_deepfashion/blob/main/image/1.jpg) | ![image](https://github.com/namjals/mask_rcnn_with_deepfashion/blob/main/image/splash_20201119T025708.png) |
| ![image](https://github.com/namjals/mask_rcnn_with_deepfashion/blob/main/image/2.jpg) | ![image](https://github.com/namjals/mask_rcnn_with_deepfashion/blob/main/image/splash_20201119T025743.png) |
| ![image](https://github.com/namjals/mask_rcnn_with_deepfashion/blob/main/image/4.jpg) | ![image](https://github.com/namjals/mask_rcnn_with_deepfashion/blob/main/image/splash_20201119T025851.png) |
| ![image](https://github.com/namjals/mask_rcnn_with_deepfashion/blob/main/image/5.jpg) | ![image](https://github.com/namjals/mask_rcnn_with_deepfashion/blob/main/image/splash_20201119T025941.png) |