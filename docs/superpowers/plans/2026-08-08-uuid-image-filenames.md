# UUID Image Filenames Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename newly uploaded images to a UUID (keeping the extension) so filenames never leak information, collide, or produce ugly URLs.

**Architecture:** One deconstructible `upload_to` callable in a new `portfolio/utils/uploads.py`, applied to the three `ImageField`s (`Profile.profile_image`, `Project.image`, `BlogPost.featured_image`). Existing files are untouched: the database stores full relative paths, and `upload_to` only shapes future uploads.

**Tech Stack:** Django 5.2, pytest.

**Spec:** issue #61 (the issue text is the spec). Scope decisions, per YAGNI: only images (the resume PDFs keep their names — a file named `resume.pdf` is a feature); no extra field storing the original filename.

## Global Constraints

- **Prerequisite:** PR #118 must be MERGED first. Then: `git fetch origin && git rebase origin/main` on this branch before Task 1 (migration numbering after `0039`).
- **Sequencing:** never execute in parallel with the Umami phase-1 plan (both generate migrations).
- Test command: `POSTGRES_HOST=127.0.0.1 POSTGRES_PORT=54329 ~/.venvs/portafolio-manager/bin/python -m pytest -p no:cacheprovider <args>` (embedded Postgres). Same env vars for `manage.py`.
- Commits: conventional style; never mention AI assistance or Claude. Never `git add -A`. Never merge the PR.
- All code, comments and repo artifacts in English.

---

### Task 1: The `UUIDUploadTo` callable

**Files:**
- Create: `portfolio/utils/uploads.py`
- Test: `portfolio/tests/test_uploads.py` (new file)

**Interfaces:**
- Produces: `UUIDUploadTo(subdir: str)` — deconstructible callable for `upload_to`; `(instance, filename) -> '<subdir>/<32-hex-uuid><ext-lowercased>'`.

- [ ] **Step 1: Write the failing tests** — create `portfolio/tests/test_uploads.py`:

```python
"""Tests for upload-path helpers (issue #61)."""
import re
from django.test import SimpleTestCase

from portfolio.utils.uploads import UUIDUploadTo


class UUIDUploadToTest(SimpleTestCase):

    def test_renames_to_uuid_keeping_extension(self):
        path = UUIDUploadTo('blog')(None, 'My Screenshot (2).PNG')
        self.assertRegex(path, r'^blog/[0-9a-f]{32}\.png$')

    def test_uses_the_configured_subdir(self):
        path = UUIDUploadTo('projects')(None, 'photo.jpg')
        self.assertTrue(path.startswith('projects/'))

    def test_names_are_unique_across_calls(self):
        upload_to = UUIDUploadTo('blog')
        self.assertNotEqual(upload_to(None, 'a.png'), upload_to(None, 'a.png'))

    def test_handles_filenames_without_extension(self):
        path = UUIDUploadTo('blog')(None, 'noextension')
        self.assertRegex(path, r'^blog/[0-9a-f]{32}$')

    def test_deconstructs_for_migrations(self):
        path, args, kwargs = UUIDUploadTo('blog').deconstruct()
        self.assertEqual(path, 'portfolio.utils.uploads.UUIDUploadTo')
        self.assertEqual(args, ('blog',))
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest portfolio/tests/test_uploads.py -v` (with the env prefix)
Expected: FAIL with `ModuleNotFoundError: No module named 'portfolio.utils.uploads'`

- [ ] **Step 3: Implement** — create `portfolio/utils/uploads.py`:

```python
"""Upload-path helpers."""
import uuid
from pathlib import Path

from django.utils.deconstruct import deconstructible


@deconstructible
class UUIDUploadTo:
    """upload_to callable that renames uploads to a UUID, keeping the extension.

    Prevents original filenames (which may carry sensitive information)
    from reaching public media URLs, and avoids name collisions.
    """

    def __init__(self, subdir):
        self.subdir = subdir.strip('/')

    def __call__(self, instance, filename):
        ext = Path(filename).suffix.lower()
        return f'{self.subdir}/{uuid.uuid4().hex}{ext}'

    def __eq__(self, other):
        return isinstance(other, UUIDUploadTo) and self.subdir == other.subdir
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest portfolio/tests/test_uploads.py -v`
Expected: 5 PASSED

