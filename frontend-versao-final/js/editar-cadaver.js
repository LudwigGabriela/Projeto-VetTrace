
const API_CADAVER = "http://127.0.0.1:5000/cadaver";

document.addEventListener("DOMContentLoaded", () => {
    document
        .getElementById("form-cadaver-btn-cancelar")
        .addEventListener("click", cancelarEdicao);

    document
        .getElementById("form-cadaver-btn-submit")
        .addEventListener("click", salvarAlteracoes);

    carregarCadaver();
});

function obterToken() {
    const token = localStorage.getItem("token");

    if (!token) {
        mostrarMensagem("Sessão expirada. Faça login novamente.");
        window.location.href = "login.html";
        return null;
    }

    return token;
}

async function carregarCadaver() {
    const id = new URLSearchParams(window.location.search).get("id");
    const token = obterToken();

    if (!id || !token) {
        if (!id) mostrarMensagem("ID do cadáver não informado.");
        return;
    }

    try {
        const resposta = await fetch(API_CADAVER, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        const dados = await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                dados.erro || dados.msg ||
                "Erro ao consultar cadáveres."
            );
        }

        const cadaveres = Array.isArray(dados)
            ? dados
            : dados.cadaveres;

        const cadaver = cadaveres?.find(
            item => String(item.id) === String(id)
        );

        if (!cadaver) {
            throw new Error("Cadáver não encontrado.");
        }

        preencherFormulario(cadaver);

    } catch (erro) {
        console.error("Erro ao carregar cadáver:", erro);
        mostrarMensagem(erro.message);
    }
}

// Converte a data retornada pela API para o formato dos inputs HTML.
function obterDataInput(dataString) {
    if (!dataString) return "";

    // Formato comum do PostgreSQL/Flask:
    // "Mon, 22 Jun 2026 21:07:00 GMT"
    const data = new Date(dataString);

    if (Number.isNaN(data.getTime())) {
        // Também aceita "2026-06-22" ou
        // "2026-06-22 21:07:00".
        const correspondencia = String(dataString).match(
            /^(\d{4}-\d{2}-\d{2})/
        );

        return correspondencia ? correspondencia[1] : "";
    }

    // Utiliza a data/hora local para os campos do formulário.
    const ano = data.getFullYear();
    const mes = String(data.getMonth() + 1).padStart(2, "0");
    const dia = String(data.getDate()).padStart(2, "0");

    return `${ano}-${mes}-${dia}`;
}

function obterHoraInput(dataString) {
    if (!dataString) return "";

    const data = new Date(dataString);

    if (Number.isNaN(data.getTime())) {
        const correspondencia = String(dataString).match(
            /(\d{2}:\d{2})/
        );

        return correspondencia ? correspondencia[1] : "";
    }

    const horas = String(data.getHours()).padStart(2, "0");
    const minutos = String(data.getMinutes()).padStart(2, "0");

    return `${horas}:${minutos}`;
}

function preencherFormulario(cadaver) {
    document.getElementById("form-cadaver-input-nome").value =
        cadaver.identificacao ?? "";

    document.getElementById("form-cadaver-input-peso").value =
        cadaver.peso_kg ?? "";

    document.getElementById("form-cadaver-input-nome-proprietario").value =
        cadaver.nome_proprietario ?? "";

    document.getElementById("form-cadaver-input-especie").value =
        cadaver.especie ?? "";

    document.getElementById("form-cadaver-input-idade").value =
        cadaver.idade_anos ?? "";

    document.getElementById("form-cadaver-input-causa").value =
        cadaver.causa_obito ?? "";

    document.getElementById("form-cadaver-input-destino").value =
        cadaver.destino_id ?? "";

    document.getElementById("form-cadaver-input-data-entrada").value =
        obterDataInput(cadaver.data_entrada);

    document.getElementById("form-cadaver-input-hora-entrada").value =
        obterHoraInput(cadaver.data_entrada);

    document.getElementById("form-cadaver-input-data-saida").value =
        obterDataInput(cadaver.data_saida);

    document.getElementById("form-cadaver-input-hora-saida").value =
        obterHoraInput(cadaver.data_saida);

    document.getElementById("form-cadaver-input-observacao").value =
        cadaver.observacoes ?? "";
}

function cancelarEdicao() {
    window.location.href = "descarte-cadaver.html";
}

