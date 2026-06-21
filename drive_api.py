import os
import sys
import io
import time
from googleapiclient.http import MediaIoBaseDownload

def get_remote_files(service, folder_id):
    """
    Lists all files (both folders and documents) inside a folder.
    Supports Shared Drives.
    """
    files = []
    page_token = None
    query = f"'{folder_id}' in parents and trashed = false"
    
    while True:
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType, size)',
            pageSize=100,
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        
        files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break
            
    return files

def download_file_oauth(service, file_id, dest_path, expected_size=None, export_mime_type=None):
    """
    Downloads a single file from Google Drive using the Drive API service.
    Supports Shared Drives and Google Doc export formats.
    """
    temp_dest = dest_path + ".tmp"
    if os.path.exists(temp_dest):
        try:
            os.remove(temp_dest)
        except Exception:
            pass
        
    start_time = time.time()
    try:
        if export_mime_type:
            request = service.files().export_media(fileId=file_id, mimeType=export_mime_type)
        else:
            request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
            
        # Using context manager 'with' guarantees that the file handle is closed
        # before we attempt to rename or remove the file.
        with io.FileIO(temp_dest, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request, chunksize=1024 * 1024)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    try:
                        progress = status.progress()
                        percent = progress * 100
                        bar = "=" * int(40 * progress) + "-" * (40 - int(40 * progress))
                        sys.stdout.write(f"\r    [{bar}] {percent:.1f}%")
                    except Exception:
                        sys.stdout.write(f"\r    Downloading...")
                    sys.stdout.flush()
                
        if os.path.exists(dest_path):
            os.remove(dest_path)
        os.rename(temp_dest, dest_path)
        
        duration = time.time() - start_time
        mb_downloaded = os.path.getsize(dest_path) / (1024 * 1024)
        speed = mb_downloaded / duration if duration > 0 else 0
        print(f"\n    [+] Completed in {duration:.1f}s ({speed:.2f} MB/s)")
        return True
    except Exception as e:
        print(f"\n[!] Error downloading file: {e}")
        if os.path.exists(temp_dest):
            try:
                os.remove(temp_dest)
            except Exception:
                pass
        return False
