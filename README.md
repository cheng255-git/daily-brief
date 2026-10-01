# skill 出厂标准包

给客户做 skill 的出厂模板。一个仓库，同时满足两件事：

1. **能挂上 GitHub 公开仓库** → 客户把链接丢给豆包 / Kimi / 扣子，一句话自动安装
2. **能打包成 `.skill` 文件** → 给不方便用 GitHub 的客户手动上传

---

## 目录结构

```
skill出厂标准包/
├── skills/                    ← 所有 skill 放这里，一个子目录一个 skill
│   └── daily-brief/           ← 示例 skill（工作日报整理）
│       └── SKILL.md           ← 核心文件：YAML frontmatter + Markdown 指令
├── build-skill.py             ← 一键打包，自动做出厂校验
├── dist/                      ← 打包产物（.skill 文件）落在这里
├── INSTALL.md                 ← 分平台安装说明，发给客户
├── LICENSE                    ← MIT 开源许可
└── README.md                  ← 本文件
```

---

## 怎么用

### 1. 加一个新 skill

在 `skills/` 下建目录，写 `SKILL.md`：

```markdown
---
name: 目录名（必须和目录名一模一样）
description: 说清楚这个技能做什么、什么时候该用（这是助手判断要不要调用它的唯一依据）
license: MIT
---

# 技能标题

## 用途
## 何时使用
## 输出格式
## 规则
```

需要脚本就加 `scripts/`，需要参考资料加 `references/`，需要素材加 `assets/`（都是可选的）。

### 2. 打包

```bash
python build-skill.py
```

会自动校验并生成 `dist/你的技能名.skill`。

想看单个：`python build-skill.py daily-brief`

### 3. 发布给客户

```bash
# 建公开仓库并推上去
git init
git add -A
git commit -m "add skill"
gh repo create 你的账号/skill出厂标准包 --public --source=. --push

# 打上标签，方便按版本安装
git tag v1.0.0 && git push --tags
```

推完把链接给客户，附带 `INSTALL.md` 就行。

---

## 出厂校验清单（打包脚本已自动检查前 4 项）

- [x] 包内恰好一个 `SKILL.md`
- [x] frontmatter 含 `name` 和 `description`
- [x] `name` 与目录名一致
- [x] `name` ≤ 64 字符、`description` ≤ 1024 字符
- [ ] 正文不超过 500 行（超了把大段示例挪到 `references/`）
- [ ] 带 `LICENSE` 文件，frontmatter 里写 `license: MIT`
- [ ] 不含任何密钥、真实客户信息、本机绝对路径
- [ ] （带脚本的 skill）脚本已在本机跑通

---

## 发布前安全检查（重要）

公开仓库会被全网抓取，发布前必须确认：

1. 私有数据、缓存、`.env` 已写进 `.gitignore`，**没有被 git 跟踪**
2. 全仓库扫一遍，没有 `sk-`、`Bearer`、`api_key=`、`-----BEGIN` 这类密钥痕迹
3. 没有客户的真实姓名、手机号、报价
4. 没有把别人的第三方 skill 一起打包发出去

---

## 为什么这样做

市面上的助手（豆包、Kimi、扣子、DeepSeek、Claude Code、Cursor 等 40+ 个）都认同一套 **Agent Skills 开放标准**：

> 一个含 `SKILL.md` 的目录 = 一个技能。

所以只要：
- 结构按标准写
- 仓库公开
- 打一次 release

各种技能市场和索引站会自动收录，客户搜得到、装得上、直接用。**不需要一家家去投稿。**
