
const API_URL = "http://127.0.0.1:5000/residuo";

document.addEventListener("DOMContentLoaded", () => {
    document
        .getElementById("form-residuo-btn-cancelar")
        .addEventListener("click", cancelarEdicao);

    document
        .getElementById("form-residuo-btn-submit")
        .addEventListener("click", salvarAlteracoes);

    carregarResiduo();
});

// Recupera o ID do resíduo pela URL e carrega seus dados
async function carregarResiduo() {
    const parametros = new URLSearchParams(window.location.search);
    const residuoId = parametros.get("id");
    const token = localStorage.getItem("token");

    if (!residuoId) {
        mostrarMensagem("ID do resíduo não informado.");
        return;
    }

    if (!token) {
        mostrarMensagem("Sessão expirada. Faça login novamente.");
        window.location.href = "login.html";
        return;
    }

    try {
        const resposta = await fetch(API_URL, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        const dados = await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                dados.erro || dados.msg || "Erro ao consultar resíduos."
            );
        }

        const residuo = dados.find(
            item => String(item.id) === String(residuoId)
        );

        if (!residuo) {
            throw new Error("Resíduo não encontrado.");
        }

        preencherFormulario(residuo);

    } catch (erro) {
        console.error("Erro ao carregar resíduo:", erro);
        mostrarMensagem(erro.message);
    }
}

// Preenche o formulário com os dados do registro selecionado
function preencherFormulario(residuo) {
    document.getElementById("form-residuo-input-grupo").value =
        residuo.tipo_grupo ?? "";

    document.getElementById("form-residuo-input-peso").value =
        residuo.quantidade ?? "";

    document.getElementById("form-residuo-input-nome").value =
        residuo.descricao ?? "";

    document.getElementById("form-residuo-input-origem").value =
        residuo.setor_gerador ?? "";

    document.getElementById("form-residuo-input-observacao").value =
        residuo.observacao ?? "";

    if (residuo.data_registro) {
        const dataHora = new Date(residuo.data_registro);

        if (!Number.isNaN(dataHora.getTime())) {
            const ano = dataHora.getFullYear();
            const mes = String(dataHora.getMonth() + 1).padStart(2, "0");
            const dia = String(dataHora.getDate()).padStart(2, "0");

            const hora = String(dataHora.getHours()).padStart(2, "0");
            const minuto = String(dataHora.getMinutes()).padStart(2, "0");

            document.getElementById("form-residuo-input-data").value =
                `${ano}-${mes}-${dia}`;

            document.getElementById("form-residuo-input-hora").value =
                `${hora}:${minuto}`;
        }
    }
}

// Cancela a edição e volta para a listagem
function cancelarEdicao() {
    window.location.href = "descarte-residuos.html";
}

// Valida e envia as alterações para o backend
async function salvarAlteracoes(event) {
    event.preventDefault();

    const parametros = new URLSearchParams(window.location.search);
    const residuoId = parametros.get("id");
    const token = localStorage.getItem("token");

    if (!residuoId) {
        mostrarMensagem("ID do resíduo não informado.");
        return;
    }

    if (!token) {
        mostrarMensagem("Sessão expirada. Faça login novamente.");
        window.location.href = "login.html";
        return;
    }

    const residuo = {
        grupo: document.getElementById("form-residuo-input-grupo").value,
        peso: document.getElementById("form-residuo-input-peso").value,
        nome: document.getElementById("form-residuo-input-nome").value.trim(),
        origem: document.getElementById("form-residuo-input-origem").value,
        data: document.getElementById("form-residuo-input-data").value,
        hora: document.getElementById("form-residuo-input-hora").value,
        observacao: document.getElementById("form-residuo-input-observacao").value.trim()
    };

    const erro = validarResiduo(residuo);

    if (erro) {
        alert(erro);
        return;
    }

    const dadosApi = {
        tipo_grupo: residuo.grupo,
        descricao: residuo.nome,
        quantidade: Number(residuo.peso),
        unidade: "kg",
        data_registro: `${residuo.data}T${residuo.hora}:00`,
        setor_gerador: residuo.origem,
        setor_destino: "-",
        observacao: residuo.observacao
    };

    const botaoSalvar = document.getElementById(
        "form-residuo-btn-submit"
    );

    botaoSalvar.disabled = true;

    try {
        const resposta = await fetch(`${API_URL}/${residuoId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(dadosApi)
        });

        const resultado = await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                resultado.erro ||
                resultado.msg ||
                "Não foi possível atualizar o resíduo."
            );
        }

        alert("Resíduo atualizado com sucesso!");

        // Retorna à listagem após salvar
        window.location.href = "descarte-residuos.html";

    } catch (erro) {
        console.error("Erro ao atualizar resíduo:", erro);
        mostrarMensagem(erro.message);

    } finally {
        botaoSalvar.disabled = false;
    }
}

function validarResiduo(residuo) {
    if (
        !residuo.grupo ||
        residuo.peso === "" ||
        !residuo.nome ||
        !residuo.origem ||
        !residuo.data ||
        !residuo.hora
    ) {
        return "Preencha todos os campos obrigatórios.";
    }

    const peso = Number(residuo.peso);

    if (!Number.isFinite(peso) || peso < 0) {
        return "Informe um peso válido, maior ou igual a zero.";
    }

    const dataHora = new Date(`${residuo.data}T${residuo.hora}`);
    const agora = new Date();

    if (Number.isNaN(dataHora.getTime())) {
        return "Informe uma data e hora válidas.";
    }

    if (dataHora > agora) {
        return "A data e hora não podem estar no futuro.";
    }

    return null;
}
