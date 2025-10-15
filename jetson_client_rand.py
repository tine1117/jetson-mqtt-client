import paho.mqtt.client as mqtt
from datetime import datetime
import random, sys, io, json, os, uuid, time, socket

import jetson_info
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


EDGI_RAND_ID = jetson_info.get_rand_id()

BROKER_IP = "192.168.35.162"    #브로커 서버 아이피 -> 추후 도메인 설정
BROKER_PORT = 1883              #브로커 서버 포트
MQTT_USERNAME = "FIRST"         #MQTT USER 이름
MQTT_PASSWORD = "1234"          #MQTT 비밀번호 -> 추후 보안을 위해 암호화 파일 관리

DISC_FORMAT     = "edgi/{}/disconnect"

def get_sample_generate(): #온도 임시 생성 코드
    return {
        "temperature" : round(random.uniform(30, 90), 2)
    }

def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("[Socket] Connection successful !", flush=True)
    elif rc == 5:
         print("[Socket-Error] Login failed", flush=True)
    else:
        print("[Socket-Error] Error : {rc}", flush=True)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"[WARN] Unexpected disconnect rc={rc}", flush=True)


"""
[Qos]
Qos 0 : 손실 가능, 중복 없음
Qos 1 : 최소 1회 전달, 중복 가능
Qos 2 : 정확히 1회, 중복, 손실 방지
"""

def main():
    edgi_id = EDGI_RAND_ID
    ip = jetson_info.get_ip()

    print("[#] Start Jetson MQTT Client")
    print(f"Connect {BROKER_IP}:{BROKER_PORT} as {edgi_id} ...")

    topic = f"edgi/{edgi_id}/data"

    client = mqtt.Client(client_id=str(edgi_id)) #인스턴스 생성
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    will_topic = f"edgi/{edgi_id}/disconnect" #연결 해제 토픽
    will_payload = json.dumps({"edgi_id": edgi_id})
    client.will_set(will_topic, payload=will_payload, qos=1, retain=False) #LWT(유언 메세지) 설정

    client.connect(BROKER_IP, BROKER_PORT, keepalive=60) #Keepalive
    client.loop_start()

    try:
        while True:
            payload = {
                "edgi_id" : edgi_id,
                "ip" : ip,
                "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data" :  get_sample_generate()  #온도 값 불러오기
            }

            client.publish(topic, json.dumps(payload))
            print(f"[INFO] sendData : {payload}", flush=True)
            time.sleep(5) #5초에 한번씩 전송
    except KeyboardInterrupt: #(ctrl + c) 프로그램 종료
        print("[INFO] Exit")

    finally: #클라이언트 종료
        disc = json.dumps({"edgi_id": edgi_id, "reason": "normal"}, ensure_ascii=False, separators=(",",":"))
        client.publish(DISC_FORMAT.format(edgi_id), disc, qos=QOS, retain=False)
        time.sleep(1)

        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()