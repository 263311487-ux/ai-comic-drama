---
name: ai-comic-drama-pipeline
description: 本机已跑通的 AI 漫剧/短剧全自动生产流水线。把一份分镜清单（manifest）自动变成成片：Seedream/Seedance 2.5 CLI 生成关键帧与带原生配音的分镜视频，再用 ffmpeg 归一化、烧字幕、拼装，最后抽帧做模型质检。也含火山「小云雀短剧Agent」四步 API 备选线。当用户要求“把剧本/分镜批量自动做成漫剧视频、出片、生成 EP、跑一集”时使用；纯编剧、分镜创意、角色设定与台词诊断走 short-drama-director 技能。
---

# AI 漫剧全自动生产流水线

把「一集的分镜清单」自动生产成「可交付成片」。本技能只做**已跑通的生产自动化**；创意和导演环节（五阶剧本、人物账、台词诊断、资产锁）由 `short-drama-director` 负责，Seedance 单镜头提示词细节由 `seedance-25` 负责。

## 何时用 / 不用
- 用：用户给出或要求生成 manifest/分镜清单，要批量出关键帧、分镜视频、成片、字幕、质检。
- 不用：只写剧本、只设计角色、只问 Seedance 提示词怎么写、只做单张海报/单段视频。
- 未定稿的剧本先回 `short-drama-director` 出人物圣经和分镜清单，再回到本技能投产。

## 前置条件
- 工具已装并确认：`seedance`、`seedream`（`~/.local/bin/`，软链到 `seedance` 包）、`ffmpeg`（`/opt/homebrew/bin/`）、`python3`。
- 环境变量：`ARK_API_KEY`（方舟 Bearer Key，Seedance/Seedream CLI 使用）；`ROUTER_ONE_API_KEY`（资产出图 gpt-image-2 与质检 gpt-6-astra 使用，可选）；`~/.volcengine/credentials`（小云雀四步 API 的 AK/SK）。
- 关键配置由 env 覆盖：`SEEDANCE_BIN`、`SEEDREAM_MODEL`、`SEEDREAM_SIZE`、`SD25_WORKERS`、`SD25_FALLBACK_T2V`。

## 主链（Seedance CLI，已交付成片验证）
**一键入口**：`python3 scripts/run_pipeline.py --manifest ep01_manifest_v2.json` 串起下面全流程（断点续跑 + 质检回环），总纲见 `WORKFLOW.md`；也可按需手动逐阶段跑。
1. **清单**：生成 `epNN_manifest.json`，字段见 `references/manifest-schema.md`，模板见 `assets/manifest.template.json`。
2. **投产前预检**：`python3 scripts/check_compliance.py --out qa_precheck.md`（平台过审红线先挡）+ `python3 scripts/validate_manifest.py --json manifest_result.json`（字段/时长/重复 ID/参考图存在性）+ `python3 scripts/estimate_cost.py --rate <元/秒> --pass-rate <0-1> --versions <n>`（烧钱前算总账）。有 ERROR 先修，别带病进生成。
3. **分镜预演**：`python3 scripts/previz.py`（批量烧钱前先审机位/站位/运镜/台词故事板），大场面与连续镜头先锁白模站位，再进关键帧。
4. **资产**：先锁角色四视图与场景参考图（防崩脸），方法见 `references/qa-and-assets.md`。跨季复用走资产银行：`python3 scripts/asset_bank.py --add-character 林昭 --files sheet=refs/林昭_四视图.png --root ~/ai-drama-assets`；`gen_character_sheets.py --bank ~/ai-drama-assets` 命中即复用、新资产自动入库；`run_pipeline.py --bank` 透传。
5. **先配音**：`TTS_CMD='edge-tts --voice zh-CN-XiaoxiaoNeural --text "{text}" --write-media "{out}"' python3 scripts/gen_tts.py --write-manifest` 给对白镜出真音频；`make_episode.py` 检测到 `TTS_CMD` 也会自动先跑这步。没 TTS 才回退 `--audio-gen` 原生配音。
6. **关键帧**：`python3 scripts/gen_keyframes.py`（Seedream pro，逐镜出图，角色描述锁 + style_lock + 缓存）。
7. **分镜视频**：`python3 scripts/make_episode.py`（Seedance 2.5，style_lock + 参考图锁脸 + 真 TTS 音频 `-a` 驱动口型 + 审核/欠费自动降级）。多版抽卡：`--seed-n 4 --pick` 每镜出 4 版并自动选最优。跑完自动写 `制作成果/production_report.json`（一次生成通过率/失败原因分布，反推真实单片成本）。质量调优（口型、镜头连贯、换版）见 `references/tools-deep-dive.md`。
8. **字幕与拼装**：`python3 scripts/assemble.py`（ffmpeg 归一化 1080x1920/25fps、逐句字幕、片头片尾钩子、concat）。字幕以剧本文本为准，时间轴优先按 `shot.audio` 真实配音时长按字数分摊、提前 0.2s 显隐（无音频才退化为镜内时长）；渲染由 `scripts/subtitles.py` 统一提供（PingFang SC Semibold + 白字黑描边 + 中下部安全区距底 16% + 行宽 70% + 最多 2 行；默认不加说话人标签，重点词高亮、标签为可选）。加 `--trim 0.3` 裁首尾模糊、`--transition fade|black` 做转场。
9. **质检**：`python3 scripts/qa_frames.py` 抽 9 帧交 gpt-6-astra 审片，结果结构化落 `qa_result.json`（`status / l1_shots / l2_shots / l3_shots`）；L1 崩脸/崩手用 `scripts/fix_shot.py` 修，或整镜重出，不用整集返工。
10. **技术交付门**：`python3 scripts/technical_qa.py` 检查成片规格、音视频流、每镜完整性、黑帧、综合响度（-24~-14 LUFS）、真峰值（≤-1 dBFS）和字幕文件；失败时禁止交付。
11. **交付清单**：`python3 scripts/delivery_manifest.py` 仅在技术门、内容审片和合规预检三个结构化结果均为 `PASS` 后生成唯一发布状态 `READY_FOR_PUBLISH`；任一报告缺失或非 PASS 都硬阻断。

