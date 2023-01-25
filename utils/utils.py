import pandas as pd
import os

def set_labels(datasets):
    
    path = f'/home/app/src/data/SKU110K_fixed/annotations/annotations_{datasets}.csv'

    columns = ['image_name','x1','y1','x2','y2','class','image_width','image_height']

    df = pd.read_csv(path, names=columns )

    df['class'] = int(1)
    
    image_name, class_id, x_min, y_min, x_max, y_max = [df['image_name'],df['class'], df['x1'], df['y1'], df['x2'], df['y2']]

    img_width, img_height = [df['image_width'], df['image_height']]
    
    bbox_height,bbox_width= [(y_max - y_min),(x_max - x_min) ]

    x_center, y_center, width, height =[((x_max + x_min) / 2) / img_width, ((y_max + y_min) / 2) / img_height, bbox_width / img_width, bbox_height / img_height]
    names = ['image_name','class_id','x_center', 'y_center', 'width', 'height']

    normalize_yolo = (pd.DataFrame(data = [image_name,class_id, x_center, y_center, width, height],index=names)).T

    normalize_yolo.set_index('image_name',inplace=True)
    
    # Set the directory where the images are located
    image_dir = f'/home/app/src/data/SKU110K_fixed/data_v2/{datasets}/images/'

    # Get a list of all the images in the directory
    image_names = os.listdir(image_dir)
    
    # Set the directory where the file should be saved
    directory = f'/home/app/src/data/SKU110K_fixed/data_v2/{datasets}/labels/'

    for name in image_names:
        # Get the data for the current image
        df = normalize_yolo.loc[name]

        # Get the name of the image without the file extension
        name_img = name.split('.')[0]
        
        # Set the file name and path
        filename = f"{name_img}.txt"
        filepath = os.path.join(directory, filename)

        # Write the dataframe to the file
        df.to_csv(filepath, sep=" ", header=False, index=False)

