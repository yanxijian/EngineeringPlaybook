# Engineering Playbook

**English** · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

[![hygiene](https://github.com/yanxijian/EngineeringPlaybook/actions/workflows/hygiene.yml/badge.svg)](https://github.com/yanxijian/EngineeringPlaybook/actions/workflows/hygiene.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

A reusable design-review protocol, role instructions, templates and a structure checker. It does not depend on a particular product, workspace layout, AI model or session history.

## Contents

- [REVIEW-PROTOCOL.md](REVIEW-PROTOCOL.md): the workflow, role ownership, the evidence standard and report naming rules.
- `.github/instructions/`: discoverable instructions for the designer and for the independent reviewer.
- `templates/`: templates for designs, review reports and the designer's drafts/replies.
- `scripts/`: a cross-platform structure checker built on the Python 3.9+ standard library, plus its fixtures.

## Shortest workflow

1. The designer creates a complete design from `templates/design-template.md` and provides navigation for the review.
2. The reviewer checks the actual evidence independently and writes `<design-name>-review.md` in the same directory.
3. The designer verifies and answers the report inside the design, then restructures it into one coherent document.
4. The reviewer rewrites only the review report, keeping the conclusions that still hold.

Roles stay fixed for the duration of a task. Neither side edits a document the other owns; questions, counter-evidence and clarifications belong in your own artifact. Details in [REVIEW-PROTOCOL.md](REVIEW-PROTOCOL.md).

## Checks

```shell
# Pre-check before submitting a design
python scripts/check_review_documents.py --design-path feature-plan.md

# Re-check after the design received a review report
python scripts/check_review_documents.py \
  --design-path feature-plan.md \
  --review-path feature-plan-review.md

# Turn unanswered class-D design suggestions into errors
python scripts/check_review_documents.py \
  --design-path feature-plan.md \
  --review-path feature-plan-review.md \
  --require-design-responses

# Run the bundled fixtures
python -m unittest discover -s scripts/tests -p "test_*.py" -v
```

Python 3.9 or newer is required; there are no third-party dependencies. The historical PowerShell implementation can be pulled from the pre-migration Git history when needed, but it is not maintained as a second implementation.

## License

[MIT](./LICENSE) © 2026 EngineeringPlaybook contributors
