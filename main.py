# main.py

"""
Automação de teste:
- Faz requisição para URL inválida
- Gera erro real
- Estoura exception
"""

import requests


def executar_automacao():
    # URL inválida para forçar erro real
    response = requests.get("https://url-inexistente-teste-orkaflow-123456.com", timeout=10)
    response.raise_for_status()

    return {
        "status": "success"
    }


def main():
    print("Iniciando automação de teste...")
    resultado = executar_automacao()
    print(resultado)


if __name__ == "__main__":
    main()