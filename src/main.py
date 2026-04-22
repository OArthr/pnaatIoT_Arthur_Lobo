from machine import Pin 
import time

print("Teste")
# ------------------ PINOS ------------------

# Pinos do shift register
data = Pin(19, Pin.OUT)   # envia os bits
clock = Pin(18, Pin.OUT)  # controla o deslocamento
latch = Pin(5, Pin.OUT)   # aplica os dados nas saídas

# Botão para trocar de modos
botao = Pin(13, Pin.IN, Pin.PULL_UP)

# Sensores PIR
sensores = [
  Pin(4, Pin.IN),
  Pin(16, Pin.IN),
  Pin(0, Pin.IN),
  Pin(2, Pin.IN)
]

# ------------------ CONSTANTES ------------------

# Estados do semáforo
OFF = 0
RED = 1
YELLOW = 2
GREEN = 3

# Controle de tempo
MIN_GREEN = 3      # tempo mínimo de verde
MAX_ADD = 5        # máximo de incrementos por sensor
INCREMENT = 1      # incremento por detecção
YELLOW_TIME = 2    # tempo do amarelo

MODOS = 4          # quantidade de modos de operação

# Buffer de 16 bits representando os LEDs
led_buffer = [0] * 16

# ------------------ CLASSE SEMÁFORO ------------------

class Semaforo:
  def __init__(self, red_bit, yellow_bit, green_bit):
    # Define quais posições no buffer controlam cada LED
    self.red_bit = red_bit
    self.yellow_bit = yellow_bit
    self.green_bit = green_bit
    self.state = OFF

  def set_state(self, state):
    # Atualiza o estado atual do semáforo
    self.state = state

  def apply(self, buffer):
    # Apaga os 3 LEDs do semáforo
    buffer[self.red_bit] = 0
    buffer[self.yellow_bit] = 0
    buffer[self.green_bit] = 0

    # Liga apenas o LED correspondente ao estado
    if self.state == RED:
      buffer[self.red_bit] = 1
    elif self.state == YELLOW:
      buffer[self.yellow_bit] = 1
    elif self.state == GREEN:
      buffer[self.green_bit] = 1
    elif self.state == OFF:
      pass  # nenhum LED ligado

# ------------------ SHIFT REGISTER ------------------

def shift_out(byte1, byte2):
  latch.off()

  # Envia primeiro o segundo registrador (encadeado)
  for byte in [byte2, byte1]:
    for i in range(8):
      bit = (byte >> (7 - i)) & 1  # extrai bit mais significativo
      data.value(bit)

      clock.on()   
      clock.off()

  latch.on()  
  latch.off()

def update_shift_register():
  byte1 = 0
  byte2 = 0

  # Converte os 16 bits do buffer em 2 bytes
  for i in range(8):
    byte1 |= (led_buffer[i] << i)

  for i in range(8, 16):
    byte2 |= (led_buffer[i] << (i - 8))

  shift_out(byte1, byte2)

def render():
  global led_buffer

  led_buffer = [0] * 16

  # Aplica estado de cada semáforo no buffer
  for s in semaforos:
    s.apply(led_buffer)

  update_shift_register()

# ------------------ SISTEMA PRINCIPAL ------------------

class SistemaSemaforo:
    def __init__(self, semaforos, sensores, botao, modos_config):
        self.semaforos = semaforos
        self.sensores = sensores
        self.botao = botao
        self.modos_config = modos_config

        self.tempo_ativo = [MIN_GREEN] * len(semaforos)
        self.adicoes = [0] * len(semaforos)
        self.tempo_amarelo = YELLOW_TIME

        self.modo = 0
        self.fase = 0  # índice dentro do modo

        self.last_press = 0

    # -------- BOTÃO --------
    def ler_botao(self):
        if not self.botao.value():
            agora = time.ticks_ms()
            if time.ticks_diff(agora, self.last_press) > 200:
                self.modo = (self.modo + 1) % len(self.modos_config)
                self.fase = 0  # reinicia ciclo do modo
                print("MODO:", self.modo)
                self.last_press = agora

    # -------- SENSORES --------
    def atualizar_tempos(self):
        for i in range(len(self.sensores)):
            if self.sensores[i].value() and self.adicoes[i] < MAX_ADD:
              self.tempo_ativo[i] += INCREMENT
              self.adicoes[i] += 1

    # -------- GRUPO ATUAL --------
    def grupo_atual(self):
        return self.modos_config[self.modo][self.fase]

    # -------- DESATIVA NÃO USADOS --------
    def aplicar_off(self):
        ativos_no_modo = set(sum(self.modos_config[self.modo], []))

        for i in range(len(self.semaforos)):
            if i not in ativos_no_modo:
                self.semaforos[i].set_state(OFF)

    # -------- PROXIMA FASE --------
    def proxima_fase(self):
        total_fases = len(self.modos_config[self.modo])
        self.fase = (self.fase + 1) % total_fases

    # -------- TEMPO DO GRUPO --------
    def tempo_grupo(self):
        # usa o maior tempo entre os semáforos do grupo
        return max([self.tempo_ativo[i] for i in self.grupo_atual()])

    # -------- RESET DO GRUPO --------
    def reset_grupo(self):
        for i in self.grupo_atual():
            self.tempo_ativo[i] = MIN_GREEN
            self.adicoes[i] = 0

    # -------- CICLO --------
    def atualizar_estado(self):
        # todos começam vermelhos
        for s in self.semaforos:
            s.set_state(RED)

        self.aplicar_off()

        # VERDE
        if self.tempo_grupo() > 0:
            for i in self.grupo_atual():
                self.semaforos[i].set_state(GREEN)
                self.tempo_ativo[i] -= 1

        # AMARELO
        elif self.tempo_amarelo > 0:
            for i in self.grupo_atual():
                self.semaforos[i].set_state(YELLOW)
            self.tempo_amarelo -= 1

        # TROCA DE FASE
        else:
            self.reset_grupo()
            self.tempo_amarelo = YELLOW_TIME
            self.proxima_fase()

    # -------- LOOP --------
    def loop(self):
        self.ler_botao()
        self.atualizar_tempos()
        self.atualizar_estado()
        render()

# ------------------ INICIALIZAÇÃO ------------------

s1 = Semaforo(0, 1, 2)
s2 = Semaforo(3, 4, 5)
s3 = Semaforo(6, 7, 8)
s4 = Semaforo(9, 10, 11)

semaforos = [s1, s2, s3, s4]

ModosConfig = {
  0: [[0],[1],[2],[3]],
  1: [[0,2],[1,3]],
  2: [[0],[2],[3]],
  3: [[0],[1]]
}

sistema = SistemaSemaforo(semaforos, sensores, botao, ModosConfig)

# ------------------ LOOP PRINCIPAL ------------------

while True:
    sistema.loop()
    print(sistema.tempo_ativo)
    time.sleep(1)
