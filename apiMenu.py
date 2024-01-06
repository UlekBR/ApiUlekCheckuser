
import os
import subprocess
import sys
import socket
import urllib.request
import json

cor_vermelha = "\033[91m"
cor_verde = "\033[92m"
cor_amarela = "\033[93m"
cor_azul = "\033[94m"
cor_reset = "\033[0m"

def adicionar_ao_cache(chave, valor):
    cache = carregar_cache()  
    cache[chave] = valor
    salvar_cache(cache)  

def remover_do_cache(chave):
    cache = carregar_cache()  
    if chave in cache:
        del cache[chave]
        salvar_cache(cache) 

def obter_do_cache(chave):
    cache = carregar_cache()  
    return cache.get(chave)

def carregar_cache():
    try:
        with open('/root/ApiUlekCheckuser/cache.json', 'r') as arquivo:
            return json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {} 
    
def salvar_cache(cache):
    with open('/root/ApiUlekCheckuser/cache.json', 'w') as arquivo:
        json.dump(cache, arquivo)


def get_public_ip():
    try:
        url = "https://ipinfo.io"
        response = urllib.request.urlopen(url)
        if response.status == 200:
            data = json.loads(response.read().decode("utf-8"))
            if 'ip' in data:
                return data['ip']
            else:
                print("Endereço IP público não encontrado na resposta.")
                return None
        else:
            print("Falha na solicitação ao servidor.")
            return None
    except Exception as e:
        print("Não foi possível obter o endereço IP público:", str(e))
        return None




def verificar_processo(nome_processo):
    try:
        resultado = subprocess.check_output(["ps", "aux"]).decode()
        linhas = resultado.split('\n')
        for linha in linhas:
            if nome_processo in linha and "python" in linha:
                return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao verificar o processo: {e}")
    return False


nome_do_script = "/root/ApiUlekCheckuser/api.py"




if __name__ == "__main__":
    while True:
        os.system('clear')


        if verificar_processo(nome_do_script):
            status = f'{cor_verde}ativo{cor_reset} - porta em uso: {obter_do_cache("porta")}'
        else:
            status = f'{cor_vermelha}parado{cor_reset} - porta que será usada: {obter_do_cache("porta")}'
       
        print(f"Status: {status}")

        print(f"")

        print(f"Selecione uma opção:")
        print(f" 1 - Iniciar api")
        print(f" 2 - Parar api")
        print(f" 3 - Sobre")
        print(f" 0 - Sair do menu")

        option = input("Digite a opção: ")

        if option == "1":

            print(f"Observação: Para funcionar com security apenas se usar a porta 5454 !")
            
            adicionar_ao_cache('porta', input("\nDigite a porta que deseja usar !"))

            os.system('clear')
            print(f'Porta escolhida: {obter_do_cache("porta")}')

            os.system(f'nohup python3 {nome_do_script} --port {obter_do_cache("porta")} & ')

            input(f"\nPressione a tecla enter para voltar ao menu\n\n")
        elif option == "2":
            if verificar_processo(nome_do_script):

                try:
                    subprocess.run(f'pkill -9 -f "/root/UlekCheckUser/checkuser.py"', shell=True)

                        
                except subprocess.CalledProcessError:
                    print("Erro ao executar o comando.")
                remover_do_cache("porta")
            else: 
                print("O Checkuser não está ativo.")
            


            input(f"Pressione a tecla enter para voltar ao menu")

        elif option == "3":
            os.system('clear')
            print(f"Olá, esse é uma api para o multi-checkuser criado por @UlekBR")
            input(f"Pressione a tecla enter para voltar ao menu")
        elif option == "0":
            sys.exit(0)
        else:
            os.system('clear')
            print(f"Selecionado uma opção invalida, tente novamente !")
            input(f"Pressione a tecla enter para voltar ao menu")
