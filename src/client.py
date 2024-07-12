# 문자열을 ASCII 아트로 출력한다.
from art import tprint

# PIL 사진을 ASCII 아트로 변환하고 변환된 ASCII 아트를 출력한다.
from ascii_magic import from_image, to_terminal

# OpenCV 사진의 색상을 PIL 색상 규격으로 변환한다.
from cv2 import COLOR_BGR2RGB, cvtColor

# I2C 프로토콜로 의사소통한다.
from luma.core.interface.serial import i2c

# SSD1306 디스플레이의 드라이버이다.
from luma.oled.device import ssd1306

# 지정한 셸을 실행한다.
from os import system

# PIL 사진 객체를 생성한다.
from PIL import Image

# HTTP POST를 요청한다.
from requests import post

# Raspberry Pi의 다용도 입출력 기능이다.
import RPi.GPIO as Gpio

# 지정한 시간동안 스레드의 실행을 멈춘다.
from time import sleep

# VidGear에서 PiCamera를 사용한다.
from vidgear.gears import PiGear

frame_names_by_id = {
    "1": "비비드 레드",
    "2": "트루 오렌지",
    "3": "라이트 옐로우",
    "4": "딥 그린",
    "5": "핫 블루",
    "6": "인디고",
    "7": "머티리얼 바이올렛",
    "11": "베이직 블랙",
    "12": "베이직 화이트",
    "13": "애쉬 그레이",
    "21": "초콜릿 민트",
    "22": "체리 밀크",
    "23": "리치 골드",
    "24": "쿨 페퍼민트",
}

# Raspberry Pi 하드웨어 초기화
Gpio.setmode(Gpio.BCM)

Gpio.setup(4, Gpio.IN, pull_up_down=Gpio.PUD_DOWN)
Gpio.setup(17, Gpio.OUT)

buzzer_pwm = Gpio.PWM(17, 523)

buzzer_pwm.start(0)

stream = PiGear().start()

display = ssd1306(i2c(port=1, address=0x3C))

# 표준 출력 초기화
def callClear():
    system("cls || clear")


callClear()

tprint("Life Five Cuts")
print("인생다섯컷에 오신 것을 환영해요!")
print("© 2022 ISTP")

print("")

print("프레임 목록")
print(
    ", ".join(
        map(lambda item: "{0}: {1}".format(item[0], item[1]), frame_names_by_id.items())
    )
)

print("")

# 초기화함
try:
    # 프레임 선택
    frame_id = input("프레임 번호를 입력해주세요: ")
    if frame_id in frame_names_by_id:
        print("{0} 프레임을 선택하였어요".format(frame_names_by_id[frame_id]))
    else:
        print("안타깝지만, 프레임을 찾을 수 없어요.")

        # 오류 유발
        raise

    # 프레임 선택함
    frame_image_pil = Image.open("frames/{0}.png".format(frame_id))
    y_offset = 100

    callClear()

    # 사진 촬영 준비됨
    for i in range(5):
        tprint("{0}".format(i + 1))
        print("스위치를 누르면 3초 후 찰칵!")

        # 스위치 누를 때까지 카메라 사진을 디스플레이에 출력
        while Gpio.input(4) != 1:
            display.display(
                Image.fromarray(cvtColor(stream.read(), COLOR_BGR2RGB))
                .resize((128, 64))
                .convert(display.mode)
            )
            sleep(0.1)

        # 스위치 누름
        for j in reversed(range(3)):
            tprint("{0}...".format(j + 1))
            buzzer_pwm.ChangeDutyCycle(80)
            sleep(0.2)
            buzzer_pwm.ChangeDutyCycle(0)
            sleep(0.8)

        # 3초가 흐름
        buzzer_pwm.ChangeDutyCycle(80)
        image_cv2 = stream.read()
        image_pil = Image.fromarray(cvtColor(image_cv2, COLOR_BGR2RGB))
        frame_image_pil.paste(image_pil, (100, y_offset))

        # 사진을 붙여넣음
        callClear()
        to_terminal(from_image(image_pil))

        # 촬영 정리
        buzzer_pwm.ChangeDutyCycle(0)
        y_offset += 580

    # 5번 촬영함
    tprint("!")

    print("촬영 완료!")

    # 결과 사진 저장
    frame_image_pil.save("result.png", "PNG")

    print("사진 파일을 저장했어요!")

    # 사진 저장함
    with open("result.png", "rb") as file:
        response = post(
            "https://tmpfiles.org/api/v1/upload", files={"file": file}
        ).json()

        # 사진 업로드하였거나 실패함
        print(
            "사진을 업로드했어요! {0} 파일은 1시간 후에 삭제되니, 꼭 다운로드해 주세요.".format(
                response["data"]["url"]
            )
            if response["status"] == "success"
            else "안타깝지만, 사진 업로드에 실패했어요. 파일은 result.png에 있어요."
        )
except:
    pass
finally:
    # 프로그램 정리
    print("인생다섯컷을 이용해주셔서 고맙습니다.")

    buzzer_pwm.stop()

    Gpio.cleanup()

    try:
        stream.stop()
    except:
        pass
