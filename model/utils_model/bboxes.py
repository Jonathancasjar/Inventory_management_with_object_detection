# Python imports
import numpy as np

# Self-made
from enum import Enum

import settings

#from settings import CLASSES, COLORMAP


class CLASSES(Enum):
  PRODUCT = 3
  MISSING = 2

# COLORMAP PER CLASS
class COLORMAPS(Enum):
  PRODUCT = 'COLORMAP_TURBO'
  MISSING = 'COLORMAP_RAINBOW'



#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Functions
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



def plot_bboxes(img, box_coordinates, style: str = 'bbox'):
    """ 
    It plots the bounding boxes in green when products are present.
    If there are missing products, then red bboxes are drawn.

    Parameters
    ----------
    img_path: str
        Path to image.
        
    box_coordinates: pd.DataFrame
        Contains the image coordinates to plot. 
        Default = None: searches for the coordinates in the static dataset (.csv)
        stored under `data/SKU110K/annotations/annotations.csv`.
        
    axes: matplotlib.axes.Axes (Optional)
        Axes in which to plot the image.
        
    skip_plot: bool
        Wether to skip or not the plot of the image.
        
    style: str
        The style of the bounding boxes. Use:
        - bbox: for standard bboxes
        - heatmap: heatmap version for (missing products only)
        
    Returns
    ----------
    img: np.array (Optional)
        Image plotted.
    """
    #Read the image
    #img = cv2.imread(img_path)
    
    if style == 'bbox':
      
        # Plot all boxes
        for row in box_coordinates:
            x1, y1, x2, y2, conf, cls = row
            if cls == CLASSES.PRODUCT.value:
                img = cv2.rectangle(img, (x1, y1), (x2, y2), settings.COLOR_BLUE, thickness=5)
            else:
                img = cv2.rectangle(img, (x1, y1), (x2, y2), settings.COLOR_RED, thickness=7)
                  
    
    elif style == 'heatmap':
        for cls in CLASSES:
          img = apply_heatmap(img,box_coordinates[box_coordinates[:,5]==cls.value], getattr(cv2, COLORMAPS[cls.name].value))

    return img

def apply_heatmap(img, bboxes, colormap):
  h, w , _ = img.shape
  img_bw = np.zeros((h,w,1), np.uint8)
  for row in bboxes:
    img_bw[row[1]:row[3], row[0]:row[2]] = 255
  img_bw = cv2.distanceTransform(img_bw, cv2.DIST_L1, maskSize=5).astype(np.uint8)
  img_bw = cv2.applyColorMap(img_bw, colormap)
  
  for row in bboxes:
    merged_bbox  = cv2.addWeighted( img_bw[row[1]:row[3], row[0]:row[2]], 0.8, img[row[1]:row[3], row[0]:row[2]], 0.2, 0)
    img[row[1]:row[3], row[0]:row[2]] = merged_bbox

  return img

def euristic_detection(img, box_coordinates):
  """
  Performs heuristic detection to detect missing objects on an image.

  Parameters
  ----------
  img:
      image file
  box_coordinates:
      array of bounding boxes coordinates for products in the image
        
  Returns
  ----------
  img: np.array (Optional)
      image with missing object detected in an heuristic way.

  """
  
  x_min,x_max,y_min,y_max = box_coordinates[:,0].min(), box_coordinates[:,2].max(), box_coordinates[:,1].min(), box_coordinates[:,3].max()
  height, width, channels = img.shape

  white = np.zeros((height, width), np.uint8)

  for row in box_coordinates:
      x1, y1, x2, y2, conf, cls = row
      if cls == CLASSES.PRODUCT.value:
        white  = cv2.rectangle(white, (x1+24, y1+6), (x2-24, y2-6),
            (255,0,0),-1)

  white =  255 - white

  crop = img[y_min:y_max, x_min:x_max]

  white = white[y_min:y_max, x_min:x_max] 
  dist = cv2.distanceTransform(white, cv2.DIST_L1 , maskSize=3).astype(np.uint8)

  heatmap_img = cv2.applyColorMap(dist, cv2.COLORMAP_JET)
  
  # return merge_empty_detection(img, heatmap_img, (x_min, y_min))

  hsv=cv2.cvtColor(heatmap_img,cv2.COLOR_BGR2HSV)

  lowerValues = np.array([100, 50, 70])
  upperValues = np.array([128, 255, 255])

  bluepenMask = cv2.inRange(hsv, lowerValues, upperValues)


  heatmap_img[bluepenMask>0] = (255,255,255)
  
  return merge_empty_detection(img.copy(), heatmap_img, (x_min, y_min))

  #This is for contour
  heatmap_img = cv2.cvtColor(heatmap_img, cv2.COLOR_BGR2GRAY)
  ret, thresh = cv2.threshold(heatmap_img , 240, 255, cv2.THRESH_BINARY)
  
  # return merge_empty_detection(img, thresh, (x_min, y_min))

  contours, _ = cv2.findContours(thresh, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE )
  cv2.drawContours(img , contours, -1, (0,0,255), 7)

  return crop

def merge_empty_detection(img, detection, x_y_min):
  """
  Merge an image file with its cropped heuristic detection
  Parameters
  ----------
  img:
      image file
  detection:
      cropped heuristic detection image
  x_y_min: tuple
      x min and y min from all bounding boxes as a tuple
        
  Returns
  ----------
  img: np.array 
      Merged image
  """
  if detection.ndim == 2:
    h,w   = detection.shape
    n_channels = 1
  else:
    h,w,_ = detection.shape
    n_channels = 3
  x_min, y_min = x_y_min
  for y in range(0, h):
    for x in range(0, w):
      if detection[y,x].sum() < 255*n_channels:
        img[y+y_min,x+x_min] = detection[y,x] if detection.ndim == 3 else (0,0,255)
  return img

def NMS(boxes, overlapThresh = 0.4):
    
    """
    Receives `boxes` as a `numpy.ndarray` and gets the best bounding 
    box when there is overlapping bounding boxes.

    Parameters
    ----------
    boxes : numpy.ndarray
        Array with all the bounding boxes in the image.

    Returns
    -------
    best_bboxes: pd.DataFrame
        Dataframe with only the best bounding boxes, 
        in the format: ["xmin","ymin","xmax","ymax","class"]
    """
    
    #return an empty list, if no boxes given
    if len(boxes) == 0:
        return []
    x1 = boxes[:, 0]  # x coordinate of the top-left corner
    y1 = boxes[:, 1]  # y coordinate of the top-left corner
    x2 = boxes[:, 2]  # x coordinate of the bottom-right corner
    y2 = boxes[:, 3]  # y coordinate of the bottom-right corner

    # compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    areas = (x2 - x1 + 1) * (y2 - y1 + 1) # We have a least a box of one pixel, therefore the +1
    indices = np.arange(len(x1))
    for i,box in enumerate(boxes):

        
        temp_indices = indices[indices!=i]
        xx1 = np.maximum(box[0], boxes[temp_indices,0])
        yy1 = np.maximum(box[1], boxes[temp_indices,1])
        xx2 = np.minimum(box[2], boxes[temp_indices,2])
        yy2 = np.minimum(box[3], boxes[temp_indices,3])
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        # compute the ratio of overlap
        overlap = (w * h) / areas[temp_indices]
        
        if np.any(overlap) > overlapThresh:
            
            if box[4] == 0.0:
                continue

            indices = indices[indices != i]
            
    best_bboxes =   boxes[indices].astype(int)
    
    return best_bboxes