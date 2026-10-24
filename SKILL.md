---
name: paper-summarizer
description: Summarize and organize academic papers into a structured technical-notes-style Markdown note (标题/前置理论/贡献/实现/评估结果/Critical Reading), then append the note into the user's running paper-reading-notes Markdown file. Use this whenever the user asks you to “总结整理” a certain essay, whether the essay is in the form of a paper URL (arXiv, journal page, PDF link), raw paper text/abstract, or a local PDF/DOCX file.
---

# Paper Summarizer

Turns a paper (web link, pasted text, or local file) into a structured Markdown summary, then appends it to the user's ongoing paper-reading-notes file so allsummaries accumulate in one place.

## Workflow

### 1. Identify the input type

- **URL** (arXiv abstract/PDF link, journal page, blog post about a paper) → use `scripts/fetch_web.py`
- **Local file** (`.pdf`, `.docx`, `.txt`, `.md`) → use `scripts/extract_local.py`
- **Pasted text** (user pasted the abstract or full text directly in chat) → skip extraction, use the text as-is

Run the relevant script to get plain text of the paper (title, abstract, and as much of the body as is extractable). If extraction is partial (e.g. only the
abstract could be fetched from a paywalled page), proceed with what you have and tell the user the summary is based on the abstract only.

```bash
conda run -n summarizer --no-capture-output python3 scripts/fetch_web.py "https://arxiv.org/xxx"
conda run -n summarizer --no-capture-output python3 scripts/extract_local.py "/xxx/paper.pdf"
```

Both scripts print a `TITLE:` line first (best-effort), then the extracted
body text. If `TITLE:` is empty, infer the title yourself from the text.



### 2. Write the structured summary

