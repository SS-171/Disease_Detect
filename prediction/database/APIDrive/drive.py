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
    return img_url
def deleteInDrive(id):
    images = drive.ListFile({'q': f"'{folderID}' in parents and trashed=false"}).GetList()
    for image in images:
        if (image['id'] == id):
            image.Trash()
            break
    
# from pydrive.drive import GoogleDrive
# from pydrive.auth import GoogleAuth
# gauth = GoogleAuth()

# drive = GoogleDrive(gauth) # Create GoogleDrive instance with authenticated GoogleAuth instance

# # Auto-iterate through all files in the root folder. Replace root with folder ID that you interested in
# file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
# for file1 in file_list:
#   print('title: %s, id: %s' % (file1['title'], file1['id']))