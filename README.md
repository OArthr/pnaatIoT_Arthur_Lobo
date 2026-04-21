# Sistema de Semáforo Inteligente com ESP32 (MicroPython)

## 👤 Identificação do Candidato

- **Nome completo:** Arthur Lobo Feitosa de Oliveira
- **GitHub:** [OArthr](https://github.com/OArthr)


## 1️⃣ Visão Geral da Solução

Este projeto simula um **cruzamento inteligente de trânsito** utilizando um ESP32 no ambiente Wokwi.

O objetivo é criar um sistema embarcado capaz de:

* Controlar **4 semáforos (12 LEDs)** via shift registers
* Adaptar o tempo de abertura com base em **sensores de movimento (PIR)**
* Permitir múltiplos modos de operação através de um **botão**

### Interação do usuário

* Pressionar o botão alterna entre diferentes modos de operação (segurar por ~1s para reconhecer)
* Sensores PIR simulam presença de veículos, influenciando o tempo dos semáforos (Sensor adjacente de seu respectivo semáforo)


## 2️⃣ Arquitetura do Sistema Embarcado

O sistema segue uma arquitetura modular baseada em:

### Estrutura lógica

* **Classe `Semaforo`**

  * Representa um semáforo individual
  * Controla estados: RED, YELLOW, GREEN, OFF

* **Classe `SistemaSemaforo`**

  * Gerencia todo o sistema
  * Controla modos, fases e tempos adaptativos

### Modos de funcionamento

Cada modo define a sequência dos semáforos, permitindo:
- Sincronizar multiplos semáforos
- Remover determinado semáforo do ciclo, desativando ele.

```text
Modo 0 → [ [0], [1], [2], [3] ]
Modo 1 → [ [0,2], [1,3] ]
Modo 2 → [ [0], [1], [2] ]
Modo 3 → [ [0], [1] ]
```

### Comunicação com hardware

* Buffer de 16 bits representa os LEDs
* Função `shift_out()` envia os dados para os registradores
* Função `render()` atualiza o estado físico dos LEDs


## 3️⃣ Componentes Utilizados na Simulação

### Plataforma

* ESP32

### Saídas

* 12 LEDs (4 semáforos × 3 cores)
* 2x 74HC595 (em sequência)

### Entradas

* 4 sensores PIR (movimento)
* 1 botão (troca de modo)

### Função dos componentes

- **ESP32** : Controle principal         
- **Shift Register** : Expansão de saídas digitais
- **LEDs** : Representação dos semáforos
- **PIR** : Detecção de tráfego        
- **Botão** : Alternância de modos       


## 4️⃣ Decisões Técnicas Relevantes

### Organização do código

* Uso de **orientação a objetos**
* Separação entre:

  * lógica de controle
  * hardware
  * renderização

### Controle por configuração

Uso de um dicionário:

```python
ModosConfig = {
  0: [[0],[1],[2],[3]],
  1: [[0,2],[1,3]],
  2: [[0],[1],[2]],
  3: [[0],[1]]
}
```

Permite criar novos modos sem alterar a lógica interna

### Temporização

* Baseada em `time.sleep(1)` (simulação em passos de 1 segundo)
* Controle de fases:

  * Verde (dinâmico)
  * Amarelo (fixo)

### Lógica adaptativa

* Sensores aumentam tempo de verde (`INCREMENT`)
* Limite de crescimento (`MAX_ADD`)
* Mantém tempo mínimo com pouco movimento

### Tratamento de botão

* Debounce via `time.ticks_ms()`
* Evita múltiplos acionamentos indesejados


## 5️⃣ Resultados Obtidos

### Funcionalidades implementadas

* Controle de 12 LEDs com apenas 3 pinos (shift register)
* Alternância de modos via botão
* Sistema adaptativo baseado em sensores
* Suporte a múltiplas fases de tráfego

### Comportamento observado

* Semáforos alternam corretamente entre:

  * verde → amarelo → vermelho
* Modos alteram a lógica de abertura (semáforos simultâneos ou desativados)
* Sensores influenciam diretamente o tempo de abertura
  * Tempos escolhidos (5s MinVerde, 2s Amarelo) apenas para facilitar testes, não representando valores práticos realistas



## 6️⃣ Comentários Adicionais

### Limitações

* Temporização baseada em `sleep`
* Sensores PIR permanecem ativos por 5 segundos a cada detecção
* Não há modelagem de conflitos reais de tráfego


### Possíveis melhorias

* Uso de `ticks_ms()` para temporização precisa
* Adicionar display (OLED) com status do sistema
* Armazenar data e hora de detecção do sensor em um banco de dados para coleta, a fim de analisar o tráfego e ajustar os tempos.


### Aprendizados

* Uso de shift registers para expansão de IO
* Modelagem de sistemas embarcados adaptativos
* Organização de código com foco em escalabilidade
* Separação entre lógica e hardware
