"""
Domain 3 · Task 3.2 — Custom slash commands and skills.

THE BIG IDEA
============
SLASH COMMANDS are saved prompts.
  .claude/commands/   -> project (version-controlled, everyone who clones gets it)
                         This is the correct answer for "the whole team should get /review".
  ~/.claude/commands/ -> personal.

SKILLS live in .claude/skills/ as folders with a SKILL.md playbook, configured via
frontmatter:
  context: fork    -> run the skill in an ISOLATED sub-agent context so verbose output
                      doesn't pollute the main conversation
  allowed-tools    -> restrict which tools the skill may use (e.g., file writes only)
  argument-hint    -> prompt the developer for required parameters when invoked bare

SKILLS vs CLAUDE.md decision rule:
  CLAUDE.md = ALWAYS-loaded universal standards.
  Skills    = ON-DEMAND, task-specific workflows.
Want a personal variant of a team skill? Create it in ~/.claude/skills/ under a DIFFERENT
name so teammates are unaffected.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause, analogy, pitfall


def main():
    banner("Domain 3 · Task 3.2", "Slash commands & skills")
    concept("Domain 3: Claude Code Configuration & Workflows (20%)",
            "Task 3.2 — Create and configure custom slash commands and skills",
            "Project vs personal scope; skill frontmatter")

    h1("Slash commands = saved prompts (sample Q4)")
    note('Goal: every developer gets /review when they clone or pull the repo.')
    kv("  .claude/commands/review.md", "PROJECT scope -> shared via version control ✓ correct")
    kv("  ~/.claude/commands/review.md", "PERSONAL scope -> only you")
    wrong("CLAUDE.md isn't for command definitions; .claude/config.json 'commands array' "
          "doesn't exist.")
    right("Put /review in .claude/commands/ inside the repo.")

    pause("skills")
    rule()
    h1("Skills live in .claude/skills/ with a SKILL.md + frontmatter")
    code("---\n"
         "name: analyze-codebase\n"
         "context: fork            # isolate verbose output from the main chat\n"
         "allowed-tools: [Read, Grep, Glob]   # read-only; no destructive actions\n"
         "argument-hint: <module-name>        # prompt when invoked without args\n"
         "---\n"
         "# Codebase analysis playbook\n"
         "1. Map the module's exports...\n", "SKILL.md")

    h2("The three frontmatter options")
    kv("  context: fork", "isolated sub-agent context; keeps pages of findings out of main chat")
    kv("  allowed-tools", "restrict tools while the skill runs (e.g., file writes only)")
    kv("  argument-hint", "prompt for required params when invoked bare (e.g., /deploy <env>)")

    pause("the decision rule")
    rule()
    h1("Skills vs CLAUDE.md — the decision rule")
    kv("CLAUDE.md", "ALWAYS-loaded universal standards (conventions, context)")
    kv("Skills", "ON-DEMAND, task-specific workflows you invoke when needed")
    right("Want a personal variant of a team skill? Create it in ~/.claude/skills/ under a "
          "DIFFERENT name so teammates are unaffected.")

    rule()
    h1("Plain-language analogy & the common confusion")
    analogy("A slash command is a saved macro; a skill is a checklist you pull out for a specific job. Keep the team's macros in the repo so everyone gets them; keep personal experiments in your home folder.")
    pitfall('Learners try to ship a team command from ~/.claude/commands (personal — nobody else gets it) or stuff command definitions into CLAUDE.md (which is for context, not commands). Team command goes in .claude/commands/ in the repo.')

    tip(".claude/commands/ = shared; ~/.claude/commands/ = personal. Skill frontmatter: "
        "context: fork, allowed-tools, argument-hint. Always-on standards -> CLAUDE.md; "
        "on-demand workflow -> skill.")
    note("\nSee runnable artifacts under domains/domain3_claude_code/examples/.")


if __name__ == "__main__":
    main()
