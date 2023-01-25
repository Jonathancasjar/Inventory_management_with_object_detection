import json
import time
from uuid import uuid4

import redis
import settings

# Connect to Redis
db = redis.Redis(
                host = settings.REDIS_IP ,
                port = settings.REDIS_PORT,
                db = settings.REDIS_DB_ID
                )


def model_predict(image_name: str, annotation_style: str, show_heuristic: bool):
    """
    Receives an image name and queues the job into Redis.
    Will loop until getting the answer from our ML service.

    Parameters
    ----------
    image_name : str
        Name for the image uploaded by the user.
    annotation_style : str
        Annotation style to display output image ('heatmap' or 'bbox')
    show_heuristic: bool 
        Whether to show heuristic detection or not

    Returns
    -------
    prediction, score : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """

    # Assign an unique ID for this job and add it to the queue..
    job_id = str(uuid4())
    job_data = {
                  "id": job_id,
                  "image_name": image_name,
                  "annotation_style": annotation_style,
                  "show_heuristic": show_heuristic
                }

    #  Send the job to the model service using Redis
    db.lpush(
              settings.REDIS_QUEUE,
              json.dumps(job_data)
            )

    # Loop until we received the response from our ML model
    while True:
        # Attempt to get model predictions using job_id
        response = db.get(job_id)
      
        if response:
            db.delete(job_id)
            break

        # Sleep some time waiting for model results
        time.sleep(settings.API_SLEEP)

    #  Change the output format
    response_dict =json.loads(response)                                                
    mAP = response_dict.values()
    
    return mAP
