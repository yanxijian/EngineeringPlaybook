# Engineering Playbook

**한국어** · [English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

<!-- translated-from: README.md sha256:37482806e847 -->

설계 리뷰 프로토콜, 역할별 지침, 템플릿, 구조 검사기를 재사용할 수 있는 형태로 모은 것입니다. 특정 제품, 워크스페이스 구성, AI 모델, 세션 이력에 의존하지 않습니다.

## 구성

- [REVIEW-PROTOCOL.md](REVIEW-PROTOCOL.md): 진행 방식, 역할별 소유권, 증거 기준, 리뷰 보고서 이름 규칙.
- `.github/instructions/`: 설계자와 독립 리뷰어를 위한, 발견 가능한 지침.
- `templates/`: 설계안, 리뷰 보고서, 설계자 초안·답변 템플릿.
- `scripts/`: Python 3.9 이상 표준 라이브러리만 쓰는 크로스 플랫폼 구조 검사기와 그 픽스처.

## 가장 짧은 흐름

1. 설계자는 `templates/design-template.md`로 완전한 설계안을 만들고 리뷰를 위한 길잡이를 붙입니다.
2. 리뷰어는 실제 증거를 독립적으로 확인하고 같은 디렉터리에 `<설계안 이름>-review.md`를 만듭니다.
3. 설계자는 보고서의 지적을 설계안 안에서 검증하고 답한 뒤, 하나의 일관된 문서로 다시 정리합니다.
4. 리뷰어는 리뷰 보고서만 다시 쓰고, 여전히 유효한 결론은 남깁니다.

역할은 작업이 끝날 때까지 고정됩니다. 상대가 소유한 문서는 어느 쪽도 편집하지 않으며, 의문·반증·보충 설명은 자기 산출물에만 적습니다. 자세한 내용은 [REVIEW-PROTOCOL.md](REVIEW-PROTOCOL.md).

## 검사

```shell
# 설계안을 제출하기 전 사전 점검
python scripts/check_review_documents.py --design-path feature-plan.md

# 리뷰 보고서를 받은 뒤 재점검
python scripts/check_review_documents.py \
  --design-path feature-plan.md \
  --review-path feature-plan-review.md

# 응답하지 않은 D 유형(확장 제안)을 오류로 처리
python scripts/check_review_documents.py \
  --design-path feature-plan.md \
  --review-path feature-plan-review.md \
  --require-design-responses

# 함께 들어 있는 픽스처 실행
python -m unittest discover -s scripts/tests -p "test_*.py" -v
```

Python 3.9 이상이 필요하며 서드파티 의존성은 없습니다. 과거 PowerShell 구현은 마이그레이션 전 Git 이력에서 필요할 때 꺼낼 수 있지만, 두 번째 구현으로 유지하지는 않습니다.

## 라이선스

[MIT](./LICENSE) © 2026 EngineeringPlaybook contributors
