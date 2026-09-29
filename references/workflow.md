# AI 漫剧全自动化生产线 · 主链工作流（v1）

> 目标：从「一集分镜清单 manifest」到「可交付成片」全程可一键跑、可断点续跑、带质检回环。
> 两条线并行：**精品主链**（Seedance 2.5，可控锁脸/配音/字幕/音效）与 **走量线**（小云雀四步，先走量后精修）。
> 本文件是「生产线」的唯一权威定义；细节参数见 `references/` 各文档。

---

## 0. 两条线的分工（什么时候走哪条）

| | 精品主链（本文件主线） | 小云雀走量线 |
|---|---|---|
| 引擎 | Seedream 出关键帧 + Seedance 2.5 出分镜 | 小云雀短剧 Agent 四步 API |
| 可控点 | 三视图锁脸 / 真配音口型 / 字幕样式 / 音效转场 | 只能靠内部一致性，锁脸弱 |
| 产物 | 1080x1920 成片 + SRT + 质检报告 | 720p 成片（需去水印 + 回补字幕） |
| 适用 | 门面集、强锁脸、过审红线、题材差异化集 | 试水、铺盘走量、验证钩子 |
| 默认策略 | **先走量、后精修**：走量出全季 → 质检挑 L1 崩镜 → 只对崩镜走主链补 |

---

## 1. 状态机与断点续跑

每集目录维护 `制作成果/pipeline_state.json`，阶段顺序固定：

```
preflight → characters → previz → tts → keyframes → video → assemble → qa → technical_qa → delivery
```

- 每阶段 = 一个幂等脚本 + 产物存在性缓存（已产出即跳过）。
- 某阶段失败：保留已完成阶段，`--resume` 从第一个未完成阶段继续，**不重烧已完成的镜头**。
- 正式全量视频阶段存在任一失败镜头时不拼接部分成片；修复后用 `--resume` 续跑。显式镜头列表仅用于冒烟和定向重试。
- `--from X` 强制从 X 开始，`--to Y` 到 Y 停止，`--force` 重跑某阶段，`--dry-run` 只打印将执行的命令。

一键入口：`python3 scripts/run_pipeline.py`（用法见文末 §8）。

---

## 2. 十道闸门（阶段表）

| # | 阶段 | 脚本 | 输入 | 输出 | 放行条件 / 失败处理 |
|---|---|---|---|---|---|
| 1 | 清单 | `short-drama-director` 出 | 剧本/人物圣经 | `epNN_manifest.json` | 字段符合 `manifest-schema.md` |
| 2 | 过审预检 | `check_compliance.py` | manifest | `qa_precheck.md` | `--fail-on error`，有硬红线=停 |
| 3 | 清单校验 | `validate_manifest.py` | manifest | 校验结论 | 有 ERROR=停 |
| 4 | 成本预算 | `estimate_cost.py` | manifest | 成本预估 | 烧钱前人工确认 |
| 5 | 角色资产 | `gen_character_sheets.py` | 角色描述 | `refs/{角色}_四视图.png` | 三视图钉死才进分镜 |
| 6 | 分镜预演 | `previz.py` | manifest | `制作成果/previz/` contact sheet | 锁机位站位，拦“大片感/运镜太宽” |
| 7 | 先配音 | `gen_tts.py --write-manifest` | manifest.text | `制作成果/audio/{id}` + 回填 `shot.audio` | 真音频就绪，口型有锚 |
| 8 | 关键帧 | `gen_keyframes.py` | manifest.img | `制作成果/images/{id}.png` | 缓存命中即跳过 |
| 9 | 分镜视频 | `make_episode.py --seed-n 4 --pick` | images+audio+roles | `制作成果/video/{id}.mov` | 抽卡 4 版，模型选最优；欠费/审核自动降级 |
| 10 | 字幕拼装 | `assemble.py` | video + shot.audio | `{title}_EP{NN}_成片.mp4` + SRT | 字幕规范见 §4 |
| 11 | 成片质检 | `qa_frames.py` | 成片 + manifest | `qa_ep.md`（L1/L2/L3） | L1 崩镜 → 修片回环 §3；全绿 → 技术门 |
| 12 | 技术交付门 | `technical_qa.py` | 成片 + manifest | `technical_qa.json` | 规格、音视频流、每镜、黑帧、响度、峰值和字幕；失败硬阻断 |
| 13 | 交付清单 | `delivery_manifest.py` | 成片 + technical_qa + content/compliance JSON | `delivery_manifest.json` | 三门全过才 `READY_FOR_PUBLISH`，否则待复核 |

---

## 3. 质检回环（闭环，不是一条直线）

```
qa_frames 分级
  ├─ L1 崩镜（锁脸漂移/口型对不上/审片红线）→ fix_shot.py（原生 edit）或 extend_shot.py 或单镜重出
  ├─ L2 可修 → 局部修片后重新 assemble
  └─ L3 通过 → 交付
循环上限 2–3 轮，每轮结论追加进 qa_ep.md，避免死循环烧钱。
```

