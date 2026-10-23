import streamlit as st

st.set_page_config(page_title="Conversa sobre Autoconhecimento", page_icon="💬")
st.title("💬 Conversa sobre Autoconhecimento")
st.caption("Uma conversa educativa sobre diferentes estilos comportamentais")

PERFIS = {
    "1": ("Pragmática", "Então creio que você foca na praticidade, na objetividade e nos resultados reais, dando mais valor ao que funciona na prática do que a teorias, idealismos ou sentimentalismos."),
    "2": ("Expressiva", "Então você é aquela pessoa que demonstra com clareza, intensidade e facilidade o que está sentindo, pensando ou vivenciando, seja por meio da comunicação não verbal (expressões faciais, olhar, tom de voz, postura e gestos com as mãos) ou da fala."),
    "3": ("Integradora", "Então você é uma pessoa que coloca as pessoas em primeiro lugar e valoriza as relações sociais. Você é flexível, cordial, fraterno e apoiador. Esse perfil de profissional costuma criar bons laços de amizade e produz excelentes resultados nos trabalhos em equipe."),
    "4": ("Analista", "Então você é um profissional que coleta, processa e interpreta dados para orientar decisões estratégicas, resolver problemas e melhorar a eficiência de uma organização."),
}

Q1 = ("Primeira questão:\n\n1) Ao falar com os outros geralmente uso expressões faciais, tais como sorrisos, caras feias e/ou aceno com a cabeça para enfatizar as ideias.\n\n2) Ao falar com os outros, geralmente procuro controlar minhas emoções, me vejo mais como uma pessoa que não demonstra emoções, calma e reservada.\n\n**Digite 1 ou 2.**")
Q2 = ("Segunda questão:\n\n1) Geralmente chego até parecer que estou brigando quando quero enfatizar uma ideia ou um ponto de vista. Falo com muita certeza e firmeza.\n\n2) Costumo ter muita cautela quando exponho uma ideia, preferindo observar a reação e opinião das pessoas antes de qualquer coisa.\n\n**Digite 1 ou 2.**")


def iniciar():
    st.session_state.etapa = "nome"
    st.session_state.nome = ""
    st.session_state.mensagens = [{"role": "assistant", "content": "Olá, tudo bem? Qual é o seu nome?"}]


def falar(msg):
    st.session_state.mensagens.append({"role": "assistant", "content": msg})


if "etapa" not in st.session_state:
    iniciar()

for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

if st.session_state.etapa != "fim":
    texto = st.chat_input("Escreva sua resposta e pressione Enter...")
    if texto is not None:
        texto = texto.strip()
        if texto:
            st.session_state.mensagens.append({"role": "user", "content": texto})
            etapa = st.session_state.etapa
            escolha = texto.lower()
            if etapa == "nome":
                st.session_state.nome = texto
                falar(f"Perfeito, {texto}! Vou te fazer umas perguntas, ok?\n\nDigite qualquer coisa para continuarmos.")
                st.session_state.etapa = "confirmar"
            elif etapa == "confirmar":
                falar("Diga-me a sua idade.")
                st.session_state.etapa = "idade"
            elif etapa == "idade":
                if texto.isdecimal() and 1 <= int(texto) <= 120:
                    falar("Você se considera mais uma pessoa?\n\n1) Pragmática\n\n2) Expressiva\n\n3) Integradora\n\n4) Analista\n\n**Digite 1, 2, 3 ou 4.**")
                    st.session_state.etapa = "perfil"
                else:
                    falar("Por favor, digite sua idade em anos, usando um número válido.")
            elif etapa == "perfil":
                if escolha in PERFIS:
                    nome_perfil, descricao = PERFIS[escolha]
                    falar(f"**{nome_perfil}**\n\n{descricao}\n\nVocê está satisfeito com o seu perfil? (Sim/Não)")
                    st.session_state.etapa = "satisfeito"
                else:
                    falar("Escolha uma opção entre 1 e 4.")
            elif etapa == "satisfeito":
                if escolha in ("sim", "s"):
                    falar("Ótimo! Isso demonstra que você já está desenvolvendo o seu autoconhecimento.\n\nMuito obrigado por responder. Um abraço!")
                    st.session_state.etapa = "fim"
                elif escolha in ("não", "nao", "n"):
                    falar("Puxa, que tal fazer um teste comportamental? Gostaria?\n\n1) Sim\n\n2) Não")
                    st.session_state.etapa = "aceitar_teste"
                else:
                    falar("Responda sim ou não.")
            elif etapa == "aceitar_teste":
                if escolha in ("2", "não", "nao"):
                    falar("Então, muito obrigado por responder. Um abraço!")
                    st.session_state.etapa = "fim"
                elif escolha in ("1", "sim"):
                    falar("Vamos então às perguntas!\n\nDigite qualquer coisa para continuarmos.")
                    st.session_state.etapa = "continuar_teste"
                else:
                    falar("Digite 1 para Sim ou 2 para Não.")
            elif etapa == "continuar_teste":
                falar(Q1)
                st.session_state.etapa = "questao1"
            elif etapa == "questao1":
                if escolha == "1":
                    falar("Este é o comportamento de uma pessoa **integradora**.\n\n" + Q2)
                    st.session_state.etapa = "questao2"
                elif escolha == "2":
                    falar("Este é o comportamento de uma pessoa **analítica**.\n\n" + Q2)
                    st.session_state.etapa = "questao2"
                else:
                    falar("Por favor, escolha 1 ou 2.")
            elif etapa == "questao2":
                if escolha == "1":
                    falar("Este é o comportamento de uma pessoa **expressiva**.\n\nObrigado por responder às duas primeiras questões!")
                    st.session_state.etapa = "fim"
                elif escolha == "2":
                    falar("Este é o comportamento de uma pessoa **analítica**.\n\nObrigado por responder às duas primeiras questões!")
                    st.session_state.etapa = "fim"
                else:
                    falar("Por favor, escolha 1 ou 2.")
            st.rerun()

if st.button("🔄 Reiniciar conversa"):
    iniciar()
    st.rerun()

st.caption("Atividade de reflexão e autoconhecimento; não é avaliação psicológica validada. As respostas não são armazenadas em banco de dados.")
