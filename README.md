---------------------------------------------------
  Inventory management with object detection.

# Data Preparation steps

1. First download the data from S3 AWS with AWS CLI:

AWS CLI
- Install: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
- Configure: aws configure
- List data: aws s3 ls s3://anyoneai-datasets/SKU-110K/SKU110K_fixed/
- mkdir data
- Download data in to data folder: aws s3 sync s3://anyoneai-datasets/SKU-110K/SKU110K_fixed/ SKU110K_fixed or now you can download from
  https://drive.google.com/file/d/1iq93lCdhaPUN0fWbLieMtzfB1850pKwd/edit
- Delete corrupt images : 
 - We obtained a list of the corrupted images from the Bad Peggy application and ran it locally.


2. Then prepare the data into the correct folder structure: 

- DOCKER CONTAINER
# Project container - Docker

## Install
You can use `Docker` to easily install all the needed packages and libraries:

- **CPU:**
### To build Docker use:
```bash
$ docker build -t casjar_obj_detect --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) -f docker/Dockerfile .
```
- **GPU:**

$ docker build -t casjar_obj_detect_gpu --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) -f docker/Dockerfile_gpu .

### To Run Docker use:

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
### To prepare the dataset run the following code:
```bash 
$ python3 scripts/prepare_train_test_dataset.py "/home/app/src/data/SKU110K_fixed/images" "/home/app/src/data/SKU110K_fixed/annotations" "/home/app/src/data/SKU110K_fixed/data_v2"
```
### Download the Yolov5 model and the Dataset with the Missing products from Roboflow

3. Run the model: 
- In the terminal run:
```bash
 - git clone https://github.com/ultralytics/yolov5
 
```
- To download the dataset with the missing spaces run the next code:
```bash
rf = Roboflow(api_key="YOUR API KEY HERE")
project = rf.workspace("final-project-object-detection-for-instore-inventory-management").project("empty-spaces-in-a-supermarket-hanger-1upsp")
dataset = project.version(26).download("yolov5")
```
### Notebooks

Open and run the notebooks located in notebooks/ folder in the following order:
- **EDA** Make an exploratory data analysis.
- **Training_notebook** Train the first model with Yolov5 and fine-tune the model with the Missing-spaces dataset
- **Evaluation** Evaluate your trained models in the test set.


### Docker API Services

6. To run the services need to use compose:

```bash
$ docker-compose up --build -d
```
7. The best model obtained is moved to the model/models folder for use in the API.

## To obtain a good model I train the model with 150 epochs, here are the results:

- Results obtained with the initial-model
https://www.comet.com/sannicosan/initial-model/79be683f051f42b7a4b38c4d152d05c1?experiment-tab=stdout

- Results obtained with the main model
https://www.comet.com/sannicosan/sku-missing/view/new/panels 
