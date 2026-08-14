# Disable Input Quality Gate Design

## Goal

Disable the linguistic input-quality rejection gate for the current deployment while preserving the classifier pipeline and basic API schema validation.

## Design

- Add `input_validation_enabled` to service settings, defaulting to `true`.
- Pass the setting into `RootCategoryClassifier` during application startup.
- When disabled, skip only `InputQualityGate.require_meaningful`.
- Keep request ID/text presence and length validation in the Pydantic API schema.
- Set `DANDAN_INPUT_VALIDATION_ENABLED=false` in the active `.env`.

The input-quality implementation remains available for later reactivation. Exact, fuzzy, semantic, fusion, and decision stages are unchanged.

## Verification

- Prove that repeated text is classified when the gate is disabled.
- Prove that the same text is rejected when the gate is enabled.
- Restart FastAPI and verify the public demo accepts the repeated text.
