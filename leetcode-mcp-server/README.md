# LeetCode MCP Server

MCP server for LeetCode (leetcode.com and leetcode.cn): problems, daily challenge, user profile, submissions, contest performance, and notes.

**Note:** LeetCode does not publish an official API. This server uses the same GraphQL backend as the website (reverse-engineered). It may break if LeetCode changes their schema or endpoints.

## Features

- **Multi-site:** `site`: `"global"` (leetcode.com) or `"china"` (leetcode.cn). Default: `"global"`.
- **Problem data:** Get problem by slug, list with filters (difficulty, tags, category, keyword), daily challenge.
- **User data:** Public profile, recent submissions, contest performance.
- **Private data (auth required):** Your submissions, submission detail (code/verdict), your notes per problem.

## Authentication

Private data (my submissions, submission detail, my notes) requires browser cookies:

1. Log in at [leetcode.com](https://leetcode.com) (or [leetcode.cn](https://leetcode.cn)).
2. Open DevTools (F12) → Application → Storage → Cookies.
3. Copy `LEETCODE_SESSION` and `csrftoken` (or `LEETCODE_CN_*` for China).

Set environment variables (do not commit real values):

| Variable | Site | Description |
|----------|------|-------------|
| `LEETCODE_SESSION` | global | Session cookie |
| `LEETCODE_CSRF` | global | CSRF token |
| `LEETCODE_CN_SESSION` | China | Session cookie |
| `LEETCODE_CN_CSRF` | China | CSRF token |

If a tool needs auth and credentials are missing, you'll get: *"Authentication required. Set LEETCODE_SESSION and LEETCODE_CSRF for global, or LEETCODE_CN_SESSION and LEETCODE_CN_CSRF for China."*

## Cursor setup

In `.cursor/mcp.json` (project or global `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "leetcode": {
      "command": "node",
      "args": ["d:/AI_Work/leetcode-mcp-server/dist/index.js"],
      "env": {
        "LEETCODE_SESSION": "",
        "LEETCODE_CSRF": "",
        "LEETCODE_CN_SESSION": "",
        "LEETCODE_CN_CSRF": ""
      }
    }
  }
}
```

Fill in the env values for the sites you use (or leave empty for public-only). Restart Cursor after changing `mcp.json`.

## Tools

| Tool | Description |
|------|-------------|
| `get_problem` | Full problem by title slug (description, constraints, examples, hints, snippets, tags). |
| `get_problem_list` | List problems; optional `difficulty`, `tags`, `category`, `keyword`, `limit`, `offset`. |
| `search_problems` | Search problems by `category`, `tags`, `difficulty`, `searchKeywords` (titles/slugs), `limit`, `offset`. Default category: `all-code-essentials`, default limit: 10. |
| `get_daily_challenge` | Today's daily challenge. |
| `get_user_profile` | Public user profile by username. |
| `get_user_submissions` | Recent public submissions for a user; use `username: "me"` with auth for own. |
| `get_my_submissions` | All submissions for the authenticated user (global only; auth required). |
| `get_submission_detail` | Submission detail including code (auth required). |
| `get_contest_performance` | User contest ranking and history. |
| `create_note` | Create or update your note for a problem: `questionId`, `content` (markdown), optional `summary`. Auth required; uses undocumented API. |
| `update_note` | Update an existing note: `noteId` (question ID or slug), `content`, optional `summary`. Auth required. |
| `get_problem_notes` | Your note(s) for one problem by `questionId` (numeric ID or title slug); `limit`, `skip`. Auth required. |
| `search_notes` | Search your notes by `keyword`, with `limit`, `skip`, `orderBy` (ASCENDING/DESCENDING). Auth required; scans up to 50 problems from your progress. |
| `get_my_notes` | Your note for a problem (auth required); pass `titleSlug`. |
| `list_problem_solutions` | Community solutions for a problem: `questionSlug`, `limit`, `skip`, `userInput`, `tagSlugs`, `orderBy` (Global: HOT/MOST_RECENT/MOST_VOTES; CN: DEFAULT/MOST_UPVOTE/HOT/NEWEST_TO_OLDEST/OLDEST_TO_NEWEST). |
| `get_problem_solution` | Full content of one community solution. Global: pass `topicId`. China: pass `slug`. |
| `get_solution` | Official solution by ID (from `problem.solution.id`); may be paid-only. |

All tools accept optional `site`: `"global"` or `"china"` (default `"global"`).

## Build and run

```bash
cd leetcode-mcp-server
npm install
npm run build
npm start
```

The server uses stdio; Cursor (or another MCP client) spawns it and communicates over stdin/stdout.

## Rate limiting

The server uses the default rate limiter from `leetcode-query` (e.g. 20 requests per 10 seconds). If you see rate-limit errors, wait and retry.
