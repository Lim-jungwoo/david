from flask import Flask, request, Response, render_template
import os
from io import BytesIO
from gtts import gTTS
from gtts.lang import tts_langs
import socket

DEFAULT_LANG = 'ko'
app = Flask(__name__)

def is_valid_lang(lang):
    return lang in tts_langs()

@app.route("/", methods=["GET", "POST"])
def home():
    error = None
    audio = None
    if request.method == "POST":
        try:
            text = request.form.get("input_text", "")
            lang = request.form.get("lang", DEFAULT_LANG)

            # 입력 내역 로그 저장
            with open("input_log.txt", "a", encoding="utf-8") as log_file:
                from datetime import datetime
                log_file.write(f"[{datetime.now()}] text: {text}, lang: {lang}\n")

            if not is_valid_lang(lang):
                raise ValueError(f"지원하지 않는 언어: {lang}. 지원되는 언어: {', '.join(tts_langs().keys())}")
            if not text.strip():
                raise ValueError("빈 텍스트 입력")

            fp = BytesIO()
            try:
                gTTS(text, lang=lang).write_to_fp(fp)
            except Exception as gtts_err:
                error = f"gTTS 변환 실패: {gtts_err}"
                fp = None
            if fp and fp.getvalue():
                import base64
                audio = base64.b64encode(fp.getvalue()).decode("utf-8")
        except Exception as e:
            if not error:
                error = str(e)
    download_url = None
    if audio:
        download_url = f"data:audio/mpeg;base64,{audio}"

    if app.debug:
        hostname = '컴퓨터(인스턴스):' + socket.gethostname()
    else:
        hostname = ''

    return render_template("index.html", error=error, audio=audio, download_url=download_url, computername=hostname)

@app.route("/menu")
def menu():
    return render_template("menu.html")

if __name__ == '__main__':
    print('디버그 모드: ' + ('True' if __debug__ == True else 'False'))
    app.run('0.0.0.0', 80, debug=True)
    # app.run('0.0.0.0', 80, debug=__debug__)
