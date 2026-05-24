# google-classroom-mcp

An [MCP](https://modelcontextprotocol.io) server that exposes Google Classroom to LLM clients (Claude Code, Claude Desktop, Cursor, etc.) — list courses and rosters, read student submissions and their Drive attachments, grade and return work, and export weighted final grades to CSV.

Designed for teachers / lecturers who want an AI assistant in the grading loop. Runs locally over stdio; single-user OAuth against your own Google account — no hosted backend, your data never leaves your machine.

## Tools exposed to the LLM

| Tool | Purpose |
|---|---|
| `list_courses(active_only)` | Courses you teach |
| `list_students(course_id)` | Enrolled students |
| `list_coursework(course_id)` | Assignments in a course |
| `list_submissions(course_id, coursework_id)` | Student submissions + Drive attachment IDs |
| `read_drive_file(file_id, max_bytes)` | Text of an attached Drive file (Docs / Sheets / Slides exported automatically) |
| `grade_submission(course_id, coursework_id, submission_id, grade, draft)` | Set a grade (draft or assigned) |
| `return_submission(course_id, coursework_id, submission_id)` | Release the grade to the student |
| `compute_final_grades(course_id, weights)` | Weighted final grade per student; weights sum to 1.0 |
| `export_grades_csv(course_id, weights, output_path)` | Same, written to CSV |

## Prerequisites

- Python 3.11+
- A Google account that teaches at least one Classroom course
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Setup

### 1. Create a Google Cloud project + OAuth client

1. Go to <https://console.cloud.google.com> → create a project.
2. **APIs & Services → Library** → enable:
   - **Google Classroom API**
   - **Google Drive API**
3. **APIs & Services → OAuth consent screen**
   - User type: **External**
   - Add your Google account under **Test users** (lets you skip Google's verification process while the app stays in Testing mode — fine for personal use).
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**
   - Application type: **Desktop app**
   - Download the JSON file → save as `secrets/credentials.json` inside this repo.

### 2. Install

```bash
git clone https://github.com/<your-username>/google-classroom-mcp-project.git
cd google-classroom-mcp-project
uv sync       # or: pip install -e .
```

### 3. First-run OAuth consent

```bash
uv run google-classroom-mcp
```

The first run opens your browser asking you to grant the requested scopes. After consenting, `secrets/token.json` is written and subsequent runs use the refresh token silently. Press Ctrl-C to exit — the server is now ready to be launched by your MCP client.

### 4. Register the server with your MCP client

#### Claude Code

Add to `~/.claude.json` (or a project-local `.mcp.json`):

```json
{
  "mcpServers": {
    "google-classroom": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/google-classroom-mcp-project", "run", "google-classroom-mcp"]
    }
  }
}
```

#### Claude Desktop

Add the same block to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows), then restart Claude Desktop.

## OAuth scopes used

```
classroom.courses.readonly
classroom.rosters.readonly
classroom.profile.emails
classroom.coursework.students            (read + write — grade & return)
classroom.student-submissions.students.readonly
drive.readonly                           (read student-submitted Drive files)
```

If you change the scopes list, delete `secrets/token.json` to force re-consent.

## Example LLM prompts

Once registered, try asking your assistant:

- "List my active courses."
- "Show me submissions for the *Midterm Project* in CS101 and read each student's attached doc."
- "Grade submission `<id>` as 85 with feedback 'Good analysis but missing error handling'."
- "Compute final grades for CS101 with midterm 30%, final 40%, homework 30%, and export to `grades.csv`."

## Project layout

```
google-classroom-mcp-project/
├── pyproject.toml
├── src/google_classroom_mcp/
│   ├── auth.py          # OAuth desktop flow + token refresh
│   ├── classroom.py     # Classroom API wrapper + pagination
│   ├── drive.py         # Drive file reader (auto-exports Google-native docs)
│   ├── grades.py        # Weighted final grade calculator + CSV export
│   └── server.py        # MCP server — registers the tools above
├── secrets/             # gitignored — credentials.json, token.json
├── LICENSE              # MIT
└── README.md
```

## Security notes

- `secrets/credentials.json` and `secrets/token.json` are listed in `.gitignore`. Never commit them.
- The OAuth client is **yours** — every user who installs this clones the repo and creates their own OAuth client. No shared keys.
- The server runs locally over stdio and talks only to Google APIs. There is no telemetry.
- To revoke access, delete `secrets/token.json` and revoke the app at <https://myaccount.google.com/permissions>.

## Contributing

Issues and pull requests welcome. Please don't include real student data in bug reports — redact or use anonymized course IDs.

## License

MIT — see [LICENSE](LICENSE).
