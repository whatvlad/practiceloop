# GitHub application runbook — prepared, not executed

> Historical preparation runbook. The owner has since approved publication and
> the repository was created. See GITHUB_STATUS.md for current state. Do not
> rerun the new-repository/orphan-branch seed steps on the published repository.

2026-10-15: local folder was empty and had no Git history/remotes. Git initialized;
bootstrap branch is chore/bootstrap-collaboration. Connector authenticated as
`whatvlad`, no organizations returned. Lookup of `whatvlad/practiceloop` returned
404: it may not exist or may be outside connector access. This is NOT proof that
creation is safe; repeat checks with full authorized owner access before creating.
GitHub CLI is not installed on this machine. No remote settings, Issues or invites
were changed. Owner must approve target account and all publication/access actions.

## 1. Confirm target and prerequisites

Proposed target: **whatvlad/practiceloop**, **Private**. Description:
"PracticeLoop — a mathematics practice platform with rule-based problem generation,
symbolic answer verification, and personalized practice history."

Install GitHub CLI using its [official installer](https://cli.github.com/), then
`gh auth login`, `gh auth status`, `gh api user --jq .login`. Use your own account.
Do not echo tokens. If an organization is chosen instead, first confirm owner
approval and permissions, substitute it in every command, and update CODEOWNERS
to actual human/team accounts with write access. Review staged content and the
manifest before committing or publishing. Never print .env contents for review.

```powershell
$repo = 'whatvlad/practiceloop' # ONLY after owner confirms this exact target
gh repo view $repo --json nameWithOwner,isPrivate,defaultBranchRef,url
gh api 'user/repos?per_page=100' --paginate --jq '.[].full_name'
```
If existing, use it; fetch and inspect its history in a separate clone before
integrating this scaffold in a branch. Do not overwrite existing default branch,
reuse a dirty checkout or create a duplicate. A 403/network/ambiguous 404 is a
blocker for automatic creation, not authorization to proceed.

## 2. Create/publish only after approval and confirmed absence

After owner approval, create an **empty** repo without auto README/license/Gitignore:
```powershell
gh repo create $repo --private --description 'PracticeLoop — a mathematics practice platform with rule-based problem generation, symbolic answer verification, and personalized practice history.'
```
For a genuinely new repo only, seed main with the original spec, then publish all
infrastructure on the bootstrap PR branch. This one-time main seed contains no
application code. Owner approves this publication before running these commands.
```powershell
git status --short --branch
git switch --orphan main
git add -- docs/PRACTICELOOP_MVP.md
git commit -m 'docs: preserve original PracticeLoop MVP specification'
git remote add origin "https://github.com/$repo.git"
git push -u origin main
git switch -c chore/bootstrap-collaboration
git add -- .
git diff --cached --stat
git diff --cached --check
# Review full staged content locally and scan for secrets BEFORE commit/push.
git commit -m 'chore: prepare collaborative development infrastructure'
git push -u origin chore/bootstrap-collaboration
```
If bootstrap branch already has a commit, or main/remote exists, STOP and adapt
by inspection; do not run this new-repository sequence blindly. No force push.
Gitleaks can scan the working tree before first commit (ignored build artifacts
excluded with --max-target-megabytes and .gitleaks.toml if needed); preferred:
```powershell
docker run --rm -v "${PWD}:/repo:ro" ghcr.io/gitleaks/gitleaks:v8.30.0 dir /repo --config /repo/.gitleaks.toml --redact --no-banner
docker run --rm -v "${PWD}:/repo:ro" ghcr.io/gitleaks/gitleaks:v8.30.0 git /repo --config /repo/.gitleaks.toml --redact --no-banner --log-opts=--all
```
Do not interpret an unscanned index/history as passed. Gitleaks errors block push.

## 3. Create the bootstrap PR and enable settings

Write the reviewed PR body to `.local/bootstrap-pr.md` (identity, tests, risks,
pending checks); use `--body-file` so text is preserved:
```powershell
gh pr create --repo $repo --base main --head chore/bootstrap-collaboration --draft --title 'chore: prepare PracticeLoop collaboration infrastructure' --body-file .local/bootstrap-pr.md
gh repo edit $repo --default-branch main --enable-issues --enable-projects --delete-branch-on-merge --enable-squash-merge --disable-merge-commit --disable-rebase-merge
gh run list --repo $repo --branch chore/bootstrap-collaboration
```
Opening a PR from an automated Codex task must also attach its returned URL to
the chat through the app's attach_artifact tool. Check each real CI job and logs;
the status names in .github/branch-protection.json must match actual run contexts.
Do not enable merge queue without adding merge_group CI support.

Apply protection after checks have been observed; token/admin permission and plan
must support private repository protection:
```powershell
gh api --method PUT "repos/$repo/branches/main/protection" --input .github/branch-protection.json
gh api "repos/$repo/branches/main/protection"
```
Prepared requirements: PR with 1 approval, dismiss stale approvals, approval from
someone other than last pusher, all four checks + up-to-date branch, admin
enforcement, resolved discussions, linear history, no force push/deletion.
No actor push restrictions (personal repos cannot use organization restrictions).
Code-owner approval is intentionally false until a second authorized human is
known; the blanket verified owner must not prevent the owner's own PR being
reviewed by Developer 2. Independent human approval remains mandatory by policy.
These are protection payload values, **not already applied rules**.

GitHub refuses author self-approval but cannot guarantee an approving account
represents an independent human; enforce that through accountable reviewers.
If API rejects a rule/plan, record exact response and limitation, keep PR unmerged
and decide with owner whether to upgrade/change hosting or use manual policy.
Do not claim the branch is protected when only documentation exists.
[GitHub protection documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches).

## 4. Security features and task board

After approval and checking available features:
```powershell
gh api --method PUT "repos/$repo/vulnerability-alerts"
gh api "repos/$repo" --jq .security_and_analysis
```
In Settings -> Code security, enable supported Dependabot alerts/security updates,
secret scanning and push protection. For private repos availability can require
additional plans/licenses. Do not copy a security_and_analysis response containing
unnecessary account data into public logs. Record successful read-back; a feature
not offered is "unavailable", never "enabled". Dependabot.yml only schedules
updates; it does not itself enable hosted security features.

Publish labels/tasks only with explicit approval:
```powershell
powershell -File scripts/publish-issues.ps1 -Repository $repo
powershell -File scripts/publish-issues.ps1 -Repository $repo -Apply
```
First invocation is a read-only preview; second creates missing labels/Issues,
checks for duplicate titles and records mapping in .local/issue-map.json. No
assignees are invented. Review returned Issue numbers; replace provisional PL IDs
in branch planning and dependencies with actual links.

Optional Projects v2 (requires owner approval and Projects permissions): create a
repository-linked board named PracticeLoop MVP through GitHub Projects, configure
Status options Backlog, Ready, In Progress, In Review, Blocked, Done; add Issues
and fields Priority, Owner, Dependencies, PR. The --enable-projects repo toggle
does not create that board. If unavailable, use prepared status labels; this is
the working fallback. No automatic board/label synchronization is configured.

## 5. Second developer and verification

Use ONBOARDING.md after owner confirms username and Write role. No invitation is
sent in this preparation. Verify non-author approval, failing CI blocks merge,
direct main push rejected, force push/deletion rejected, and one human can review
the other's PR. Use a disposable test branch/repository for destructive tests;
inspect the main protection configuration without attempting deletion of main.
Read back default branch, visibility, issues, security and protection, record
unsupported settings. Only an authorized human merges after successful checks.
