# main 分支改动审查（Stroke / 多义词补充 / 学习缓存优先级 / 远程地址迁移）

> 执行方式：⚠️ 未隔离上下文审查（由当前 agent 直接审查）

## 前置分析
- 负载：4 文件，+86/-3，无安全/支付模块，无跨模块 → 无告警
- Scope Check：CLEAN。意图=修复“Stroke→中风”机翻并迁移仓库地址；实际改动与之相符
- Diff Scope：frontend（油猴脚本）、config（远程词库地址）
- Secret 扫描：`gitleaks git --pre-commit --redact`，scanned ~2433 bytes，no leaks found
- 兼容性基线：未声明；风险面：不涉及新语法/API/CSS；兼容审查：未执行
- 架构定性：改动落在词典与加载逻辑所属位置，依赖方向无变化

## 修改总结
| 文件 | 类型 | 要点 |
|---|---|---|
| dict/figma-zh-CN.json | 修改 | +Stroke 及 25 个多义设计词 |
| tampermonkey/replacements.js | 修改 | 同上 |
| tampermonkey/figma-zh-cn.user.js | 修改 | 同上；`loadLearnedDictionary` 丢弃与内置词典冲突的学习缓存并回写；REMOTE_DICT.url 改为 liuhean2021 |
| README.md | 修改 | 安装/远程地址改为 liuhean2021 |

## 场景矩阵
| 场景 | 预期 | 结论 | 对抗性检查 |
|---|---|---|---|
| 缓存含 `Stroke:中风` | 启动时被清除，显示“描边” | ✅（rebuild 在 load 之前，lookup 可命中） | ✅已查 |
| 缓存含小写 `stroke` | canonicalMap 小写匹配，同样清除 | ✅ | ✅已查 |
| 缓存为空/损坏 JSON | 提前 return / catch 忽略 | ✅ | ✅已查 |
| 新仓库尚未推送 | 远程词库 404，`requestJson` 返回 null，静默跳过 | ✅ | ✅已查 |
| 长句中含 Screen/Layer 等单词 | 单词只走精确匹配，句内走 TOKEN_MAP，不受影响 | ✅ | ✅已查 |
| 整段文本恰为 `Screen`/`Ready` | 译为“滤色”/“可开发” | ⚠️ 见 🟡 | ⬜未查 |

## 审查结论
🔴 阻塞：无

🟡 [重要]〔代码审查〕dict 三处 `Screen`、`Ready` — 单词级精确匹配会把独立出现的 “Screen”“Ready” 一律译成“滤色”“可开发”。
  → 如果某处界面单独显示 “Screen”（如屏幕/设备）或 “Ready”（状态），会被误译。
  → 建议：改为带语境的完整词条（如 `Ready for dev`），去掉独立的 `Ready`；`Screen` 视实际界面确认，必要时保留。

🟢 [建议] `figma-zh-cn.user.js` `loadLearnedDictionary` — 每次启动都 `persistLearnedDictionary()`，无变化时也写存储；可仅在有删除时回写。
🟢 [建议] 三处词典手工同步易漂移，后续可由 `dict/figma-zh-CN.json` 生成另两处。
🎉 [亮点] 让人工词典优先于机翻缓存，从根上避免同类错译复发。

统计：🔴 0 | 🟡 1 | 🟢 2 | 💡 0 | 🎉 1

### 审查反思
🔍 最没把握：`Screen`/`Ready` 在真实界面的出现语境，未在 Figma 页面实测。
👁 可能遗漏：未在浏览器/Tampermonkey 中实测缓存清除；README 其余内容未逐行核对。

### 结论
✅ 通过（建议先处理 🟡）。改动 < 200 行，Self-Test 不触发。

## 复审（处理上述 🟡/🟢）
- 🟡 已处理：删除独立的 `Screen`、`Ready`，新增带语境的 `Ready for dev: 可开发`
- 🟢 已处理：`loadLearnedDictionary` 仅在有条目被删除时才回写存储
- 🟢 已处理：新增 `scripts/sync_dict.py`，以 `dict/figma-zh-CN.json` 为唯一来源重新生成两个 JS 内的词典块（三处现为 307 条，完全一致）
- 复审结论：✅ 通过，无新增 🔴/🟡
