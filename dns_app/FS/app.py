from flask import Flask, request
import socket

app = Flask(__name__)


def fibonacci(n):
    if n < 0:
        return None

    a, b = 0, 1

    for _ in range(n):
        a, b = b, a + b

    return a


@app.route("/register", methods=["PUT"])
def register():
    data = request.get_json(silent=True)

    if not data:
        return "Bad Request", 400

    hostname = data.get("hostname")
    ip = data.get("ip")
    as_ip = data.get("as_ip")
    as_port = data.get("as_port")

    if not all([hostname, ip, as_ip, as_port]):
        return "Bad Request", 400

    try:
        as_port = int(as_port)
    except ValueError:
        return "Bad Request", 400

    message = (
        f"TYPE=A\n"
        f"NAME={hostname} VALUE={ip} TTL=10"
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)

    try:
        sock.sendto(message.encode("utf-8"), (as_ip, as_port))
        sock.recvfrom(1024)
    except socket.timeout:
        return "Authoritative Server Timeout", 500
    finally:
        sock.close()

    return "Registered", 201


@app.route("/fibonacci", methods=["GET"])
def get_fibonacci():
    number = request.args.get("number")

    if number is None:
        return "Bad Request", 400

    try:
        number = int(number)
    except ValueError:
        return "Bad Request", 400

    result = fibonacci(number)

    if result is None:
        return "Bad Request", 400

    return str(result), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9090)
    