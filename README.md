# Canvas Course Members & Files API Tools

Python scripts that use the Canvas LMS API:

- **app.py**: fetches course members, writes `members.csv`, and can generate an HTML roster.
- **files.py**: downloads all course files into `course_files/`.
- **user.py**: prints the JSON profile of one Canvas user.

## Setup (Bash)

Requires Python 3.10+.

```bash
# If a venv from another OS exists, remove it first
rm -rf venv

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create an access token in Canvas (**Account** → **Settings** → **Approved Integrations** → **+ New Access Token**) and provide it as `CANVAS_TOKEN` in one of two ways.

**Option 1: `.env` file** (git-ignored). Edit `.env` in the project folder:

```
CANVAS_TOKEN=your_canvas_api_access_token_here
```

**Option 2: environment variable**:

```bash
export CANVAS_TOKEN="your_canvas_api_access_token_here"
```

If both are set, the environment variable wins over `.env`. For a single run: `CANVAS_TOKEN=other_token python app.py`.

## Usage

```bash
# Members -> members.csv
python app.py

# HTML roster (roster.html, or a custom filename)
python app.py --html
python app.py --html my_course_roster.html

# Custom columns / course
python app.py --html roster.html --columns 5 --course-id 33075

# Download course files
python files.py

# Inspect a single user
python user.py
```

`app.py` options:

| Option | Default | Description |
| :--- | :--- | :--- |
| `--html [FILENAME]` | off (`roster.html` if no value) | Generate HTML roster |
| `--columns N` | `5` | Columns in the HTML roster |
| `--course-id ID` | `33075` | Canvas course ID |
| `--csv FILENAME` | `members.csv` | Output CSV (`""` disables) |
| `-h`, `--help` | | Show help |