快速冒烟：`make_episode.py S01,S05` 只跑指定镜头；全量：不加参数。

## 修片与续写（文档级，正式用前先跑 1 条验证；均可加 `--dry-run` 只预览命令不烧钱）
- 修崩脸/崩手/多余元素：`python3 scripts/fix_shot.py --task-id <ID> --prompt "修复..."`（原生 edit），无 task id 时 `--video S01.mov` 走 V2V。
- 镜头拉长/拼接：`python3 scripts/extend_shot.py --video S01.mov --prompt "向后延..." --duration 6`（2.5 原生 extend，可 bridge 2-3 段）。
- 独立 TTS 口型音频：`scripts/gen_tts.py`（可插拔，`TTS_CMD` 接任意 TTS CLI，`--write-manifest` 自动回填 `shot.audio`）。

## 备选线（火山小云雀短剧 Agent API）
四步接口：剧本解析 → 素材设计 → 分镜视频 → 单集合成。第一步已实测，2-4 步契约已核对、整链未全跑。用法：`FILE_URL=<剧本URL> python3 scripts/xiaoyunqiao_pipeline.py --episodes 1,2 --download`。

**最优用法（hybrid）**：小云雀=量产走量线（剧本进、整集出），Seedance 主链=精品精修线（锁脸/抽卡/音效/转场可控）。小云雀素材设计**不支持重传外部图**，锁脸只能靠其内部一致性，所以它出的片必须再过 `qa_frames.py` 审片，L1 崩镜用主链补——这条回环已一键化：`run_volume.py --auto-refine --manifest ep01_manifest_v2.json`。完整分工与五条铁律见 `references/xiaoyunqiao-api.md`。

**小云雀成片后处理**：下载的成片自带 AI 水印、不带字幕，用 `scripts/burn_srt.py --video 成片.mp4 --srt 台词.srt --out 出片.mp4 --delogo x:y:w:h` 去水印并回补字幕（简体 Semibold，非繁体面；SRT 建议按剧本生成，别直接用 whisper 原始转写以免增漏字）。

## 生产策略：先走量、后精修（推荐默认）
- **先走量**：`python3 scripts/run_volume.py --script 第1集.txt --episodes 1,2,3 --download` —— 本地剧本一键上传公网 → 小云雀四步 → 下载整季成片（默认 catbox 匿名托管，仅试水；量产换 TOS 私密 URL）。
- **自动精修（一键）**：`python3 scripts/run_volume.py --script 第1集.txt --episodes 1 --download --auto-refine --manifest ep01_manifest_v2.json --refine-budget 3` —— 下载后自动 QA、挑 L1 崩镜、只把崩镜+缺镜送回主链重出并重拼；超预算只警告不烧钱。
- **手动精修**：对下载的成片跑 `qa_frames.py` 抽帧审片 → 挑出 L1 崩镜/锁脸漂移/口型对不上的镜 → `python3 scripts/refine_shots.py --manifest ep01.json --shots S03,S05 --auto --rebuild` 只补崩镜并重拼，或对单镜 `fix_shot.py` 修。
- **何时必须精修**：门面集、强锁脸角色、口型严格、平台过审红线（血雾/斩首/特写）、题材同质化风险高的集。
- **何时不必精修**：纯试水、验证剧情钩子、走量铺盘的普通集，走量出片即可。

## 爆款方法论（2026 最新对标，详见 references/hit-method.md）
本 skill 除生产自动化外，还内置一层「爆款工艺」标准，凡要出片就按它卡：

