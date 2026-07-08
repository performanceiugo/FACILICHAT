Use the `ctx7` CLI sparingly — each lookup costs tokens (fetched docs enter context), so default to answering from training knowledge and only reach for this when there's a concrete reason to distrust it.

Use it when:
- The user explicitly asks to check, verify, or look up documentation (mentions "Context7", "ctx7", "docs atualizados", "confere a documentação", etc.)
- You're about to write code against an API you're genuinely unsure about (not just "haven't memorized the exact signature") — e.g., a library version far newer than your training cutoff, a recent breaking change you suspect happened, or an area known for frequent API churn
- A bug looks like it could be caused by a version-specific behavior change, and training knowledge isn't resolving it

Do NOT use for: refactoring, writing scripts from scratch, debugging business logic, code review, general programming concepts, or routine use of stable/well-established APIs you already know confidently (standard library usage, common framework patterns you've used correctly many times). Do not treat "the user mentioned a library name" as a trigger by itself — only the conditions above count. When in doubt, proceed with training knowledge and note the assumption rather than looking it up.

## Steps

1. Resolve library: `npx ctx7@latest library <name> "<user's question>"` — use the official library name with proper punctuation (e.g., "Next.js" not "nextjs", "Customer.io" not "customerio", "Three.js" not "threejs")
2. Pick the best match (ID format: `/org/project`) by: exact name match, description relevance, code snippet count, source reputation (High/Medium preferred), and benchmark score (higher is better). If results don't look right, try alternate names or queries (e.g., "next.js" not "nextjs", or rephrase the question)
3. Fetch docs: `npx ctx7@latest docs <libraryId> "<user's question>"` — run a separate `docs` command per distinct concept if the question spans multiple topics, unless it's about how they interact
4. Answer using the fetched documentation

You MUST call `library` first to get a valid ID unless the user provides one directly in `/org/project` format. Use the user's full question as the query — specific and detailed queries return better results than vague single words, but keep each query to a single concept unless the question is about how concepts interact; combined multi-topic queries dilute ranking and return shallow results for each topic. Do not run more than 3 commands per question. Do not include sensitive information (API keys, passwords, credentials) in queries.

For version-specific docs, use `/org/project/version` from the `library` output (e.g., `/vercel/next.js/v14.3.0`).

If a command fails with a quota error, inform the user and suggest `npx ctx7@latest login` or setting `CONTEXT7_API_KEY` env var for higher limits. Do not silently fall back to training data.
