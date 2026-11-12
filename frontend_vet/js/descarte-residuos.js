document.addEventListener("DOMContentLoaded", carregarResiduos)
document.addEventListener("DOMContentLoaded", carregarPesoResiduos)

const btnSubmit = document.getElementById("form-residuo-btn-submit")
const btnCancelar = document.getElementById("form-residuo-btn-cancelar")

btnSubmit.addEventListener("click", enviarFormulario)
btnCancelar.addEventListener("click", limparFormulario)

// Elementos do modal de exclusão
const modalExclusao = document.getElementById("modal-exclusao");
const nomeResiduoExclusao = document.getElementById("nome-residuo-exclusao");

const btnCancelarExclusao = document.getElementById("btn-cancelar-exclusao");
const btnConfirmarExclusao = document.getElementById("btn-confirmar-exclusao");

// ID do resíduo selecionado
let residuoSelecionado = null;

// Eventos do modal
btnCancelarExclusao.addEventListener("click", fecharModalExclusao);
btnConfirmarExclusao.addEventListener("click", confirmarExclusao);

// Fecha o modal ao clicar fora dele
modalExclusao.addEventListener("click", function(event) {
    if (event.target === modalExclusao) {
        fecharModalExclusao();
    }
});

// Fecha o modal com ESC
document.addEventListener("keydown", function(event) {
    if (event.key === "Escape" && !modalExclusao.hidden) {
        fecharModalExclusao();
    }
});

function enviarFormulario(event) {
    event.preventDefault()

    const residuo = {
        grupo: document.getElementById("form-residuo-input-grupo").value,
        peso: document.getElementById("form-residuo-input-peso").value,
        nome: document.getElementById("form-residuo-input-nome").value,
        origem: document.getElementById("form-residuo-input-origem").value,
        data: document.getElementById("form-residuo-input-data").value,
        hora: document.getElementById("form-residuo-input-hora").value,
        observacao: document.getElementById("form-residuo-input-observacao").value
    }

    const erro = validarCampos(residuo)

    if (erro) {
        mostrarMensagem(erro)
        return
    }

    // Recupera o usuário logado
    const usuario = JSON.parse(localStorage.getItem("usuario"));

    if (!usuario || !usuario.id) {
        mostrarMensagem("Usuário não identificado. Faça login novamente.");
        window.location.href = "login.html";
        return;
    }

    // Recupera o token JWT
    const token = localStorage.getItem("token");

    if (!token) {
        mostrarMensagem("Sessão expirada. Faça login novamente.");
        window.location.href = "login.html";
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
        responsavel_id: usuario.id
    }
    console.log("Usuário logado:", usuario);
    console.log("ID responsável:", usuario.id);
    console.log("Dados enviados:", dadosApi);

    fetch("http://127.0.0.1:5000/residuo", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(dadosApi)
    })
        .then(async response => {

            const data = await response.json();

            console.log("Resposta da API:", data);

            if (!response.ok) {
                throw new Error(data.msg || data.erro || "Erro ao registrar resíduo");
            }

            return data;
        })
        .then(data => {
            mostrarMensagem("Resíduo registrado com sucesso");

            limparFormulario();
            carregarResiduos();
            carregarPesoResiduos();
        })
        .catch(error => {
            console.error(error);
            mostrarMensagem(error.message);
        })
}

function validarCampos(campos) {

    // obrigatórios
    if (!campos.grupo || !campos.peso || !campos.nome || !campos.origem || !campos.data || !campos.hora) {
        return "Preencha todos os campos obrigatórios"
    }

    // peso
    if (campos.peso < 0) {
        return "Peso deve ser um valor positivo"
    }

    // data e hora não podem estar no futuro
    const dataHoraEntrada = new Date(`${campos.data}T${campos.hora}`)
    const agora = new Date()
    if (dataHoraEntrada > agora) {
        return "A data e hora do registro não podem estar no futuro"
    }

    return null

}

function limparFormulario() {

    const campos = [
        "form-residuo-input-grupo",
        "form-residuo-input-peso",
        "form-residuo-input-nome",
        "form-residuo-input-origem",
        "form-residuo-input-data",
        "form-residuo-input-hora",
        "form-residuo-input-observacao"
    ]

    campos.forEach(id => {
        document.getElementById(id).value = ""
    })

}

function carregarResiduos() {

    fetch("http://127.0.0.1:5000/residuo")
        .then(response => response.json())
        .then(residuos => {
            preencherTabela(residuos)
        })
        .catch(error => {
            console.error(error)
        })

}

