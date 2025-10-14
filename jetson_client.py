import paho.mqtt.client as mqtt
from datetime import datetime
import random, sys, io, json, os, uuid, time, socket

import jetson_info
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BROKER_IP = "192.168.35.162"    #브로커 서버 아이피 -> 추후 도메인 설정
BROKER_PORT = 1883              #브로커 서버 포트
MQTT_USERNAME = "FIRST"         #MQTT USER 이름
MQTT_PASSWORD = "1234"          #MQTT 비밀번호 -> 추후 보안을 위해 암호화 파일 관리

def get_ip():
    return socket.gethostbyname(socket.gethostname())

def generate_data(): #온도 임시 생성 코드
    return {
        "temperature" : round(random.uniform(30, 90), 2)
    }

def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("[Socket] connection successful !", flush=True)
    elif rc == 5:
         print("[Socket-Error] 로그인 실패, 비밀번호 확인", flush=True)
    else:
        print("[Socket-Error] 기타 에러코드 {rc}", flush=True)




def main():
    print("[#] Client Start !")
    edgi_id = jetson_info.get_id()
    ip = get_ip()
    topic = "edgi/{edgi_id}/data"

    client = mqtt.Client(client_id=str(edgi_id))
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect

    will_topic = f"edgi/{edgi_id}/disconnect" #연결 해제 토픽
    will_payload = json.dumps({"edgi_id": edgi_id})
    client.will_set(will_topic, payload=will_payload, qos=1, retain=False)

    client.connect(BROKER_IP, BROKER_PORT, keepalive=60) #Keepalive
    client.loop_start()

    try:
        while True:
            payload = {
                "edgi_id" : edgi_id,
                "ip" : ip,
                "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data" : generate_data()
            }

            client.publish(topic, json.dumps(payload))
            print(f"[Send] data : {payload}", flush=True)
            time.sleep(5) #5초에 한번씩 전송
    except KeyboardInterrupt:
        print("Exit")
    finally:
        disconnect_payload = json.dumps({"edgi_id": edgi_id})
        disconnect_topic = f"edgi/{edgi_id}/disconnect"
        client.publish(disconnect_topic, disconnect_payload, qos=1, retain=False)
        time.sleep(1)

        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()