# Prompt Management Strategy

## Principles

- Keep prompts short, explicit, and deterministic.
- Separate system behavior from example content.
- Prefer versioned files over inline prompt strings.
- Keep examples realistic and minimal.
- Never hide business rules inside prompts.

## File layout

- `app/prompts/system/`: primary instruction set.
- `app/prompts/few_shots/`: short examples and counterexamples.
- `app/prompts/templates/`: human prompt templates.
- `app/prompts/versions/`: prompt version history and release markers.

## Recommended pattern

1. Load the prompt bundle from the versioned directory tree.
2. Append only the smallest useful context for the task.
3. Inject user story and acceptance criteria as structured variables.
4. Use low temperature for reproducibility.
5. Validate the final response with a Pydantic schema.

## Why this matters

This approach makes prompt changes auditable, easy to test, and safer to evolve than embedding instructions directly in Python code.

## Future improvements

- Add version tags for prompt files.
- Track prompt regression tests with sample stories.
- Introduce prompt templates per domain once the MVP branches out.
- Split prompts per agent when multi-agent orchestration is added.
- Add prompt evaluation baselines for every major prompt version.
