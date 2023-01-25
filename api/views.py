import json
import os
import settings
import utils
from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from middleware import model_predict

router = Blueprint("app_router", __name__, template_folder="templates")

@router.route("/new_prediction", methods=["GET"])
def new_upload():
  # context = {
  #             'models' : settings.AVAILABLE_MODELS
  #           }
  #return render_template("index.html", context=context, scroll="upload_image")
  return render_template("index.html",  scroll="upload_image")




@router.route("/", methods=["GET", "POST"])
def index():
    """
    GET: Index endpoint, renders our HTML code.

    POST: Used in our frontend so we can upload and show an image.
    When it receives an image from the UI, it also calls our ML model to
    get and display the predictions.
    """
    
    if request.method == "GET":
        return render_template("index.html")

    if request.method == "POST":
        # No file received, show basic UI
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)

        # File received but no filename is provided, show basic UI
        file = request.files["file"]
        if file.filename == "":
            flash("No image selected for uploading")
            return redirect(request.url)

        # File received and it's an image, we must show it and get predictions
        if file and utils.allowed_file(file.filename):
            
            # Creates unique name
            img_name = utils.get_file_hash(file)
            img_path = os.path.join(settings.UPLOAD_FOLDER,img_name)
            
            # Stores image in 'static\uploads'
            print('PATH:' , img_path)
            file.save(img_path)
            file.close()
            if 'rbtn_output_selection' in request.form:
              annotation_style = request.form['rbtn_output_selection']
            else:
              flash("** Please select an annotation style")
              return redirect(request.url+"#upload_image")

            if "heuristic" in request.form:
              show_heuristic = True
            else:
              show_heuristic = False
            
            print(request.form)
            print(img_name)
            print(annotation_style)

            # Sent image to be processed by the ML model
            mAP = model_predict(img_name, annotation_style, show_heuristic)
        
            # Updates context
            context = {
                    "mAP": mAP,
                    "filename": img_path,
                    "annotation_style": annotation_style,
                    "show_heuristic": show_heuristic
                    }
            
            # Update `render_template()` parameters as needed 
            return render_template("index.html", filename=img_name, context=context)
        # File received and but it isn't an image
        else:
            flash("Allowed image types are -> png, jpg, jpeg, gif")
            return redirect(request.url)


@router.route("/display/<filename>")
def display_image(filename):
    """
    Display image uploaded.
    """
    return redirect(url_for("static", filename="uploads/" + filename))

@router.route("/display_bbox/<filename>")
def display_bbox(filename):
    """
    Display image predicted by the model in our UI.
    """
    basename, extension = os.path.splitext(filename)
    filename2 = basename + "_bbox" + extension

    return redirect(url_for("static", filename="predictions/" + filename2))

@router.route("/display_heatmap/<filename>")
def display_heatmap(filename):
    """
    Display image predicted by the model in our UI.
    """
    basename, extension = os.path.splitext(filename)
    filename2 = basename + "_heat" + extension

    return redirect(url_for("static", filename="predictions/" + filename2))

@router.route("/display_heuristic/<filename>")
def display_heuristic(filename):
    """
    Display image predicted by the model in our UI.
    """
    basename, extension = os.path.splitext(filename)
    filename2 = basename + "_heur" + extension

    return redirect(url_for("static", filename="predictions/" + filename2))

@router.route("/predict", methods=["GET", "POST"])
def predict(file = None):
    """
    Endpoint used to get predictions without need to access the UI.

    Parameters
    ----------
    file : str
        Input image we want to get predictions from.

    Returns
    -------
    flask.Response
        JSON response from our API having the following format:
            {
                "success": bool,
                "prediction": str,
                "score": float,
            }

        - "success" will be True if the input file is valid and we get a
          prediction from our ML model.
        - "prediction" model predicted class as string.
        - "score" model confidence score for the predicted class as float.
    """
    
    response_data = {"success": False, "prediction": None, "score": None} 
    status_code = 400
     
    if request.method == "GET":  
        status_code = 405
        
    elif request.method == "POST":
        
        # Check for file received 
        if "file" in request.files: file = request.files['file']
        
        # File received and it's an image, we must show it and get predictions
        if file and utils.allowed_file(file.filename):
            
            # 1. Creates unique name
            img_name = utils.get_file_hash(file)
            img_path = os.path.join(settings.UPLOAD_FOLDER,img_name)
            # 2. Stores image in '\upload'
            file.save(img_path)
            
            # 3. Sents image to be processed by the ML model
            prediction, score = model_predict(img_name)
            
            # 4. Updates Response
            response_data  = {"success": True, "prediction": prediction, "score": score}
            status_code = 200
            
            # checks for BottleNeck response
            if prediction == 'BottleNeck': 
                response_data  = {"success": False, "prediction": prediction, "score": score}
                status_code = 400
            
        # File received but it isn't an image
        else:
            flash("Allowed image types are -> png, jpg, jpeg, gif") 
            # rpse = current_app.response_class( response = json.dumps(data), status = 400, mimetype = 'application/json')    # Instead of: rpse = {"Error": 'HTTP Bad Request', "status_code": 400, "prediction": None, "score": None}
        
    return current_app.response_class( response = json.dumps(response_data), status = status_code, mimetype = settings.RPSE_MIMETYPE) 
    


@router.route("/feedback", methods=["GET", "POST"])
def feedback():
    """
    Store feedback from users about wrong predictions on a plain text file.

    Parameters
    ----------
    report : request.form
        Feedback given by the user with the following JSON format:
            {
                "filename": str,
                "prediction": str,
                "score": float
            }

        - "filename" corresponds to the image used stored in the uploads
          folder.
        - "prediction" is the model predicted class as string reported as
          incorrect.
        - "score" model confidence score for the predicted class as float.
    """
    # Get report 
    if request.method == "GET": 
        report_str = request.form.get("report")
        
    elif request.method == "POST":
        
        report_str = request.form.get("report")
        if report_str:
            report_path = settings.FEEDBACK_FILEPATH
            with open(report_path, 'a') as f:
                f.write(report_str+'\n')

    return render_template("index.html")