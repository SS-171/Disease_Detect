from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive =GoogleDrive(gauth)
folderID = "1jjGgoBnkTXLNKt2SjZk45mnqKtH28k-R"
def saveToDrive(img, name):
    file1 = drive.CreateFile({"parents":[{"id": f"{folderID}"}],
    "title" :f"{name}"})
    file1.SetContentFile(img)
    file1.Upload()
    print("title : %s, id: %s" % (file1['title'], file1['id']))
    img_url = f"https://drive.google.com/uc?export=view&id={file1['id']}"
    res = {"image_url": img_url, "image_id" : file1['id']}
    return res
def deleteDateDriveData(id_list):
    images = drive.ListFile({'q': f"'{folderID}' in parents and trashed=false"}).GetList()
    for image in images:
        if (image['id'] in id_list):
            image.Delete()

    
