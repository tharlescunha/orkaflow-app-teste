# main.py

import requests
import json
import sys
from datetime import datetime
from pathlib import Path


def executar_automacao(execucao_numero: int):
    inicio = datetime.now()

    # Simula erro na 3ª execução
    if execucao_numero == 3:
        raise Exception("Erro simulado para teste do worker")

    response = requests.get("https://jsonplaceholder.typicode.com/todos", timeout=30)
    response.raise_for_status()
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


def salvar_json(resultados):
    output_path = Path("resultado_execucao.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)
    print(f"Arquivo gerado em: {output_path.resolve()}")


def main():
    resultados = []

    for i in range(1, 4):
        try:
            resultado = executar_automacao(i)
            print(f"[Execução {i}] -> {resultado}")
            resultados.append(resultado)

        except Exception as e:
            erro = {
                "status": "error",
                "execucao": i,
                "erro": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            print(f"[Execução {i}] -> {erro}")
            resultados.append(erro)

            salvar_json(resultados)

            # aqui faz o processo falhar de verdade
            raise

    salvar_json(resultados)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(1)
        