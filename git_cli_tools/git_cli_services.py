import subprocess
from common import logger
from typing import Optional


def _run_command(command: list[str], cwd: str = ".") -> dict:
    """
    Helper function to run git commands and return the output.
    
    :param command: Git command as a list of strings
    :param cwd: Working directory for the git command
    :return: Dictionary with success status, stdout, stderr, and return code
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "Command timed out after 30 seconds",
            "return_code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "return_code": -1
        }


def git_issue_list(
    repo_path: str = ".",
    assignee: Optional[str] = None,
    author: Optional[str] = None,
    jq: Optional[str] = None,
    json_fields: Optional[list[str]] = None,
    label: Optional[list[str]] = None,
    limit: int = 30,
    mention: Optional[str] = None,
    milestone: Optional[str] = None,
    search: Optional[str] = None,
    state: str = "open"
) -> dict:
    """
    List GitHub issues using the GitHub CLI (gh issue list).
    
    Supported flags and their usage:
    
    :param repo_path: Path to the git repository (default: current directory)
    :param assignee: Filter by assignee username (e.g., "octocat" or "@me" for yourself)
    :param author: Filter by author username
    :param jq: Filter JSON output using a jq expression (e.g., ".[] | .title")
    :param json_fields: Output JSON with specified fields. Supported fields:
                        ["assignees", "author", "body", "closed", "closedAt", "comments",
                         "createdAt", "id", "labels", "milestone", "number", "projectCards",
                         "projectItems", "reactionGroups", "state", "title", "updatedAt", "url"]
    :param label: Filter by label names (e.g., ["bug", "feature"])
    :param limit: Maximum number of issues to fetch (default: 30, max: 1000)
    :param mention: Filter by mentioned username
    :param milestone: Filter by milestone number or title
    :param search: Search issues with query string (GitHub search syntax)
    :param state: Filter by state - must be one of: "open", "closed", "all" (default: "open")
    :return: Dictionary with success status, output, error, and return code
    
    Examples:
        # List open issues:
        git_issue_list(repo_path="/path/to/repo")
        
        # List closed issues assigned to you:
        git_issue_list(repo_path="/path/to/repo", assignee="@me", state="closed")
        
        # List issues with bug label as JSON:
        git_issue_list(repo_path="/path/to/repo", label=["bug"], json_fields=["number", "title", "state"])
        
        # Search issues:
        git_issue_list(repo_path="/path/to/repo", search="crash in testing")
    """
    logger.info(f"Listing GitHub issues in {repo_path} with filters")
    
    # Build the gh issue list command
    command = ["gh", "issue", "list"]
    
    # Add flags based on parameters
    if assignee:
        command.extend(["--assignee", assignee])
    
    if author:
        command.extend(["--author", author])
    
    if jq:
        command.extend(["--jq", jq])
    
    if json_fields:
        command.extend(["--json", ",".join(json_fields)])
    
    if label:
        for lbl in label:
            command.extend(["--label", lbl])
    
    if limit != 30:  # Only add if not default
        command.extend(["--limit", str(limit)])
    
    if mention:
        command.extend(["--mention", mention])
    
    if milestone:
        command.extend(["--milestone", milestone])
    
    if search:
        command.extend(["--search", search])
    
    if state != "open":  # Only add if not default
        command.extend(["--state", state])
    
    result = _run_command(command, cwd=repo_path)
    
    if result["success"]:
        logger.info(f"Successfully listed issues")
    else:
        logger.error(f"Failed to list issues: {result['error']}")
    
    return result


def git_issue_view(
    issue_identifier: str,
    repo_path: str = ".",
    comments: bool = False,
    jq: Optional[str] = None,
    json_fields: Optional[list[str]] = None
) -> dict:
    """
    View a specific GitHub issue using the GitHub CLI (gh issue view).
    
    Supported flags and their usage:
    
    :param issue_identifier: Issue number or URL (required, e.g., "123" or full GitHub issue URL)
    :param repo_path: Path to the git repository (default: current directory)
    :param comments: View issue comments (default: False)
    :param jq: Filter JSON output using a jq expression (e.g., ".title")
    :param json_fields: Output JSON with specified fields. Supported fields:
                        ["assignees", "author", "body", "closed", "closedAt",
                         "closedByPullRequestsReferences", "comments", "createdAt", "id",
                         "isPinned", "labels", "milestone", "number", "projectCards",
                         "projectItems", "reactionGroups", "state", "stateReason",
                         "title", "updatedAt", "url"]
    :return: Dictionary with success status, output, error, and return code
    
    Examples:
        # View issue #42:
        git_issue_view(issue_identifier="42", repo_path="/path/to/repo")
        
        # View issue with comments:
        git_issue_view(issue_identifier="42", repo_path="/path/to/repo", comments=True)
        
        # View issue as JSON with specific fields:
        git_issue_view(issue_identifier="42", json_fields=["number", "title", "state", "body"])
        
        # View issue by URL:
        git_issue_view(issue_identifier="https://github.com/owner/repo/issues/42")
    """
    if not issue_identifier:
        return {
            "success": False,
            "output": "",
            "error": "issue_identifier is required (e.g., issue number or URL)",
            "return_code": -1
        }
    
    logger.info(f"Viewing GitHub issue '{issue_identifier}' in {repo_path}")
    
    # Build the gh issue view command
    command = ["gh", "issue", "view", issue_identifier]
    
    # Add flags based on parameters
    if comments:
        command.append("--comments")
    
    if jq:
        command.extend(["--jq", jq])
    
    if json_fields:
        command.extend(["--json", ",".join(json_fields)])
    
    result = _run_command(command, cwd=repo_path)
    
    if result["success"]:
        logger.info(f"Successfully viewed issue '{issue_identifier}'")
    else:
        logger.error(f"Failed to view issue '{issue_identifier}': {result['error']}")
    
    return result


def git_pr_list(
    repo_path: str = ".",
    assignee: Optional[str] = None,
    author: Optional[str] = None,
    base: Optional[str] = None,
    draft: Optional[bool] = None,
    head: Optional[str] = None,
    jq: Optional[str] = None,
    json_fields: Optional[list[str]] = None,
    label: Optional[list[str]] = None,
    limit: int = 30,
    search: Optional[str] = None,
    state: str = "open"
) -> dict:
    """
    List GitHub pull requests using the GitHub CLI (gh pr list).
    
    Supported flags and their usage:
    
    :param repo_path: Path to the git repository (default: current directory)
    :param assignee: Filter by assignee username (e.g., "octocat" or "@me")
    :param author: Filter by author username
    :param base: Filter by base branch (e.g., "main", "develop")
    :param draft: Filter by draft state (True for drafts only, False for ready PRs, None for all)
    :param head: Filter by head branch
    :param jq: Filter JSON output using a jq expression (e.g., ".[] | .title")
    :param json_fields: Output JSON with specified fields. Supported fields:
                        ["additions", "assignees", "author", "autoMergeRequest", "baseRefName",
                         "baseRefOid", "body", "changedFiles", "closed", "closedAt",
                         "closingIssuesReferences", "comments", "commits", "createdAt",
                         "deletions", "files", "fullDatabaseId", "headRefName", "headRefOid",
                         "headRepository", "headRepositoryOwner", "id", "isCrossRepository",
                         "isDraft", "labels", "latestReviews", "maintainerCanModify",
                         "mergeCommit", "mergeStateStatus", "mergeable", "mergedAt", "mergedBy",
                         "milestone", "number", "potentialMergeCommit", "projectCards",
                         "projectItems", "reactionGroups", "reviewDecision", "reviewRequests",
                         "reviews", "state", "statusCheckRollup", "title", "updatedAt", "url"]
    :param label: Filter by label names (e.g., ["bug", "feature"])
    :param limit: Maximum number of PRs to fetch (default: 30)
    :param search: Search pull requests with query string (GitHub search syntax)
    :param state: Filter by state - must be one of: "open", "closed", "merged", "all" (default: "open")
    :return: Dictionary with success status, output, error, and return code
    
    Examples:
        # List open PRs:
        git_pr_list(repo_path="/path/to/repo")
        
        # List merged PRs by author:
        git_pr_list(repo_path="/path/to/repo", author="octocat", state="merged")
        
        # List draft PRs:
        git_pr_list(repo_path="/path/to/repo", draft=True)
        
        # List PRs targeting main branch as JSON:
        git_pr_list(repo_path="/path/to/repo", base="main", json_fields=["number", "title", "state"])
        
        # Search PRs:
        git_pr_list(repo_path="/path/to/repo", search="fix bug in login")
    """
    logger.info(f"Listing GitHub pull requests in {repo_path} with filters")
    
    # Build the gh pr list command
    command = ["gh", "pr", "list"]
    
    # Add flags based on parameters
    if assignee:
        command.extend(["--assignee", assignee])
    
    if author:
        command.extend(["--author", author])
    
    if base:
        command.extend(["--base", base])
    
    if draft is not None:
        if draft:
            command.append("--draft")
        else:
            # To filter for non-draft PRs, we use --draft=false
            command.append("--draft=false")
    
    if head:
        command.extend(["--head", head])
    
    if jq:
        command.extend(["--jq", jq])
    
    if json_fields:
        command.extend(["--json", ",".join(json_fields)])
    
    if label:
        for lbl in label:
            command.extend(["--label", lbl])
    
    if limit != 30:  # Only add if not default
        command.extend(["--limit", str(limit)])
    
    if search:
        command.extend(["--search", search])
    
    if state != "open":  # Only add if not default
        command.extend(["--state", state])
    
    result = _run_command(command, cwd=repo_path)
    
    if result["success"]:
        logger.info(f"Successfully listed pull requests")
    else:
        logger.error(f"Failed to list pull requests: {result['error']}")
    
    return result


def git_pr_view(
    pr_identifier: Optional[str] = None,
    repo_path: str = ".",
    comments: bool = False,
    jq: Optional[str] = None,
    json_fields: Optional[list[str]] = None,
    repo: Optional[str] = None
) -> dict:
    """
    View a specific GitHub pull request using the GitHub CLI (gh pr view).
    
    Supported flags and their usage:
    
    :param pr_identifier: PR number, URL, or branch name (optional - defaults to current branch)
    :param repo_path: Path to the git repository (default: current directory)
    :param comments: View pull request comments (default: False)
    :param jq: Filter JSON output using a jq expression (e.g., ".title")
    :param json_fields: Output JSON with specified fields. Supported fields:
                        ["additions", "assignees", "author", "autoMergeRequest", "baseRefName",
                         "baseRefOid", "body", "changedFiles", "closed", "closedAt",
                         "closingIssuesReferences", "comments", "commits", "createdAt",
                         "deletions", "files", "fullDatabaseId", "headRefName", "headRefOid",
                         "headRepository", "headRepositoryOwner", "id", "isCrossRepository",
                         "isDraft", "labels", "latestReviews", "maintainerCanModify",
                         "mergeCommit", "mergeStateStatus", "mergeable", "mergedAt", "mergedBy",
                         "milestone", "number", "potentialMergeCommit", "projectCards",
                         "projectItems", "reactionGroups", "reviewDecision", "reviewRequests",
                         "reviews", "state", "statusCheckRollup", "title", "updatedAt", "url"]
    :param repo: Select another repository using [HOST/]OWNER/REPO format (e.g., "microsoft/vscode")
    :return: Dictionary with success status, output, error, and return code
    
    Examples:
        # View PR #42:
        git_pr_view(pr_identifier="42", repo_path="/path/to/repo")
        
        # View PR with comments:
        git_pr_view(pr_identifier="42", repo_path="/path/to/repo", comments=True)
        
        # View PR as JSON with specific fields:
        git_pr_view(pr_identifier="42", json_fields=["number", "title", "state", "body"])
        
        # View PR by URL:
        git_pr_view(pr_identifier="https://github.com/owner/repo/pull/42")
        
        # View PR by branch name:
        git_pr_view(pr_identifier="feature-branch", repo_path="/path/to/repo")
        
        # View PR from another repository:
        git_pr_view(pr_identifier="42", repo="owner/repo")
        
        # View current branch's PR:
        git_pr_view(repo_path="/path/to/repo")
    """
    logger.info(f"Viewing GitHub pull request '{pr_identifier or 'current branch'}' in {repo_path}")
    
    # Build the gh pr view command
    command = ["gh", "pr", "view"]
    
    # Add PR identifier if provided
    if pr_identifier:
        command.append(pr_identifier)
    
    # Add flags based on parameters
    if comments:
        command.append("--comments")
    
    if jq:
        command.extend(["--jq", jq])
    
    if json_fields:
        command.extend(["--json", ",".join(json_fields)])
    
    if repo:
        command.extend(["--repo", repo])
    
    result = _run_command(command, cwd=repo_path)
    
    if result["success"]:
        logger.info(f"Successfully viewed pull request '{pr_identifier or 'current branch'}'")
    else:
        logger.error(f"Failed to view pull request '{pr_identifier or 'current branch'}': {result['error']}")
    
    return result


def git_pr_diff(
    pr_identifier: Optional[str] = None,
    repo_path: str = ".",
    color: str = "auto",
    name_only: bool = False,
    patch: bool = False
) -> dict:
    """
    View the diff for a GitHub pull request using the GitHub CLI (gh pr diff).
    
    Supported flags and their usage:
    
    :param pr_identifier: PR number, URL, or branch name (optional - defaults to current branch)
    :param repo_path: Path to the git repository (default: current directory)
    :param color: Use color in diff output - must be one of: "always", "never", "auto" (default: "auto")
    :param name_only: Display only names of changed files (default: False)
    :param patch: Display diff in patch format (default: False)
    :return: Dictionary with success status, output, error, and return code
    
    Examples:
        # View diff for PR #42:
        git_pr_diff(pr_identifier="42", repo_path="/path/to/repo")
        
        # View only changed file names:
        git_pr_diff(pr_identifier="42", repo_path="/path/to/repo", name_only=True)
        
        # View diff in patch format:
        git_pr_diff(pr_identifier="42", repo_path="/path/to/repo", patch=True)
        
        # View diff with color always enabled:
        git_pr_diff(pr_identifier="42", repo_path="/path/to/repo", color="always")
        
        # View diff by URL:
        git_pr_diff(pr_identifier="https://github.com/owner/repo/pull/42")
        
        # View diff by branch name:
        git_pr_diff(pr_identifier="feature-branch", repo_path="/path/to/repo")
        
        # View current branch's PR diff:
        git_pr_diff(repo_path="/path/to/repo")
    """
    logger.info(f"Viewing diff for GitHub pull request '{pr_identifier or 'current branch'}' in {repo_path}")
    
    # Build the gh pr diff command
    command = ["gh", "pr", "diff"]
    
    # Add PR identifier if provided
    if pr_identifier:
        command.append(pr_identifier)
    
    # Add flags based on parameters
    if color != "auto":  # Only add if not default
        command.extend(["--color", color])
    
    if name_only:
        command.append("--name-only")
    
    if patch:
        command.append("--patch")
    
    result = _run_command(command, cwd=repo_path)
    
    if result["success"]:
        logger.info(f"Successfully retrieved diff for pull request '{pr_identifier or 'current branch'}'")
    else:
        logger.error(f"Failed to retrieve diff for pull request '{pr_identifier or 'current branch'}': {result['error']}")
    
    return result


def git_log(
    repo_path: str = ".",
    max_count: Optional[int] = None,
    skip: Optional[int] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    author: Optional[str] = None,
    committer: Optional[str] = None,
    grep: Optional[str] = None,
    all_refs: bool = False,
    branches: Optional[str] = None,
    tags: Optional[str] = None,
    remotes: Optional[str] = None,
    first_parent: bool = False,
    no_merges: bool = False,
    merges: bool = False,
    reverse: bool = False,
    date_order: bool = False,
    author_date_order: bool = False,
    topo_order: bool = False,
    oneline: bool = False,
    format: Optional[str] = None,
    pretty: Optional[str] = None,
    abbrev_commit: bool = False,
    graph: bool = False,
    decorate: Optional[str] = None,
    stat: bool = False,
    patch: bool = False,
    name_only: bool = False,
    name_status: bool = False,
    follow: bool = False,
    revision_range: Optional[str] = None,
    paths: Optional[list[str]] = None
) -> dict:
    """
    Show commit logs using git log command.
    
    Supported flags and their usage:
    
    :param repo_path: Path to the git repository (default: current directory)
    :param max_count: Limit the number of commits to output (e.g., 10)
    :param skip: Skip number commits before starting to show the commit output
    :param since: Show commits more recent than a specific date (e.g., "2 weeks ago", "2024-01-01")
    :param until: Show commits older than a specific date (e.g., "2024-12-31")
    :param author: Limit commits to those with author matching the pattern
    :param committer: Limit commits to those with committer matching the pattern
    :param grep: Limit commits with log message matching the pattern
    :param all_refs: Pretend as if all refs in refs/ are listed on command line (default: False)
    :param branches: Pretend as if all refs in refs/heads are listed. Optional pattern to filter (e.g., "feature*")
    :param tags: Pretend as if all refs in refs/tags are listed. Optional pattern to filter (e.g., "v1.*")
    :param remotes: Pretend as if all refs in refs/remotes are listed. Optional pattern to filter (e.g., "origin/*")
    :param first_parent: Follow only the first parent commit upon seeing a merge (default: False)
    :param no_merges: Do not print commits with more than one parent (default: False)
    :param merges: Print only merge commits (default: False)
    :param reverse: Output commits in reverse order (default: False)
    :param date_order: Show commits in commit timestamp order (default: False)
    :param author_date_order: Show commits in author timestamp order (default: False)
    :param topo_order: Show commits in topological order (default: False)
    :param oneline: Shorthand for --pretty=oneline --abbrev-commit (default: False)
    :param format: Pretty-print the contents using custom format string (e.g., "%h - %an, %ar : %s")
    :param pretty: Pretty-print format - one of: oneline, short, medium, full, fuller, reference, email, raw
    :param abbrev_commit: Show abbreviated commit object name (default: False)
    :param graph: Draw a text-based graphical representation of commit history (default: False)
    :param decorate: Print out ref names of commits - one of: short, full, auto, no
    :param stat: Generate a diffstat (default: False)
    :param patch: Generate patch/diff output (default: False)
    :param name_only: Show only names of changed files (default: False)
    :param name_status: Show only names and status of changed files (default: False)
    :param follow: Continue listing history of a file beyond renames (works only for single file)
    :param revision_range: Show only commits in the specified revision range (e.g., "main..feature", "HEAD~5..HEAD")
    :param paths: Show only commits that are enough to explain how files matching paths came to be
    :return: Dictionary with success status, output, error, and return code
    
    Examples:
        # Show last 10 commits:
        git_log(repo_path="/path/to/repo", max_count=10)
        
        # Show commits from last 2 weeks:
        git_log(repo_path="/path/to/repo", since="2 weeks ago")
        
        # Show commits by specific author with graph:
        git_log(repo_path="/path/to/repo", author="John Doe", graph=True, oneline=True)
        
        # Show commits in a range:
        git_log(repo_path="/path/to/repo", revision_range="main..feature-branch")
        
        # Show commits that changed specific file:
        git_log(repo_path="/path/to/repo", follow=True, paths=["src/main.py"])
        
        # Show commits with custom format:
        git_log(repo_path="/path/to/repo", format="%h - %an, %ar : %s", max_count=20)
        
        # Show all branches with graph:
        git_log(repo_path="/path/to/repo", all_refs=True, graph=True, oneline=True, max_count=50)
        
        # Show commits with stats:
        git_log(repo_path="/path/to/repo", stat=True, max_count=5)
        
        # Search commits by message:
        git_log(repo_path="/path/to/repo", grep="fix bug", oneline=True)
    """
    logger.info(f"Showing commit logs in {repo_path}")
    
    # Build the git log command
    command = ["git", "log"]
    
    # Add limit/skip options
    if max_count is not None:
        command.extend(["-n", str(max_count)])
    
    if skip is not None:
        command.extend(["--skip", str(skip)])
    
    # Add date filters
    if since:
        command.extend(["--since", since])
    
    if until:
        command.extend(["--until", until])
    
    # Add author/committer filters
    if author:
        command.extend(["--author", author])
    
    if committer:
        command.extend(["--committer", committer])
    
    # Add message filter
    if grep:
        command.extend(["--grep", grep])
    
    # Add ref selection options
    if all_refs:
        command.append("--all")
    
    if branches is not None:
        if branches:
            command.extend(["--branches", branches])
        else:
            command.append("--branches")
    
    if tags is not None:
        if tags:
            command.extend(["--tags", tags])
        else:
            command.append("--tags")
    
    if remotes is not None:
        if remotes:
            command.extend(["--remotes", remotes])
        else:
            command.append("--remotes")
    
    # Add merge options
    if first_parent:
        command.append("--first-parent")
    
    if no_merges:
        command.append("--no-merges")
    
    if merges:
        command.append("--merges")
    
    # Add ordering options
    if reverse:
        command.append("--reverse")
    
    if date_order:
        command.append("--date-order")
    
    if author_date_order:
        command.append("--author-date-order")
    
    if topo_order:
        command.append("--topo-order")
    
    # Add formatting options
    if oneline:
        command.append("--oneline")
    
    if format:
        command.extend(["--format", format])
    
    if pretty:
        command.extend(["--pretty", pretty])
    
    if abbrev_commit:
        command.append("--abbrev-commit")
    
    if graph:
        command.append("--graph")
    
    if decorate is not None:
        if decorate:
            command.extend(["--decorate", decorate])
        else:
            command.append("--decorate")
    
    # Add diff output options
    if stat:
        command.append("--stat")
    
    if patch:
        command.append("--patch")
    
    if name_only:
        command.append("--name-only")
    
    if name_status:
        command.append("--name-status")
    
    # Add follow option
    if follow:
        command.append("--follow")
    
    # Add revision range if specified
    if revision_range:
        command.append(revision_range)
    
    # Add path filters if specified
    if paths:
        command.append("--")
        command.extend(paths)
    
    result = _run_command(command, cwd=repo_path)
    
    if result["success"]:
        logger.info(f"Successfully retrieved commit logs")
    else:
        logger.error(f"Failed to retrieve commit logs: {result['error']}")
    
    return result