function carregarPesoResiduos() {

    const hoje = new Date()
    const mes = hoje.getMonth() + 1
    const ano = hoje.getFullYear()

    fetch(`http://127.0.0.1:5000/residuo/peso-total?mes=${mes}&ano=${ano}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("kpi-peso-total").textContent =
                `${data.peso_total}`
        })
        .catch(error => console.error(error))

    fetch("http://127.0.0.1:5000/residuo/peso-total")
        .then(response => response.json())
        .then(data => {
            document.getElementById("kpi-peso-aguardando").textContent =
                `${data.peso_total}`
        })
        .catch(error => console.error(error))

}

function formatarData(dataString) {

    const partes = dataString.split(" ")

    const data = partes[0]
    const hora = partes[1]

    const [ano, mes, dia] = data.split("-")

    return `${dia}/${mes}/${ano} ${hora.substring(0, 5)}`
}



function preencherTabela(residuos) {

    const tbody = document.getElementById("tabela-residuos");

    tbody.replaceChildren();

    residuos.forEach(residuo => {

        const linha = document.createElement("tr");

        const valores = [
            residuo.id,
            formatarData(residuo.data_registro),
            residuo.tipo_grupo,
            residuo.descricao,
            residuo.quantidade,
            residuo.setor_gerador,
            residuo.responsavel_nome ?? "-",
            residuo.status
        ];

        valores.forEach(valor => {
            const celula = document.createElement("td");
            celula.textContent = valor;
            linha.appendChild(celula);
        });

        // Coluna de ações
        const celulaAcoes = document.createElement("td");

        // Botão editar
        const btnEditar = document.createElement("button");
        btnEditar.type = "button";
        btnEditar.className = "btn btn-sm btn-primary btn-editar";
        btnEditar.textContent = "Editar";
        btnEditar.dataset.id = residuo.id;

        // Botão excluir
        const btnExcluir = document.createElement("button");
        btnExcluir.type = "button";
        btnExcluir.className = "btn btn-sm btn-danger btn-excluir";
        btnExcluir.textContent = "Excluir";
        btnExcluir.dataset.id = residuo.id;
        btnExcluir.dataset.descricao = residuo.descricao;

        celulaAcoes.appendChild(btnEditar);
        celulaAcoes.appendChild(btnExcluir);

        linha.appendChild(celulaAcoes);

        tbody.appendChild(linha);
    });

    // Eventos dos botões da tabela
    tbody.onclick = function(event) {

        const botaoEditar = event.target.closest(".btn-editar");
        const botaoExcluir = event.target.closest(".btn-excluir");

        if (botaoEditar) {

            const id = botaoEditar.dataset.id;

            window.location.href =
                `editar-residuo.html?id=${encodeURIComponent(id)}`;

            return;
        }

        if (botaoExcluir) {

            const id = botaoExcluir.dataset.id;
            const descricao = botaoExcluir.dataset.descricao;

            abrirModalExclusao(id, descricao);
        }
    };
}


function abrirModalExclusao(id, descricao) {

    residuoSelecionado = id;

    nomeResiduoExclusao.textContent = descricao;

    modalExclusao.hidden = false;
}

function fecharModalExclusao() {

    modalExclusao.hidden = true;

    residuoSelecionado = null;

    btnConfirmarExclusao.disabled = false;
    btnConfirmarExclusao.textContent = "Sim, excluir";
}

async function confirmarExclusao() {

    if (!residuoSelecionado) {
        return;
    }

    const token = localStorage.getItem("token");

    if (!token) {
        mostrarMensagem("Sessão expirada. Faça login novamente.");
        window.location.href = "login.html";
        return;
    }

    try {

        btnConfirmarExclusao.disabled = true;
        btnCancelarExclusao.disabled = true;
        btnConfirmarExclusao.textContent = "Excluindo...";

        const response = await fetch(
            `http://127.0.0.1:5000/residuo/${encodeURIComponent(residuoSelecionado)}`,
            {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(
                data.msg || data.erro || "Não foi possível excluir o resíduo."
            );
        }

        fecharModalExclusao();

        mostrarMensagem("Resíduo excluído com sucesso!");

        carregarResiduos();
        carregarPesoResiduos();

    } catch (error) {

        console.error("Erro ao excluir resíduo:", error);

        mostrarMensagem(error.message);

        btnConfirmarExclusao.disabled = false;
        btnCancelarExclusao.disabled = false;
        btnConfirmarExclusao.textContent = "Sim, excluir";
    }
}

