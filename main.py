# main.py

"""
Automação de teste:
- Executa 3 vezes
- 2 sucessos
- 1 erro simulado
- Gera saída em JSON
"""

import requests
import json
from datetime import datetime
from pathlib import Path


def executar_automacao(execucao_numero: int):
    inicio = datetime.now()

    try:
        # Simula erro na 3ª execução
        if execucao_numero == 3:
            raise Exception("Erro simulado para teste do worker")

        # Chamada externa
        response = requests.get("https://jsonplaceholder.typicode.com/todos")
        dados = response.json()

        total = len(dados)
        concluidos = sum(1 for item in dados if item["completed"])
        pendentes = total - concluidos

        fim = datetime.now()

        return {
            "status": "success",
            "execucao": execucao_numero,
            "total": total,
            "concluidos": concluidos,
            "pendentes": pendentes,
            "duracao_segundos": round((fim - inicio).total_seconds(), 2),
            "timestamp": fim.isoformat(),
        }

    except Exception as e:
        fim = datetime.now()

        return {
            "status": "error",
            "execucao": execucao_numero,
            "erro": str(e),
            "duracao_segundos": round((fim - inicio).total_seconds(), 2),
            "timestamp": fim.isoformat(),
        }


def main():
    resultados = []

    for i in range(1, 4):  # 3 execuções
        resultado = executar_automacao(i)
        print(f"[Execução {i}] -> {resultado}")
        resultados.append(resultado)

    # Salvar JSON de saída
    output_path = Path("resultado_execucao.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)

    print(f"\nArquivo gerado em: {output_path.resolve()}")


if __name__ == "__main__":
    main()
    