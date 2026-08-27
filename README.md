# Kazike Thinking Skills

**12 个中文思考与自我探索技能：问清问题、理解概念、核查信息、比较选择，再用小实验验证。**

本项目将数字生命卡兹克分享的 12 条提示词，整理为遵循 [Agent Skills 规范](https://agentskills.io/specification) 的独立技能目录。每个技能都有明确的触发场景、执行流程、输出要求和适用边界，可按需选用。

例如：在你还没想清问题时，助手先逐轮提问；面对两个都有道理的选择，先认真呈现双方依据；陷入反复纠结时，把关键假设转成可逆的小实验。

> 本项目是对原方法的提炼与改写，不是原文逐字转录，也不是原作者、Anthropic 或 OpenAI 的官方项目。当前尚未添加开源许可证，使用与分发前请阅读下方「来源与许可」。

## 项目特点

- **按需使用**：12 个技能相互独立，不要求全部安装，也不会自动串行执行全部方法。
- **中文流程**：保留一问一答、确认后再建议、比较口径一致等关键规则。
- **证据明确**：区分事实、推断与价值判断；无法核查时说明缺口，不把未知写成确定。
- **轻量文件**：技能由 Markdown 和 YAML 元数据构成，没有需要运行的安装脚本或服务。
- **保留选择权**：自我探索不作心理诊断，实验设计不等于授权助手花钱、联系他人或替你作决定。

## 技能清单

| 场景 | 方法 | 技能目录 | 适合用来做什么 |
| --- | --- | --- | --- |
| 问清问题 | 苏格拉底提问 | [socratic-questioning](skills/socratic-questioning/SKILL.md) | 最多六轮逐步追问，确认真正要解决的问题 |
| 学习 | 双层解释法 | [two-layer-explaining](skills/two-layer-explaining/SKILL.md) | 同时理解通俗类比和专业机制，并检查理解 |
| 学习 | 反向拆解 | [reverse-engineering-examples](skills/reverse-engineering-examples/SKILL.md) | 从优秀范例提炼规律、操作清单与练习 |
| 研究 | 纵横分析法 | [longitudinal-comparative-research](skills/longitudinal-comparative-research/SKILL.md) | 结合历史演变、横向比较和有条件的未来情景 |
| 核查 | 事实核查 | [claim-fact-checking](skills/claim-fact-checking/SKILL.md) | 分别检查事实证据、推理过程和结论范围 |
| 解决问题 | 专家会诊 | [multi-perspective-consultation](skills/multi-perspective-consultation/SKILL.md) | 用三个互补视角交叉质疑，再综合成方案 |
| 解决问题 | 第一性原理 | [first-principles-solving](skills/first-principles-solving/SKILL.md) | 分离事实、假设和约束，从根本推导新路径 |
| 解决问题 | 跨领域借解 | [cross-domain-transfer](skills/cross-domain-transfer/SKILL.md) | 寻找其他领域的相似机制，并检查迁移边界 |
| 决策 | 双向钢人论证 | [two-sided-steelmanning](skills/two-sided-steelmanning/SKILL.md) | 为双方构建最强论证，追问关键变量后再判断 |
| 决策 | 最小实验 | [minimum-experiment-design](skills/minimum-experiment-design/SKILL.md) | 将纠结变成低成本、可逆、有停止条件的实验 |
| 认识自己 | 挖掘隐藏天赋 | [hidden-strengths-discovery](skills/hidden-strengths-discovery/SKILL.md) | 从具体经历寻找可迁移优势，区分擅长与消耗 |
| 认识自己 | 人生设计术 | [life-design-prototyping](skills/life-design-prototyping/SKILL.md) | 探索三个愿意认真考虑的五年版本，再用小原型验证 |

## 快速开始

### 1. 获取文件

在本仓库页面选择 **Code → Download ZIP**，解压后打开同时包含 `README.md` 和 `skills/` 的目录；也可以使用 Git 克隆仓库。

第一次使用可以从 `socratic-questioning` 或 `two-layer-explaining` 中选一个。打开其 `SKILL.md` 阅读流程后，再按下文安装。

### 2. 复制完整技能目录

复制 `skills/` 下选中的**整个子目录**，不要只复制 `SKILL.md`，也不要把整个仓库当成一个技能。

| 客户端 | 个人使用位置 | 单个项目使用位置 |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/<skill-name>/` | `<项目根目录>/.claude/skills/<skill-name>/` |
| Codex 本地技能 | `~/.agents/skills/<skill-name>/` | `<项目根目录>/.agents/skills/<skill-name>/` |

路径依据 [Claude Code 官方说明](https://code.claude.com/docs/en/skills#where-skills-live) 和 [OpenAI 官方技能说明](https://learn.chatgpt.com/docs/build-skills)。核对日期：2026-08-28；不同客户端版本或组织配置可能影响发现方式，请以实际环境为准。

`~` 表示当前用户目录；Windows 可在文件资源管理器地址栏输入 `%USERPROFILE%` 找到它。目标目录不存在时先创建；已有同名技能时，先备份并比较，不要直接覆盖。

例如，为 Claude Code 安装苏格拉底提问后，目录应当是：

```text
~/.claude/skills/
└── socratic-questioning/
    └── SKILL.md
```

安装带辅助资料的技能时，保留同级的 `references/`。本仓库没有插件清单或一键安装器；上面是手动安装本地技能的方法。

### 3. 显式调用并检查行为

在 **Claude Code** 的对话输入框中输入：

```text
/socratic-questioning 我总想换工作，但不确定自己真正不满意的是什么。先帮我问清楚，不要直接给建议。
```

在 **Codex CLI 或 IDE 扩展** 的对话输入框中输入：

```text
$socratic-questioning 我总想换工作，但不确定自己真正不满意的是什么。先帮我问清楚，不要直接给建议。
```

以上是聊天输入，**不是终端命令**。Claude Code 支持 `/技能名`；Codex CLI／IDE 支持 `$` 提及技能或通过 `/skills` 选择。桌面客户端请使用其技能选择入口。参见 [Claude Code 调用说明](https://code.claude.com/docs/en/skills) 与 [OpenAI 调用说明](https://learn.chatgpt.com/docs/build-skills)。

这个例子的合理首轮行为是：先问一个具体经历问题，而不是一次发出整套问卷或马上推荐辞职。若未发现技能，检查目录层级和文件名，再按客户端说明刷新或重启。

**没有技能安装功能也可以先试用**：将选中技能的完整 `SKILL.md`，以及需要的引用文件提供给支持这些文件的助手，请它按照流程处理你的问题。这是将文件作为上下文使用，不等于客户端已经支持自动发现技能。

## 使用示例

先选择对应技能，再发送下面的请求。把示例背景替换成自己的具体情况，结果通常更有针对性。

### 从“听说过”到理解机制

选择 `two-layer-explaining`：

```text
我没有机器学习基础，想理解什么是向量检索。
请先用一个生活例子解释，再讲专业机制，说明类比在哪些地方不成立。
最后给我三道理解题，先不要展示答案。
```

预期产物：两层解释、术语对应、类比边界和理解题。

### 把纠结转成可验证的行动

选择 `minimum-experiment-design`：

```text
我想尝试做线上课程，但不确定自己是否喜欢持续备课和讲解。
请设计一个七天的最小实验：每天最多30分钟，预算不超过100元，
不公开发布，不替我联系任何人。说明它能验证什么、不能证明什么。
```

预期产物：关键假设、实验步骤、成本上限、记录方式、继续与停止条件，以及第一步行动。这里的“设计实验”不代表实验已经执行。

### 探索优势，不急着贴标签

选择 `hidden-strengths-discovery`：

```text
同事说我很会整理复杂资料，但每次整理完都特别累。
请通过具体经历帮我区分擅长、喜欢和精力消耗，每次只问一个问题。
不要直接给我人格标签或职业结论。
```

预期行为：逐轮访谈，先收集经历，再给出有证据、可修正的优势假设。

更多示例见 [使用说明](使用说明.md)。

## 如何选择与衔接

| 你现在卡在哪里 | 可以先用 | 何时考虑下一步 |
| --- | --- | --- |
| 连问题本身都说不清 | 苏格拉底提问 | 确认问题后，再研究或制定方案 |
| 对一个概念只有模糊印象 | 双层解释法 | 理解机制后，用反向拆解学习具体范例 |
| 不知道信息是否可信 | 事实核查 | 证据范围清楚后，再比较选择 |
| 两个方向都说得通 | 双向钢人论证 | 关键变量仍不确定时，设计最小实验 |
| 知道自己不满意，却没有方向 | 人生设计术 | 形成候选版本后，再验证一个小原型 |

这些只是可选衔接方式。一次调用只使用当前需要的方法；自我探索类技能需要你的回答，不会凭空生成完整个人画像。

## 目录结构

```text
.
├── README.md
├── skills/                        # 12 个独立技能，目录名称见上表
│   ├── socratic-questioning/
│   │   └── SKILL.md
│   ├── hidden-strengths-discovery/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── life-design-prototyping/
│   │   ├── SKILL.md
│   │   └── references/
│   └── …
├── validation/                    # 初始版本的校验结果和行为抽查记录
├── 内容提炼与来源.md
├── 使用说明.md
└── 验证报告.md
```

每个技能的 `SKILL.md` 使用 YAML 定义 `name`、`description` 和来源元数据，正文描述实际流程。较长的条件性说明放在 `references/`，由入口按需引用。文件结构参照 [Agent Skills 规范](https://agentskills.io/specification)。

## 运行条件与边界

- **需要合适的助手**：客户端应支持技能加载，或能够读取你提供的 Markdown 文件。模型能否稳定遵守多轮流程仍需实际检查。
- **工具由宿主提供**：本仓库不提供搜索服务。研究、核查和跨领域案例可能需要联网；用户禁止联网或工具不可用时，应只分析现有资料并标明缺口。
- **无需启动服务**：使用技能文件不需要运行 npm、pip、MCP 服务或本项目专用脚本；助手平台本身的账号、权限和费用另行适用。
- **不自动开展外部行动**：提出方案不等于已获准发送消息、预约、采购、公开发布或修改账户。
- **不替代专业服务**：自我探索不构成心理诊断；高风险的健康、法律、财务决定不能仅凭模型输出。
- **请保护隐私**：可以使用匿名化经历，跳过不愿分享的问题；提交反馈时不要附带凭证、私人聊天或他人个人资料。

## 验证状态

初始技能版本于 **2026-08-28** 完成以下检查：

| 检查 | 结果与范围 |
| --- | --- |
| 结构校验 | 12/12 通过：元数据、名称、目录对应、引用文件和来源编号 |
| 行为抽查 | 六个场景生成了实际回答，并对其中两项窄修订进行了复测 |
| 对话深度 | 交互类主要覆盖首轮，未完成所有多轮访谈和最终报告验证 |
| 客户端兼容性 | 安装路径依据官方文档；尚未实测本包在各客户端的导入、自动触发 |
| 跨模型效果 | 未完成 Claude Haiku、Sonnet、Opus 等跨模型测试 |

这里的校验通过不等于效果认证，也不能证明模型在所有任务上都会严格遵守流程。详见 [验证报告](验证报告.md)、[结构结果](validation/structural-validation.json)、[交互抽查](validation/interactive-forward-test.md) 和 [分析抽查](validation/analysis-forward-test.md)。

`validation/` 保存的是该版本的记录，不是随修改自动更新的 CI 结果。本仓库当前未附带自动化测试运行器；修改技能后应重新检查并记录验证范围。

## 参与改进

欢迎通过 Issue 提交可复现的问题，或通过 Pull Request 改进触发描述、流程、边界和示例。

报告问题时，尽量包含：技能名称、客户端与模型版本、匿名化输入、实际回答、期望行为，以及当时能否联网。仅提交能够说明问题的最少信息即可。

修改技能时请保持：

1. 一个技能解决一种明确需求，不随意扩大触发范围。
2. 目录名与 YAML 中的 `name` 一致，辅助资料使用相对链接。
3. 用真实输入测试修改后的行为，尤其检查信息不足、禁网、提前停止等情况。
4. 将新增解释与原方法区分，保留来源；不要提交无权分发的图片或大段第三方文本。
5. 在 PR 中说明改了什么、为什么改、实际测试了什么，以及仍未验证什么。

## 来源与许可

方法来源：**数字生命卡兹克**的抖音图文《强烈建议所有人试一下这些提示词》，共16页、12个方法。[查看原帖](https://www.douyin.com/user/self?from_tab_name=main&modal_id=7676403117654641926&showTab=like)。

本项目对内容进行了结构化提炼和工作流改写，补充了证据限制、用户授权和交互边界。没有附带原始图文，也不宣称获得原作者背书。逐项对应与改写说明见 [内容提炼与来源](内容提炼与来源.md)。

**当前许可状态：尚未添加 `LICENSE`，不宣称采用 MIT、Apache-2.0 或其他开源许可证。** 公开仓库与明确授予开源许可是不同事项；维护者应先确认第三方来源的使用边界，再为有权授权的内容确定许可证并更新本节。原始材料的权利不因本仓库的整理而转移。参考 [GitHub 关于仓库许可的说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)。
