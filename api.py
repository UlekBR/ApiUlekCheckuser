import os
import argparse
from datetime import datetime

from flask import Flask, jsonify

app = Flask(__name__)


def runCommand(command):
    return os.popen(command).read().strip()

def days_difference(date_string):
    date_object = datetime.strptime(date_string, '%d/%m/%Y')
    today = datetime.now()
    difference = today - date_object
    days_difference = abs(difference.days)

    return days_difference

def format_date_for_anymod(date_string):
    date = datetime.strptime(date_string, "%d/%m/%Y")
    formatted_date = date.strftime("%Y-%m-%d-")
    return formatted_date

@app.route('/user=<username>', methods=['GET'])
def get_user_info(username):
    try:

        user_exists = int(runCommand(f"/bin/grep -wc {username} /etc/passwd")) != 0

        if user_exists:
            expiration_date = runCommand(f"chage -l {username} | grep -i co | awk -F : '{{print $2}}'")
            formatted_expiration_date = datetime.strptime(expiration_date, '%b %d, %Y').strftime('%d/%m/%Y')
            formatted_expiration_date_for_anymod = format_date_for_anymod(formatted_expiration_date)

            limit = runCommand(f"grep -w {username} /root/usuarios.db | cut -d' ' -f2 | head -n 1")

            ssh_connections = runCommand(f"ps -u {username}  | grep sshd | wc -l")

            days = days_difference(formatted_expiration_date)

            user_info = {
                "username": username,
                "user_connected": ssh_connections,
                "user_limit": limit,
                "expiration_date": expiration_date,
                "formatted_expiration_date": formatted_expiration_date,
                "formatted_expiration_date_for_anymod": formatted_expiration_date_for_anymod,
                "remaining_days": days
            }

            return jsonify(user_info), 200
        else:
            return f"O Usuario [{username}] não foi encontrado", 200

    except Exception as e:
        return str(e), 500 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ApiCheckuser")
    parser.add_argument('--port', type=int, default=5555, help="Porta do servidor (padrão: 5555)")
    args = parser.parse_args()

    porta = args.port
    app.run(host="0.0.0.0", port=porta)
