/**
 * LeetCode MCP Server – tools for leetcode.com and leetcode.cn.
 * Transport: stdio. Credentials via env: LEETCODE_SESSION, LEETCODE_CSRF, LEETCODE_CN_*.
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import * as z from "zod";
import { getClient, requireAuth } from "./leetcode.js";
function textResult(text, isError = false) {
    return { content: [{ type: "text", text }], isError };
}
function safeJson(obj) {
    return JSON.stringify(obj, null, 2);
}
const server = new McpServer({ name: "leetcode-mcp-server", version: "1.0.0" }, { capabilities: {} });
const siteSchema = z.enum(["global", "china"]).optional().default("global");
// Global: TopicSortingOption is typically lowercase in API (hot, most_recent, most_votes)
// CN: may use different enum values
const COMMUNITY_SOLUTIONS_QUERY = `
query communitySolutions($questionSlug: String!, $skip: Int!, $first: Int!, $query: String, $orderBy: TopicSortingOption, $languageTags: [String!], $topicTags: [String!]) {
  questionSolutions(
    filters: {questionSlug: $questionSlug, skip: $skip, first: $first, query: $query, orderBy: $orderBy, languageTags: $languageTags, topicTags: $topicTags}
  ) {
    hasDirectResults
    totalNum
    solutions {
      id
      title
      commentCount
      topLevelCommentCount
      viewCount
      pinned
      isFavorite
      solutionTags { name slug }
      post {
        id
        status
        voteCount
        creationDate
        isHidden
        author {
          username
          isActive
          nameColor
          activeBadge { displayName icon }
          profile { userAvatar reputation }
        }
      }
      searchMeta { content contentType }
    }
  }
}
`;
// Single community solution by topic ID (Global). CN may use slug.
const COMMUNITY_SOLUTION_TOPIC_QUERY = `
query communitySolution($topicId: Int!) {
  topic(id: $topicId) {
    id
    viewCount
    topLevelCommentCount
    commentCount
    subscribed
    title
    pinned
    solutionTags { name slug }
    hideFromTrending
    isFavorite
    post {
      id
      voteCount
      voteStatus
      content
      updationDate
      creationDate
      status
      isHidden
      author {
        isDiscussAdmin
        isDiscussStaff
        username
        nameColor
        activeBadge { displayName icon }
        profile { userAvatar reputation }
        isActive
      }
      authorIsModerator
      isOwnPost
    }
  }
}
`;
// --- get_problem ---
server.registerTool("get_problem", {
    description: "Get full problem details by title slug (description, constraints, examples, hints, code snippets, tags).",
    inputSchema: {
        titleSlug: z.string().describe("Problem slug, e.g. two-sum"),
        site: siteSchema,
    },
}, async ({ titleSlug, site }) => {
    try {
        const { client } = getClient(site);
        const slug = titleSlug.toLowerCase().replace(/\s/g, "-");
        const problem = await client.problem(slug);
        return textResult(safeJson(problem));
    }
    catch (err) {
        return textResult(`Error: ${err instanceof Error ? err.message : String(err)}`, true);
    }
});
// --- get_problem_list ---
server.registerTool("get_problem_list", {
    description: "List problems with optional filters: difficulty, tags, category, keyword. Returns id, title, slug, difficulty, tags.",
    inputSchema: {
        difficulty: z.enum(["EASY", "MEDIUM", "HARD"]).optional(),
        tags: z.array(z.string()).optional().describe("Tag slugs"),
        category: z.string().optional().describe("e.g. algorithm, database"),
        keyword: z.string().optional().describe("Filter by title/slug keyword (client-side)"),
        limit: z.number().min(1).max(100).optional().default(50),
        offset: z.number().min(0).optional().default(0),
        site: siteSchema,
    },
}, async ({ difficulty, tags, category, limit, offset, keyword, site }) => {
    try {
        const { client } = getClient(site);
        const filters = {};
        if (difficulty)
            filters.difficulty = difficulty;
        if (tags?.length)
            filters.tags = tags;
        const list = await client.problems({
            category: category ?? "",
            offset,
            limit,
            filters: Object.keys(filters).length ? filters : {},
        });
        let questions = list.questions ?? [];
        if (keyword?.trim()) {
            const k = keyword.toLowerCase();
            questions = questions.filter((q) => {
                const o = q;
                return ((o.title && String(o.title).toLowerCase().includes(k)) ||
                    (o.titleSlug && String(o.titleSlug).toLowerCase().includes(k)));
            });
        }
        return textResult(safeJson({ total: list.total ?? questions.length, questions }));
    }
    catch (err) {
        return textResult(`Error: ${err instanceof Error ? err.message : String(err)}`, true);
    }
});
// --- search_problems ---
server.registerTool("search_problems", {
    description: "Searches for LeetCode problems based on multiple filter criteria: category, tags, difficulty, and keywords in problem titles. Returns matching problems with id, title, slug, difficulty, and tags.",
    inputSchema: {
        category: z
            .string()
            .optional()
            .default("all-code-essentials")
            .describe("Problem category filter (e.g. all-code-essentials, algorithm, database)"),
        tags: z.array(z.string()).optional().describe("Topic tags to filter by (e.g. array, hash-table)"),
        difficulty: z.enum(["EASY", "MEDIUM", "HARD"]).optional().describe("Difficulty level"),
        searchKeywords: z
            .string()
            .optional()
            .describe("Keywords to search in problem titles and slugs"),
        limit: z.number().min(1).max(100).optional().default(10).describe("Maximum number of problems to return"),
        offset: z.number().min(0).optional().default(0).describe("Number of problems to skip"),
        site: siteSchema,
    },
}, async ({ category, tags, difficulty, searchKeywords, limit, offset, site }) => {
    try {
        const { client } = getClient(site);
        const filters = {};
        if (difficulty)
            filters.difficulty = difficulty;
        if (tags?.length)
            filters.tags = tags;
        const list = await client.problems({
            category: category ?? "all-code-essentials",
            offset,
            limit,
            filters: Object.keys(filters).length ? filters : {},
        });
        let questions = list.questions ?? [];
        if (searchKeywords?.trim()) {
            const k = searchKeywords.toLowerCase();
            questions = questions.filter((q) => {
                const o = q;
                return ((o.title && String(o.title).toLowerCase().includes(k)) ||
                    (o.titleSlug && String(o.titleSlug).toLowerCase().includes(k)));
            });
        }
        return textResult(safeJson({ total: list.total ?? questions.length, questions }));
    }
    catch (err) {
        return textResult(`Error: ${err instanceof Error ? err.message : String(err)}`, true);
    }
});
// --- get_daily_challenge ---
server.registerTool("get_daily_challenge", {
    description: "Retrieves today's LeetCode Daily Challenge problem with complete details: description, constraints, examples, hints, code snippets, tags, solution metadata, and challenge date/link.",
    inputSchema: { site: siteSchema },
}, async ({ site }) => {
    try {
        const { client } = getClient(site);
        const c = client;
        const daily = await c.daily();
        // Global: daily has .question; China: daily is todayRecord[0], question may be at .question
        const questionRef = daily?.question ?? daily;
        const titleSlug = (questionRef && "titleSlug" in questionRef && questionRef.titleSlug) ||
            (daily && "titleSlug" in daily && daily.titleSlug);
        if (!titleSlug) {
            return textResult(safeJson({ daily, note: "Could not resolve titleSlug for full problem fetch" }));
        }
        const fullProblem = await c.problem(titleSlug);
        const meta = daily;
        const result = {
            date: meta?.date,
            link: meta?.link,
            question: fullProblem,
        };
        return textResult(safeJson(result));
    }
    catch (err) {
        return textResult(`Error: ${err instanceof Error ? err.message : String(err)}`, true);
    }
});
// --- get_user_profile ---
server.registerTool("get_user_profile", {
    description: "Get public user profile (avatar, ranking, stats, etc.).",
    inputSchema: {
        username: z.string().describe("LeetCode username"),
        site: siteSchema,
    },
}, async ({ username, site }) => {
    try {
        const { client } = getClient(site);
        const profile = await client.user(username);
        return textResult(safeJson(profile));
    }
    catch (err) {
        return textResult(`Error: ${err instanceof Error ? err.message : String(err)}`, true);
    }
});
// --- get_user_submissions ---
server.registerTool("get_user_submissions", {
    description: "Get recent public submissions for a user (global: max 20; China may return more). Use username 'me' with auth for own submissions on global.",
    inputSchema: {
        username: z.string(),
        limit: z.number().min(1).max(50).optional().default(20),
        site: siteSchema,
    },
}, async ({ username, limit, site }) => {
    try {
        const { client, hasAuth } = getClient(site);
        const c = client;
        let uname = username;
        if (username === "me" && hasAuth) {
            if (site === "china" && c.userStatus) {
                const status = await c.userStatus();
                uname = status?.userSlug ?? status?.username ?? username;
            }
            else if (c.whoami) {
                const who = await c.whoami();
                uname = who?.username ?? username;
            }
        }
        const submissions = site === "china"
            ? await c.recent_submissions(uname)
            : await c.recent_submissions(uname, limit);
        return textResult(safeJson(submissions));
    }
    catch (err) {
        return textResult(`Error: ${err instanceof Error ? err.message : String(err)}`, true);
    }
});
// --- get_my_submissions ---
server.registerTool("get_my_submissions", {
    description: "Get all submissions for the authenticated user. Auth required. Global only; for China use get_user_submissions with your username.",
    inputSchema: {
        limit: z.number().min(1).max(100).optional().default(20),
        offset: z.number().min(0).optional().default(0),
        slug: z.string().optional().describe("Filter by problem slug"),
        site: siteSchema,
    },
}, async ({ limit, offset, slug, site }) => {
    try {
        requireAuth(site);
        const { client } = getClient(site);
        if (site === "china") {
            return textResult("On China site use get_user_submissions with your username, or problem_submissions per problem. get_my_submissions (full list) is supported for global site only.", true);
        }
        const submissions = await client.submissions({ limit, offset, slug });
        return textResult(safeJson(submissions));
    }
    catch (err) {
        return textResult(err instanceof Error ? err.message : String(err), true);
    }
});
// --- get_submission_detail ---
server.registerTool("get_submission_detail", {
    description: "Get submission detail including code and verdict. Auth required for full detail.",
    inputSchema: {
        submissionId: z.union([z.string(), z.number()]).describe("Submission ID"),
        site: siteSchema,
    },
}, async ({ submissionId, site }) => {
    try {
        requireAuth(site);
        const { client } = getClient(site);
        const id = typeof submissionId === "string" ? submissionId : String(submissionId);
        const numId = typeof submissionId === "number" ? submissionId : parseInt(id, 10);
        if (site === "china") {
            const detail = await client.submissionDetail(id);
            return textResult(safeJson(detail));
        }
        const detail = await client.submission(Number.isNaN(numId) ? parseInt(id, 10) : numId);
        return textResult(safeJson(detail));
    }
    catch (err) {
        return textResult(err instanceof Error ? err.message : String(err), true);
    }
});
// --- get_contest_performance ---
server.registerTool("get_contest_performance", {
    description: "Get user contest ranking and history.",
    inputSchema: {
        username: z.string(),
        site: siteSchema,
    },
}, async ({ username, site }) => {
    try {
        const { client } = getClient(site);
        const info = await client.user_contest_info(username);
        return textResult(safeJson(info));
    }
    catch (err) {
        return textResult(`Error: ${err instanceof Error ? err.message : String(err)}`, true);
    }
});
// --- create_note ---
const UPDATE_NOTE_MUTATION = `
  mutation updateNote($titleSlug: String!, $content: String!) {
    updateNote(titleSlug: $titleSlug, content: $content) {
      ok
      __typename
    }
  }
`;
server.registerTool("create_note", {
    description: "Creates or updates your note for a specific LeetCode problem. Auth required. Uses LeetCode's undocumented GraphQL mutation; may not be available on all sites.",
    inputSchema: {
        questionId: z.string().describe("Question ID (e.g. 1) or title slug (e.g. two-sum) of the problem"),
        content: z.string().describe("The content of the note (supports markdown)"),
        summary: z.string().optional().describe("Optional short summary or title for the note (prepended to content)"),
        site: siteSchema,
    },
}, async ({ questionId, content, summary, site }) => {
    try {
        requireAuth(site);
        const { client } = getClient(site);
        const c = client;
        const idTrim = questionId.trim();
        let titleSlug;
        if (/^\d+$/.test(idTrim)) {
            const list = await c.problems({ category: "", offset: 0, limit: 3000 });
            const q = (list.questions ?? []).find((p) => String(p.questionFrontendId) === idTrim);
            if (!q?.titleSlug) {
                return textResult(safeJson({ error: `No problem found with question ID "${questionId}"` }), true);
            }
            titleSlug = q.titleSlug;
        }
        else {
            titleSlug = idTrim.toLowerCase().replace(/\s/g, "-");
        }
        const noteContent = summary?.trim()
            ? `## ${summary.trim()}\n\n${content.trim()}`
            : content.trim();
        if (!c.graphql) {
            return textResult(safeJson({
                error: "create_note is not supported: GraphQL mutation not available on this client.",
            }), true);
        }
        const res = await c.graphql({
            query: UPDATE_NOTE_MUTATION,
            variables: { titleSlug, content: noteContent },
        });
        if (res?.errors?.length) {
            const msg = res.errors.map((e) => e?.message ?? "Unknown error").join("; ");
            return textResult(safeJson({
                error: "LeetCode API rejected the note update.",
                details: msg,
                hint: "The note mutation may have changed or may not be available for your account.",
            }), true);
        }
        return textResult(safeJson({
            success: true,
            questionId,
            titleSlug,
            summary: summary ?? null,
            message: "Note created or updated. Verify on LeetCode.",
        }));
    }
    catch (err) {
        return textResult(err instanceof Error ? err.message : String(err), true);
    }
});
// --- update_note ---
server.registerTool("update_note", {
    description: "Updates an existing note for a LeetCode problem with new content or summary. noteId is the problem's question ID or title slug. Auth required. Uses same undocumented API as create_note.",
    inputSchema: {
        noteId: z.string().describe("ID of the note to update (question ID e.g. 1, or title slug e.g. two-sum)"),
        content: z.string().describe("The new content for the note (supports markdown)"),
        summary: z.string().optional().describe("Optional new short summary or title for the note (prepended to content)"),
        site: siteSchema,
    },
}, async ({ noteId, content, summary, site }) => {
    try {
        requireAuth(site);
        const { client } = getClient(site);
        const c = client;
        const idTrim = noteId.trim();
        let titleSlug;
        if (/^\d+$/.test(idTrim)) {
            const list = await c.problems({ category: "", offset: 0, limit: 3000 });
            const q = (list.questions ?? []).find((p) => String(p.questionFrontendId) === idTrim);
            if (!q?.titleSlug) {
                return textResult(safeJson({ error: `No problem found with note ID "${noteId}"` }), true);
            }
            titleSlug = q.titleSlug;
        }
        else {
            titleSlug = idTrim.toLowerCase().replace(/\s/g, "-");
        }
        const noteContent = summary?.trim()
            ? `## ${summary.trim()}\n\n${content.trim()}`
            : content.trim();
        if (!c.graphql) {
            return textResult(safeJson({
                error: "update_note is not supported: GraphQL mutation not available on this client.",
            }), true);
        }
        const res = await c.graphql({
            query: UPDATE_NOTE_MUTATION,
            variables: { titleSlug, content: noteContent },
        });
        if (res?.errors?.length) {
            const msg = res.errors.map((e) => e?.message ?? "Unknown error").join("; ");
            return textResult(safeJson({
                error: "LeetCode API rejected the note update.",
                details: msg,
                hint: "The note mutation may have changed or may not be available for your account.",
            }), true);
        }
        return textResult(safeJson({
            success: true,
            noteId,
            titleSlug,
            summary: summary ?? null,
            message: "Note updated. Verify on LeetCode.",
        }));
    }
    catch (err) {
        return textResult(err instanceof Error ? err.message : String(err), true);
    }
});
// --- get_problem_notes ---
server.registerTool("get_problem_notes", {
    description: "Retrieves user notes for a specific LeetCode problem by question ID or title slug. Auth required. Returns your note(s) for that problem with optional pagination (skip/limit).",
    inputSchema: {
        questionId: z.string().describe("Question ID (e.g. 1) or title slug (e.g. two-sum) of the problem"),
        limit: z.number().min(1).max(50).optional().default(10).describe("Maximum number of notes to return"),
        skip: z.number().min(0).optional().default(0).describe("Number of notes to skip"),
        site: siteSchema,
    },
}, async ({ questionId, limit, skip, site }) => {
    try {
        requireAuth(site);
        const { client } = getClient(site);
        const c = client;
        const idTrim = questionId.trim();
        let titleSlug;
        if (/^\d+$/.test(idTrim)) {
            const list = await c.problems({ category: "", offset: 0, limit: 3000 });
            const q = (list.questions ?? []).find((p) => String(p.questionFrontendId) === idTrim);
            if (!q?.titleSlug) {
                return textResult(safeJson({ error: `No problem found with question ID "${questionId}"` }), true);
            }
            titleSlug = q.titleSlug;
        }
        else {
            titleSlug = idTrim.toLowerCase().replace(/\s/g, "-");
        }
        const problem = await c.problem(titleSlug);
        const noteContent = problem?.note?.trim() ?? "";
        const notes = noteContent ? [{ content: noteContent }] : [];
        const total = notes.length;
        const paginated = notes.slice(skip, skip + limit);
        return textResult(safeJson({
            questionId: problem?.questionFrontendId ?? problem?.questionId ?? questionId,
            titleSlug: problem?.titleSlug ?? titleSlug,
            title: problem?.title,
            total,
            skip,
            limit,
            notes: paginated,
        }));
    }
    catch (err) {
        return textResult(err instanceof Error ? err.message : String(err), true);
    }
});
// --- search_notes ---
const MAX_NOTES_FETCH = 50; // cap problem fetches to avoid rate limit / timeout
server.registerTool("search_notes", {
    description: "Searches for user notes on LeetCode. Returns notes from problems you have attempted/solved; optional keyword filter, pagination (skip/limit), and sort order. Auth required.",
    inputSchema: {
        keyword: z.string().optional().describe("Search term to filter notes (matches note content and problem title)"),
        limit: z.number().min(1).max(50).optional().default(10).describe("Maximum number of notes to return"),
        skip: z.number().min(0).optional().default(0).describe("Number of notes to skip"),
        orderBy: z
            .enum(["ASCENDING", "DESCENDING"])
            .optional()
            .default("DESCENDING")
            .describe("Sort order for returned notes (by problem title)"),
        site: siteSchema,
    },
}, async ({ keyword, limit, skip, orderBy, site }) => {
    try {
        requireAuth(site);
        const { client } = getClient(site);
        const c = client;
        if (!c.user_progress_questions) {
            return textResult("search_notes is not supported for this site (user progress list not available).", true);
        }
        const toFetch = Math.min(MAX_NOTES_FETCH, skip + limit);
        const progress = await c.user_progress_questions({ skip: 0, limit: toFetch });
        const questions = progress?.questions ?? [];
        const results = [];
        for (const q of questions) {
            const slug = q?.titleSlug;
            if (!slug)
                continue;
            try {
                const problem = await c.problem(slug);
                const note = problem?.note?.trim() ?? "";
                const title = problem?.title ?? q?.title ?? slug;
                if (keyword?.trim()) {
                    const k = keyword.toLowerCase();
                    if (!note.toLowerCase().includes(k) &&
                        !title.toLowerCase().includes(k) &&
                        !slug.toLowerCase().includes(k))
                        continue;
                }
                results.push({ titleSlug: slug, title, note: note || "(no note)" });
            }
            catch {
                continue;
            }
        }
        results.sort((a, b) => {
            const cmp = a.title.localeCompare(b.title, "en", { sensitivity: "base" });
            return orderBy === "ASCENDING" ? cmp : -cmp;
        });
        const paginated = results.slice(skip, skip + limit);
        return textResult(safeJson({
            total: results.length,
            skip,
            limit,
            orderBy,
            notes: paginated,
        }));
    }
    catch (err) {
        return textResult(err instanceof Error ? err.message : String(err), true);
    }
});
// --- get_my_notes ---
server.registerTool("get_my_notes", {
    description: "Get your note for a problem (auth required). Provide titleSlug to fetch that problem's note.",
    inputSchema: {
        titleSlug: z.string().optional().describe("Problem slug to get note for"),
        site: siteSchema,
    },
}, async ({ titleSlug, site }) => {
    try {
        requireAuth(site);
        const { client } = getClient(site);
        if (!titleSlug?.trim()) {
            return textResult("Provide titleSlug to get your note for a specific problem (e.g. two-sum).", false);
        }
        const slug = titleSlug.toLowerCase().replace(/\s/g, "-");
        const problem = await client.problem(slug);
        const note = problem?.note ?? "";
        return textResult(safeJson({ titleSlug: slug, note: note || "(no note saved)" }));
    }
    catch (err) {
        return textResult(err instanceof Error ? err.message : String(err), true);
    }
});
// --- list_problem_solutions ---
// Map display enum to LeetCode API value (Global: TopicSortingOption; CN may differ)
const GLOBAL_ORDER_MAP = {
    HOT: "hot",
    MOST_RECENT: "newest_to_oldest",
    MOST_VOTES: "most_votes",
};
const CN_ORDER_MAP = {
    DEFAULT: "DEFAULT",
    MOST_UPVOTE: "MOST_UPVOTE",
    HOT: "HOT",
    NEWEST_TO_OLDEST: "NEWEST_TO_OLDEST",
    OLDEST_TO_NEWEST: "OLDEST_TO_NEWEST",
};
server.registerTool("list_problem_solutions", {
    description: "Retrieves a list of community solutions for a specific LeetCode problem. Supports filters (userInput, tagSlugs), pagination (limit, skip), and sort order (orderBy). Global: HOT, MOST_RECENT, MOST_VOTES. China: DEFAULT, MOST_UPVOTE, HOT, NEWEST_TO_OLDEST, OLDEST_TO_NEWEST.",
    inputSchema: {
        questionSlug: z.string().describe("URL slug/identifier of the problem (e.g. two-sum)"),
        limit: z.number().min(1).max(50).optional().default(10).describe("Maximum number of solutions to return"),
        skip: z.number().min(0).optional().default(0).describe("Number of solutions to skip"),
        userInput: z.string().optional().describe("Search term to filter solutions"),
        tagSlugs: z.array(z.string()).optional().default([]).describe("Tag identifiers to filter solutions"),
        orderBy: z.string().optional().describe("Global: HOT|MOST_RECENT|MOST_VOTES (default HOT). China: DEFAULT|MOST_UPVOTE|HOT|NEWEST_TO_OLDEST|OLDEST_TO_NEWEST (default DEFAULT)"),
        site: siteSchema,
    },
}, async ({ questionSlug, limit, skip, userInput, tagSlugs, orderBy, site }) => {
    try {
        const { client } = getClient(site);
        const c = client;
        if (!c.graphql) {
            return textResult("list_problem_solutions is not supported: GraphQL not available.", true);
        }
        const slug = questionSlug.trim().toLowerCase().replace(/\s/g, "-");
        const orderByVal = orderBy?.trim().toUpperCase() ?? (site === "china" ? "DEFAULT" : "HOT");
        const apiOrderBy = site === "china"
            ? (CN_ORDER_MAP[orderByVal] ?? orderByVal)
            : (GLOBAL_ORDER_MAP[orderByVal] ?? "hot");
        const variables = {
            questionSlug: slug,
            skip,
            first: limit,
            query: userInput?.trim() || null,
            orderBy: apiOrderBy,
            languageTags: [],
            topicTags: tagSlugs ?? [],
        };
        const res = await c.graphql({
            query: COMMUNITY_SOLUTIONS_QUERY,
            variables,
        });
        if (res?.errors?.length) {
            const msg = res.errors.map((e) => e?.message ?? "Unknown").join("; ");
            return textResult(safeJson({ error: "API error", details: msg }), true);
        }
        const qs = res?.data
            ?.questionSolutions;
        const totalNum = qs?.totalNum ?? 0;
        const solutions = qs?.solutions ?? [];
        return textResult(safeJson({
            questionSlug: slug,
            totalNum,
            skip,
            limit,
            orderBy: orderByVal,
            solutions,
        }));
    }
    catch (err) {
        return textResult(`Error: ${err instanceof Error ? err.message : String(err)}`, true);
    }
});
// --- get_problem_solution ---
server.registerTool("get_problem_solution", {
    description: "Retrieves the complete content of a specific community solution. Global: use topicId (from list_problem_solutions). China: use slug.",
    inputSchema: {
        topicId: z.string().optional().describe("Unique topic ID of the solution (Global only; from list_problem_solutions)"),
        slug: z.string().optional().describe("Unique slug/identifier of the solution (CN only)"),
        site: siteSchema,
    },
}, async ({ topicId, slug, site }) => {
    try {
        if (site === "china") {
            if (!slug?.trim()) {
                return textResult(safeJson({ error: "For China site, slug is required to retrieve a solution." }), true);
            }
            const { client } = getClient(site);
            const c = client;
            if (!c.graphql) {
                return textResult("get_problem_solution is not supported for this client.", true);
            }
            // CN may use a different query (e.g. topic by slug). Try topic with slug if available.
            const res = await c.graphql({
                query: `query topicBySlug($slug: String!) { topic(slug: $slug) { id title post { content voteCount author { username profile { userAvatar } } creationDate } solutionTags { name slug } viewCount commentCount } }`,
                variables: { slug: slug.trim() },
            });
            const errs = res?.errors;
            if (errs?.length) {
                return textResult(safeJson({
                    error: "China: solution by slug may not be supported or slug format may differ.",
                    details: errs.map((e) => e?.message ?? "Unknown").join("; "),
                }), true);
            }
            return textResult(safeJson(res));
        }
        if (!topicId?.trim()) {
            return textResult(safeJson({ error: "For Global site, topicId is required (get it from list_problem_solutions)." }), true);
        }
        const topicIdNum = parseInt(topicId.trim(), 10);
        if (Number.isNaN(topicIdNum)) {
            return textResult(safeJson({ error: "topicId must be a numeric string (e.g. 3678229)." }), true);
        }
        const { client } = getClient(site);
        const c = client;
        if (!c.graphql) {
            return textResult("get_problem_solution is not supported: GraphQL not available.", true);
        }
        const res = await c.graphql({
            query: COMMUNITY_SOLUTION_TOPIC_QUERY,
            variables: { topicId: topicIdNum },
        });
        if (res?.errors?.length) {
            const msg = res.errors.map((e) => e?.message ?? "Unknown").join("; ");
            return textResult(safeJson({ error: "API error", details: msg }), true);
        }
        const topic = res?.data?.topic;
        return textResult(safeJson({ topic }));
    }
    catch (err) {
        return textResult(`Error: ${err instanceof Error ? err.message : String(err)}`, true);
    }
});
// --- get_solution (optional) ---
server.registerTool("get_solution", {
    description: "Fetch official solution by ID (from problem.solution.id). May be paid-only; auth may be required.",
    inputSchema: {
        solutionId: z.string(),
        site: siteSchema,
    },
}, async ({ solutionId, site }) => {
    try {
        const { client } = getClient(site);
        const c = client;
        if (!c.graphql) {
            return textResult("Solution fetch not implemented for this client.", true);
        }
        const query = `
        query solution($id: ID!) {
          solution(id: $id) { content }
        }
      `;
        const res = await c.graphql({
            query,
            variables: { id: solutionId },
        });
        return textResult(safeJson(res));
    }
    catch (err) {
        return textResult(`Error: ${err instanceof Error ? err.message : String(err)}`, true);
    }
});
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
}
main().catch((err) => {
    console.error(err);
    process.exit(1);
});
//# sourceMappingURL=index.js.map