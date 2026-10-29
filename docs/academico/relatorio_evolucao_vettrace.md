# Relatório de Evolução do Sistema VetTrace

## 1. Introdução

O presente documento tem como objetivo registrar as atividades de desenvolvimento e as melhorias realizadas no sistema web VetTrace, desenvolvido para auxiliar no gerenciamento de resíduos e cadáveres da clínica veterinária do CEUB.

Nesta etapa, foram realizadas melhorias nas funcionalidades de navegação e gerenciamento de registros, além de alterações na organização dos arquivos do projeto e na configuração do ambiente de execução. Também foram implementadas melhorias para permitir que todos os componentes do sistema sejam iniciados de forma integrada por meio do Docker.

## 2. Implementação das rotas

Foram desenvolvidas as rotas necessárias para o funcionamento e a navegação entre as funcionalidades do sistema. Essa implementação contribui para a organização do backend e para a comunicação entre as diferentes partes da aplicação.

## 3. Funcionalidades de edição e exclusão de registros

Foram implementadas as funcionalidades de edição e exclusão dos registros, permitindo realizar alterações e remover informações cadastradas no sistema.

### 3.1 Edição de registros

A funcionalidade de edição foi desenvolvida por meio da abertura de um formulário contendo as informações do registro selecionado. Dessa forma, o usuário pode modificar os dados existentes e realizar as atualizações necessárias.

### 3.2 Exclusão de registros

A funcionalidade de exclusão foi implementada com a abertura de uma janela de confirmação (*pop-up*) antes da remoção do registro. Esse procedimento permite que o usuário confirme a ação antes de prosseguir, reduzindo a possibilidade de exclusões acidentais.

## 4. Atualização do arquivo principal

O arquivo principal do sistema (`main`) foi atualizado para adequar sua estrutura às alterações realizadas durante o desenvolvimento.

Essa atualização contribui para a integração das funcionalidades implementadas e para o funcionamento do sistema em seu ambiente de execução.

## 5. Reorganização da estrutura do projeto

Foram realizadas alterações na organização dos arquivos e diretórios do projeto, incluindo a renomeação das pastas que armazenam os códigos-fonte.

Além disso, a documentação do sistema foi centralizada no diretório `docs/`, facilitando a localização, a organização e a manutenção dos documentos relacionados ao projeto.

## 6. Integração e execução do sistema com Docker

O sistema foi configurado para funcionar integralmente por meio do Docker, permitindo que seus principais componentes sejam iniciados de maneira conjunta.

A configuração contempla a inicialização integrada de:

- **Banco de dados:** responsável pelo armazenamento das informações do sistema.
- **Backend:** responsável pelo processamento das requisições e pelas regras de funcionamento da aplicação.
- **Frontend:** responsável pela interface de interação com o usuário.

Com essa implementação, o banco de dados, o backend e o frontend passam a ser iniciados conjuntamente por meio do Docker, simplificando o processo de execução e tornando o ambiente de desenvolvimento mais organizado e padronizado.

## 7. Considerações finais

As melhorias realizadas nesta etapa contribuíram para o aprimoramento das funcionalidades de gerenciamento de registros, para a organização da estrutura do projeto e para a integração dos componentes da aplicação.

A implementação das rotas e das funcionalidades de edição e exclusão tornou o gerenciamento das informações mais prático. Além disso, a reorganização dos diretórios, a centralização da documentação e a configuração do Docker favoreceram a manutenção e a execução integrada do sistema VetTrace.
