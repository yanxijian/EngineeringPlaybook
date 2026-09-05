---
name: "Design Author Review Workflow"
description: "Use when writing or revising an architecture design, implementation plan, technical proposal, or response to a review. Defines design-author ownership, review feedback handling, and evidence requirements."
---
# 设计者评审工作流

- 遵守仓库根目录的 `REVIEW-PROTOCOL.md`。
- 当前任务中保持设计者角色。只修改设计或实施方案；不得修改独立评审报告，除非用户在当前任务中明确授权。
- 方案必须提供“评审依据导航”：仓库/提交、相关路径与符号、验证命令/结果、跨项目依赖。
- 收到未带路径的“看下评审报告”“继续”或“再来”时，按协议从当前方案同目录发现 `<方案名>-review.md`；候选不唯一时请求用户指定。
- 先独立核实报告中的每项依据，再决定采纳、部分采纳、不采纳或需澄清；不得将报告视为自动正确。
- 在方案中维护“评审反馈与采纳说明”，逐条回应 P 类发现及 D 类扩展建议，并写明核实结果、方案落点、处理说明和验证方式。
- 对报告的疑问、反证和异议只能写入方案，不得批注、修订、删除或格式化评审报告。
- 每轮必须重整生成完整方案，使正文与反馈一致；不得只追加零散补丁。
- 明确区分已验证事实、方案承诺和风险/假设。
- 用户说“继续”或“再来”时重复读取报告、核实、重整方案并提交复审的闭环。
- 评审通过后，仍须在代码实现和验证完成后请求代码级复审。