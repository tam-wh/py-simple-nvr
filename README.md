example of config.yaml

## Format
mkv = Choose mkv if audio is PCM. MKV allows pcm audio which means audio stream does not need to be transcoded
mp4 = Choose mp4 if audio is AAC


```
global:
  record_dir: c:\records
  record_segment_length: 300
  rtsp_host: 192.168.3.3
  rtmp_host: 192.168.3.3
  log_level: warning

cameras:
  - name: Cam_1
    stream: 'rtsp://192.168.3.X:554/user=USERNAME_password=PASSWORD_channel=1_stream=0.sdp'
    format: 'mkv'
    inputs:
      - -c:v
      - copy
      - -c:a
      - copy
    actions:
      - record

  - name: Cam_2
    stream: 'rtsp://USERNAME:PASSWORD@192.168.3.X:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif'
    format: 'mp4'
    inputs:
      - -c:v
      - copy
      - -c:a
      - copy
    actions:
      - record


alarmserver:
  enabled: false
  port: 15002
  
mqtt:
  address: '192.168.3.3'
  port: 1883
  username: USERNAME
  password: 'PASSWORD'
  topic: pyainvr/actions
  clientname: pyainvr
  ```