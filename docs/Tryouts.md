# Versuche, Ideen die zu Versuchen werden und umgekehrt

## Visualisierung über Webcam:

```yaml
  deamon-heimdall:
    build:
      context: ./../pkg/deamon-heimdall
      dockerfile: ./Dockerfile
    image: deamon-heimdall-image
    container_name: deamon-heimdall
    volumes:
      - ./../pkg/deamon-heimdall:/app
    working_dir: /app
    command: >
      /bin/sh -c "modprobe v4l2loopback devices=1
      && ffmpeg -i rtsp://192.168.178.21:8080/h264.sdp -fflags nobuffer -pix_fmt yuv420p -f v4l2 /dev/video0
      && pip install -r requirements.txt 
      && python -u main.py"
    environment:
      - VIDEO_STREAM_URL=http://192.168.178.21:8080/video
    cpu_shares: 1024
    healthcheck:
      test: 
        - CMD-SHELL
        - pgrep -f 'main.py' || exit 1
      interval: 2s
      timeout: 2s
      retries: 3
```