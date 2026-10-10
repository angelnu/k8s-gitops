# AGENTS.md

Guidance for AI agents and contributors working in this repository.

## Issue tracking

- **Issues are created as GitHub issues in this repository** (angelnu/k8s-gitops) or handled **directly via PRs** — never in Jira.
  - Small fixes: open a PR directly.
  - Larger work (migrations, epics): open a GitHub issue first (e.g. #6432 for the ingress-nginx → Gateway API migration) and reference it from the PRs.
- **Do not create Jira tickets for this repo.** Jira (E26 / Phoenix Systems) belongs to Phoeniqs work — this is a personal/home project.
- **Never post private information in public content** (GitHub issues, PRs, comments):
  - **Hostnames are private** — never post real hostnames (e.g. `*.angelnu.com`, cluster domains, service URLs). Use placeholders like `nextcloud.example.com` instead.
  - Never post credentials, tokens, passwords, or secrets of any kind.
  - Internal entity IDs, pod names, image tags, and revision SHAs are fine.
- Decision records and analysis docs live in the repo itself (e.g. `apps/ingress-nginx/README.md` ADR-style docs; `*.md` files are excluded from the Flux artifact via `.sourceignore`).
