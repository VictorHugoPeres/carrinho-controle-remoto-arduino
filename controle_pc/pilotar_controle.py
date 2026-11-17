"""
============================================================================
Projeto: Carrinho de Controle Remoto via Rádio 2.4GHz
Arquivo: pilotar_controle.py
Descrição: Interface de controle via Joystick/Gamepad utilizando Pygame.
           Lê as entradas dos eixos analógicos e envia os comandos seriais
           correspondentes ao Arduino Transmissor.
============================================================================
"""

import os
import sys
import time
import serial
import serial.tools.list_ports
import pygame

# ============================================================================
# PARÂMETROS DE CONFIGURAÇÃO
# ============================================================================
PORTA_COM_PADRAO = "COM3"
BAUD_RATE = 9600
DEADZONE = 0.4
INTERVALO_AMOSTRAGEM = 0.05  # 50 ms


def listar_portas_disponiveis() -> list[str]:
    """Retorna uma lista com os identificadores das portas seriais disponíveis."""
    return [porta.device for porta in serial.tools.list_ports.comports()]


def conectar_serial(porta: str, taxa: int) -> serial.Serial:
    """
    Inicializa a conexão serial com o Arduino Transmissor.
    
    :param porta: Identificador da porta serial (ex.: 'COM3').
    :param taxa: Taxa de transmissão em baud (ex.: 9600).
    :return: Instância de serial.Serial configurada.
    """
    try:
        conexao = serial.Serial(porta, taxa, timeout=0.1)
        time.sleep(2.0)  # Aguarda estabilização do bootloader do Arduino
        return conexao
    except serial.SerialException as erro:
        portas_ativas = listar_portas_disponiveis()
        print(f"[ERRO] Não foi possível estabelecer conexão na porta '{porta}': {erro}")
        if portas_ativas:
            print(f"[INFO] Portas seriais ativas no sistema: {', '.join(portas_ativas)}")
        else:
            print("[INFO] Nenhuma porta serial detectada. Verifique a conexão do cabo USB.")
        print("[DICA] Certifique-se de que o Monitor Serial da Arduino IDE ou outra aplicação esteja fechada.")
        sys.exit(1)


def inicializar_joystick() -> pygame.joystick.Joystick:
    """
    Inicializa o subsistema de joystick do Pygame e conecta ao primeiro dispositivo.
    
    :return: Objeto do joystick inicializado.
    """
    # Suprime mensagens informativas automáticas do Pygame no console
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    pygame.init()
    pygame.joystick.init()

    total_dispositivos = pygame.joystick.get_count()
    if total_dispositivos == 0:
        print("[ERRO] Nenhum controle/joystick detectado pelo sistema.")
        print("[INFO] Conecte um controle compatível via USB ou Bluetooth e tente novamente.")
        pygame.quit()
        sys.exit(1)

    dispositivo = pygame.joystick.Joystick(0)
    dispositivo.init()
    return dispositivo


def main() -> None:
    porta_com = PORTA_COM_PADRAO
    if len(sys.argv) > 1:
        porta_com = sys.argv[1].strip()

    print("====================================================================")
    print("           CENTRAL DE PILOTAGEM - CONTROLE DE VIDEOGAME            ")
    print("====================================================================")
    print(f"[STATUS] Conectando à porta serial {porta_com} a {BAUD_RATE} baud...")
    arduino = conectar_serial(porta_com, BAUD_RATE)
    print(f"[STATUS] Conexão serial estabelecida com sucesso na porta {porta_com}.")

    joystick = inicializar_joystick()
    nome_controle = joystick.get_name()
    print(f"[STATUS] Dispositivo detectado: {nome_controle}")
    print("[STATUS] Pilotagem iniciada. Utilize o analógico esquerdo para condução.")
    print("[INFO] Pressione [Ctrl + C] para encerrar a sessão de forma segura.\n")

    ultimo_comando = "X"

    try:
        while True:
            pygame.event.pump()

            try:
                eixo_y = joystick.get_axis(1)  # Vertical (negativo = frente, positivo = ré)
                eixo_x = joystick.get_axis(0)  # Horizontal (negativo = esquerda, positivo = direita)
            except pygame.error as erro_pad:
                print(f"[AVISO] Falha de comunicação com o controle: {erro_pad}")
                break

            comando_atual = "X"

            # Priorização de comandos baseada na zona morta
            if eixo_y < -DEADZONE:
                comando_atual = "W"  # Avanço frontal
            elif eixo_y > DEADZONE:
                comando_atual = "S"  # Marcha à ré
            elif eixo_x < -DEADZONE:
                comando_atual = "A"  # Giro à esquerda
            elif eixo_x > DEADZONE:
                comando_atual = "D"  # Giro à direita

            # Transmissão serial mediante alteração de estado
            if comando_atual != ultimo_comando:
                arduino.write(comando_atual.encode("ascii"))
                descricao = {
                    "W": "FRENTE",
                    "S": "RÉ",
                    "A": "ESQUERDA",
                    "D": "DIREITA",
                    "X": "PARAR",
                }.get(comando_atual, "DESCONHECIDO")
                print(f"[COMANDO] {comando_atual} -> {descricao}")
                ultimo_comando = comando_atual

            time.sleep(INTERVALO_AMOSTRAGEM)

    except KeyboardInterrupt:
        print("\n[STATUS] Interrupção solicitada pelo usuário.")
    except Exception as erro_geral:
        print(f"\n[ERRO] Ocorreu uma exceção não prevista durante a execução: {erro_geral}")
    finally:
        print("[STATUS] Enviando comando de parada de segurança ('X')...")
        try:
            if arduino.is_open:
                arduino.write(b"X")
                time.sleep(0.1)
                arduino.close()
        except Exception:
            pass

        pygame.quit()
        print("[STATUS] Sessão de controle finalizada com segurança.")


if __name__ == "__main__":
    main()
