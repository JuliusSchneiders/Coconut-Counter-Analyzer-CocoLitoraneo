# 🎨 Guia de Estilo e Padrões de Código

Este documento define as diretrizes que estabeleci para manter a qualidade, legibilidade e escalabilidade do código fonte deste projeto.

## 1. Padrões Gerais (PEP 8)

Adoto o **PEP 8** como base para todo o código Python, com atenção especial para:

* **Indentação:** Uso estrito de 4 espaços.
* **Limite de linha:** Mantenho linhas abaixo de 100 caracteres para facilitar a leitura em telas divididas.
* **Organização de Imports:** Agrupo em três blocos: *Biblioteca Padrão* -> *Bibliotecas de Terceiros (OpenCV, Ultralytics)* -> *Módulos Locais*.

## 2. Convenção de Idioma e Nomenclatura

Para simular um ambiente de desenvolvimento globalizado, mas mantendo a usabilidade local, adotei a seguinte estratégia:

* **Código Interno (Lógica em INGLÊS):**
    * Escrevo nomes de variáveis, funções, classes e comentários técnicos internos exclusivamente em inglês.
    * *Ex:* `def calculate_brightness(roi):`, `is_cracked = True`.
    * *Motivo:* Padrão da indústria internacional.

* **Interface com Usuário (Output em PORTUGUÊS):**
    * Todos os logs de terminal, textos no painel (Dashboard) e labels visuais são em português.
    * *Ex:* `print("[INFO] Sistema Iniciado")`, `cv2.putText(..., "RACHADO")`.
    * *Motivo:* Facilidade para o operador final da esteira.

## 3. Type Hinting (Tipagem Estática)

Considero o uso de **Type Hints** obrigatório nas assinaturas de métodos. Isso torna meu código auto-documentável e facilita a depuração.

**❌ O que evito:**
```python
def somar(a, b):
    return a + b
```
**✅ Como eu escrevo:**
```python
def somar(a: int, b: int) -> int:
    return a + b
```
## 4. Estrutura de Comentários

Para facilitar a navegação em arquivos maiores (como o system.py), utilizo divisores de seção visuais:
```python
## === [ NOME DA SEÇÃO ] ===
# Explicação breve da lógica implementada abaixo
```

## 5. Docstrings

Documento todas as minhas classes e métodos públicos explicando:

    O propósito da função.

    Os argumentos esperados (Args).

    O que é retornado (Returns).

Exemplo do meu padrão:
``` python
def draw_lines(frame: np.ndarray, width: int) -> None:
    """
    Desenha as linhas de referência e buffer na imagem.
    
    Args:
        frame (np.ndarray): O frame atual do vídeo.
        width (int): Largura total do frame para traçar a linha.
    """
    ...
```

## 6. Arquitetura Modular

Para evitar "código espaguete", separei as responsabilidades:

    config.py: Centralizo aqui todas as constantes e calibrações. Não coloco lógica neste arquivo.

    src/: Contém apenas classes e funções puras (lógica e visualização).

    main.py: Serve apenas como ponto de entrada para instanciar e rodar o sistema.