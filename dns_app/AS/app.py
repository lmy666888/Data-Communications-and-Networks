import json
import os
import socket

HOST = "0.0.0.0"
PORT = 53533
RECORD_FILE = "records.json"


def load_records():
    if not os.path.exists(RECORD_FILE):
        return {}

    with open(RECORD_FILE, "r") as file:
        return json.load(file)


def save_records(records):
    with open(RECORD_FILE, "w") as file:
        json.dump(records, file, indent=2)


def parse_message(message):
    fields = {}

    for line in message.strip().splitlines():
        for item in line.split():
            if "=" in item:
                key, value = item.split("=", 1)
                fields[key] = value

    return fields


def main():
    records = load_records()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))

    print(f"Authoritative Server listening on UDP port {PORT}")

    while True:
        data, client_address = sock.recvfrom(1024)

        message = data.decode("utf-8").strip()

        print(f"\nReceived from {client_address}:")
        print(message)

        fields = parse_message(message)

        record_type = fields.get("TYPE")
        name = fields.get("NAME")
        value = fields.get("VALUE")
        ttl = fields.get("TTL", "10")

        if record_type != "A" or not name:
            response = "ERROR=INVALID_REQUEST"
            sock.sendto(response.encode("utf-8"), client_address)
            continue

        # Registration request
        if value:
            records[name] = {
                "value": value,
                "type": record_type,
                "ttl": ttl,
            }

            save_records(records)

            response = (
                f"TYPE={record_type}\n"
                f"NAME={name} VALUE={value} TTL={ttl}"
            )

            print(f"Registered {name} -> {value}")
            sock.sendto(response.encode("utf-8"), client_address)

        # DNS query
        else:
            record = records.get(name)

            if record is None:
                response = "ERROR=NOT_FOUND"
            else:
                response = (
                    f"TYPE={record['type']}\n"
                    f"NAME={name} VALUE={record['value']} TTL={record['ttl']}"
                )

            print("Sending response:")
            print(response)

            sock.sendto(response.encode("utf-8"), client_address)


if __name__ == "__main__":
    main()