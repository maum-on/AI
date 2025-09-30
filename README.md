flowchart TD

    A[Diary Input<br/>(text, meta)] --> B[Guard:<br/>Mask PII + Detect Crisis]

    B -->|Crisis Detected| C[[Crisis Reply]]
    B -->|No & Short| D[Normal Mode:<br/>Analyze Diary]
    B -->|No & Long| E[Long Mode:<br/>Chunk + Summarize]

    D --> F[Generate Replies<br/>(short & normal)]
    E --> F

    F --> G[DiaryReplyOutput<br/>(reply_short, reply_normal,<br/>analysis, flags)]
