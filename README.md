---------------------------------------------------
  Inventory management with object detection .

## Team Members
---------------------------------------------------
  + Federico Saban - federicosaban10@gmail.com
  + José Cisneros - jcisneros@meicaperu.com
  + Jimmy Llaiqui - jim.llr01@gmail.com
  + Jonathan Castillo - jcasjar@gmail.com
  + Laura Argüello  - lau.bluee3@gmail.com
  + Nicolás Sánchez - nicolassanca95@gmail.com

# Data Preparation steps

1. First download the data from S3 AWS with AWS CLI:

AWS CLI
- Install: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
- Configure: aws configure
- List data: aws s3 ls s3://anyoneai-datasets/SKU-110K/SKU110K_fixed/
- mkdir data
- Download data in to data folder: aws s3 sync s3://anyoneai-datasets/SKU-110K/SKU110K_fixed/ SKU110K_fixed
- Delete corrupt images : 
 - First we obtained a list of the corrupted images from the Bad Peggy 
   application run on the local.
 - 

2. Then we prepare the data into the correct folder structure: 

- DOCKER CONTAINER
# Project containter - Docker

## Install
You can use `Docker` to easily install all the needed packages and libraries:

- **CPU:**

```bash
$ docker build -t casjar_obj_detect --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) -f docker/Dockerfile .
```
- **GPU:**

$ docker build -t casjar_obj_detect_gpu --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) -f docker/Dockerfile_gpu .

### Run Docker

- **CPU:**
```bash
$ docker run --rm --net host -it \
    -v $(pwd):/home/app/src \
    --workdir /home/app/src \
    casjar_obj_detect \
    bash
```

- **GPU:**
```bash
$ docker run --rm --net host --gpus all -it \
    -v $(pwd):/home/app/src \
    --workdir /home/app/src \
    casjar_obj_detect_gpu \
    bash

```
### Run this code to prepare the dataset
```bash 
$ python3 scripts/prepare_train_test_dataset.py "/home/app/src/data/SKU110K_fixed/images" "/home/app/src/data/SKU110K_fixed/annotations" "/home/app/src/data/SKU110K_fixed/data_v2"
```
### Download the Yolov5 model

3. Run the model: 
- In the terminal run:
```bash
 - git clone https://github.com/ultralytics/yolov5
 
```
### Run the notebooks

4. Run Training_notebook to start training models

5. Run Evaluation notebook to evaluate all the trainings


### Docker API Services

6. To run the services using compose:

```bash
$ docker-compose up --build -d
```
7. The best model obtained is moved to the model/models folder for use in the Api.

## To obtain a model with a larger number of epochs we decided to have one of the members train his model with 150 epochs, here are the results:

- Results obtained with the initial-model
https://www.comet.com/sannicosan/initial-model/79be683f051f42b7a4b38c4d152d05c1?experiment-tab=stdout

- Results obtained with the main model
https://www.comet.com/sannicosan/sku-missing/view/new/panels 