# 验证与复跑

这里区分三件事：文件结构是否合法、记录是否对应当前文件、模型在实际对话中是否遵守流程。前两项可自动检查；第三项需要运行对话并审阅实际回答，不能用关键词命中替代。

## 自动检查

使用虚拟环境安装 [开发依赖](../requirements-dev.txt)。技能使用者无需安装 Python；这些依赖只供维护者运行校验。本轮实测 Python 3.14、PyYAML 6.0.3，不把它等同于其他 Python 版本已验证。

在仓库根目录运行；`python` 应指向你的虚拟环境解释器：

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests
python -m compileall -q scripts tests
python scripts/validate_skills.py
python scripts/validate_skills.py --check-snapshot validation/structural-validation.json
python scripts/validate_skills.py --check-behavior validation/behavior-results.json
```

Windows 也可显式使用虚拟环境的 `.venv\Scripts\python.exe`；其他平台通常为 `.venv/bin/python`。仓库根目录默认从脚本位置确定，不依赖终端当前目录；`--root` 可指定另一份技能包。`--output` 和检查记录的参数路径相对于当前目录。

- 退出码为零表示所请求的检查通过，非零表示错误或记录过期。
- `--check-snapshot` 比较被测文件清单及 SHA-256、校验器版本及脚本哈希、Python/PyYAML 版本。换了环境也可能提示过期：重新检查并保存自己的报告，不应绕过比较。
- `--check-behavior` 检查行为记录的来源哈希、场景对应和轮数等一致性；它不重新调用模型，不证明评分正确，也不证明客户端自动触发生效。
- 校验脚本默认只读，不联网、不调用模型、不需要 Git，也不安装技能。

## 更新结构记录

完成修改、复核差异后运行：

```sh
python scripts/validate_skills.py --output validation/structural-validation.json --force
```

只在明确需要刷新既有校验报告时使用 `--force`。它不能覆盖技能、脚本或任意 JSON；首次生成新路径时不需要 `--force`，目标父目录须已存在。检查退出码，失败报告不能当作通过记录。

报告记录 UTC 时间、环境版本、校验器身份和被测文件哈希，不依赖机器绝对路径或仅靠 Git 提交号。未提交的修改、ZIP 下载环境也能得到内容指纹。结构报告覆盖技能入口、技能内 Markdown 辅助资料、根目录 Markdown、此目录内 Markdown 和行为用例；不把输出 JSON 纳入自身指纹，避免循环变化。

## 行为复跑协议

[行为用例](behavior-cases.json) 保存合成输入与评分准则，[行为结果](behavior-results.json) 保存本次原始回答、环境限制、文件哈希和逐场景审阅。旧的 [交互抽查](interactive-forward-test.md) 与 [分析抽查](analysis-forward-test.md) 是历史记录，不替代本轮结果。

1. 每个场景使用独立对话。提供指定技能及必要引用文件，按 `user_turns` 顺序逐轮发送，等上一轮真实回答完成后再发下一轮。不要让同一个模型一次性伪造整段双人对话。
2. 只给作答者技能、当前用户输入和只读/禁网约束；不要给评分准则、预期答案或前次评分。`description-only-routing` 场景只提供技能描述和分类请求。
3. 保存实际回答，注明宿主、可见的模型标识及版本、执行日期、工具可用性和被测文件哈希。未知字段写 `null` 并解释，不猜测。若复用同一测试上下文，明确披露。
4. 另行按用例准则检查行为：是否尊重停止/跳过、是否处理矛盾、是否等待确认、是否保留证据及授权边界。记录通过、失败或未运行以及具体理由，不追求逐字匹配。
5. 技能或用例改变后重新运行受影响场景，再更新来源哈希；不能只改哈希把旧回答伪装成新结果。最后用 `--check-behavior` 核对记录完整性。

本轮用例覆盖四个多轮场景和三个单轮场景；路由判断只是描述级检查。完整长访谈、真实客户端导入、真实联网故障和跨模型效果仍须另外验证。

## 检查边界

本地链接检查支持普通内联 Markdown 链接（简单目标、尖括号路径、可选标题）及技能中反引号包裹的辅助资料路径，忽略围栏代码块。它不是完整 Markdown 解析器：不验证引用式链接、HTML、带嵌套括号的目标、标题锚点或外部 URL 可用性。新增此类写法时需要额外检查。

仓库没有独立配置的类型检查器、格式化器或构建系统；当前 Python 验证由单元测试和语法编译组成，不将它描述为完整 lint/typecheck。