Always use this exact structure (in Chinese, matching the user's preference).
This is a technical-notes style — denser and more detailed than a plain abstract summary, meant to let the user re-derive the paper's core mechanism without rereading it.

```markdown
## <论文的简短昵称/关键词式标题，2-6个词，英文>

<论文完整标题（英文）>

<会议名称（如有）发表时间 YYYY.M> by <一作机构/单位>

#### 前置理论

<仅当论文依赖读者可能不熟悉的背景概念时才写这一节；如果论文是自包含的、不需要额外背景知识，跳过整节>

##### <概念1名称：英文全称或缩写展开>

<用简洁的分步/列表方式解释这个概念是什么、怎么运作的。可以包含关键公式（用 LaTeX，$...$ 或 $$...$$）。如果这个背景方法本身有明显局限，用一句斜体点出，例如 *缺点：...*>

##### <概念2名称，如果有>

<同上>

#### 贡献
<一句话写清楚这个方法主要针对哪一个历史缺陷进行优化>
> 历史方法存在的问题：blabla

<再用数字列表列出论文相对已有工作的核心贡献点，一般 2-4 条，每条 1-2 句话，直接说清"做了什么/发现了什么"，不用展开论证>

1. ...
2. ...
3. ...

#### 实现

<论文的核心方法/pipeline，按执行顺序拆成数字步骤，每一步一个短标题 + 说明；每步内部如果有多个子要点用缩进的 `-` 列表；涉及数学定义的地方给出公式；每一步里如果论文自己承认了局限或作者觉得有局限，直接嵌在该步骤下用一句话点出（不用单独开"局限"大节）>

1. <步骤1的短名称>
   - ...
   - ...
2. <步骤2的短名称>
   - ...
3. <步骤3的短名称>
   - ...

#### 评估结果

<列出论文用了哪些测试集/实验设置/评估方式，一句话说清每个测试集是测什么的，不需要展开具体数字，除非某个数字是论文的核心卖点。如果哪一部分很显然，比如评估方式就是测试集中问题回答正确数目，就不用特别写了。如果哪一部分没有，比如并没有使用测试集，那就也不用写。>

测试集：

- <测试集1>：<一句话说明测的是什么>
- <测试集2>：<一句话说明测的是什么>

实验设置：
<比如使用的模型、验证了哪些ablation>

- <一句话说明重点>
- <一句话说明重点>

评估方式：

- <一句话说明重点>
- <一句话说明重点>

#### Critical Reading

- Weaknesses: <如果有需要可以分条列出，每条一句话说明重点>
- Open questions: <如果有需要可以分条列出，每条一句话说明重点>

```

Notes on tone and depth:
- This format is denser than a plain abstract paraphrase — the user wants enough mechanistic detail (formulas, pipeline steps, named sub-methods) to reconstruct how the method works, not just what it claims.
- Still never quote the paper verbatim beyond short (<15 word) phrases; formulas and step names in your own structuring are fine, but prose explanations must be your own words. Be natural and concise.
- `前置理论` is optional per paper — include it only when the paper leans on named prior techniques (like SAE, CAA, a specific loss, a prior algorithm) that a reader would need explained to follow the rest of the note. Skip it entirely for self-contained papers. The purpose of this section is to introduce the reader into the background of this work and the field in order to understand the proposed method.
- If the source text is too short to fill a section confidently (e.g. only an
  abstract was available), write what's inferable and note `（仅基于摘要，信息有限）`
  in that section rather than fabricating details.
- DO NOT USE BOLD.
- NEVER INVENT ANYTHING.

Examples:

```markdown
## Mechanistic Knobs

Mechanistic Knobs in LLMs: Retrieving and Steering High-Order Semantic Features via Sparse Autoencoders

ACL 2026.1 by Peking University

#### 前置理论

##### SAE：Sparse Autoencoder

SAE 是一个非常简单的三层神经网络，它的独特之处在于其中间的隐藏层维度极大且极其稀疏。

1. 输入（Input）： 大模型某一层的激活向量 $x$。
2. 编码器（Encoder）：通过一个线性变换和 ReLU 激活函数，将 $x$ 投影到超高维的空间中。
   - 例如，原始向量是 1024 维，SAE 的中间层可能会扩展到 32768 维甚至更高。
3. 稀疏约束（Sparsity Constraint）：这是关键。通过 $L_1$ 正则化等手段，强迫中间层只有极少数（例如几十个）特征同时处于激活状态。
4. 解码器（Decoder）：尝试用这些稀疏的特征重新重构出原始的激活向量 $x$。
5. 训练 loss：L1 loss 和 重建损失

##### CAA：Contrastive Activation Addition

- 构造对比对（Contrastive Pairs）： 准备两组相反的提示词。

  - 组 A (诚实): "In this scenario, I will tell the truth..."
  - 组 B (欺骗): "In this scenario, I will be deceptive..."

- 提取激活差值： 让模型分别运行这两组提示词，记录下中间层的激活向量（Activations）。将“诚实组”的向量减去“欺骗组”的向量，得到一个方向向量（Steering Vector），也就是 CAA 向量。

- 注入（Addition）： 在模型正常推理时，强行把这个“诚实向量”加到模型的中间层里。

- 结果：模型会变得比平时更诚实，即使你没要求它这么做。

*缺点：vector会有杂质，可解释性也没有那么高。*



#### 贡献

1. 使用了语义对立数据（比如“极其外向”vs“极其内向”的对话）。通过对比这两组数据在模型内部激发的特征差异（特征通过SAE提取得到），直接定位出哪些特征在控制特定的高阶行为。

2. 可以通过调节这些值来改变模型性格，并且不影响模型的其他能力。

3. 发现大模型内部的人格组织方式与人类心理学的元分析结果惊人地一致。这意味着大模型在学习人类语言的过程中，自动“内化”了人类的心理结构。

   功能忠实效应 (Functional Faithfulness)： 当你强行改变模型的一种人格（比如让它变得极端极端的随和），模型其他方面的表现会产生连锁反应。这些反应不是随机的乱码，而是符合人类心理学框架的折衷（Trade-offs）。



#### 实现

1. 语义对立数据 (Contrastive Data Synthesis)

   - 利用 LLM 生成大量成对的提示词。例如，针对“大五人格”中的尽责性（Conscientiousness）：
   - 正向提示：“你是一个极其严谨、有计划、追求完美的人，请回答……”
   - 负向提示：“你是一个随性、马虎、不负责任的人，请回答……”

2. 提取 CAA 引导向量 (Steering Vector Extraction)

   - 将模型在“正向”和“负向”提示下的中间层激活值（Activations）相减：$$V_{steer} = \text{Mean}(A_{positive}) - \text{Mean}(A_{negative})$$

   - 局限：这个生成的 $V_{steer}$ 混合了目标行为（性格）和杂质（特定的词汇、语调等）。

3. SAE 特征过滤与定位 (Feature Localization via SAE)

   - 映射（Projection）： 将 $V_{steer}$ 投影到 SAE 的特征空间中。

   - 评分机制：计算每个 SAE 特征与这个引导方向的余弦相似度或激活差异。

   - 锁定“旋钮”：只有那些在高阶行为差异中表现最显著、最纯粹的少数特征（Features）会被选出。这些特征就是论文所说的 Mechanistic Knobs（机械旋钮）。

4. 验证与实操 (Intervention & Evaluation)

   - 精准转向（Precision Steering）：手动调高某个 SAE 特征的激活值（如“社交敏感度”），观察模型在不同任务中的表现。
   - 稳定性测试（Model Stability）：检查在改变性格的同时，模型的基础逻辑能力（如 MMLU 测试集）是否受损。
   - 跨维度分析：也就是论文提到的“功能忠实效应”。研究当你旋转“亲和力”旋钮时，模型内部其他性格维度（如“情绪稳定性”）会如何发生协同变化。



#### 评估结果

测试集：

- TRAIT：measure LLM personality
- Interpersonal Ability Evaluation (IAE) part of SocialEval：a comprehensive test of the model’s social intelligence.





## HistLens

HistLens: Mapping Idea Change across Concepts and Corpora

ACL 2026.1 by Tsinghua University

#### 贡献

- 使用SAE，使得多概念、多语料分析可以在同一个框架下分析
- 概念的可分解性：一个概念可以拆解为若干SAE语义分量，各自有独立的历时轨迹
- 隐性概念计算：传统词频统计无法捕捉隐性概念，而SAE 可以捕捉到
- 证据可追溯性：所有信号都可以锚定到高激活文本证据，交由历史学专家验证解读，兼具计算规模化与人文阐释细腻度

#### 实现

1. 得到句子级的稀疏表示

   - 取第 29 层残差流的 token 级隐藏状态 ---> 通过SAE 得到稀疏激活向量，只保留激活值最大的 κ 个坐标 ---> 再对同一句子内所有 token 的稀疏激活做 max pooling

2. 对每个 SAE 基向量（维度）k，按年份计算均值激活 μ_{k,s}，然后定义累积漂移量：

   D_k = Σ|μ_{k,s} − μ_{k,s−1}|

   选出 D_k 最大的一批基向量，认为它们是"随时间变化最剧烈"的语义成分。然后：

   - 检索每个基向量激活最高的文本片段
   - 交给历史学专家阅读这些证据文本，人工赋予语义标签（例如"能动主体性""个人主义话语""财产与经济个体性"等）

3. 分析

   - 峰值年（概念强度最大的年份）、转折点（相邻切片变化最剧烈的年份，及其带符号强度 I）......
   - 单概念分解：将“个人”相关的维度进一步分解为{Individualism，property rights，independent subjects}，发现各自有不同趋势
   - 多概念比较：用差异热力图对比某几个概念在两个时间窗口之间的特征份额变化（如"个人"强化能动性的同时，"社会"从制度蓝图转向组织实践）
   - 跨语料比较（没看懂）：先构造"显著集合" I_{c,r}：对每个（概念，语料）组合，取概念强度处于高分位数（q=0.95）的文本子集，只在这个子集上做后续统计（避免语料规模、写作风格差异带来的偏差）。
     然后比较两个语料中 Top-30 漂移基向量集合的 Jaccard 重叠度，把跨语料差异分解为"共享语义骨架"与"语料特异的重加权"两部分。
   - 隐性概念计算（Implicit Concept Computation）：把显著集合 I_{c,r} 按"是否包含概念的规范词形"切分为显性和隐性两个子集，发现了"隐性领先显性"（implicit-leads-explicit）的语义扩散模式。

#### 评估结果

实验设置：

- OpenSAE + Llama-3.1-8B-Instruct
- 语料为《新青年》《向导》等民国期刊（共 3,277 期，803 万字）
- 概念选取"个人、社会、国家、世界"

验证方式：

- 跨层鲁棒性：在第 06/14/22/29 层重跑整个流程，看转折年份、峰值年份、证据上下文的 2-gram Jaccard 相似度是否稳定
- 历史学家人工验证：对每个概念抽样 20 条隐性高激活案例，由历史学者判断是否真实体现了该概念的隐性语义支撑，一致率在 75%–100% 之间
- 与既有史学分期对照：把模型识别出的最强转折年份，与史学界公认的语料转折点（如新青年 1919 年五四转折、向导 1923/1926 年国民革命与北伐节点）对比，误差普遍在 ±1 年以内
- 与基线方法对比：额外对比了在线 LDA 式动态主题模型和静态词向量（PPMI+SVD+Procrustes）两种基线，发现 SAE 方法在"隐性证据捕获能力"和"结果稳定性"之间取得了更好的平衡，而两个基线各自只能满足其中一项
```



### 3. Find the target notes file

Check `config/target_file.txt` in this skill directory for a saved path.

- **If it exists and the file it points to exists**: append there directly, no need to ask.
- **If it doesn't exist yet**: ask the user once where their paper-reading-notes
  Markdown file is (or should be created), e.g. "你的论文阅读笔记文档在哪？没有的话我可以帮你新建一个（比如 `~/Documents/论文阅读笔记.md`）。"
  Then save their answer to `config/target_file.txt` (create the `config/`
  folder if missing) so future runs don't ask again.
- The user can always override for a single run by explicitly naming a
  different file in their message — don't force the saved path on them.

### 4. Append the summary

Run:

```bash
conda run -n summarizer --no-capture-output python3 scripts/append_notes.py "<target_file_path>" "<summary_markdown_text>"
```

This appends the new `##` section to the end of the file. It does not
overwrite or reorder existing content.

Confirm to the user in one line what was added and where, e.g. "已将...的总结追加到 `~/Documents/论文阅读笔记.md`。"

