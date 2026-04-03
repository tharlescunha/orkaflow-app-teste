# main.py

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests


STATE_FILE = Path("estado_execucao.json")
RESULT_FILE = Path("resultado_execucao.json")


CENARIOS = [
    "success_todos",
    "success_posts",
    "error_timeout",
    "error_connection",
    "error_value",
    "error_runtime",
    "error_http",
    "error_generic",
]


def agora_iso() -> str:
    return datetime.now().isoformat()


def carregar_estado() -> Dict[str, Any]:
    if not STATE_FILE.exists():
        return {
            "indice_cenario": 0,
            "total_execucoes": 0,
            "historico_resumido": [],
        }

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_estado(estado: Dict[str, Any]) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(estado, f, indent=4, ensure_ascii=False)


def salvar_resultado(resultado: Dict[str, Any]) -> None:
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=4, ensure_ascii=False)


def proximo_cenario(estado: Dict[str, Any]) -> str:
    indice = estado["indice_cenario"]
    return CENARIOS[indice]


def avancar_estado(estado: Dict[str, Any], cenario: str, status: str) -> None:
    estado["total_execucoes"] += 1
    estado["indice_cenario"] = (estado["indice_cenario"] + 1) % len(CENARIOS)

    historico = estado.get("historico_resumido", [])
    historico.append(
        {
            "execucao_global": estado["total_execucoes"],
            "cenario": cenario,
            "status": status,
            "timestamp": agora_iso(),
        }
    )

    # mantém só os últimos 20 registros
    estado["historico_resumido"] = historico[-20:]


def consultar_todos() -> Dict[str, Any]:
    inicio = datetime.now()

    response = requests.get(
        "https://jsonplaceholder.typicode.com/todos",
        timeout=20,
    )
    response.raise_for_status()

    dados = response.json()
    total = len(dados)
    concluidos = sum(1 for item in dados if item.get("completed") is True)
    pendentes = total - concluidos

    fim = datetime.now()

    return {
        "fonte": "jsonplaceholder",
        "endpoint": "https://jsonplaceholder.typicode.com/todos",
        "tipo_dado": "tarefas",
        "total_registros": total,
        "concluidos": concluidos,
        "pendentes": pendentes,
        "duracao_segundos": round((fim - inicio).total_seconds(), 2),
        "timestamp_consulta": fim.isoformat(),
    }


def consultar_posts() -> Dict[str, Any]:
    inicio = datetime.now()

    response = requests.get(
        "https://jsonplaceholder.typicode.com/posts",
        timeout=20,
    )
    response.raise_for_status()

    dados = response.json()
    total = len(dados)
    total_usuarios = len({item["userId"] for item in dados})
    maior_titulo = max(len(item["title"]) for item in dados)
    menor_titulo = min(len(item["title"]) for item in dados)

    fim = datetime.now()

    return {
        "fonte": "jsonplaceholder",
        "endpoint": "https://jsonplaceholder.typicode.com/posts",
        "tipo_dado": "posts",
        "total_registros": total,
        "usuarios_unicos": total_usuarios,
        "maior_titulo_caracteres": maior_titulo,
        "menor_titulo_caracteres": menor_titulo,
        "duracao_segundos": round((fim - inicio).total_seconds(), 2),
        "timestamp_consulta": fim.isoformat(),
    }


def simular_erro(cenario: str) -> None:
    if cenario == "error_timeout":
        raise requests.Timeout("Erro simulado: timeout ao consultar serviço externo.")

    if cenario == "error_connection":
        raise requests.ConnectionError("Erro simulado: falha de conexão com serviço externo.")

    if cenario == "error_value":
        raise ValueError("Erro simulado: valor inválido encontrado no processamento.")

    if cenario == "error_runtime":
        raise RuntimeError("Erro simulado: falha inesperada em tempo de execução.")

    if cenario == "error_http":
        raise requests.HTTPError("Erro simulado: resposta HTTP 500 do serviço externo.")

    if cenario == "error_generic":
        raise Exception("Erro simulado genérico para teste do worker.")

    raise Exception(f"Cenário de erro desconhecido: {cenario}")


def executar_cenario(execucao_global: int, cenario: str) -> Dict[str, Any]:
    inicio = datetime.now()

    if cenario == "success_todos":
        dados = consultar_todos()
        fim = datetime.now()
        return {
            "status": "success",
            "execucao_global": execucao_global,
            "cenario": cenario,
            "mensagem": "Execução concluída com sucesso consultando endpoint de tarefas.",
            "inicio": inicio.isoformat(),
            "fim": fim.isoformat(),
            **dados,
        }

    if cenario == "success_posts":
        dados = consultar_posts()
        fim = datetime.now()
        return {
            "status": "success",
            "execucao_global": execucao_global,
            "cenario": cenario,
            "mensagem": "Execução concluída com sucesso consultando endpoint de posts.",
            "inicio": inicio.isoformat(),
            "fim": fim.isoformat(),
            **dados,
        }

    simular_erro(cenario)
    raise Exception("Fluxo inesperado na execução do cenário.")


def main() -> None:
    estado = carregar_estado()

    cenario = proximo_cenario(estado)
    execucao_global = estado["total_execucoes"] + 1

    print("=" * 80)
    print(f"Iniciando execução global #{execucao_global}")
    print(f"Cenário selecionado: {cenario}")
    print("=" * 80)

    try:
        resultado = executar_cenario(execucao_global, cenario)

        avancar_estado(estado, cenario, "success")
        salvar_estado(estado)
        salvar_resultado(resultado)

        print("[SUCESSO]")
        print(json.dumps(resultado, indent=4, ensure_ascii=False))

    except Exception as e:
        erro = {
            "status": "error",
            "execucao_global": execucao_global,
            "cenario": cenario,
            "tipo_erro_classe": e.__class__.__name__,
            "erro": str(e),
            "timestamp": agora_iso(),
        }

        avancar_estado(estado, cenario, "error")
        salvar_estado(estado)
        salvar_resultado(erro)

        print("[ERRO]")
        print(json.dumps(erro, indent=4, ensure_ascii=False))

        # Falha real do processo para o orquestrador capturar
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(1)
        