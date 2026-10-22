import os
import requests
from dotenv import load_dotenv

load_dotenv()  # .env fills in values; real environment variables take precedence

# ==== CONFIGURATION ====
API_URL = "https://eaaa.instructure.com/api/v1"
ACCESS_TOKEN = os.environ["CANVAS_TOKEN"]  # Generate from Canvas user settings
COURSE_ID = 29933 # ID for ITA-F24V - IT Arkitektur og infrastruktur
DOWNLOAD_DIR = "course_files"        # Local folder to save files

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# ==== API HELPERS ====
def get_json(url, params=None):
    """Fetch JSON from Canvas API with pagination."""
    results = []
    while url:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        results.extend(data)

        # pagination
        if "next" in resp.links:
            url = resp.links["next"]["url"]
            params = None
        else:
            url = None
    return results


def get_course_root_folder(course_id):
    url = f"{API_URL}/courses/{course_id}/folders"
    folders = get_json(url)
    for f in folders:
        if f.get("full_name") == "course files":
            return f
    return folders[0] if folders else None


def download_file(file_obj, local_path):
    """Download a file from Canvas to the local path."""
    file_url = file_obj["url"]  # Direct download URL
    filename = file_obj["filename"]

    os.makedirs(local_path, exist_ok=True)
    file_path = os.path.join(local_path, filename)

    if os.path.exists(file_path):
        print(f"  ⏩ Skipping (already exists): {file_path}")
        return

    print(f"  ⬇️  Downloading {filename} → {file_path}")
    resp = requests.get(file_url, headers=headers, stream=True)
    resp.raise_for_status()
    with open(file_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


def process_folder(folder_id, local_path, indent=0):
    """Recursively process a folder: list + download files."""
    # List subfolders
    subfolders = get_json(f"{API_URL}/folders/{folder_id}/folders")
    files = get_json(f"{API_URL}/folders/{folder_id}/files")

    # Print and recurse into subfolders
    for sf in sorted(subfolders, key=lambda x: x["name"].lower()):
        print("  " * indent + f"📂 {sf['name']}")
        process_folder(sf["id"], os.path.join(local_path, sf["name"]), indent + 1)

    # Download files
    for f in sorted(files, key=lambda x: x["filename"].lower()):
        print("  " * indent + f"📄 {f['filename']}")
        download_file(f, local_path)


# ==== MAIN ====
if __name__ == "__main__":
    root = get_course_root_folder(COURSE_ID)
    if not root:
        print("No root folder found for this course.")
    else:
        print(f"Course File Hierarchy for course {COURSE_ID}:")
        print(f"📂 {root['name']}")
        process_folder(root["id"], os.path.join(DOWNLOAD_DIR, root["name"]), indent=1)
        print("\n✅ All files downloaded into:", DOWNLOAD_DIR)
