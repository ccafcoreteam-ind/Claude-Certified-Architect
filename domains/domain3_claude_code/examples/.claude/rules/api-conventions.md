---
paths: ["src/api/**/*"]
---
# API conventions — example PATH-SCOPED rule (Domain 3, Task 3.3)
#
# Loads only when editing files under src/api/. This is how you give different areas of a
# codebase different conventions without one giant CLAUDE.md the model has to infer from.

API handler conventions:
- Use async/await; never mix with raw promise chains.
- Validate input at the boundary; return structured errors with an errorCategory
  (transient / validation / business_rule / permission) — see Domain 2, Task 2.2.
- Never log secrets or full request bodies.
- All money fields are integers in cents.
