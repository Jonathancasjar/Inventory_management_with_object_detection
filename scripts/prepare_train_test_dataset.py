"""
This script will be used to separate and copy images coming from
`SKU110K_fixed` dataset between `train`, `test` and `valid`.

It will also create all the needed subfolders inside `train`/`test`/`valid` in order
to copy each image to the folder corresponding to its class.

The resulting directory structure should look like this:
    data/
    ├── annotations
    ├── images
    │   ├── test_0.jpg
    │   ├── test_1.jpg
    │   ├── ...
    ├── data_V2
    │   ├── test
    │   │   ├── images 
    │   │   │   ├── test_0.jpg
    │   │   │   ├── test_1.jpg
    │   │   │   ├── ...
    │   │   ├── labels
    │   │   │   ├── data.yaml
    │   │   │   ├── test_01.txt
    │   │   │   ├── test_02.txt
    │   │   │   ├── ...
    │   ├── train
    │   │   ├── images 
    │   │   │   ├── train_0.jpg
    │   │   │   ├── train_1.jpg
    │   │   │   ├── ...
    │   │   ├── labels
    │   │   │   ├── data.yaml
    │   │   │   ├── train_01.txt
    │   │   │   ├── train_02.txt
    │   │   │   ├── ...
    │   ├── val
    │   │   ├── images 
    │   │   │   ├── val_0.jpg
    │   │   │   ├── val_1.jpg
    │   │   │   ├── ...
    │   │   ├── labels
    │   │   │   ├── data.yaml
    │   │   │   ├── val_01.txt
    │   │   │   ├── val_02.txt
    │   │   │   ├── ...
"""

import argparse
import os
import pandas as pd
from utils.utils import set_labels

def parse_args():
    parser = argparse.ArgumentParser(description="Train your model.")
    parser.add_argument(
        "data_folder",
        type=str,
        help=(
            "Full path to the directory having all the images. E.g. "
            "`../data/SKU110K_fixed/images`."
        ),
    )
    parser.add_argument(
        "labels",
        type=str,
        help=(
            "Full path to the CSV file with data labels. E.g. "
            "`../data/SKU110K_fixed/annotations`."
        ),
    )
    parser.add_argument(
        "output_data_folder",
        type=str,
        help=(
            "Full path to the directory in which we will store the resulting "
            "train/test splits. E.g. " "`../data/SKU110K_fixed/data_v2`."
        ),
    )

    args = parser.parse_args()

    return args


def main(data_folder, labels, output_data_folder):
    """
    Parameters
    ----------
    data_folder : str
        Full path to raw images folder.

    labels : str
        Full path to CSV file with data annotations.

    output_data_folder : str
        Full path to the directory in which we will store the resulting
        train/test splits.
    """       
    subsets = ['train','test','val']
    subsets_2 = ['images','labels'] 
    
    #   1. Create the corresponding folders

    if not os.path.exists(output_data_folder):
            os.makedirs(output_data_folder) 
            for subset in subsets:
                path = os.path.join(output_data_folder,subset)
                os.makedirs(path)
                for s in subsets_2:
                    path2 = os.path.join(output_data_folder,subset,s)
                    os.makedirs(path2)

            #   2. Load labels CSV file
            columns_name = ['image_name','x1','y1','x2','y2','class','image_width','image_height']
            
            cvs = ['annotations_train.csv',
                    'annotations_val.csv',
                    'annotations_test.csv']

            for n in cvs:
            
                df = pd.read_csv(labels+'/'+n,names=columns_name)

                #   3. Copy the image to the new folder structure. 
                    # Get list of corrupted images from corrupted_imgs_txt
                corrupted_df = pd.read_csv('/home/app/src/notebooks/badpeggy_list.txt', header=None, names=['Path'])

                corrupted_list = corrupted_df['Path'].str.split(pat='/').str[-1].tolist()
                                           
                for i in range(len(df['image_name'].unique())):
                    if df['image_name'].unique()[i] in corrupted_list:
                        pass
                    else:
                        src = data_folder+'/'+str(df['image_name'].unique()[i])
                        dst = output_data_folder+'/'+str(df['image_name'][0].split('_')[0])+'/'+'images'+'/'+str(df['image_name'].unique()[i])

                        if not os.path.exists(dst):
                            if os.path.exists(src):
                                os.link(src, dst)
            
    for name in subsets:
        set_labels(name)


                
                

if __name__ == "__main__":
    args = parse_args()
    main(args.data_folder, args.labels, args.output_data_folder)
