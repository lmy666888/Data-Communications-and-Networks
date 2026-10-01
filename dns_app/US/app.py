from flask import Flask, request
import socket
import requests

app = Flask(__name__)


def parse_dns_response(message):
    fields = {}

    for line in message.strip().splitlines():
        for item in line.split():
            if "=" in item:
                key, value = item.split("=", 1)
                fields[key] = value

    return fields


@app.route("/fibonacci", methods=["GET"])
def fibonacci():
    hostname = request.args.get("hostname")
    fs_port = request.args.get("fs_port")
    number = request.args.get("number")
    as_ip = request.args.get("as_ip")
    as_port = request.args.get("as_port")

    if not all([hostname, fs_port, number, as_ip, as_port]):
        return "Bad Request", 400

    try:
        fs_port = int(fs_port)
        as_port = int(as_port)
        int(number)
    except ValueError:
        return "Bad Request", 400

    dns_query = (
        f"TYPE=A\n"
        f"NAME={hostname}"
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)

    try:
        sock.sendto(
            dns_query.encode("utf-8"),
            (as_ip, as_port)
        )

        data, _ = sock.recvfrom(1024)

    except socket.timeout:
        return "Authoritative Server Timeout", 500

    finally:
        sock.close()

    dns_response = data.decode("utf-8")

    if dns_response.startswith("ERROR="):
        return "DNS Record Not Found", 404

    fields = parse_dns_response(dns_response)
    fs_ip = fields.get("VALUE")

    if not fs_ip:
        return "Invalid DNS Response", 500

    fs_url = (
        f"http://{fs_ip}:{fs_port}/fibonacci"
        f"?number={number}"
    )

    try:
        response = requests.get(fs_url, timeout=3)
    except requests.RequestException:
        return "Fibonacci Server Error", 500

    return response.text, response.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)