# Documentation Index

Use this index to quickly locate the guide that answers your question. All files are written in Markdown and live in the repository root or in the `docs/` directory.  
**Nota**: Cada guía incluye un breve resumen en inglés y español; consulta la sección inicial de cada archivo.

---

## Getting Started

| File | Purpose | When to read |
| ---- | ------- | ------------ |
| `README.md` | High-level overview and quick start commands. | First contact with the project. |
| `SETUP.md` | Step-by-step installation, configuration, and troubleshooting. | Setting up a local environment or a new machine. |

## Configuration

| File | Purpose | When to read |
| ---- | ------- | ------------ |
| `docs/CONFIGURATION_GUIDE.md` | Environment variables, Django settings per environment, security hardening. | Preparing staging or production deployments. |
| `docs/EMAIL_SETUP.md` | SMTP configuration examples and diagnostics. | Enabling the contact form or transactional email. |

## Daily Operations

| File | Purpose | When to read |
| ---- | ------- | ------------ |
| `docs/ADMIN_USAGE.md` | Walkthrough of the custom admin dashboard, content workflows, and translation controls. | Managing portfolio content, projects, and blog entries. |
| `docs/TEST_DATA.md` | Instructions for the `populate_test_data` command and other sample data helpers. | Demonstrations, QA, or rapid prototyping. |

## Historical Reports

| File | Purpose | When to read |
| ---- | ------- | ------------ |
| `docs/COMMANDS_CLEANUP_SUMMARY.md` | Reference of available management commands after cleanup. | Auditing or extending CLI utilities. |
| `docs/FINAL_CLEANUP_REPORT.md` | Summary of the first cleanup phase (removed files, gains). | Understanding legacy refactors. |
| `docs/PHASE_2_CLEANUP_REPORT.md` | Highlights from the second cleanup phase. | Reviewing prior template and code consolidation. |

## Project Planning

| File | Purpose | When to read |
| ---- | ------- | ------------ |
| `TODO.md` | Open tasks, completed work, and priorities. | Sprint planning or backlog reviews. |

---

## Common Journeys

### Fresh Installation
1. `README.md` – grasp the big picture.
2. `SETUP.md` – follow the installation steps.
3. `docs/CONFIGURATION_GUIDE.md` – tune environment variables.
4. `docs/TEST_DATA.md` – load demo content.
5. `docs/ADMIN_USAGE.md` – learn day-to-day operations.

### Preparing Production
1. `docs/CONFIGURATION_GUIDE.md`
2. `docs/EMAIL_SETUP.md`
3. `docs/ADMIN_USAGE.md`

### Development & QA
1. `docs/TEST_DATA.md`
2. `docs/COMMANDS_CLEANUP_SUMMARY.md`
3. `TODO.md`

---

**Last updated:** 2025-10-23  
**Maintainer:** Portfolio Manager team  
**Status:** Current
