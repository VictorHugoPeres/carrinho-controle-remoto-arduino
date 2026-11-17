/**
 * ============================================================================
 * Projeto: Carrinho de Controle Remoto via Rádio 2.4GHz
 * Arquivo: carrinho_receptor.ino
 * Descrição: Firmware do nó receptor embarcado no veículo. Recebe comandos
 *            via rádio NRF24L01 e comanda a ponte H L298N para tração diferencial.
 * ============================================================================
 */

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

/* ============================================================================
 * MAPEAMENTO DE PINOS - NRF24L01 (Interface SPI)
 * ============================================================================
 * VCC  -> 3.3V do Arduino (ATENÇÃO: Não conectar aos 5V)
 * GND  -> GND do Arduino (comum com bateria e L298N)
 * CE   -> D7
 * CSN  -> D8
 * SCK  -> D13
 * MOSI -> D11
 * MISO -> D12
 */
const uint8_t PINO_CE  = 7;
const uint8_t PINO_CSN = 8;
RF24 radio(PINO_CE, PINO_CSN);

// Endereço de comunicação do pipe RF (deve ser idêntico ao do transmissor)
const byte ENDERECO_PIPE[6] = "00001";

/* ============================================================================
 * MAPEAMENTO DE PINOS - PONTE H L298N (Controle de Direção dos Motores)
 * ============================================================================
 * IN1  -> D3 (Motor Esquerdo - Sentido Horário / Frente)
 * IN2  -> D5 (Motor Esquerdo - Sentido Anti-horário / Ré)
 * IN3  -> D6 (Motor Direito  - Sentido Horário / Frente)
 * IN4  -> D9 (Motor Direito  - Sentido Anti-horário / Ré)
 * ENA  -> Jumper ativo (5V fixo para velocidade plena)
 * ENB  -> Jumper ativo (5V fixo para velocidade plena)
 */
const uint8_t PIN_IN1 = 3;
const uint8_t PIN_IN2 = 5;
const uint8_t PIN_IN3 = 6;
const uint8_t PIN_IN4 = 9;

/**
 * @brief Interrompe imediatamente o acionamento de todos os motores.
 */
void pararMotores() {
  digitalWrite(PIN_IN1, LOW);
  digitalWrite(PIN_IN2, LOW);
  digitalWrite(PIN_IN3, LOW);
  digitalWrite(PIN_IN4, LOW);
}

/**
 * @brief Aciona ambos os motores para avanço frontal.
 */
void moverFrente() {
  digitalWrite(PIN_IN1, HIGH);
  digitalWrite(PIN_IN2, LOW);
  digitalWrite(PIN_IN3, HIGH);
  digitalWrite(PIN_IN4, LOW);
}

/**
 * @brief Aciona ambos os motores para deslocamento em marcha à ré.
 */
void moverRe() {
  digitalWrite(PIN_IN1, LOW);
  digitalWrite(PIN_IN2, HIGH);
  digitalWrite(PIN_IN3, LOW);
  digitalWrite(PIN_IN4, HIGH);
}

/**
 * @brief Executa giro à esquerda com tração diferencial.
 */
void virarEsquerda() {
  digitalWrite(PIN_IN1, LOW);
  digitalWrite(PIN_IN2, LOW);
  digitalWrite(PIN_IN3, HIGH);
  digitalWrite(PIN_IN4, LOW);
}

/**
 * @brief Executa giro à direita com tração diferencial.
 */
void virarDireita() {
  digitalWrite(PIN_IN1, HIGH);
  digitalWrite(PIN_IN2, LOW);
  digitalWrite(PIN_IN3, LOW);
  digitalWrite(PIN_IN4, LOW);
}

void setup() {
  Serial.begin(9600);
  Serial.println(F("[STATUS] Inicializando sistema receptor embarcado..."));

  // Configuração dos pinos de acionamento dos motores
  pinMode(PIN_IN1, OUTPUT);
  pinMode(PIN_IN2, OUTPUT);
  pinMode(PIN_IN3, OUTPUT);
  pinMode(PIN_IN4, OUTPUT);
  pararMotores();

  // Autoteste preventivo dos atuadores (1 segundo)
  Serial.println(F("[STATUS] Executando autoteste dos motores..."));
  moverFrente();
  delay(1000);
  pararMotores();
  Serial.println(F("[STATUS] Autoteste finalizado com sucesso."));

  // Inicialização do módulo de radiofrequência NRF24L01
  if (!radio.begin()) {
    Serial.println(F("[ERRO] Falha ao comunicar com o modulo NRF24L01. Verifique conexoes e alimentacao."));
    while (true) {
      // Bloqueio de segurança em caso de falha de hardware
    }
  }

  radio.openReadingPipe(0, ENDERECO_PIPE);
  radio.setPALevel(RF24_PA_LOW);
  radio.startListening();

  Serial.println(F("[STATUS] Modulo NRF24L01 pronto. Aguardando comandos..."));
}

void loop() {
  if (radio.available()) {
    char comando = ' ';
    radio.read(&comando, sizeof(comando));

    switch (comando) {
      case 'W': // Frente
        moverFrente();
        break;

      case 'S': // Ré
        moverRe();
        break;

      case 'A': // Esquerda
        virarEsquerda();
        break;

      case 'D': // Direita
        virarDireita();
        break;

      case 'X': // Parar
        pararMotores();
        break;

      default:
        // Ignora caracteres não mapeados
        break;
    }
  }
}
