/**
 * ============================================================================
 * Projeto: Carrinho de Controle Remoto via Rádio 2.4GHz
 * Arquivo: pc_transmissor.ino
 * Descrição: Firmware do nó transmissor conectado ao computador via USB/Serial.
 *            Recebe comandos do host e os transmite via rádio NRF24L01 ao receptor.
 * ============================================================================
 */

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

/* ============================================================================
 * MAPEAMENTO DE PINOS - NRF24L01 (Interface SPI)
 * ============================================================================
 * VCC  -> 3.3V do Arduino (ATENÇÃO: Não conectar aos 5V)
 * GND  -> GND do Arduino
 * CE   -> D7
 * CSN  -> D8
 * SCK  -> D13
 * MOSI -> D11
 * MISO -> D12
 */
const uint8_t PINO_CE  = 7;
const uint8_t PINO_CSN = 8;
RF24 radio(PINO_CE, PINO_CSN);

// Endereço de comunicação do pipe RF (deve ser idêntico ao do receptor)
const byte ENDERECO_PIPE[6] = "00001";

void setup() {
  Serial.begin(9600);
  Serial.println(F("[STATUS] Inicializando transmissor NRF24L01..."));

  // Inicialização do módulo de radiofrequência NRF24L01
  if (!radio.begin()) {
    Serial.println(F("[ERRO] Modulo NRF24L01 nao detectado. Verifique a pinagem e alimentacao 3.3V."));
    while (true) {
      // Bloqueio de segurança em caso de falha de hardware
    }
  }

  radio.openWritingPipe(ENDERECO_PIPE);
  radio.setPALevel(RF24_PA_LOW);
  radio.stopListening(); // Coloca o rádio em modo de transmissão contínua

  Serial.println(F("[STATUS] Transmissor pronto. Aguardando dados via porta serial (9600 baud)..."));
}

void loop() {
  if (Serial.available() > 0) {
    char comando = Serial.read();

    // Filtra caracteres de quebra de linha e retorno de carro
    if (comando != '\n' && comando != '\r') {
      comando = toupper(comando);

      // Transmite o comando ao receptor via RF
      radio.write(&comando, sizeof(comando));
    }
  }
}
