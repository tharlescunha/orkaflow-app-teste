# main.py

"""
Automação simples sem interação.
Faz uma requisição HTTP, processa dados e retorna resultado.
"""

import requests
from datetime import datetime


def executar_automacao():
    inicio = datetime.now()

    # Simula chamada externa (API pública)
    response = requests.get("https://jsonplaceholder.typicode.com/todos")
    dados = response.json()

    total = len(dados)
    concluidos = sum(1 for item in dados if item["completed"])
    pendentes = total - concluidos

    fim = datetime.now()

    resultado = {
        "status": "success",
        "total": total,
        "concluidos": concluidos,
        "pendentes": pendentes,
        "duracao_segundos": round((fim - inicio).total_seconds(), 2),
    }

    return resultado


if __name__ == "__main__":
    resultado = executar_automacao()
    print(resultado)

