---
name: token-scout
description: Cache OpenRouter's public free-model list. No key. No paid models.
---

# Token scout

Read `GET https://openrouter.ai/api/v1/models` with no API key.

Keep a model when its id ends in `:free`, when the id is `openrouter/free`, or when prompt and completion prices are both zero.

Save the list in `data/free-models.json`. If the request fails, keep the previous list and write the failure on the activity list.

This scout does not hunt for leaked keys. Keys come only from the local `.env`.
