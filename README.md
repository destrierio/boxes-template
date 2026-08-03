# Destrier Box Template

Everything you need to build a challenge box for [Destrier](https://destrier.io).


## What's here

- `schemas/` — the JSON Schema your `box.yaml` is validated against.
- `scripts/` — the validation script CI runs on your box.
- `example-box/` — a complete reference box showing how everything fits together.
- `templates/` — Starter skeletons for `container`, `vm`, and `network` boxes.
- `your-box/` — Build your box here. Start by copying a template into this directory, then rename it to your box's ID before submitting.


## Build a box

1. Click **Use this template → Create a new repository** and set it to **Private**.
2. Copy a skeleton from `templates/` into `your-box/`, then rename the directory to your box's ID.
3. Build your box by following the guide at [docs.destrier.io](https://docs.destrier.io/contributing/overview).


## Validation

Every push runs a check that validates `your-box/box.yaml` against the schema and verifies your box's structure. Fix anything it reports before submitting.


## Submission

When your box is ready and the validation check passes:

1. Keep your repository **private**.
2. Add your Destrier reviewer as a collaborator with read access.
3. Share the repository link.

> Keep your repository private. It contains your reference exploit and other review-only material.


## Domain controller boxes

If your box includes a **domain controller**, its disk image is uploaded separately. Building Active Directory from source for every evaluation is too slow, so domain controllers use a prebuilt image (`build.type: image`).

1. Request an upload URL using your access token and box ID:
   ```bash
   curl -s -X POST https://upload.destrier.io/request-upload \
     -H "Authorization: Bearer <your-token>" \
     -d '{"box_id":"<your-box-id>","filename":"dc.vmdk"}'
   ```
   The response contains a short-lived upload URL.

2. Upload the image to the returned URL:
   ```bash
   curl -X PUT --upload-file dc.vmdk "<upload-url>"
   ```

3. Set `build.image` in `box.yaml` to the uploaded filename (for example, `dc.vmdk`).

Your access token is provided during onboarding. Everything else—including `box.yaml`, `solver/`, and all source-built hosts—is submitted through your repository as usual.


## Learn more

See the full contributor guide at **[docs.destrier.io](https://docs.destrier.io/contributing/overview)**.