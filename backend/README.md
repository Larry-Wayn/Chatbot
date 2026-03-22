# ChatBot - Backend

## 目录

```
.
├── README.md
├── manage.py
├── pyproject.toml
├── requirements.txt
├── start.sh
│
├── COSYVoice/                             // CosyVoice2 仓库（原样放置）
│   ├── cosyvoice/
│   │   ├── cli/
│   │   │   └── cosyvoice.py               // CosyVoice2 类
│   │   └── utils/
│   │       └── file_utils.py              // load_wav
│   ├── pretrained_models/
│   │   └── CosyVoice2-0.5B/              // 模型权重
│   └── third_party/
│       └── Matcha-TTS/                    // 依赖子包
│
├── resource/
│   ├── database/
│   │   ├── NeZha.json                     // 角色知识库
│   │   ├── db_hash.txt
│   │   └── index.faiss / index.pkl        // 自动生成
│   └── voice/
│       └── NZ_angry.mp3                   // TTS 参考音频
│
├── generated_audio/                       // TTS 输出目录（自动创建）
│   └── tts_<timestamp>_<i>.wav
│
├── logs/
│   └── chat_api.log                       // 统一日志
│
├── docker/
│   ├── build.sh
│   ├── dev.Dockerfile
│   └── docker-compose.yml                 // 加 PYTORCH_CUDA_ALLOC_CONF 环境变量
│
├── docs/
│   └── api/
│       ├── ASR.md
│       ├── chat.md
│       ├── TTS.md                         
│       └── status.md
│
├── server/
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── settings.py                        // 加 tts + COSYVOICE_* 配置项
│   └── urls.py                            // 加 /api/tts/
│
├── asr/
│   ├── __init__.py
│   ├── apps.py
│   ├── models/
│   │   └── TranscribeTask.py
│   ├── services/
│   │   └── transcribe/
│   │       ├── __init__.py
│   │       └── WhisperTranscriber.py
│   ├── tests.py
│   ├── urls.py                            // POST /api/asr/transcribe
│   └── views.py
│
├── chat/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── rag.py
│   ├── tests.py
│   ├── urls.py                            // POST /api/chat/message  POST /api/chat/reset
│   ├── views.py
│   └── services/
│       └── chat/
│           ├── __init__.py
│           └── ChatService.py
│
└── tts/                                   
    ├── __init__.py
    ├── apps.py
    ├── models.py
    ├── tests.py
    ├── urls.py                            // POST /api/tts/synthesize  GET  /api/tts/status  GET  /api/tts/audio/<filename>                                                                       
    ├── views.py
    └── services/
        └── tts/
            ├── __init__.py
            └── TtsService.py              // CosyVoice2 懒加载单例 + 推理
```
## Build&Run

### Build Docker Image

Use `docker compose` to build and run the container:

```bash
❯ cd docker
❯ docker compose up -d
```

To view logs, use the following command:

```bash
❯ docker compose logs -f
```