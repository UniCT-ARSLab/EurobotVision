import datetime
from io import BytesIO

from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaIoBaseUpload
from numpy import ndarray

# Define the Google Drive API scopes and service account file path
SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "./datacollector-419114-bdc0fad0e57d.json"
PARENT_FOLDER_ID = "1ne0IuBRl5cK_PeAnpU8PIaaRpVKQ1lFB"
drive_service: Resource | None = None


def init_drive_service() -> bool:
    """
    This function initializes the Google Drive service
    :return:
    """
    global drive_service
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        drive_service = build("drive", "v3", credentials=credentials)
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
    return False


def upload_photo(image: ndarray) -> None:
    """
    This function uploads an image to Google Drive
    :param image: The encoded image to upload
    """
    name: str = f"{datetime.datetime.now().timestamp()}.jpg"
    file_metadata = {"name": name, "parents": [PARENT_FOLDER_ID]}
    media = MediaIoBaseUpload(BytesIO(image.tobytes()), mimetype="image/jpeg")
    _ = drive_service.files().create(body=file_metadata, media_body=media).execute()
