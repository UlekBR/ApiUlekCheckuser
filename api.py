import os
import argparse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import socket
import re


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



class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Extract username from the path
        parsed_path = urlparse(self.path)
        path_segments = parsed_path.path.split('/')
        username = path_segments[-1].split('user=')[1]

        # Get user information
        user_info = self.get_user_info(username)

        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(user_info.encode())

    def get_user_info(self, username):
        try:
            user_exists = int(runCommand(f"/bin/grep -wc {username} /etc/passwd")) != 0

            if user_exists:
                expiration_date = runCommand(f"chage -l {username} | grep -i co | awk -F : '{{print $2}}'")
                formatted_expiration_date = datetime.strptime(expiration_date, '%b %d, %Y').strftime('%d/%m/%Y')
                formatted_expiration_date_for_anymod = format_date_for_anymod(formatted_expiration_date)

                limit = 0

                if os.path.exists("/root/usuarios.db"): 
                    limit = runCommand(f"grep -w {username} /root/usuarios.db | cut -d' ' -f2 | head -n 1") 
                elif os.path.exists("/opt/DragonCore"): 
                    limit = runCommand('php /opt/DragonCore/menu.php printlim | awk \'/' + username +'/ {print $3}\'') 
                else: limit = 999

                ssh_connections = runCommand(f"ps -u {username}  | grep sshd | wc -l")

                days = days_difference(formatted_expiration_date)

                user_info = (
                    '{'
                    '"username": "%s",'
                    '"user_connected": "%s",'
                    '"user_limit": "%s",'
                    '"expiration_date": "%s",'
                    '"formatted_expiration_date": "%s",'
                    '"formatted_expiration_date_for_anymod": "%s",'
                    '"remaining_days": "%s"'
                    '}'
                ) % (username, ssh_connections, limit, expiration_date, formatted_expiration_date, formatted_expiration_date_for_anymod, days)

                return user_info
            else:
                return f"O Usuario [{username}] não foi encontrado"

        except Exception as e:
            return str(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ApiCheckuser")
    parser.add_argument('--port', type=int, default=8080, help="Porta do servidor (padrão: 8080)")
    args = parser.parse_args()

    port = args.port
    server_address = ('0.0.0.0', port)  # Change this line to listen on all available network interfaces
    
    httpd = HTTPServer(server_address, MyRequestHandler)
    print(f"Servidor rodando na porta {port} e acessível em http://0.0.0.0:{port}")
    httpd.serve_forever()