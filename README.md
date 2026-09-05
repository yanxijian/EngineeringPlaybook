# Engineering Playbook

可独立复用的技术方案评审协议、角色指令、模板和结构检查工具。它不依赖特定产品、工作区路径、AI 模型或会话历史。

## 内容

- [REVIEW-PROTOCOL.md](REVIEW-PROTOCOL.md)：流程、角色所有权、证据标准与报告命名规则。
- `.github/instructions/`：方案设计者和独立评审员的可发现指令。
- `templates/`：方案、评审报告和设计者草稿回应模板。
- `scripts/`：Python 3.9+ 标准库实现的跨平台结构检查及其 fixtures。

## 最短流程

1. 设计者以 `templates/design-template.md` 创建完整方案，提供评审依据导航。
2. 评审员独立核查实际证据，在同目录创建 `<方案名>-review.md`。
3. 设计者只在方案中核实并回应报告，重整完整方案。
4. 评审员只重写评审报告，保留当前有效结论。

角色在当前任务中固定。双方都不得修改对方拥有的文档；疑问、反证和补充说明只能写入自己拥有的产物。详情见 [REVIEW-PROTOCOL.md](REVIEW-PROTOCOL.md)。

## 检查

```shell
# 首次提交方案前的预检
python scripts/check_review_documents.py --design-path feature-plan.md

# 方案收到评审报告后的复审检查
python scripts/check_review_documents.py \
  --design-path feature-plan.md \
  --review-path feature-plan-review.md

# 将未回应的 D 类扩展设计建议提升为错误
python scripts/check_review_documents.py \
  --design-path feature-plan.md \
  --review-path feature-plan-review.md \
  --require-design-responses

# 运行内置 fixtures
python -m unittest discover -s scripts/tests -p "test_*.py" -v
```

需要 Python 3.9 或更高版本，不需要第三方依赖。历史 PowerShell 实现可从迁移前的 Git 提交中临时取回，但不作为长期维护的第二套实现。