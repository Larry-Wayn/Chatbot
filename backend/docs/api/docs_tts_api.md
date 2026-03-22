# TTS API

Base path: `/api/tts`

---

## POST `/api/tts/synthesize`

将文本转为哪吒角色语音（CosyVoice2 零样本克隆）。

### Request

```json
{ "text": "我是哪吒，你来打我啊！" }
```

| 字段   | 类型   | 必填 | 说明         |
|--------|--------|------|--------------|
| `text` | string | ✅   | 要合成的文本 |

### Response — 200 OK

```json
{ "audio_files": ["tts_1712345678_0.wav", "tts_1712345678_1.wav"] }
```

长文本会被模型自动分段，`audio_files` 可能包含多个文件，需按顺序拼接播放。

### Error responses

| Status | Body | 原因 |
|--------|------|------|
| 400 | `{"error": "Missing or empty 'text' field."}` | text 为空 |
| 400 | `{"error": "Invalid JSON body."}` | 请求体格式错误 |
| 500 | `{"error": "..."}` | 模型/参考音频未找到，或推理失败 |

---

## GET `/api/tts/audio/<filename>`

获取已生成的 `.wav` 音频文件。

- `filename`：由 `synthesize` 接口返回，如 `tts_1712345678_0.wav`
- Response：`audio/wav` 二进制流

---

## GET `/api/tts/status`

TTS 服务健康检查。

### Response — 200 OK

```json
{
  "status": "running",
  "reference_audio": "loaded",
  "audio_dir": "/app/generated_audio"
}
```

---

## Notes

- 音频文件保存在 `settings.COSYVOICE_AUDIO_DIR`（默认 `BASE_DIR/generated_audio/`）。
- CosyVoice2 模型在**首次请求时懒加载**，Django 启动不受影响。
- 长文本自动分段，客户端需按返回列表顺序顺序播放或合并。
- `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` 建议在启动脚本或 docker-compose 中设置。
