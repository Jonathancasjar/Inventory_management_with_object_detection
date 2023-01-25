import hashlib
import settings 
from posixpath import splitext

def allowed_file(filename):
    """
    Checks if the format for the file received is acceptable. For this
    particular case, we must accept only image files. This is, files with
    extension ".png", ".jpg", ".jpeg" or ".gif".

    Parameters
    ----------
    filename : str
        Filename from werkzeug.datastructures.FileStorage file.

    Returns
    -------
    bool
        True if the file is an image, False otherwise.
    """
    extension = filename.split('.')[-1]
    return extension.lower() in settings.ALLOWED_EXTENSIONS and '.' in filename


def get_file_hash(file):
    """
    Returns a new filename based on the file content using MD5 hashing.
    It uses hashlib.md5() function from Python standard library to get
    the hash.

    Parameters
    ----------
    file : werkzeug.datastructures.FileStorage
        File sent by user.

    Returns
    -------
    str
        New filename based in md5 file hash.
    """
    
    extension = '.' + file.filename.split('.')[-1].lower()
    file_contents = file.read()
    md5hash = hashlib.md5(file_contents).hexdigest()
    extension = splitext(file.filename)[1]
    hashed_name = md5hash + extension
    file.seek(0)
    return hashed_name