- [ ] **Step 5: Commit**

```bash
git add portfolio/utils/uploads.py portfolio/tests/test_uploads.py
git commit -m "feat: add UUIDUploadTo upload-path helper (#61)"
```

---

### Task 2: Apply to the three ImageFields + migration

**Files:**
- Modify: `portfolio/models.py` (`Profile.profile_image` ~line 194, `Project.image` ~line 610, `BlogPost.featured_image` ~line 1066)
- Create: `portfolio/migrations/00NN_*.py` (generated)
- Test: `portfolio/tests/test_models.py` (append at end)

**Interfaces:**
- Consumes: `UUIDUploadTo` from Task 1.

- [ ] **Step 1: Write the failing test** — append to `portfolio/tests/test_models.py` (add `from django.core.files.uploadedfile import SimpleUploadedFile` and `import io`, `from PIL import Image as PILImage` to the imports if missing; `BlogPost` and `Category` are already imported):

```python
class UUIDImageFilenameTest(TestCase):
    """Uploaded images are renamed to a UUID (issue #61)."""

    @staticmethod
    def _png(name='Sensitive Customer Data.PNG'):
        buffer = io.BytesIO()
        PILImage.new('RGB', (10, 10), color='red').save(buffer, format='PNG')
        return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')

    def test_blog_featured_image_gets_uuid_name(self):
        category = Category.objects.create(slug='tech-uuid')
        category.set_current_language('en')
        category.name = 'Tech'
        category.save()
        post = BlogPost()
        post.set_current_language('en')
        post.title = 'UUID upload test'
        post.content = 'Body'
        post.category = category
        post.status = 'draft'
        post.featured_image = self._png()
        post.save()
        self.assertRegex(post.featured_image.name, r'^blog/[0-9a-f]{32}\.png$')
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest portfolio/tests/test_models.py -k UUIDImage -v`
Expected: FAIL — the stored name still contains `Sensitive_Customer_Data` under `blog/`.

- [ ] **Step 3: Apply the callable** — in `portfolio/models.py`, add the import near the other local imports at the top of the file:

```python
from .utils.uploads import UUIDUploadTo
```

Then change exactly three `upload_to` values (leave every other argument untouched):

```python
# Profile.profile_image:      upload_to='profile/'   ->  upload_to=UUIDUploadTo('profile'),
# Project.image:              upload_to='projects/'  ->  upload_to=UUIDUploadTo('projects'),
# BlogPost.featured_image:    upload_to='blog/'      ->  upload_to=UUIDUploadTo('blog'),
```

The resume PDF fields (`resume_pdf`, `resume_pdf_es`, `upload_to='projects/pdfs/'`) are deliberately NOT changed.

- [ ] **Step 4: Generate the migration**

Run: `python manage.py makemigrations portfolio`
Expected: one migration with three `AlterField` operations (no data changes — existing stored paths are unaffected).

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest portfolio/tests/test_models.py -k UUIDImage -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add portfolio/models.py portfolio/migrations/ portfolio/tests/test_models.py
git commit -m "feat: rename uploaded images with UUIDs (#61)"
```

---

### Task 3: Full suite, push, PR

- [ ] **Step 1: Run the entire test suite**

Run: `python -m pytest portfolio/tests/ -q`
Expected: everything green (nothing else uploads images by original name).

- [ ] **Step 2: Push and open the PR** (do NOT merge):

```bash
git push -u origin feat/uuid-image-filenames
gh pr create --title "feat: rename uploaded images with UUID filenames" \
  --body "Closes #61.

- New deconstructible UUIDUploadTo helper; applied to Profile.profile_image, Project.image and BlogPost.featured_image.
- New uploads become <dir>/<uuid32><ext>; original filenames never reach public URLs.
- Existing files and their stored paths are untouched (upload_to only shapes future uploads).
- Resume PDFs deliberately keep their filenames.
- Covered by unit tests for the helper and a model-level upload test."
```

- [ ] **Step 3: Report the PR URL and stop.**