async function salvarAlteracoes(event) {
    event.preventDefault();

    const id = new URLSearchParams(window.location.search).get("id");
    const token = obterToken();

    if (!id || !token) {
        if (!id) mostrarMensagem("ID do cadáver não informado.");
        return;
    }

    const cadaver = {
        nome: document.getElementById("form-cadaver-input-nome").value.trim(),
        peso: document.getElementById("form-cadaver-input-peso").value,
        nome_proprietario: document
            .getElementById("form-cadaver-input-nome-proprietario").value.trim(),
        especie: document.getElementById("form-cadaver-input-especie").value,
        idade: document.getElementById("form-cadaver-input-idade").value,
        causa: document.getElementById("form-cadaver-input-causa").value.trim(),
        destino: document.getElementById("form-cadaver-input-destino").value,
        data_entrada: document.getElementById("form-cadaver-input-data-entrada").value,
        hora_entrada: document.getElementById("form-cadaver-input-hora-entrada").value,
        data_saida: document.getElementById("form-cadaver-input-data-saida").value,
        hora_saida: document.getElementById("form-cadaver-input-hora-saida").value,
        observacao: document.getElementById("form-cadaver-input-observacao").value.trim()
    };

    const erro = validarCadaver(cadaver);

    if (erro) {
        mostrarMensagem(erro);
        return;
    }

    const dadosApi = {
        especie: cadaver.especie,
        identificacao: cadaver.nome,
        idade_anos: Number(cadaver.idade),
        peso_kg: Number(cadaver.peso),
        nome_proprietario: cadaver.nome_proprietario,
        status: "congelado",
        causa_obito: cadaver.causa,
        destino_id: Number(cadaver.destino),
        data_entrada: `${cadaver.data_entrada}T${cadaver.hora_entrada}:00`,
        data_saida: cadaver.data_saida && cadaver.hora_saida
            ? `${cadaver.data_saida}T${cadaver.hora_saida}:00`
            : null,
        observacoes: cadaver.observacao
    };

    const botao = document.getElementById("form-cadaver-btn-submit");
    botao.disabled = true;

    try {
        const resposta = await fetch(`${API_CADAVER}/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(dadosApi)
        });

        const texto = await resposta.text();
        let resultado = {};

        try {
            resultado = texto ? JSON.parse(texto) : {};
        } catch {
            resultado = { erro: texto };
        }

        if (!resposta.ok) {
            throw new Error(
                resultado.erro ||
                resultado.msg ||
                "Não foi possível atualizar o cadáver."
            );
        }

        alert("Cadastro de cadáver atualizado com sucesso!");

        setTimeout(() => {
            window.location.href = "descarte-cadaver.html";
        }, 500);

    } catch (erro) {
        console.error("Erro ao atualizar cadáver:", erro);
        mostrarMensagem(erro.message);
    } finally {
        botao.disabled = false;
    }
}

function validarCadaver(cadaver) {
    if (
        !cadaver.nome ||
        !cadaver.peso ||
        !cadaver.nome_proprietario ||
        !cadaver.especie ||
        !cadaver.idade ||
        !cadaver.causa ||
        !cadaver.destino ||
        !cadaver.data_entrada ||
        !cadaver.hora_entrada
    ) {
        return "Preencha todos os campos obrigatórios.";
    }

    if (!Number.isFinite(Number(cadaver.peso)) ||
        Number(cadaver.peso) < 0) {
        return "Informe um peso válido.";
    }

    if (!Number.isInteger(Number(cadaver.idade)) ||
        Number(cadaver.idade) < 0) {
        return "Informe uma idade válida.";
    }

    const entrada = new Date(
        `${cadaver.data_entrada}T${cadaver.hora_entrada}`
    );

    if (entrada > new Date()) {
        return "A data e hora de entrada não podem estar no futuro.";
    }

    if (cadaver.data_saida && !cadaver.hora_saida) {
        return "Informe a hora de saída.";
    }

    if (!cadaver.data_saida && cadaver.hora_saida) {
        return "Informe a data de saída.";
    }

    if (cadaver.data_saida && cadaver.hora_saida) {
        const saida = new Date(
            `${cadaver.data_saida}T${cadaver.hora_saida}`
        );

        if (saida < entrada) {
            return "A saída não pode ser anterior à entrada.";
        }
    }

    return null;
}
