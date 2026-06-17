"""
Domain 2 · Task 2.4 — Integrate MCP servers into Claude Code and agent workflows.

THE BIG IDEA
============
  CONFIG SCOPING:
    .mcp.json (in the repo)   -> PROJECT-level, shared with the team via version control.
                                 Use for tooling everyone needs (issue tracker, shared DBs).
    ~/.claude.json (home dir) -> USER-level, personal, NOT shared.
                                 Use for personal/experimental servers.

  CREDENTIALS via env-var expansion: write ${GITHUB_TOKEN} in .mcp.json, not the secret —
  the config can be committed safely; each machine supplies its own token.

  ALL servers, all at once: tools from every configured MCP server are discovered at
  connection time and available simultaneously (project + personal coexist).

  RESOURCES vs TOOLS: tools = ACTIONS; resources = readable CONTENT CATALOGS (issue
  summaries, doc hierarchies, DB schemas) so the agent sees what data exists without
  burning turns on exploratory calls.

  RICH descriptions matter doubly: a thin MCP tool description makes the agent prefer a
  familiar built-in (like Grep) over your more capable specialized tool.

  BUY BEFORE BUILD: use community servers for standard integrations (Jira); write custom
  only for team-specific workflows.
"""

import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


PROJECT_MCP = {
    "mcpServers": {
        "jira": {
            "command": "npx",
            "args": ["-y", "@community/mcp-jira"],
            "env": {"JIRA_TOKEN": "${JIRA_TOKEN}"}   # <-- env expansion, not the secret
        }
    }
}

USER_MCP = {
    "mcpServers": {
        "my-scratch-db": {"command": "python", "args": ["-m", "my_experimental_server"]}
    }
}


def main():
    banner("Domain 2 · Task 2.4", "MCP server integration & scoping")
    concept("Domain 2: Tool Design & MCP Integration (18%)",
            "Task 2.4 — Integrate MCP servers",
            ".mcp.json (shared) vs ~/.claude.json (personal); resources vs tools")

    h1("Where the config lives decides who gets the server")
    h2(".mcp.json  (in the repo → shared with the whole team)")
    code(json.dumps(PROJECT_MCP, indent=2), ".mcp.json")
    h2("~/.claude.json  (home dir → personal only)")
    code(json.dumps(USER_MCP, indent=2), "~/.claude.json")
    right("Team tooling -> .mcp.json (travels via version control). Personal/experimental "
          "-> ~/.claude.json (stays on your machine).")

    pause("secrets")
    rule()
    h1("Credentials via environment-variable expansion")
    wrong('Pasting the real token into .mcp.json and committing it. Now the secret is in '
          'git history forever.')
    right('Write ${JIRA_TOKEN}. The config is safe to commit; each machine supplies its '
          'own token from the environment.')

    rule()
    h1("All servers available simultaneously")
    note("At connection time, tools from EVERY configured server (project + personal) are "
         "discovered and usable together. You don't pick one server per session.")

    rule()
    h1("Resources vs tools")
    kv("tools", "ACTIONS the agent performs (create_issue, run_query)")
    kv("resources", "readable CONTENT CATALOGS (issue summaries, doc hierarchies, DB schemas)")
    right("Expose catalogs as RESOURCES so the agent can SEE what data exists without "
          "burning turns on exploratory tool calls.")

    rule()
    h1("Two more tested points")
    note("- RICH MCP descriptions matter doubly: a thin description makes the agent fall "
         "back to a familiar built-in (Grep) instead of your better specialized tool.")
    note("- BUY before BUILD: community server for Jira; custom servers only for "
         "team-specific workflows.")

    tip(".mcp.json = project/shared; ~/.claude.json = personal; secrets via ${ENV_VAR}; "
        "resources = catalogs, tools = actions; all servers coexist.")


if __name__ == "__main__":
    main()
