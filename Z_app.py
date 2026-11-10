from flask import Flask, request, jsonify
import subprocess
import requests as req_lib
from markupsafe import escape

app = Flask(__name__)

@app.route("/")
def hello():
    name = escape(request.args.get("name", "человек"))
    old = request.args.get("old", 0)
    try:
        if float(old)<18:
            return f"Приветствую тебя, {name}!<br>Хе-хе, ты слишком мал для этого сайта...<br>Возвращайся, когда подрастёшь)<br>Однако, ты можешь воспользоваться некоторыми функциями сайта: /ping или /fetch."
        else:
            return f"Приветствую тебя, {name}!<br>Я ждал этого момента 4... Нет, 5 тысяч лет!<br>Однако, ты можешь воспользоваться некоторыми функциями сайта: /ping или /fetch."
    except:
        return f"Приветствую тебя, {name}!<br>Ты ввёл кхм-кхм... нехорошие значения.<br>Недостойные этого сайта...<br>Попробуй исправиться)<br>Однако, ты можешь воспользоваться некоторыми функциями сайта: /ping или /fetch."
# Уязвимость 1: Command Injection
@app.route('/ping')
def ping():
    host = request.args.get('host', '127.0.0.1')
    
    # ОПАСНО: прямая подстановка в shell-команду
    cmd = f"ping -c 2 {host}"
    try:
        # shell=True — ключевой фактор уязвимости
        result = subprocess.check_output(cmd, shell=True, universal_newlines=True, timeout=5)
        return jsonify({"output": result})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "timeout"}), 504
 
# Уязвимость 2: SSRF
@app.route('/fetch')
def fetch():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "url is required"}), 400
    
    # ОПАСНО: сервер делает запрос по любому URL от клиента
    try:
        r = req_lib.get(url, timeout=5)
        return jsonify({
            "status": r.status_code,
            "content": r.text[:500]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
if __name__ == '__main__':
    # ВНИМАНИЕ: запускать ТОЛЬКО в Docker/VM из-за Command Injection
    app.run(host='0.0.0.0', port=5000, debug=False)
