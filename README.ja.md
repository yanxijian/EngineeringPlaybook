# Engineering Playbook

**日本語** · [English](README.md) · [简体中文](README.zh-CN.md) · [한국어](README.ko.md)

<!-- translated-from: README.md sha256:37482806e847 -->

設計レビューのプロトコル、役割ごとの指示、テンプレート、構造チェッカーを再利用できる形でまとめたものです。特定の製品、ワークスペースの構成、AI モデル、セッション履歴には依存しません。

## 収録内容

- [REVIEW-PROTOCOL.md](REVIEW-PROTOCOL.md)：進め方、役割ごとの所有権、証拠の基準、レビュー報告の命名規則。
- `.github/instructions/`：設計者と独立レビュアー向けの、発見可能な指示。
- `templates/`：設計案、レビュー報告、設計者の下書き・回答のテンプレート。
- `scripts/`：Python 3.9 以降の標準ライブラリだけで動くクロスプラットフォームの構造チェッカーと、そのフィクスチャ。

## 最短の進め方

1. 設計者は `templates/design-template.md` から完全な設計案を作り、レビューの手がかりを添える。
2. レビュアーは実際の証拠を独立に確認し、同じディレクトリに `<設計案名>-review.md` を作る。
3. 設計者はレポートの指摘を設計案の中で検証・回答し、一つの筋の通った文書に整える。
4. レビュアーはレビュー報告だけを書き直し、なお有効な結論を残す。

役割はタスクの間ずっと固定です。相手が所有する文書はどちらも編集しません。疑問・反証・補足は自分の成果物にだけ書きます。詳細は [REVIEW-PROTOCOL.md](REVIEW-PROTOCOL.md)。

## チェック

```shell
# 設計案を提出する前の事前チェック
python scripts/check_review_documents.py --design-path feature-plan.md

# レビュー報告を受け取った後の再チェック
python scripts/check_review_documents.py \
  --design-path feature-plan.md \
  --review-path feature-plan-review.md

# 未回答の D 種（拡張提案）をエラーとして扱う
python scripts/check_review_documents.py \
  --design-path feature-plan.md \
  --review-path feature-plan-review.md \
  --require-design-responses

# 同梱のフィクスチャを実行
python -m unittest discover -s scripts/tests -p "test_*.py" -v
```

Python 3.9 以降が必要で、サードパーティの依存はありません。過去の PowerShell 実装は移行前の Git 履歴から必要に応じて取り出せますが、第二の実装として保守はしません。

## ライセンス

[MIT](./LICENSE) © 2026 EngineeringPlaybook contributors
