import boto3
import os
import settings
import torch

def get_model(mode:str = "local", model_folder_s3: str = settings.MODELS_FOLDER_S3):
    """
    Connects to S3 bucket services and download the best custo Yolov5 model 
    trained by the user

    Parameters
    ----------
    model_folder_s3 : str
        Path to the folder where the best model is contained.

    Returns
    -------
    model: yolov5 model
        Custom Yolov5 trained model.
    """
     
    if mode == 'aws':
        # fetch credentials from env variables
        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')             #
        aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')     #
        
        # setup a AWS S3 client/resource
        s3 = boto3.resource(
            's3', 
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            )

        # point the resource at the existing bucket
        bucket = s3.Bucket(model_folder_s3)

        # download the training dataset
        with open(settings.BEST_MODEL, 'wb') as data:
            bucket.download_fileobj(settings.MODEL_NAME, data)
    
    # Load the yolov5 model
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=os.path.join(settings.MODELS_FOLDER,settings.BEST_MODEL))
    
    return model