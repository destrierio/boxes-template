# Destrier Box Template

Everything you need to build a challenge box for [Destrier](https://destrier.io).


## What's here

- **`schemas/`** — The JSON Schema used to validate `box.yaml`.
- **`example-box/`** — A complete reference box showing how everything fits together.
- **`templates/`** — Starter templates for `container`, `vm`, and `network` boxes.
- **`scripts/`** — Validation scripts used by CI.
- **`your-box/`** — Build your box here. Rename this directory to your box's ID before submitting.


## Getting started

1. Click **Use this template** and create a **private** repository.
2. Start from a template in `templates/` or adapt `example-box/`.
3. Build your box in `<your-box>/` by following the contributor guide.


## Validation

Each push automatically validates `<your-box>/box.yaml` against the schema. Resolve any validation errors before submitting your box.


## Submission

When your box is ready:

1. Keep the repository **private**.
2. Add your assigned Destrier reviewer as a collaborator with read access.
3. Send them the repository link.

> [!IMPORTANT] Never make your repository public. It contains your reference exploit and other review-only material.


## Learn more

See the full contributor guide at **[docs.destrier.io](https://docs.destrier.io/contributing/overview)**.