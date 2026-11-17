"""
============================================================================
Projeto: Carrinho de Controle Remoto via Rádio 2.4GHz
Arquivo: pilotar_terminal.py
Descrição: Interface de controle direto via teclado no terminal.
           Permite ao operador enviar comandos seriais de navegação
           ('W', 'S', 'A', 'D', 'X') ao Arduino Transmissor em tempo real.
============================================================================
"""

import sys
import time
import serial
import serial.tools.list_ports

# ============================================================================
# PARÂMETROS DE CONFIGURAÇÃO
# ============================================================================
PORTA_COM_PADRAO = "COM3"
BAUD_RATE = 9600

MAPA_COMANDOS = {
    "W": "AVANÇO FRONTAL",
    "S": "MARCHA À RÉ",
    "A": "GIRO À ESQUERDA",
    "D": "GIRO À DIREITA",
    "X": "PARADA DE SEGURANÇA",
}


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
        time.sleep(2.0)  # Aguarda reinicialização do Arduino via DTR
        return conexao
    except serial.SerialException as erro:
        portas_ativas = listar_portas_disponiveis()
        print(f"[ERRO] Falha ao conectar à porta '{porta}': {erro}")
        if portas_ativas:
            print(f"[INFO] Portas seriais identificadas: {', '.join(portas_ativas)}")
        else:
            print("[INFO] Nenhuma porta serial detectada no sistema.")
        print("[DICA] Certifique-se de fechar o Monitor Serial da Arduino IDE ou outros terminais.")
        sys.exit(1)


def capturar_caractere() -> str:
    """
    Captura um único caractere do teclado sem necessidade de pressionar Enter (se compatível).
    """
    try:
        import msvcrt  # Específico para ambiente Windows
        tecla_bytes = msvcrt.getch()
        try:
            return tecla_bytes.decode("utf-8").upper()
        except UnicodeDecodeError:
            return ""
    except ImportError:
        # Fallback para ambientes POSIX / padrão
        entrada = input("Digite o comando e pressione Enter: ").strip().upper()
        return entrada[:1] if entrada else ""


def exibir_painel_instrucoes(porta: str) -> None:
    """Exibe no console a tabela de comandos disponíveis para o operador."""
    print("====================================================================")
    print("              CENTRAL DE PILOTAGEM - TERMINAL SERIAL                ")
    print("====================================================================")
    print(f" Porta Conectada: {porta} | Baud Rate: {BAUD_RATE}")
    print("--------------------------------------------------------------------")
    print("  [W] Avançar (Frente)        |  [S] Recuar (Ré)")
    print("  [A] Virar à Esquerda        |  [D] Virar à Direita")
    print("  [X] Parar Motores           |  [Q] Encerrar Sessão")
    print("====================================================================")
    print(" [MODO EM TEMPO REAL] Pressione as teclas para manobrar o veículo.\n")


def main() -> None:
    porta_com = PORTA_COM_PADRAO
    if len(sys.argv) > 1:
        porta_com = sys.argv[1].strip()

    print(f"[STATUS] Inicializando conexão na porta serial {porta_com}...")
    arduino = conectar_serial(porta_com, BAUD_RATE)
    print(f"[STATUS] Conexão estabelecida com sucesso.")

    exibir_painel_instrucoes(porta_com)

    try:
        while True:
            tecla = capturar_caractere()

            if not tecla:
                continue

            if tecla == "Q":
                print("\n[STATUS] Finalização manual solicitada pelo operador.")
                break

            if tecla in MAPA_COMANDOS:
                arduino.write(tecla.encode("ascii"))
                descricao = MAPA_COMANDOS[tecla]
                print(f"[COMANDO ENVIADO] {tecla} -> {descricao}")
            else:
                print(f"[AVISO] Tecla '{tecla}' não mapeada. Utilize W, S, A, D, X ou Q.")

    except KeyboardInterrupt:
        print("\n[STATUS] Interrupção detectada (Ctrl + C).")
    except Exception as erro:
        print(f"\n[ERRO] Falha durante a operação do terminal: {erro}")
    finally:
        print("[STATUS] Transmitindo comando de parada ('X')...")
        try:
            if arduino.is_open:
                arduino.write(b"X")
                time.sleep(0.1)
                arduino.close()
        except Exception:
            pass
        print("[STATUS] Porta serial desconectada. Sessão finalizada.")


if __name__ == "__main__":
    main()
