"""
Domain 4 · Task 4.3 — Structured output via tool use and JSON schemas.

THE BIG IDEA
============
THE RELIABLE TRICK: to get guaranteed schema-compliant JSON, define a "tool" whose INPUT
PARAMETERS ARE your desired output schema, and read the data from the model's tool_use
call. This eliminates JSON SYNTAX errors entirely.

THE LIMIT: schemas eliminate SYNTAX errors but NOT SEMANTIC errors — line items that don't
sum to the total, or values in the wrong field, still happen and need validation (Task 4.4).

SCHEMA DESIGN RULES that prevent hallucination:
  * Make fields NULLABLE/optional when sources may genuinely lack the info. If a field is
    REQUIRED, the model will FABRICATE a value to satisfy the schema — the single most
    important schema-design fact on the exam.
  * EXTENSIBLE ENUMS: add "unclear" for ambiguous cases and "other" + a free-text detail
    field, so real-world variety isn't force-fit into wrong categories.
  * Pair NORMALIZATION rules with strict schemas (how to standardize dates/currencies).
  * Combine with tool_choice (Task 2.3): "any" guarantees structured output when the doc
    type (hence schema) is unknown; forced selection guarantees a specific extraction runs.
"""

import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause, analogy, pitfall


# The tool's input_schema IS the output contract.
EXTRACTION_TOOL = {
    "name": "record_invoice",
    "description": "Record the structured fields extracted from an invoice document.",
    "input_schema": {
        "type": "object",
        "properties": {
            "vendor": {"type": "string"},
            # nullable: the model may legitimately not find an amount
            "amount": {"type": ["number", "null"]},
            "currency": {"type": ["string", "null"]},
            "date": {"type": ["string", "null"], "description": "ISO 8601 YYYY-MM-DD"},
            # extensible enum: 'other' + detail prevents force-fitting
            "category": {"type": "string", "enum": ["goods", "services", "unclear", "other"]},
            "category_detail": {"type": ["string", "null"],
                                "description": "Required when category == 'other'"},
        },
        "required": ["vendor", "category"],   # only the ALWAYS-present fields are required
    },
}


def main():
    banner("Domain 4 · Task 4.3", "Structured output via tool use + JSON schema")
    concept("Domain 4: Prompt Engineering & Structured Output (20%)",
            "Task 4.3 — Enforce structured output using tool use and JSON schemas",
            "Tool input_schema = output contract; nullable prevents fabrication")

    h1("The trick: the tool's input_schema IS your output schema")
    code(json.dumps(EXTRACTION_TOOL, indent=2), "extraction tool")
    note("You read the data from the model's tool_use call. No free-form JSON text means "
         "no JSON SYNTAX errors, ever.")

    pause("the limit")
    rule()
    h1("The limit you MUST know")
    wrong("Believing a schema guarantees CORRECT data. It only guarantees well-formed data.")
    note("Schema-valid but SEMANTICALLY wrong examples:")
    code('{"line_items": [10, 20], "total": 35}   # 10+20 != 35  (math wrong)\n'
         '{"vendor": "2025-03-04", "date": "Acme"} # values in the wrong fields',
         "semantic errors a schema won't catch")
    right("Schemas kill syntax errors; you still need VALIDATION + retry for semantics "
          "(Task 4.4).")

    pause("nullable")
    rule()
    h1("The single most important schema-design fact")
    wrong("Marking `amount` REQUIRED. When the document genuinely lacks an amount, the "
          "model FABRICATES one to satisfy the schema.")
    right("Make fields NULLABLE/optional when sources may lack them, so the model can "
          "honestly emit null instead of inventing.")

    rule()
    h1("Extensible enums")
    right('Add "unclear" for ambiguous cases and "other" + a free-text detail field. '
          'Real-world variety stops getting force-fit into wrong categories.')

    rule()
    h1("Combine with tool_choice (Task 2.3)")
    kv('tool_choice "any"', "guarantees SOME structured tool is called when doc type/schema is unknown")
    kv('forced selection', "guarantees a SPECIFIC extraction runs first")

    rule()
    h1("Plain-language analogy & the common confusion")
    analogy('A JSON schema is a form with labeled boxes. It guarantees every box is the right TYPE and present — but it cannot guarantee someone wrote the TRUTH in the boxes. Shape, not correctness.')
    pitfall('The biggest schema mistake: making a field REQUIRED when the document might not contain it. A required field forces the model to FABRICATE a value. Make uncertain fields nullable so it can honestly emit null.')

    tip("Tool use kills SYNTAX errors, not SEMANTIC errors. Required fields cause "
        "fabrication — make uncertain fields nullable. Enums need 'unclear'/'other'+detail.")


if __name__ == "__main__":
    main()