- **一场一冲突**：一场戏 = 同一时间 + 同一地点 + 一个核心冲突，不夹带别的时空；一场 20–40s → 5–8 镜 → 每镜 3–5s。
- **单镜单动作**：一个镜头只做一个动作，运镜写具体（`缓慢推近`/`横向跟拍`/`低角度仰拍`），不写“大片感/震撼”。
- **分镜七项**：镜号 / 时长 / 画面 / 动作 / 运镜 / 台词 / 音效；对应 manifest 的 `id/dur/img/motion/text/sfx`（画面与动作分离）。
- **三视图锁脸**：正面/侧面/背面钉死才进分镜；场景资产与角色分开建（全景 + 三档景深），资产建一次、多季复用。
- **抽卡筛废片**：每镜先出 3–5 版挑可用版；废片根因=角色没锁 / 场景没存全景 / 运镜太宽。
- **风格双层锁 + 色卡**：底层质感层全片逐字不变，上层类型调性层按段替换；进阶挂 13 色色卡图与“命名铁律”。
- **音频分层**：兵器金属 / 妖气低频 / 风声环境 / BGM 分层；情绪戏降 BGM、保呼吸与布料摩擦，不盖台词。
- **转场三选一**：硬切 / 淡入 / 遮黑；颜色统一（冷青夜景 / 暖黄烛光）。裁掉每镜首尾模糊再拼装。
- **红果红线**：不侵权、不低俗、不价值观偏差、不做 PPT 式动画、不题材同质化；血雾不过红、斩首不过长、特写不超限、口型对齐、AI 标识。合规前置流程见 `references/compliance.md`，全网痛点靶点见 `references/industry-painpoints.md`。
- 六大题材公式、五类锚定、分季伏笔回收等完整机制见 `references/hit-method.md`；剧本/开篇/金手指层走 `short-drama-director`。

## 分镜最优速查（详见 references/tools-deep-dive.md）
- 时长按节奏分配：对白 4–6s、动作/转场 8–12s、大场面 ≤30s；拿不准用 `-1`。
- 角色锁是命根：每角色挂正脸+三四侧脸参考图，描述原文原样带、只追加动作。
- 口型默认“先配音后画面”：`gen_tts.py` 出真音频，`make_episode.py` 自动带 `-a` 且不再同时挂 `--audio-gen`；没有 TTS 才降级原生配音。
- 连续镜头用 `--return-last-frame` 拿尾帧接力下一镜首帧；长叙事用 `extend` 前伸/后延，修片用 `edit` 不整镜重出。
- 烧钱前先 `previz.py` 锁机位站位；大场面/连续镜头先白模过一遍，把“大片感/运镜太宽”废片拦在预演阶段。

## 硬约束速查（详见 references/production-constraints.md）
- 过审红线先跑 `check_compliance.py`；批量烧钱前先 `previz.py` 锁机位站位；两条详见 `references/compliance.md`。
- Seedance 2.5 只有 480p/720p，没有 1080p；成片 1080p 靠 ffmpeg 放大。
- `--first-frame` 与 `--image/--audio` 参考素材互斥；用参考图锁角色时用 `--image`。
- 真人脸/半写实特写易触发隐私审核，失败自动降级纯文生视频。
- 出图/出片模型默认：`doubao-seedream-5-0-pro-260628`、`doubao-seedance-2-5-260628`。
- 每次正式跑前先小额度冒烟，确认账户余额与 `charge_count` 口径（欠费会返回 `AccountOverdue`）。
- 正式全量任务只要有一个镜头失败就停止并进入修复/续跑；只有显式指定镜头列表的冒烟任务允许保留局部产物。拼装阶段遇到缺镜头同样硬阻断。
- 生成重试受 `SD25_MAX_SHOT_ATTEMPTS` 限制（默认 2）；生产报告记录每镜重试预算与估算尝试次数，禁止无限重试烧钱。
- 整集提交前受 `SD25_MAX_TOTAL_ATTEMPTS` 限制（默认 200）；预计尝试数超过总预算时硬阻断，不提交任何视频任务。
- 配音音轨：`SD25_AUDIO_MODE=legacy|reference-gen|mix` + `assemble.py --mix-tts`（默认 `legacy` 保持既有行为；切新档前先 1 镜冒烟实测，见 `references/seedance-25-truth.md` §7）。
- 精品生产默认单并发（`SD25_WORKERS=1`），提交间隔默认 8 秒（`SD25_SUBMIT_GAP`），提交阶段 429 会记录并退避（`SD25_429_BACKOFF` 默认 60 秒）。批量并发必须显式覆盖并承担限流风险。
- 精品抽卡可设置 `SD25_REQUIRE_PICK=1`；启用后必须有模型选片结果，缺少审片 Key、模型失败或返回无效版本都会阻断，不再按文件体积冒险选片。

## 自动工厂边界

主链现在自动推进到技术交付门，并在缺镜头、成片规格错误、无音频或技术 QA 失败时硬阻断。`qa_frames.py` 的模型结论仍是内容质量证据，不得把 API 成功、文件存在或技术 QA PASS 误写成“精品”或“爆款”；只有内容审片、合规审片和技术门都通过，才可发布。

阶段状态写入前必须通过产物契约验证；恢复任务也要核验已完成阶段的产物仍存在且结果为 PASS。TTS 阶段验证真实音频文件，QA 阶段验证结构化 PASS 状态，禁止仅凭字段或报告文件存在就缓存为完成。

主链按创意 manifest 指纹隔离版本：TTS 自动回填的 `shot.audio` 不改变创意指纹；创意 manifest 改动会使旧阶段缓存失效，并把已付费生成物归档到 `制作成果/archive/<timestamp>/` 后再重新生产。
