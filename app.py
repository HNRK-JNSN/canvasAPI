import os
import requests
from dotenv import load_dotenv
import csv
import argparse
import html

load_dotenv()  # .env fills in values; real environment variables take precedence

# ==== CONFIGURATION ====
API_URL = "https://eaaa.instructure.com/api/v1"
ACCESS_TOKEN = os.environ["CANVAS_TOKEN"]
#COURSE_ID = 31225 # ID for ITA-E23A - Arkitektur Principper i praksis
# COURSE_ID = 29931 # ITA-E24A - Cloud Computing
# COURSE_ID = 29933 # ID for ITA-F24V - IT Arkitektur og infrastruktur
#COURSE_ID = 33072 # ID for ITA-F25v - IT Arkitektur og infrastruktur
COURSE_ID = 33075 # ID for ITA-F24 - Arkitektur principper i praksis


# ==== API CALL FUNCTION ====
def get_course_members(course_id):
    url = f"{API_URL}/courses/{course_id}/enrollments"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    params = {
        "per_page": 100,   # get 100 users per page
        "type[]": ["StudentEnrollment", "TaEnrollment"],
        "include[]": ["avatar_url"]
    }

    members = []
    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        members.extend(data)

        # Handle pagination
        if "next" in response.links:
            url = response.links["next"]["url"]
            params = {}
        else:
            url = None

    return members

# ==== SAVE TO CSV ====
def save_to_csv(members, filename="members.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "User ID", "Login ID", "Avatar URL"])  # header row
        for m in members:
            user = m.get("user", {})
            writer.writerow([
                user.get("name"),
                user.get("id"),
                user.get("login_id"),
                user.get("avatar_url"),
            ])

# ==== GENERATE HTML ROSTER MATRIX ====
def generate_roster_html(members, filename="roster.html", columns=5, course_id=None):
    default_avatar = (
        "data:image/svg+xml;utf8,"
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' fill='%2394a3b8'>"
        "<rect width='100' height='100' fill='%23f1f5f9'/>"
        "<circle cx='50' cy='36' r='22' fill='%23cbd5e1'/>"
        "<path d='M18,90 C18,66 32,60 50,60 C68,60 82,66 82,90 Z' fill='%23cbd5e1'/>"
        "</svg>"
    )

    cards_html = []
    for m in members:
        user = m.get("user", {})
        name = html.escape(user.get("name") or "Unknown")
        avatar_url = user.get("avatar_url") or default_avatar
        login_id = html.escape(user.get("login_id") or "")
        role = html.escape(m.get("type", "").replace("Enrollment", ""))

        cards_html.append(f"""
        <div class="card">
            <div class="avatar-container">
                <img src="{avatar_url}" alt="{name}" onerror="this.onerror=null;this.src='{default_avatar}';" class="avatar" loading="lazy" />
            </div>
            <div class="name" title="{name}">{name}</div>
            <div class="meta">{login_id}</div>
            {f'<div class="badge">{role}</div>' if role and role != "Student" else ''}
        </div>""")

    cards_str = "\n".join(cards_html)
    course_title = f"Course Roster - Course ID {course_id}" if course_id else "Course Roster"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(course_title)}</title>
    <style>
        :root {{
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #0f172a;
            --text-sub: #64748b;
            --border: #e2e8f0;
            --accent: #2563eb;
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.07), 0 2px 4px -2px rgb(0 0 0 / 0.07);
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            padding: 2.5rem 1.5rem;
        }}
        .header {{
            max-width: 1400px;
            margin: 0 auto 2.5rem auto;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-main);
            margin-bottom: 0.5rem;
            letter-spacing: -0.025em;
        }}
        .header p {{
            color: var(--text-sub);
            font-size: 1.05rem;
        }}
        .matrix-grid {{
            max-width: 1400px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat({columns}, 1fr);
            gap: 1.25rem;
        }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.25rem 1rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            box-shadow: var(--shadow);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        }}
        .avatar-container {{
            width: 96px;
            height: 96px;
            margin-bottom: 0.85rem;
            border-radius: 50%;
            overflow: hidden;
            background: #e2e8f0;
            border: 2px solid #cbd5e1;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .avatar {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }}
        .name {{
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 0.25rem;
            line-height: 1.3;
            max-width: 100%;
            word-wrap: break-word;
        }}
        .meta {{
            font-size: 0.8rem;
            color: var(--text-sub);
        }}
        .badge {{
            margin-top: 0.4rem;
            font-size: 0.7rem;
            font-weight: 600;
            padding: 0.15rem 0.5rem;
            border-radius: 9999px;
            background: #eff6ff;
            color: #1d4ed8;
        }}
        @media (max-width: 1100px) {{
            .matrix-grid {{
                grid-template-columns: repeat(3, 1fr);
            }}
        }}
        @media (max-width: 680px) {{
            .matrix-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        @media (max-width: 440px) {{
            .matrix-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .matrix-grid {{
                grid-template-columns: repeat({columns}, 1fr) !important;
                gap: 0.75rem;
            }}
            .card {{
                box-shadow: none;
                border: 1px solid #ccc;
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>{html.escape(course_title)}</h1>
        <p>Total Members: {len(members)} &bull; {columns}-Column Matrix View</p>
    </header>
    <main class="matrix-grid">
        {cards_str}
    </main>
</body>
</html>
"""
    with open(filename, mode="w", encoding="utf-8") as f:
        f.write(html_content)

# ==== MAIN ====
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch Canvas course members and optionally generate an HTML roster matrix or CSV export."
    )
    parser.add_argument(
        "--course-id",
        type=int,
        default=COURSE_ID,
        help=f"Canvas Course ID (default: {COURSE_ID})",
    )
    parser.add_argument(
        "--csv",
        type=str,
        default="members.csv",
        help="Path to output CSV file (default: members.csv, pass '' to disable)",
    )
    parser.add_argument(
        "--html",
        nargs="?",
        const="roster.html",
        default=None,
        metavar="FILENAME",
        help="Generate an HTML roster matrix view of students in columns (default: roster.html)",
    )
    parser.add_argument(
        "--columns",
        type=int,
        default=5,
        help="Number of columns in the HTML roster matrix (default: 5)",
    )

    args = parser.parse_args()

    course_id = args.course_id
    members = get_course_members(course_id)

    # Extract names and sort alphabetically
    sorted_members = sorted(
        members, key=lambda m: m.get("user", {}).get("name", "").lower()
    )

    print(f"Found {len(sorted_members)} members in course {course_id}:\n")
    for m in sorted_members:
        user = m.get("user", {})
        print(f"- {user.get('name')} ({m.get('type')}) | Avatar: {user.get('avatar_url')}")

    # Save to CSV if specified
    if args.csv:
        save_to_csv(sorted_members, filename=args.csv)
        print(f"\n✅ Members saved to CSV: {args.csv}")

    # Generate HTML matrix view if specified
    if args.html:
        generate_roster_html(
            sorted_members,
            filename=args.html,
            columns=args.columns,
            course_id=course_id,
        )
        print(f"✅ Roster matrix view generated ({args.columns} columns): {args.html}")

