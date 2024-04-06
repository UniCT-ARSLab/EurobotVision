import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from PIL.Image import Image
import datetime

# Define the Google Drive API scopes and service account file path
SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "./datacollector-419114-bdc0fad0e57d.json"
PARENT_FOLDER_ID = "1ne0IuBRl5cK_PeAnpU8PIaaRpVKQ1lFB"
# Create credentials using the service account file
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Build the Google Drive service
drive_service = build("drive", "v3", credentials=credentials)


def upload_photo(image: Image) -> None:
    name: str = f"{datetime.datetime.now().timestamp()}.jpg"
    file_metadata = {"name": name, "parents": [PARENT_FOLDER_ID]}
    media = MediaIoBaseUpload(io.BytesIO(image.tobytes()), mimetype="image/jpeg")
    _ = drive_service.files().create(body=file_metadata, media_body=media).execute()
