document.addEventListener("DOMContentLoaded", carregarMateriais)


function carregarMateriais() {

    fetch("http://127.0.0.1:5000/material")
        .then(response => response.json())
        .then(materiais => {
            preencherTabela(materiais)
        })
        .catch(error => {
            console.error(error)
        })

}


function formatarData(dataString) {

    const partes = dataString.split(" ")

    const data = partes[0]
    const hora = partes[1]

    const [ano, mes, dia] = data.split("-")

    return `${dia}/${mes}/${ano} ${hora.substring(0, 5)}`
}


function preencherTabela(materiais) {

    const tbody = document.getElementById("tabela-materiais");

    tbody.replaceChildren();

    materiais.forEach(material => {

        const linha = document.createElement("tr");

        const valores = [
            material.id,
            material.nome,
            material.tipo,
            "-",
            "-",
            "-",
            "-",
            "-"
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
        btnEditar.dataset.id = material.id;

        // Botão excluir
        const btnExcluir = document.createElement("button");
        btnExcluir.type = "button";
        btnExcluir.className = "btn btn-sm btn-danger btn-excluir";
        btnExcluir.textContent = "Excluir";
        btnExcluir.dataset.id = material.id;
        btnExcluir.dataset.descricao = material.descricao;

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

            //window.location.href =
                //`editar-material.html?id=${encodeURIComponent(id)}`;

            return;
        }

        if (botaoExcluir) {

            const id = botaoExcluir.dataset.id;
            const descricao = botaoExcluir.dataset.descricao;

            abrirModalExclusao(id, descricao);
        }
    };
}

