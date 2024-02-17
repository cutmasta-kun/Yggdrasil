# ntfy.sh

## Documentation 
[ntfy.sh Documentation](https://docs.ntfy.sh/)

## Publish Message

```python
import requests
import json

requests.post("https://ntfy.sh/",
    data=json.dumps({
        "topic": "mytopic",
        "message": "Disk space is low at 5.1 GB",
        "title": "Low disk space alert",
        "tags": ["warning", "cd"],
        "priority": 4,
        "attach": "https://filesrv.lan/space.jpg",
        "filename": "diskspace.jpg",
        "click": "https://homecamera.lan/xasds1h2xsSsa/",
        "actions": [{"action": "view", "label": "Admin panel", "url": "https://filesrv.lan/admin"}]
    })
)
```

## Message Type Specification

| Field     | Required | Type                  | Example                        | Description                                   |
|-----------|----------|-----------------------|--------------------------------|-----------------------------------------------|
| `topic`   | ✔️       | string                | `topic1`                       | Target topic name                             |
| `message` | -        | string                | `Some message`                 | Message body; set to triggered if empty       |
| `title`   | -        | string                | `Some title`                   | Message title                                 |
| `tags`    | -        | string array          | `["tag1", "tag2"]`             | List of tags, may map to emojis               |
| `priority`| -        | int (1, 2, 3, 4, 5)   | `4`                            | Message priority (1=min, 3=default, 5=max)    |
| `actions` | -        | JSON array            | See action buttons             | Custom user action buttons for notifications  |
| `click`   | -        | URL                   | `https://example.com`          | Website opened when notification is clicked  |
| `attach`  | -        | URL                   | `https://example.com/file.jpg` | URL of an attachment (see attach via URL)     |
| `markdown`| -        | bool                  | `true`                         | Set true if message is Markdown-formatted     |
| `icon`    | -        | string                | `https://example.com/icon.png` | URL for notification icon                     |
| `filename`| -        | string                | `file.jpg`                     | File name of the attachment                   |
| `delay`   | -        | string                | `30min`, `9am`                 | Timestamp or duration for delayed delivery    |
| `email`   | -        | e-mail address        | `phil@example.com`             | E-mail address for e-mail notifications       |
| `call`    | -        | phone number or 'yes' | `+1222334444` or `yes`         | Phone number for voice call notifications     |
