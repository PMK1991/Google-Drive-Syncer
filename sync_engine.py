import os
import time
from googleapiclient.errors import HttpError
from utils import sanitize_filename
from drive_api import get_remote_files, download_file_oauth

class SyncEngine:
    def __init__(self, service):
        self.service = service
        self.stats = {
            "downloaded": 0,
            "skipped": 0,
            "failed": 0
        }

    def sync_folder_recursive(self, folder_id, local_dir):
        """
        Recursively crawls the remote folder structure and syncs files incrementally.
        """
        if not os.path.exists(local_dir):
            print(f"[*] Creating local directory: {local_dir}")
            os.makedirs(local_dir, exist_ok=True)
            
        print(f"[*] Listing files in remote folder ID: {folder_id}...")
        try:
            items = get_remote_files(self.service, folder_id)
        except HttpError as error:
            print(f"[!] API Error while listing folder {folder_id}: {error}")
            return
            
        for item in items:
            item_id = item.get("id")
            name = item.get("name")
            mime_type = item.get("mimeType")
            size_str = item.get("size")
            
            # Avoid downloading local configuration files or sync scripts
            if name in ["sync_gdrive.py", "sync_gdrive_oauth.py", "gdrive_syncer.py", ".env", "token.json", "credentials.json", "cookies.txt", "auth.py", "utils.py", "drive_api.py", "sync_engine.py"]:
                continue
                
            safe_name = sanitize_filename(name)
            
            # Map Google Workspace files to their export MIME types and file extensions
            export_mime_type = None
            if mime_type == "application/vnd.google-apps.document":
                export_mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                if not safe_name.lower().endswith(".docx"):
                    safe_name += ".docx"
            elif mime_type == "application/vnd.google-apps.spreadsheet":
                export_mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                if not safe_name.lower().endswith(".xlsx"):
                    safe_name += ".xlsx"
            elif mime_type == "application/vnd.google-apps.presentation":
                export_mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                if not safe_name.lower().endswith(".pptx"):
                    safe_name += ".pptx"
                    
            local_path = os.path.join(local_dir, safe_name)
            
            if mime_type == "application/vnd.google-apps.folder":
                print(f"\n[dir] Entering subfolder: '{safe_name}'")
                self.sync_folder_recursive(item_id, local_path)
            else:
                size = int(size_str) if size_str else None
                print(f"\n[file] Processing file: '{safe_name}'")
                
                # Incremental check - download incrementally only
                if os.path.exists(local_path):
                    print(f"    [=] Present locally. Skipping.")
                    self.stats["skipped"] += 1
                    continue
                else:
                    print(f"    [+] Downloading new file.")
                    
                success = download_file_oauth(self.service, item_id, local_path, size, export_mime_type)
                if success:
                    self.stats["downloaded"] += 1
                else:
                    self.stats["failed"] += 1

    def sync(self, folder_id, local_dir):
        """
        Runs the full incremental sync.
        """
        start_time = time.time()
        self.sync_folder_recursive(folder_id, local_dir)
        duration = time.time() - start_time
        
        print("\n" + "="*50)
        print("Incremental Sync Summary:")
        print(f"  Up-to-date (skipped): {self.stats['skipped']}")
        print(f"  Downloaded:           {self.stats['downloaded']}")
        print(f"  Failed:               {self.stats['failed']}")
        print(f"  Total Duration:       {duration/60:.1f} minutes")
        print("="*50)
