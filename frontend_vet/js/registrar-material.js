const btnSubmit = document.getElementById("form-material-btn-submit")
const btnCancelar = document.getElementById("form-material-btn-cancelar")

btnSubmit.addEventListener("click", enviarFormulario)
btnCancelar.addEventListener("click", limparFormulario)

function enviarFormulario(event) {
    event.preventDefault()

    const material = {
        nome: document.getElementById("kit-name-select").value,
        tipo: document.getElementById("form-material-input-tipo").value,
        descricao: document.getElementById("form-material-input-descricao").value,
    }

    const erro = validarCampos(material)

    if (erro) {
        alert(erro)
        return
    }

    /*

    // Recupera o usuário logado
    const usuario = JSON.parse(localStorage.getItem("usuario"))

    if (!usuario || !usuario.id) {
        mostrarMensagem("Usuário não identificado. Faça login novamente.")
        window.location.href = "login.html"
        return
    }

    // Recupera o token JWT
    const token = localStorage.getItem("token")

    if (!token) {
        mostrarMensagem("Sessão expirada. Faça login novamente.")
        window.location.href = "login.html"
        return
    }

    const dadosApi = {
        nome: material.nome,
        tipo: material.tipo,
        descricao: material.descricao,
        //status: "congelado",

        // Usuário que está logado
        registrado_por: usuario.id,
    }

    console.log("Usuário logado:", usuario)
    console.log("ID responsável pelo cadastro:", usuario.id)
    console.log("Dados enviados:", dadosApi)

    fetch("http://127.0.0.1:5000/material", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(dadosApi)
    })
        .then(async response => {

            const data = await response.json()

            console.log("Resposta da API:", data)

            if (!response.ok) {
                throw new Error(
                    data.msg ||
                    data.erro ||
                    "Erro ao registrar material"
                )
            }

            return data
        })
        .then(data => {

            mostrarMensagem("Material registrado com sucesso")

            limparFormulario()
            carregarmateriales()

        })
        .catch(error => {

            console.error(error)
            mostrarMensagem(error.message)

        })

        */
    
}

function validarCampos(campos) {

    // obrigatórios
    if (!campos.nome || !campos.tipo) {
        return "Preencha todos os campos obrigatórios"
    }

    return null

}

function limparFormulario() {

    document.getElementById("kit-name-select").value = ""
    document.getElementById("form-material-input-tipo").value = "Médio"
    document.getElementById("form-material-input-descricao").value = ""

}