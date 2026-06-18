/* CCA Teaching Console — content model.
   Original teaching material written for this study aid, mapped to the
   Claude Certified Architect – Foundations domain/task structure. */
(function () {
  // line types: info | cmd | dim | bad | good | tip | head
  const L = (type, text) => ({ type, text });

  const domains = [
    {
      id: "d1",
      n: 1,
      title: "Agentic Architecture & Orchestration",
      short: "Orchestration",
      weight: 27,
      blurb:
        "How agents loop, when to add more of them, and how to make must-follow rules actually hold.",
      folder: "domain1_orchestration/",
    },
    {
      id: "d2",
      n: 2,
      title: "Tool Design & MCP Integration",
      short: "Tools & MCP",
      weight: 18,
      blurb:
        "Designing tools the model can pick correctly, with schemas and errors that guide behaviour.",
      folder: "domain2_tools_mcp/",
    },
    {
      id: "d3",
      n: 3,
      title: "Claude Code Configuration & Workflows",
      short: "Claude Code",
      weight: 20,
      blurb:
        "Config scope, plan vs direct, permissions, hooks, and delegation in Claude Code.",
      folder: "domain3_claude_code/",
    },
    {
      id: "d4",
      n: 4,
      title: "Prompt Engineering & Structured Output",
      short: "Prompting",
      weight: 20,
      blurb:
        "Getting reliable, parseable output through structure, examples, and tool-use schemas.",
      folder: "domain4_prompt_output/",
    },
    {
      id: "d5",
      n: 5,
      title: "Context Management & Reliability",
      short: "Context",
      weight: 15,
      blurb:
        "Treating context as scarce: extract facts, trim noise, hand off explicitly, verify outputs.",
      folder: "domain5_context_reliability/",
    },
  ];

  const themes = [
    {
      id: "t1",
      title: "Guarantees beat instructions",
      body:
        "Must-follow rules — verify identity before a refund — belong in code: hooks, gates, schemas. Prompts are probabilistic; code is deterministic.",
    },
    {
      id: "t2",
      title: "Fix the root cause, proportionately",
      body:
        "A vague tool description calls for a better description — not a routing classifier. The exam loves over-engineered distractors.",
    },
    {
      id: "t3",
      title: "Context is a scarce, leaky resource",
      body:
        "Extract the key facts, trim the noise, and pass information explicitly between agents. Never assume the next step can see everything.",
    },
  ];

  // ---- Tasks (30) -------------------------------------------------------
  const tasks = [
    // Domain 1
    {
      id: "1.1",
      d: "d1",
      title: "The Agentic Loop",
      concept:
        "An agent isn't one prompt — it's a loop: gather context, take an action via tools, verify the result, repeat until the goal is met or a stop condition fires.",
      antipattern:
        "Treating the model as a single request/response and hoping one giant prompt does everything.",
      right:
        "A bounded loop with an explicit stop condition and a verification step each turn.",
      tip: "If a question describes 'one prompt that must do many dependent steps', the answer is almost always: make it a loop.",
      output: [
        L("cmd", "$ python3 domains/domain1_orchestration/task1_1_agentic_loop.py"),
        L("head", "Agentic loop — resolve a flaky test"),
        L("dim", "turn 1  gather → read test output"),
        L("dim", "turn 2  act    → patch off-by-one in pager.py"),
        L("dim", "turn 3  verify → re-run suite"),
        L("bad", "Anti-pattern: single mega-prompt, no verify step — silent failure"),
        L("good", "Loop with per-turn verification — stops at green suite (3 turns)"),
        L("tip", "Stop condition + verification are what make it an agent, not a chatbot."),
      ],
      q: ["q1"],
      links: ["1.5", "5.5"],
    },
    {
      id: "1.2",
      d: "d1",
      title: "Single-Agent vs Multi-Agent",
      concept:
        "Add agents only when work is genuinely parallel or needs isolated context. Most tasks are a single agent with good tools.",
      antipattern:
        "Spinning up a coordinator and five subagents for a linear task that one agent handles fine.",
      right:
        "Start single-agent. Split only when subtasks are independent and each needs its own context budget.",
      tip: "More agents = more context handoffs = more places to lose information. Default to one.",
      output: [
        L("cmd", "$ python3 domains/domain1_orchestration/task1_2_single_vs_multi.py"),
        L("head", "Choosing an architecture"),
        L("bad", "Linear refactor split across 5 agents — 4 redundant handoffs, slower"),
        L("good", "Single agent + Grep/Read/Edit tools — same result, no handoff loss"),
        L("good", "Parallel research over 8 sources → genuinely benefits from subagents"),
        L("tip", "Independence + isolated context justify multi-agent. Nothing else does."),
      ],
      q: ["q2"],
      links: ["1.3", "1.4"],
    },
    {
      id: "1.3",
      d: "d1",
      title: "Orchestrator–Worker Pattern",
      concept:
        "A coordinator decomposes the goal, dispatches independent subtasks to workers, and synthesises their results. Workers don't talk to each other.",
      antipattern:
        "Workers sharing mutable state or chaining outputs implicitly through a global.",
      right:
        "Coordinator owns the plan and the synthesis; each worker gets an explicit, self-contained brief.",
      tip: "The coordinator is the only place that sees the whole picture — keep synthesis there.",
      output: [
        L("cmd", "$ python3 domains/domain1_orchestration/task1_3_orchestrator_worker.py"),
        L("head", "Coordinator dispatches 3 research workers"),
        L("dim", "coordinator → brief(worker A: pricing), brief(worker B: docs), brief(worker C: reviews)"),
        L("good", "each worker returns a structured finding + sources"),
        L("good", "coordinator synthesises → single cited summary"),
        L("bad", "Anti-pattern: worker B reads worker A's scratch buffer → hidden coupling"),
        L("tip", "Self-contained briefs in, structured findings out, synthesis in the coordinator."),
      ],
      q: ["q2", "q3"],
      links: ["1.2", "1.4", "5.4"],
    },
    {
      id: "1.4",
      d: "d1",
      title: "Task Decomposition",
      concept:
        "Decompose to the right grain. Subtasks too narrow lose the context needed to do them well; too broad and you're back to one mega-task.",
      antipattern:
        "Slicing 'summarise this repo' into 'read line 1–50', 'read line 51–100' — each worker is blind to the whole.",
      right:
        "Decompose by independent unit of meaning (per-module summary), not by arbitrary size.",
      tip: "Narrow-decomposition failure is a favourite distractor. The fix is re-grain, not more agents.",
      output: [
        L("cmd", "$ python3 domains/domain1_orchestration/task1_4_decomposition.py"),
        L("head", "Decompose: summarise a 6-module service"),
        L("bad", "By line-range → worker can't tell what the code is for (no context)"),
        L("good", "By module → each worker owns a coherent unit, summary is accurate"),
        L("tip", "Re-grain the decomposition before you reach for a classifier or more workers."),
      ],
      q: ["q3"],
      links: ["1.3", "5.3"],
    },
    {
      id: "1.5",
      d: "d1",
      title: "Prerequisite Gates",
      concept:
        "A gate blocks an action until a condition is provably met — identity verified before a refund, tests green before a deploy. It lives in code, not the prompt.",
      antipattern:
        "Instructing the model 'always verify identity first' and trusting it every time.",
      right:
        "A code gate that refuses the refund tool call unless verified==true. Deterministic.",
      tip: "Theme 1 in one sentence: a guarantee you need = a gate in code, not a line in a prompt.",
      output: [
        L("cmd", "$ python3 domains/domain1_orchestration/task1_5_prerequisite_gate.py"),
        L("head", "Refund requires verified identity"),
        L("dim", "model → refund(order=1182, amount=49.00)"),
        L("bad", "Prompt-only rule: model skips verification under pressure → unsafe refund"),
        L("good", "Gate: refund() raises GateError('identity unverified') → blocked deterministically"),
        L("good", "after verify_identity() passes → refund proceeds"),
        L("tip", "If the question says 'must never happen', look for the code mechanism, not better wording."),
      ],
      q: ["q1", "q4"],
      links: ["1.6", "3.4"],
    },
    {
      id: "1.6",
      d: "d1",
      title: "Interception Hooks",
      concept:
        "A hook intercepts a tool call before/after it runs to enforce policy, redact, log, or veto — independent of what the model intended.",
      antipattern:
        "Relying on the model to remember to redact PII before calling an external tool.",
      right:
        "A pre-tool hook that strips PII from every outbound call, regardless of the prompt.",
      tip: "Hooks are deterministic interception points — the exam's go-to for 'enforce on every call'.",
      output: [
        L("cmd", "$ python3 domains/domain1_orchestration/task1_6_interception_hook.py"),
        L("head", "Pre-tool hook redacts PII"),
        L("dim", "model → web_search('refund for card 4111 1111 1111 1111')"),
        L("good", "pre_tool_hook → redacts PAN → web_search('refund for card ****')"),
        L("bad", "No hook: card number leaves the system → compliance failure"),
        L("tip", "‘On every tool call, without exception’ ⇒ a hook."),
      ],
      q: ["q4"],
      links: ["1.5", "3.4"],
    },
    {
      id: "1.7",
      d: "d1",
      title: "Escalation & Human-in-the-loop",
      concept:
        "Some outcomes need a human. Design explicit escalation paths with the context the human needs, not a dead-end apology.",
      antipattern:
        "Looping forever on an unsolvable request, or escalating with no case context.",
      right:
        "Detect the stop condition, package the case facts, and hand to a human with a clear reason.",
      tip: "Escalation is a designed exit, not a failure — and it carries extracted facts (Theme 3).",
      output: [
        L("cmd", "$ python3 domains/domain1_orchestration/task1_7_escalation.py"),
        L("head", "Escalate a stuck refund dispute"),
        L("dim", "loop detects: 2 failed resolutions + policy edge case"),
        L("bad", "Anti-pattern: retry the same path a 3rd time → user frustration"),
        L("good", "escalate(reason, case_facts={order, history, attempted}) → human queue"),
        L("tip", "A good escalation hands over extracted facts, not the raw transcript."),
      ],
      q: ["q1"],
      links: ["5.3", "1.1"],
    },

    // Domain 2
    {
      id: "2.1",
      d: "d2",
      title: "Tool Description Quality",
      concept:
        "The model picks tools from their names and descriptions. Most 'wrong tool' problems are description problems.",
      antipattern:
        "Adding a routing/classifier layer to fix tool confusion caused by vague descriptions.",
      right:
        "Rewrite the description: say what it does, when to use it, and when NOT to.",
      tip: "Theme 2: vague descriptions → better descriptions, not a new component.",
      output: [
        L("cmd", "$ python3 domains/domain2_tools_mcp/task2_1_descriptions.py"),
        L("head", "lookup_order vs search_orders confusion"),
        L("bad", "‘search’ and ‘lookup’ both say 'find an order' → model guesses wrong 40%"),
        L("good", "lookup_order: 'fetch ONE order by exact id'; search_orders: 'find many by filter'"),
        L("good", "selection accuracy 60% → 98% with no extra component"),
        L("tip", "Disambiguate with description text before adding any routing logic."),
      ],
      q: ["q5"],
      links: ["2.5", "2.2"],
    },
    {
      id: "2.2",
      d: "d2",
      title: "Tool Schema Design",
      concept:
        "A typed schema constrains inputs: required vs optional, enums, and types do validation the prompt can't guarantee.",
      antipattern:
        "Accepting a single free-text 'query' blob and parsing it yourself afterward.",
      right:
        "Explicit typed params with required/optional and enums where the value set is known.",
      tip: "Enums and required fields move correctness from the prompt into the schema.",
      output: [
        L("cmd", "$ python3 domains/domain2_tools_mcp/task2_2_schema.py"),
        L("head", "book_flight schema"),
        L("bad", "params: { query: string } → 'cheap flight nyc maybe friday' (unparseable)"),
        L("good", "params: { from:str*, to:str*, date:date*, cabin: enum[economy,business] }"),
        L("tip", "If a field has a known value set, make it an enum — not a string."),
      ],
      q: ["q5"],
      links: ["2.1", "4.4"],
    },
    {
      id: "2.3",
      d: "d2",
      title: "MCP Servers & Integration",
      concept:
        "MCP is a standard way to expose tools/resources to a model. A server publishes capabilities; the client (Claude) consumes them uniformly.",
      antipattern:
        "Hard-wiring one bespoke integration per tool with no shared contract.",
      right:
        "Expose tools through an MCP server so any compatible client gets them with one contract.",
      tip: "MCP = a uniform contract for tools/resources, not a model feature you prompt.",
      output: [
        L("cmd", "$ python3 domains/domain2_tools_mcp/task2_3_mcp.py"),
        L("head", "Connect a filesystem MCP server"),
        L("dim", "server advertises: read_file, list_dir, search"),
        L("good", "client discovers tools via the MCP handshake — no per-tool glue code"),
        L("tip", "Think 'USB-C for tools': one contract, many clients."),
      ],
      q: ["q6"],
      links: ["2.1", "3.5"],
    },
    {
      id: "2.4",
      d: "d2",
      title: "Structured Tool Errors",
      concept:
        "A tool's error is part of its interface. A structured, actionable error lets the model recover; a stack trace doesn't.",
      antipattern:
        "Returning a raw exception string and hoping the model figures it out.",
      right:
        "Return { error, code, hint } so the next turn can correct the call.",
      tip: "Good errors are recovery instructions. Structure them like outputs.",
      output: [
        L("cmd", "$ python3 domains/domain2_tools_mcp/task2_4_errors.py"),
        L("head", "book_flight with a bad date"),
        L("bad", "raise ValueError('time data ...') → model retries the same bad call"),
        L("good", "{error:'invalid_date', hint:'use YYYY-MM-DD'} → model fixes it next turn"),
        L("tip", "An error the model can act on beats a precise error it can't."),
      ],
      q: ["q6"],
      links: ["5.5", "2.2"],
    },
    {
      id: "2.5",
      d: "d2",
      title: "Tool Selection & Ambiguity",
      concept:
        "When two tools overlap, the model stalls or guesses. Reduce the surface: merge, rename, or scope tools so each has one clear job.",
      antipattern:
        "Ten near-identical tools and a prompt paragraph explaining which to use when.",
      right:
        "Fewer, sharper tools — or one tool with an enum mode — so selection is unambiguous.",
      tip: "Reducing tool overlap beats explaining the overlap in the prompt.",
      output: [
        L("cmd", "$ python3 domains/domain2_tools_mcp/task2_5_selection.py"),
        L("head", "3 overlapping search tools"),
        L("bad", "search_web / search_news / search_docs → model picks wrong source"),
        L("good", "one search(source: enum[web,news,docs]) → selection is trivial"),
        L("tip", "Collapse overlap into an enum param when the tools share a shape."),
      ],
      q: ["q5"],
      links: ["2.1", "2.2"],
    },

    // Domain 3
    {
      id: "3.1",
      d: "d3",
      title: "Configuration Scope",
      concept:
        "Claude Code config is layered: enterprise → user → project (CLAUDE.md, settings). Put each rule at the scope it should apply to.",
      antipattern:
        "Pasting a project's build rules into your personal user settings — they leak everywhere.",
      right:
        "Project rules in the repo's CLAUDE.md; personal preferences in user settings; org policy at enterprise scope.",
      tip: "Right rule, right scope. Project knowledge ⇒ project file, not global.",
      output: [
        L("cmd", "$ python3 domains/domain3_claude_code/task3_1_config_scope.py"),
        L("head", "Where does 'use pnpm, never npm' go?"),
        L("bad", "user settings → applies to every repo you touch, even npm ones"),
        L("good", "project CLAUDE.md → travels with the repo, applies only here"),
        L("tip", "Scope precedence: enterprise > user > project for policy; project owns repo facts."),
      ],
      q: ["q7"],
      links: ["3.3", "3.6"],
    },
    {
      id: "3.2",
      d: "d3",
      title: "Plan Mode vs Direct Execution",
      concept:
        "Plan mode proposes a plan for approval before touching anything. Use it for risky/multi-file work; direct execution for small, reversible edits.",
      antipattern:
        "Letting an agent directly rewrite 40 files with no plan or review.",
      right:
        "Plan mode for high-blast-radius changes; direct for a one-line fix.",
      tip: "Match the ceremony to the blast radius. Big/irreversible ⇒ plan first.",
      output: [
        L("cmd", "$ python3 domains/domain3_claude_code/task3_2_plan_vs_direct.py"),
        L("head", "Rename a public API across the repo"),
        L("good", "plan mode → review 23-file plan → approve → execute"),
        L("bad", "direct execution → half-applied rename, broken build, no review point"),
        L("tip", "Reversibility and blast radius decide plan vs direct."),
      ],
      q: ["q8"],
      links: ["3.3", "3.1"],
    },
    {
      id: "3.3",
      d: "d3",
      title: "Permissions & Path Rules",
      concept:
        "Allow/deny rules scope what tools can touch. Deny by default for destructive ops; allow-list the paths an agent may write.",
      antipattern:
        "Granting blanket write/exec everywhere because setting rules is tedious.",
      right:
        "Allow-list writable paths, deny shell/network unless needed, review escalations.",
      tip: "Least privilege is a config, not a hope. Deny destructive by default.",
      output: [
        L("cmd", "$ python3 domains/domain3_claude_code/task3_3_permissions.py"),
        L("head", "Agent tries to edit /etc and run curl"),
        L("bad", "blanket allow → agent edits outside the repo"),
        L("good", "allow: ./src/** ; deny: bash(curl|rm) → out-of-scope action blocked"),
        L("tip", "Path allow-lists + denied destructive commands = safe autonomy."),
      ],
      q: ["q7", "q8"],
      links: ["3.1", "1.5"],
    },
    {
      id: "3.4",
      d: "d3",
      title: "Hooks in Claude Code",
      concept:
        "Pre/post-tool hooks run your shell commands around tool calls — format on save, run tests after edits, block a forbidden command.",
      antipattern:
        "Asking the model in the prompt to 'remember to run the formatter'.",
      right:
        "A post-edit hook runs the formatter every time, deterministically.",
      tip: "Same idea as Domain 1 hooks: guarantee via interception, not instruction.",
      output: [
        L("cmd", "$ python3 domains/domain3_claude_code/task3_4_hooks.py"),
        L("head", "Format-on-edit hook"),
        L("good", "PostToolUse(Edit) → prettier --write → always formatted"),
        L("bad", "prompt-only reminder → formatting skipped under load"),
        L("tip", "Claude Code hooks are the project-level form of 'guarantees beat instructions'."),
      ],
      q: ["q4"],
      links: ["1.6", "3.3"],
    },
    {
      id: "3.5",
      d: "d3",
      title: "Subagents & Delegation",
      concept:
        "Delegate a self-contained chunk (e.g. 'explore the codebase') to a subagent so the main context stays clean.",
      antipattern:
        "Dumping a 4,000-line grep dump into the main agent's context.",
      right:
        "A subagent explores, returns a short structured finding; the main agent stays focused.",
      tip: "Delegation protects the main context window (Theme 3) — that's the point.",
      output: [
        L("cmd", "$ python3 domains/domain3_claude_code/task3_5_subagents.py"),
        L("head", "Delegate repo exploration"),
        L("bad", "inline grep → 4k lines flood main context → later steps degrade"),
        L("good", "subagent returns: '3 call sites in api/*, see lines …' (12 lines)"),
        L("tip", "Delegate noisy exploration; keep only the distilled finding."),
      ],
      q: ["q9"],
      links: ["5.3", "1.3"],
    },
    {
      id: "3.6",
      d: "d3",
      title: "Slash Commands & Custom Workflows",
      concept:
        "Reusable slash commands capture a repeatable workflow (e.g. /review) so it runs the same way every time.",
      antipattern:
        "Re-typing a 200-word review prompt from memory, differently each time.",
      right:
        "A committed /review command encodes the steps; everyone runs the identical workflow.",
      tip: "Slash commands make a good workflow a shared, versioned artifact.",
      output: [
        L("cmd", "$ python3 domains/domain3_claude_code/task3_6_commands.py"),
        L("head", "/review command"),
        L("good", ".claude/commands/review.md → consistent multi-step review"),
        L("tip", "If you do it twice, make it a command."),
      ],
      q: ["q7"],
      links: ["3.1", "5.5"],
    },

    // Domain 4
    {
      id: "4.1",
      d: "d4",
      title: "Clear Instructions & Role",
      concept:
        "Specific instructions and an explicit role beat clever phrasing. Say the task, the constraints, and the output shape.",
      antipattern:
        "‘Be helpful and do your best’ with no role, constraints, or format.",
      right:
        "‘You are a release-notes editor. Given commits, output 3 bullets, ≤12 words each.’",
      tip: "Specificity is the cheapest reliability win on the exam.",
      output: [
        L("cmd", "$ python3 domains/domain4_prompt_output/task4_1_clear_instructions.py"),
        L("head", "Vague vs specific"),
        L("bad", "‘summarise this’ → length and tone vary wildly run to run"),
        L("good", "role + constraints + format → stable, on-spec output"),
        L("tip", "Name the role, the constraints, and the exact output shape."),
      ],
      q: ["q10"],
      links: ["4.3", "4.5"],
    },
    {
      id: "4.2",
      d: "d4",
      title: "Few-Shot Examples",
      concept:
        "A couple of well-chosen examples teach format and edge-case handling better than a paragraph of description.",
      antipattern:
        "Describing the desired format in prose and hoping it's followed exactly.",
      right:
        "2–4 examples that show the format and at least one tricky case.",
      tip: "Show, don't tell — and include the edge case you care about.",
      output: [
        L("cmd", "$ python3 domains/domain4_prompt_output/task4_2_few_shot.py"),
        L("head", "Classify support tickets"),
        L("bad", "zero-shot prose spec → inconsistent labels on edge cases"),
        L("good", "3 examples incl. a refund-vs-cancel edge → consistent labels"),
        L("tip", "Pick examples that cover the boundary, not just the easy middle."),
      ],
      q: ["q10"],
      links: ["4.1", "4.4"],
    },
    {
      id: "4.3",
      d: "d4",
      title: "XML / Structured Prompting",
      concept:
        "Delimiters (XML tags) separate instructions, context, and data so the model parses your intent unambiguously.",
      antipattern:
        "One run-on prompt where the document and the instructions blur together.",
      right:
        "<instructions>…</instructions><document>…</document> — clean boundaries.",
      tip: "Tags reduce 'the model answered about the wrong part' errors.",
      output: [
        L("cmd", "$ python3 domains/domain4_prompt_output/task4_3_xml.py"),
        L("head", "Q&A over a contract"),
        L("bad", "instructions + contract concatenated → model quotes the instructions"),
        L("good", "tagged sections → model answers only from <document>"),
        L("tip", "Wrap the data so it can't be mistaken for the instructions."),
      ],
      q: ["q11"],
      links: ["4.1", "4.5"],
    },
    {
      id: "4.4",
      d: "d4",
      title: "Tool-Use for Structured Output",
      concept:
        "To get reliable JSON, define a tool/schema and let the model 'call' it. The schema enforces shape; nullable fields handle 'unknown'.",
      antipattern:
        "Asking for JSON in prose and regex-parsing whatever comes back.",
      right:
        "A schema with required fields and nullable optionals; validate, retry on miss.",
      tip: "Structured output = schema + validation, not 'please return valid JSON'.",
      output: [
        L("cmd", "$ python3 domains/domain4_prompt_output/task4_4_structured.py"),
        L("head", "Extract invoice fields"),
        L("bad", "‘return JSON’ → trailing prose, broken parse 1 in 5"),
        L("good", "schema {total:num*, tax:num?, po:str?} + validate → 100% parseable"),
        L("tip", "Make 'unknown' representable (nullable) so the model never invents a value."),
      ],
      q: ["q12"],
      links: ["2.2", "5.5"],
    },
    {
      id: "4.5",
      d: "d4",
      title: "Prefilling & Output Control",
      concept:
        "Prefilling the start of the response (e.g. '{') forces format and skips preamble. Constrain endings with stop sequences.",
      antipattern:
        "Letting the model open with 'Sure! Here's the JSON:' before the payload.",
      right:
        "Prefill '{' to force straight-to-JSON; stop sequence to bound the output.",
      tip: "Prefill = a steering wheel for the first tokens; cheap and reliable.",
      output: [
        L("cmd", "$ python3 domains/domain4_prompt_output/task4_5_prefill.py"),
        L("head", "Force JSON-only"),
        L("bad", "no prefill → chatty preamble breaks the parser"),
        L("good", "assistant prefilled with '{' → clean JSON from token 1"),
        L("tip", "Prefill the opening delimiter to kill preamble."),
      ],
      q: ["q11"],
      links: ["4.4", "4.1"],
    },
    {
      id: "4.6",
      d: "d4",
      title: "Chain-of-Thought & Extended Thinking",
      concept:
        "For multi-step reasoning, give the model room to think before answering — then separate the reasoning from the final answer.",
      antipattern:
        "Demanding an instant final answer on a problem that needs working-out.",
      right:
        "Let it reason in a <thinking> block, then emit a clean final answer.",
      tip: "Reasoning room raises accuracy; just don't ship the scratch work as the answer.",
      output: [
        L("cmd", "$ python3 domains/domain4_prompt_output/task4_6_cot.py"),
        L("head", "Multi-step pricing calc"),
        L("bad", "‘answer only’ → arithmetic slip, wrong total"),
        L("good", "think step-by-step → correct total; final answer extracted cleanly"),
        L("tip", "Separate the thinking from the deliverable so downstream parses only the answer."),
      ],
      q: ["q12"],
      links: ["5.3", "4.3"],
    },

    // Domain 5
    {
      id: "5.1",
      d: "d5",
      title: "Context as a Scarce Resource",
      concept:
        "The context window is finite and every token competes. Spend it on what the current step needs; evict the rest.",
      antipattern:
        "Keeping the entire transcript and every tool dump in context 'just in case'.",
      right:
        "Curate: keep the goal, the live facts, and the last useful result; drop the noise.",
      tip: "Theme 3. 'Just in case' context is how later steps quietly degrade.",
      output: [
        L("cmd", "$ python3 domains/domain5_context_reliability/task5_1_scarcity.py"),
        L("head", "Long support session"),
        L("bad", "full 40-turn transcript retained → model loses the current ask"),
        L("good", "keep goal + case-facts + last turn → focused, accurate"),
        L("tip", "Curate context every turn; don't hoard it."),
      ],
      q: ["q9"],
      links: ["5.2", "5.3"],
    },
    {
      id: "5.2",
      d: "d5",
      title: "Compaction & Summarisation",
      concept:
        "When context fills, compact it: replace old turns with a faithful summary that preserves decisions and open threads.",
      antipattern:
        "Hard-truncating the oldest messages and silently losing key decisions.",
      right:
        "Summarise older turns into a compact state note; keep recent turns verbatim.",
      tip: "Compaction preserves meaning; truncation just drops tokens.",
      output: [
        L("cmd", "$ python3 domains/domain5_context_reliability/task5_2_compaction.py"),
        L("head", "Compact at 80% window"),
        L("bad", "truncate oldest 20 turns → forgets the agreed refund cap"),
        L("good", "summarise → 'decided: cap £50; pending: address change' → nothing lost"),
        L("tip", "Summarise to preserve decisions; never blind-truncate state."),
      ],
      q: ["q9"],
      links: ["5.1", "5.3"],
    },
    {
      id: "5.3",
      d: "d5",
      title: "Fact Extraction & Scratchpads",
      concept:
        "Pull the durable facts (IDs, decisions, constraints) into a small structured scratchpad the agent carries forward.",
      antipattern:
        "Re-deriving the order id and the policy from the raw transcript every turn.",
      right:
        "A case-facts object: { order_id, tier, policy_cap, verified } updated as you go.",
      tip: "Extracted facts are cheap to carry and survive compaction.",
      output: [
        L("cmd", "$ python3 domains/domain5_context_reliability/task5_3_scratchpad.py"),
        L("head", "Case-facts scratchpad"),
        L("good", "facts = {order:1182, tier:gold, cap:50, verified:true}"),
        L("good", "survives compaction; every turn reads facts, not the transcript"),
        L("tip", "Promote durable facts out of the transcript into a structured note."),
      ],
      q: ["q9"],
      links: ["5.1", "5.4"],
    },
    {
      id: "5.4",
      d: "d5",
      title: "Explicit Context Handoff",
      concept:
        "When one agent hands to another, pass the facts explicitly. The receiver can't see the sender's context.",
      antipattern:
        "Assuming the next agent 'remembers' what the previous one found.",
      right:
        "Hand off a structured brief: goal, facts, constraints, what's done, what's next.",
      tip: "Between agents, nothing is shared unless you pass it. Make handoffs explicit.",
      output: [
        L("cmd", "$ python3 domains/domain5_context_reliability/task5_4_handoff.py"),
        L("head", "Research → writer handoff"),
        L("bad", "writer agent gets only 'write it up' → invents details"),
        L("good", "handoff brief: {findings[], sources[], constraints} → faithful writeup"),
        L("tip", "Each handoff is a fresh context; package what the receiver needs."),
      ],
      q: ["q3"],
      links: ["1.3", "5.3"],
    },
    {
      id: "5.5",
      d: "d5",
      title: "Retries, Validation & Idempotency",
      concept:
        "Validate outputs against a schema; retry on failure with the error fed back; make actions idempotent so retries are safe.",
      antipattern:
        "Retrying a non-idempotent 'charge card' call and double-charging.",
      right:
        "Validate → retry-with-error for reads; idempotency keys for writes.",
      tip: "Retry safely: validate everything, and key your writes.",
      output: [
        L("cmd", "$ python3 domains/domain5_context_reliability/task5_5_retry.py"),
        L("head", "Validate & retry extraction"),
        L("bad", "retry charge() → second charge lands → duplicate"),
        L("good", "charge(idempotency_key=…) → retry is a no-op; validate → 1 retry fixes schema"),
        L("tip", "Idempotency keys turn a dangerous retry into a safe one."),
      ],
      q: ["q12"],
      links: ["2.4", "4.4"],
    },
    {
      id: "5.6",
      d: "d5",
      title: "Provenance & Citations",
      concept:
        "Tie claims back to sources so output is auditable and the model is discouraged from inventing facts.",
      antipattern:
        "A confident summary with no link back to where each claim came from.",
      right:
        "Each finding carries its source id; the synthesis cites them.",
      tip: "Provenance makes hallucination visible — and the answer trustworthy.",
      output: [
        L("cmd", "$ python3 domains/domain5_context_reliability/task5_6_provenance.py"),
        L("head", "Cited research summary"),
        L("bad", "uncited summary → can't tell fact from invention"),
        L("good", "each bullet → [src #3]; coordinator preserves citations end-to-end"),
        L("tip", "Carry source ids through every handoff so the final answer is auditable."),
      ],
      q: ["q3"],
      links: ["1.3", "5.4"],
    },
  ];

  // ---- Scenarios (6) ----------------------------------------------------
  const scenarios = [
    {
      id: "s1",
      n: 1,
      title: "Customer Support Resolution Agent",
      domains: ["d1", "d2", "d5"],
      summary:
        "A real support agent: an agentic loop guarded by a prerequisite gate and an interception hook, returning structured errors, carrying case-facts, and escalating cleanly.",
      steps: [
        { t: "Agent loop", d: "Gather → act → verify until resolved or stop.", task: "1.1" },
        { t: "Prerequisite gate", d: "No refund tool call until identity is verified — in code.", task: "1.5" },
        { t: "Interception hook", d: "Redact PII on every outbound tool call.", task: "1.6" },
        { t: "Structured errors", d: "Tools return { error, hint } so the loop recovers.", task: "2.4" },
        { t: "Case-facts", d: "Durable scratchpad survives compaction.", task: "5.3" },
        { t: "Escalation", d: "Stuck → hand to a human with packaged facts.", task: "1.7" },
      ],
    },
    {
      id: "s2",
      n: 2,
      title: "Code Generation with Claude Code",
      domains: ["d3", "d5"],
      summary:
        "Config-scope decisions, plan-vs-direct execution, path permission rules, and iterative refinement on a real change.",
      steps: [
        { t: "Config scope", d: "Repo rules in CLAUDE.md, prefs in user settings.", task: "3.1" },
        { t: "Plan vs direct", d: "Plan mode for the multi-file API rename.", task: "3.2" },
        { t: "Path rules", d: "Allow ./src/**, deny destructive shell.", task: "3.3" },
        { t: "Refinement", d: "Validate, feed errors back, iterate.", task: "5.5" },
      ],
    },
    {
      id: "s3",
      n: 3,
      title: "Multi-Agent Research System",
      domains: ["d1", "d2", "d5"],
      summary:
        "A coordinator with subagents. Shows a narrow-decomposition failure and its fix, error propagation, and end-to-end provenance.",
      steps: [
        { t: "Orchestrator–worker", d: "Coordinator briefs independent workers.", task: "1.3" },
        { t: "Decomposition fix", d: "Re-grain from line-ranges to topics.", task: "1.4" },
        { t: "Explicit handoff", d: "Findings + sources passed to the writer.", task: "5.4" },
        { t: "Provenance", d: "Citations preserved through synthesis.", task: "5.6" },
      ],
    },
    {
      id: "s4",
      n: 4,
      title: "Developer Productivity",
      domains: ["d2", "d3", "d1"],
      summary:
        "Real incremental exploration (Grep → Read) over a sample repo, with delegation to a subagent and a carried scratchpad.",
      steps: [
        { t: "Incremental exploration", d: "Grep to locate, Read only what matters.", task: "2.5" },
        { t: "Delegation", d: "Subagent explores; main context stays clean.", task: "3.5" },
        { t: "Scratchpad", d: "Carry the distilled findings forward.", task: "5.3" },
      ],
    },
    {
      id: "s5",
      n: 5,
      title: "Claude Code for CI/CD",
      domains: ["d3", "d4"],
      summary:
        "Non-interactive review in a pipeline: headless -p mode, structured output, false-positive control, and a multi-pass review.",
      steps: [
        { t: "Headless run", d: "Non-interactive -p for CI.", task: "3.6" },
        { t: "Structured output", d: "Schema'd findings the pipeline can gate on.", task: "4.4" },
        { t: "False-positive control", d: "Few-shot + thresholds cut noise.", task: "4.2" },
      ],
    },
    {
      id: "s6",
      n: 6,
      title: "Structured Data Extraction",
      domains: ["d4", "d5"],
      summary:
        "A tool-use schema with nullable fields, validation/retry, batch routing, and confidence-based routing to a human.",
      steps: [
        { t: "Tool-use schema", d: "Typed fields, nullable optionals.", task: "4.4" },
        { t: "Validate & retry", d: "Schema miss → retry with the error.", task: "5.5" },
        { t: "Confidence routing", d: "Low confidence → human review queue.", task: "1.7" },
      ],
    },
  ];

  // ---- Sample quiz (12, original questions) -----------------------------
  const questions = [
    {
      id: "q1",
      task: "1.5",
      domain: "d1",
      prompt:
        "A support agent must NEVER issue a refund before the customer's identity is verified. Under load, a prompt instruction to 'always verify first' occasionally gets skipped. What's the right fix?",
      options: [
        "Reword the system prompt more forcefully",
        "Add a code gate that blocks the refund tool unless verified == true",
        "Train a classifier to detect risky refunds",
        "Add a second model to double-check the first",
      ],
      answer: 1,
      why: "A must-follow guarantee belongs in code, not a prompt. A prerequisite gate makes the rule deterministic. (Theme 1.)",
    },
    {
      id: "q2",
      task: "1.2",
      domain: "d1",
      prompt:
        "A linear, three-step refactor is currently split across a coordinator and four subagents and runs slowly. What should you do?",
      options: [
        "Add a fifth subagent to parallelise further",
        "Collapse it to a single agent with good tools",
        "Add a message bus between the subagents",
        "Cache the subagent outputs",
      ],
      answer: 1,
      why: "Multi-agent only pays off for independent, parallel work. A linear task is one agent — fewer handoffs, less loss.",
    },
    {
      id: "q3",
      task: "1.4",
      domain: "d1",
      prompt:
        "Research subagents each summarise an arbitrary 50-line slice of a document and produce shallow, context-free notes. The best fix is to:",
      options: [
        "Give each subagent the whole document too",
        "Re-grain the decomposition to coherent topics/sections",
        "Add a routing classifier before the subagents",
        "Increase the number of subagents",
      ],
      answer: 1,
      why: "Narrow-decomposition failure: fix the grain, not the agent count. Decompose by unit of meaning.",
    },
    {
      id: "q4",
      task: "1.6",
      domain: "d1",
      prompt:
        "PII must be stripped from every outbound tool call, no exceptions. Where does this belong?",
      options: [
        "A reminder in the system prompt",
        "A pre-tool interception hook that redacts on every call",
        "A note in the tool's description",
        "A post-hoc audit log",
      ],
      answer: 1,
      why: "'On every call, without exception' is a deterministic-interception job — a hook, not an instruction.",
    },
    {
      id: "q5",
      task: "2.1",
      domain: "d2",
      prompt:
        "The model frequently picks search_orders when it should pick lookup_order. Both descriptions say 'find an order'. Best first move?",
      options: [
        "Add a routing classifier to choose the tool",
        "Merge them into one mega-tool",
        "Rewrite the descriptions to disambiguate (one vs many)",
        "Remove search_orders entirely",
      ],
      answer: 2,
      why: "Tool confusion from vague descriptions is fixed by better descriptions — proportionate root-cause fix. (Theme 2.)",
    },
    {
      id: "q6",
      task: "2.4",
      domain: "d2",
      prompt:
        "A tool raises a raw Python traceback on bad input and the agent keeps retrying the same wrong call. Best fix?",
      options: [
        "Return a structured { error, hint } the model can act on",
        "Suppress the error and return null",
        "Add a retry limit and give up",
        "Log the traceback and continue",
      ],
      answer: 0,
      why: "Errors are part of the interface. An actionable structured error lets the next turn self-correct.",
    },
    {
      id: "q7",
      task: "3.1",
      domain: "d3",
      prompt:
        "Your team standard is 'use pnpm, never npm' for this repo. Where should that rule live?",
      options: [
        "Your personal user settings",
        "The repo's project CLAUDE.md",
        "An enterprise-wide policy",
        "A comment in package.json",
      ],
      answer: 1,
      why: "Repo-specific facts go in the project config so they travel with the repo and apply only there.",
    },
    {
      id: "q8",
      task: "3.2",
      domain: "d3",
      prompt:
        "An agent needs to rename a public API across 23 files. Which execution mode fits?",
      options: [
        "Direct execution — it's faster",
        "Plan mode — review the plan before applying",
        "Run it twice and diff",
        "Split into 23 separate prompts",
      ],
      answer: 1,
      why: "High blast radius and low reversibility ⇒ plan mode with a review/approval checkpoint.",
    },
    {
      id: "q9",
      task: "5.2",
      domain: "d5",
      prompt:
        "A long session is nearing the context limit and you must not lose the agreed refund cap. What do you do?",
      options: [
        "Hard-truncate the oldest messages",
        "Summarise older turns into a state note, keep recent turns",
        "Start a brand-new session",
        "Lower the temperature",
      ],
      answer: 1,
      why: "Compaction preserves decisions and open threads; blind truncation silently drops state.",
    },
    {
      id: "q10",
      task: "4.1",
      domain: "d4",
      prompt:
        "Summaries vary wildly in length and tone between runs. The cheapest reliability fix is to:",
      options: [
        "Lower temperature to 0 and hope",
        "Specify role, constraints, and exact output format",
        "Switch to a larger model",
        "Add three more paragraphs of context",
      ],
      answer: 1,
      why: "Specificity — role + constraints + format — is the cheapest, highest-yield reliability win.",
    },
    {
      id: "q11",
      task: "4.3",
      domain: "d4",
      prompt:
        "When answering questions over a contract, the model sometimes answers about the instructions themselves. Best mitigation?",
      options: [
        "Put the contract first, instructions last",
        "Wrap data and instructions in distinct XML tags",
        "Shorten the contract",
        "Ask the question twice",
      ],
      answer: 1,
      why: "Delimiting with tags gives clean boundaries so the model answers only from the data section.",
    },
    {
      id: "q12",
      task: "4.4",
      domain: "d4",
      prompt:
        "You need reliably parseable JSON from extraction, and 'unknown' values must not be invented. Best approach?",
      options: [
        "Ask for JSON in the prompt and regex-parse it",
        "Define a tool schema with required + nullable fields, then validate",
        "Lower temperature and retry until it parses",
        "Post-process with a second model",
      ],
      answer: 1,
      why: "Tool-use schema enforces shape; nullable fields make 'unknown' representable so nothing is fabricated.",
    },
  ];

  // ---- Cheat sheet ------------------------------------------------------
  const cheat = [
    { d: "d1", fact: "An agent is a loop with a stop condition and per-turn verification — not one prompt.", task: "1.1" },
    { d: "d1", fact: "Default to a single agent; add agents only for independent, parallel work.", task: "1.2" },
    { d: "d1", fact: "Must-follow rules = code gates, not prompt instructions.", task: "1.5" },
    { d: "d1", fact: "‘On every tool call’ ⇒ an interception hook.", task: "1.6" },
    { d: "d2", fact: "Most 'wrong tool' bugs are vague-description bugs — fix the text first.", task: "2.1" },
    { d: "d2", fact: "Known value set ⇒ enum, not free-text string.", task: "2.2" },
    { d: "d2", fact: "MCP = one uniform contract for tools/resources across clients.", task: "2.3" },
    { d: "d2", fact: "Return structured, actionable errors the model can recover from.", task: "2.4" },
    { d: "d3", fact: "Project facts in CLAUDE.md; personal prefs in user settings; org rules at enterprise scope.", task: "3.1" },
    { d: "d3", fact: "Plan mode for high blast radius; direct execution for small reversible edits.", task: "3.2" },
    { d: "d3", fact: "Least privilege via allow/deny path rules — deny destructive by default.", task: "3.3" },
    { d: "d3", fact: "Claude Code hooks enforce steps (format/test) deterministically.", task: "3.4" },
    { d: "d4", fact: "Role + constraints + output format = cheap reliability.", task: "4.1" },
    { d: "d4", fact: "Few-shot examples should cover the boundary case you care about.", task: "4.2" },
    { d: "d4", fact: "Tag data vs instructions so the model answers the right part.", task: "4.3" },
    { d: "d4", fact: "Structured output = schema + validation + nullable fields.", task: "4.4" },
    { d: "d5", fact: "Context is scarce — curate every turn, don't hoard.", task: "5.1" },
    { d: "d5", fact: "Compact (summarise) instead of truncating to preserve decisions.", task: "5.2" },
    { d: "d5", fact: "Promote durable facts into a structured scratchpad.", task: "5.3" },
    { d: "d5", fact: "Between agents nothing is shared unless you pass it explicitly.", task: "5.4" },
    { d: "d5", fact: "Validate outputs; key your writes so retries are safe (idempotency).", task: "5.5" },
  ];

  window.CCA = { domains, themes, tasks, scenarios, questions, cheat,
    taskById: Object.fromEntries(tasks.map((t) => [t.id, t])),
    questionById: Object.fromEntries(questions.map((q) => [q.id, q])),
    domainById: Object.fromEntries(domains.map((d) => [d.id, d])),
  };
})();