`qa_frames.py` 现在把审片结论结构化落盘：`qa_result.json` 含 `status / l1_shots / l2_shots / l3_shots / verdict_source`，供下游自动回环直接消费（`run_volume.py --auto-refine` 就吃这份结果）。

---

## 4. 字幕规范（2026-09-26 定版，对齐爆款共识）

- 白字 + 黑描边 3px；重点词单独变色（`--highlight 关键词`），**不整句变色**。
- 最多 2 行，单行 ≤ 画面宽 70%；字号 45px（1080 宽基准）。
- 中下部安全区：距底 **16%**（抖音/红果字节系 UI 底线）；`--safe-area tight=12% / normal=16% / wide=19%`。
- 提前 0.2s 出现，按句义断句；说话人标签默认关（`--speaker-tag` 可开）。
- 时间轴**优先用 `shot.audio` 真实时长按字数分摊**（先配音后画面的自然结果），无音频才退化为镜内均分。
- 逐字 force-align（WhisperX 级）是下一级增强，本机暂无本地 ASR，需先装 `faster-whisper`。

---

## 5. 成本与风控闸门

- `estimate_cost.py --rate --pass-rate --versions`：烧钱前先算总账（关键帧 + TTS + 分镜 + 重试放大）。
- 每镜 `--seed-n 4` 抽卡、`--pick` 选片；门面集才开高 N。
- `AccountOverdue` 自动拦截整批；真人脸/半写实特写触发隐私审核时自动降级纯文生视频。
- 大场面/连续镜头先 `previz` 白模，把废片拦在预演阶段，不烧 Seedance 的钱。

---

## 6. 产物与命名

```
制作成果/
  previz/       分镜预演 contact sheet
  audio/{id}    配音（先配音后画面）
  images/{id}   关键帧
  video/{id}.mov 分镜（原生配音或 -a 驱动口型）
  norm/{id}.mp4  归一化 1080x1920/25fps
  subs/{id}/     字幕 PNG 临时
  pick_frames/   抽卡选片帧
  qa_precheck.md 过审预检报告
  qa_ep.md       成片质检报告
  technical_qa.json 技术交付门
  delivery_manifest.json 交付文件清单
{title}_EP{NN}_成片.mp4 + .srt
```

---

## 7. 已知边界与升级路线（按优先级）

1. **字幕逐字对齐**：装 `faster-whisper` 对 `shot.audio` 做词级时间戳，替换“按字数分摊”。（待做）
2. **口型评测量化**：抽嘴部帧 + 模型打分，把“口型对不上”从人工目测变成硬指标。（待做，可选 Wav2Lip 后期同步）
3. **资产仓库化**：✅ 已落地 `scripts/asset_bank.py`（跨季资产银行：角色四视图/场景全景建一次多季复用）+ `gen_character_sheets.py --bank` + `run_pipeline.py --bank`。奇观模板/多机位全景仍是下一级增强。
4. **走量线回环**：✅ 已落地 `run_volume.py --auto-refine --manifest ...`：小云雀成片 → `qa_frames` 结构化挑 L1 崩镜 → `refine_shots.py` 把崩镜+缺镜送回 Seedance 主链重出 → `assemble.py` 重拼。超 `--refine-budget` 打印成本警告并跳过，不偷偷烧钱。
5. **配音音轨正确性（已知 bug）**：`make_episode.py` 对“先配音”镜只传 `-a` 不传 `--audio-gen`，2.5 大概率静音（见 `references/seedance-25-truth.md` §7）。已加开关 `SD25_AUDIO_MODE=legacy|reference-gen|mix` 与 `assemble.py --mix-tts`，但默认仍 `legacy`——正式切之前先 1 镜冒烟实测定论，再改默认。

---

## 8. 一键入口

```bash
cd 集目录
# 全自动：预检→配音→关键帧→分镜→字幕拼装→质检（断点续跑）
python3 ~/.codex/skills/ai-comic-drama-pipeline/scripts/run_pipeline.py --manifest ep01_manifest_v2.json

# 带抽卡选片 + 角色资产 + 分镜预演
python3 ~/.codex/skills/ai-comic-drama-pipeline/scripts/run_pipeline.py \
  --manifest ep01_manifest_v2.json --characters --previz --seed-n 4 --pick

# 只跑到字幕拼装 / 只重跑质检 / 预览不执行
python3 ~/.codex/skills/ai-comic-drama-pipeline/scripts/run_pipeline.py --manifest ep01_manifest_v2.json --to assemble
python3 ~/.codex/skills/ai-comic-drama-pipeline/scripts/run_pipeline.py --manifest ep01_manifest_v2.json --from qa --force
python3 ~/.codex/skills/ai-comic-drama-pipeline/scripts/run_pipeline.py --manifest ep01_manifest_v2.json --dry-run
```
