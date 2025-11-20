# 🥥 CocoVision AI: Sistema de Contagem e QC em Esteira

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![YOLOv11](https://img.shields.io/badge/YOLO-v11-magenta?style=for-the-badge&logo=ultralytics&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red?style=for-the-badge&logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> Um sistema industrial de Visão Computacional para contagem bidirecional, classificação de tamanho e detecção de defeitos em tempo real.

---

## 📹 Demo

![Dashboard Preview](Demo.mp4)

## 🚀 Funcionalidades

O sistema utiliza o estado da arte em detecção de objetos (**YOLOv11**) combinado com processamento de imagem clássico (**Morfologia Matemática**) para entregar métricas precisas:

- **📦 Contagem Bidirecional:** Detecta automaticamente o fluxo (Subida/Descida) e conta objetos com zona de histerese (anti-flicker).
- **📏 Classificação de Tamanho:** Categoriza geometricamente em *Pequeno*, *Médio* e *Grande*.
- **🔍 Controle de Qualidade (QC):**
  - **Cor/Maturação:** Analisa o brilho e uniformidade via espaço de cor HSV.
  - **Detecção de Rachaduras:** Algoritmo *Black Hat Transform* para identificar fissuras estruturais.
- **📊 Dashboard em Tempo Real:** Painel translúcido com CPM (Cocos por Minuto), vetores de direção e estatísticas acumuladas.

## 📂 Estrutura do Projeto

```text
COLIT/
├── data/               # Datasets e configurações YAML
├── documents/          # Documentação Técnica e Guias
│   ├── CodingGuide.md
│   └── documents.md
├── runs/               # Pesos do modelo treinado
│   └── detect/CocoDetec/weights/best.pt
├── src/                # Código Fonte Modular
│   ├── qc_analyzer.py  # Matemática de QC (Rachaduras/Cor)
│   ├── visualizer.py   # Renderização de UI e Dashboards
│   └── system.py       # Lógica principal e Pipeline
├── test_vid/           # Vídeos de teste
├── config.py           # Arquivo central de configuração e calibração
├── main.py             # Ponto de entrada da aplicação
├── train.py            # Script de treinamento/finetuning
└── requirements.txt    # Dependências do projeto
```

## 🛠️ Instalação

- **Clone o repositório:**

```bash

git clone https://github.com/JuliusSchneiders/Coconut-Counter-Analyzer-CocoLitoraneo.git

cd Coconut-Counter-Analyzer-CocoLitoraneo
```

- **Instale as dependências:**

```bash
    pip install -r requirements.txt

    Verifique o modelo: Certifique-se de que o arquivo best.pt está no caminho definido em config.py.
```
  - **Descompacte o Dataset em uma pasta no diretório raiz do projeto chamada data/**
  [Dataset](https://drive.google.com/file/d/1tKlclZxYukKMgrTViyY7OBIfzMiiwSnK/view?usp=sharing)

## ▶️ Como Usar

- **Para rodar a inferência (Sistema Principal):**

```bash
python main.py
```

- **Para treinar um novo modelo:**

```bash
python train.py
```

## ⚙️ Configuração e Calibração

- **Não é necessário alterar o código fonte. Ajuste sensibilidades e caminhos diretamente em config.py:**

```Python
# Exemplo de ajuste de sensibilidade de rachadura
CRACK_LIMIT_RATIO = 0.2  # 20% da área com fissuras
QUALITY_BRIGHTNESS_THRESH = 127 # Brilho mínimo para aprovação
```

## 📚 Documentação

Para detalhes técnicos sobre os algoritmos utilizados e padrões de código, consulte a pasta documents/

## Adendos

É importante ressaltar a restrição do cenário.

- **O vídeo em análise é uma esteira de cocos marroms, dada uma outra análise de um outro cenário a abordagem seria diferente da feita neste projeto.**
