import streamlit as st
import io
import re
import json
import base64
import urllib.request
import urllib.error
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

st.set_page_config(page_title="Autoconhecimento | Avaliação comportamental", page_icon="💬")
st.title("💬 Chatbot de Autoconhecimento")
st.caption("Questionário de reflexão comportamental — 13 questões")

# Cada questão contém duas alternativas: (letra, descrição).
QUESTOES = [[('E',
   'Ao falar com os outros geralmente uso expressões faciais, tais como: sorrisos, caras feias '
   'e/ou aceno com a cabeça para enfatizar as ideias.'),
  ('C',
   'Ao falar com os outros, geralmente procuro controlar minhas emoções, me vejo mais como uma '
   'pessoa que não demonstra emoções, calma e reservada.')],
 [('D',
   'Geralmente chego até parecer que estou brigando quando quero enfatizar uma ideia ou um ponto '
   'de vista. Falo com muita certeza e firmeza.'),
  ('P',
   'Costumo ter muita cautela quando exponho uma ideia, preferindo observar a reação e opinião '
   'das pessoas antes de qualquer coisa.')],
 [('C',
   'Quando me relaciono com as pessoas, minhas atitudes são geralmente cuidadosas e analíticas.'),
  ('E',
   'Quando me relaciono com as pessoas, minhas atitudes são geralmente abertas e entusiastas.')],
 [('P',
   'Minha expressão facial e postura corporal são retraídas, às vezes causo a impressão de que '
   'tenho muita timidez e insegurança demais.'),
  ('D',
   'Minha expressão facial e postura corporal são expansivas, dando a impressão de que tenho '
   'agressividade ou quero me impor aos outros.')],
 [('P', 'Geralmente pareço ter cautela e lentidão nas minhas explicações e apresentações.'),
  ('D', 'Geralmente pareço ter objetividade e rapidez nas minhas explicações e apresentações.')],
 [('C', 'Gosto que as pessoas sejam específicas e me deem detalhes sobre as coisas'),
  ('E', 'Não me preocupo tanto com detalhes e ajo de uma maneira mais intuitiva.')],
 [('E', 'Tenho muita expressão. Me aproximo e uso muito as mãos quando converso com as pessoas.'),
  ('C',
   'Quando converso com as pessoas, mantenho minha postura. Faço poucos gestos com as mãos. '
   'Geralmente fico com as mãos fechadas ou apoiadas, ou as coloco no rosto pensativamente.')],
 [('D', 'Ao me apresentar às pessoas, procuro sorrir e dar um firme aperto de mão.'),
  ('P',
   'Ao me apresentar às pessoas, procuro demonstrar seriedade e cumprimentá-las discretamente.')],
 [('C',
   'Quando falo com as pessoas, procuro não me envolver emocionalmente, não contar piadinhas, '
   'nem contar fatos que não tenham importância.'),
  ('E',
   'Quando falo com as pessoas, geralmente me envolvo emocionalmente (positiva ou '
   'negativamente), gosto de contar piadas e falar sobre tudo.')],
 [('P', 'Quando converso, geralmente faço mais perguntas do que respostas'),
  ('D', 'Quando converso, geralmente faço mais afirmações do que perguntas')],
 [('D',
   'Geralmente tenho organização, clareza e objetividade nas minhas atitudes. Procuro sempre '
   'demonstrar o que estou querendo.'),
  ('P', 'Nem sempre consigo definir ou transmitir claramente o que estou querendo.')],
 [('E',
   'Normalmente, em meus relacionamentos, acredito que me veem como um indivíduo atencioso, uma '
   'pessoa que corresponde e aprecia o contato com os outros.'),
  ('C',
   'Normalmente, em meus relacionamentos, acredito que me veem como um indivíduo preocupado e '
   'uma pessoa um tanto cuidadosa no contato com os outros.')],
 [('D', 'Geralmente, em uma reunião, prefiro ouvir e só me pronunciar se for chamado.'),
  ('P', 'Em uma reunião, procuro sempre manifestar minha opinião seja ela contra ou a favor.')]]

PERFIS = {'Pragmático': 'Perfil pragmático\n'
               'Se você tem um perfil pragmático, provavelmente gosta de entender o que precisa ser feito e como '
               'chegar a um resultado. Você tende a valorizar a praticidade, a objetividade e soluções que funcionem '
               'no dia a dia. Isso não significa que você não tenha sentimentos ou imaginação: quer dizer que costuma '
               'se sentir mais seguro quando consegue transformar ideias em ações concretas.\n'
               'Como você costuma agir\n'
               'Você pode ser uma pessoa direta, organizada e focada. Quando surge um desafio, tende a perguntar: '
               '“Qual é o objetivo?”, “O que temos de fazer?” e “Qual é o próximo passo?”. Em vez de ficar muito tempo '
               'apenas conversando sobre um problema, prefere encontrar uma solução e colocá-la em prática.\n'
               'Por exemplo, se um trabalho em grupo está atrasado, você talvez organize as tarefas, combine prazos e '
               'ajude a equipe a retomar o foco. Se precisa escolher um curso, pode comparar o conteúdo, o tempo e as '
               'oportunidades que ele oferece antes de decidir.\n'
               'O que você costuma gostar\n'
               'Você pode gostar de:\n'
               '•\tTer objetivos claros e saber o que esperam de você.\n'
               '•\tResolver problemas e perceber que seu esforço trouxe um resultado.\n'
               '•\tPlanejar, organizar tarefas e acompanhar o progresso.\n'
               '•\tAprender algo que possa usar na prática.\n'
               '•\tConversar com clareza e tomar decisões com base em informações.\n'
               'O que pode incomodar você\n'
               'Talvez você se sinta desconfortável quando há muita demora para decidir, mudanças sem explicação ou '
               'conversas que não chegam a uma ação. Também pode se irritar quando as instruções são confusas ou '
               'quando as pessoas não cumprem os combinados.\n'
               'Lembre-se: nem toda situação tem uma solução imediata. Às vezes, ouvir com calma, considerar outras '
               'opiniões e dar espaço para a tentativa e o erro também ajuda você a chegar a bons resultados.\n'
               'Sabotadores para observar\n'
               'Seu desejo de fazer as coisas acontecerem pode ser uma qualidade, mas, em alguns momentos, pode '
               'atrapalhar. Observe se você:\n'
               '•\tFica impaciente quando os outros precisam de mais tempo.\n'
               '•\tQuer resolver tudo sozinho para garantir que saia como imaginou.\n'
               '•\tPresta tanta atenção ao resultado que esquece de reconhecer o próprio esforço.\n'
               '•\tDescarta uma ideia antes de escutar como ela poderia funcionar.\n'
               '•\tEvita demonstrar dúvidas ou pedir ajuda por achar que precisa dar conta de tudo.\n'
               'Quando perceber isso, experimente pausar e perguntar: “O que ainda não considerei?” ou “Como posso '
               'alcançar esse resultado sem deixar de cuidar das pessoas e de mim?”.\n'
               'Um conselho para sua vida profissional\n'
               'No trabalho, sua objetividade pode ajudar bastante. Procure ambientes em que os objetivos sejam claros '
               'e em que você possa organizar processos, resolver questões e acompanhar resultados. Ao mesmo tempo, '
               'lembre-se de que bons resultados também dependem de comunicação, cooperação e flexibilidade.\n'
               'Se algo mudar, tente entender o motivo antes de concluir que a mudança não funciona. E, ao trabalhar '
               'com outras pessoas, explique suas ideias com respeito e dê espaço para que elas contribuam.\n'
               'Um conselho para sua vida pessoal\n'
               'Nas relações, você pode demonstrar carinho ajudando, resolvendo problemas e cumprindo o que promete. '
               'Mas quem está perto de você talvez também precise de atenção, conversa e acolhimento, mesmo quando não '
               'há nada para “consertar”.\n'
               'Às vezes, em vez de oferecer uma solução, você pode perguntar: “Você quer que eu ajude a pensar no que '
               'fazer ou prefere que eu apenas escute?”. Essa pequena pergunta pode aproximar você das pessoas.\n'
               'Profissões que podem combinar com você\n'
               'Seu jeito pode combinar com áreas em que planejamento, organização, análise e resolução de problemas '
               'sejam importantes, como gestão de projetos, administração, logística, tecnologia, finanças, '
               'engenharia, produção, qualidade, operações e empreendedorismo.\n'
               'Isso não determina a profissão que você deve escolher. Uma carreira também precisa levar em conta seus '
               'interesses, valores, habilidades e oportunidades. O perfil pragmático pode ser um ponto de partida '
               'para você refletir sobre ambientes e tarefas em que se sente motivado.\n'
               'Se você se reconhece nesse perfil, sua capacidade de transformar planos em ações pode ser uma grande '
               'força. Use essa praticidade com abertura para aprender, escutar e ajustar o caminho quando necessário.',
 'Expressivo': 'Perfil expressivo\n'
               'Se você tem um perfil expressivo, provavelmente gosta de se comunicar, compartilhar ideias e criar '
               'conexão com as pessoas. Você pode demonstrar com facilidade o que pensa e sente, seja pela fala, pelas '
               'expressões do rosto, pelos gestos ou pelo jeito animado de contar uma história. Isso não quer dizer '
               'que você esteja sempre alegre ou queira ser o centro das atenções. Significa que a comunicação e a '
               'troca com as pessoas podem ser importantes para você.\n'
               'Como você costuma agir\n'
               'Você talvez goste de participar, conversar e contribuir com ideias. Em uma atividade em grupo, por '
               'exemplo, pode ajudar a deixar o ambiente mais animado, incentivar quem está quieto ou apresentar uma '
               'proposta com entusiasmo. Quando aprende algo de que gosta, pode sentir vontade de contar para outras '
               'pessoas e mostrar por que aquilo chamou sua atenção.\n'
               'O que você costuma gostar\n'
               'Você pode gostar de:\n'
               '•\tConversar, trocar ideias e conhecer pessoas.\n'
               '•\tTrabalhar em equipe e participar de atividades criativas.\n'
               '•\tTer espaço para apresentar suas ideias e mostrar o que sabe fazer.\n'
               '•\tAmbientes acolhedores, dinâmicos e cheios de interação.\n'
               '•\tReceber retorno sobre o que fez e perceber que sua contribuição foi valorizada.\n'
               'O que pode incomodar você\n'
               'Talvez seja difícil para você ficar muito tempo em tarefas solitárias ou repetitivas, especialmente '
               'quando não entende o propósito delas. Você também pode se sentir desanimado quando não tem espaço para '
               'participar, quando suas ideias são ignoradas ou quando o ambiente é muito rígido e pouco acolhedor.\n'
               'Mesmo assim, nem toda tarefa interessante será movimentada o tempo todo. Algumas atividades mais '
               'silenciosas e repetidas ajudam a concluir projetos importantes. Dividir o trabalho em etapas pequenas '
               'pode tornar essas tarefas mais leves.\n'
               'Sabotadores para observar\n'
               'Seu entusiasmo e sua facilidade para se comunicar são qualidades, mas podem atrapalhar quando você:\n'
               '•\tComeça várias coisas ao mesmo tempo e tem dificuldade para terminar.\n'
               '•\tFala antes de ouvir todas as opiniões.\n'
               '•\tDecide no impulso, sem conferir prazos ou detalhes.\n'
               '•\tAssume compromissos demais para agradar ou não perder uma oportunidade.\n'
               '•\tFica muito desanimado quando não recebe reconhecimento ou resposta imediata.\n'
               'Quando perceber isso, faça uma pausa e pergunte a si mesmo: “O que é prioridade agora?”, “Já ouvi o '
               'que a outra pessoa quis dizer?” e “Consigo cumprir esse compromisso com tranquilidade?”. Anotar ideias '
               'e combinar prazos também pode ajudar você a transformar entusiasmo em realização.\n'
               'Um conselho para sua vida profissional\n'
               'No trabalho, sua comunicação e sua capacidade de envolver as pessoas podem ser muito valiosas. Procure '
               'oportunidades para colaborar, apresentar ideias, atender pessoas ou participar de projetos. Ao mesmo '
               'tempo, cuide da organização: registre os combinados, confira os detalhes e reserve momentos para '
               'concluir o que começou.\n'
               'Antes de apresentar uma ideia, tente ouvir as necessidades da equipe ou do público. Assim, seu '
               'entusiasmo ganha ainda mais força, porque se conecta ao que as outras pessoas realmente precisam.\n'
               'Um conselho para sua vida pessoal\n'
               'Nas relações, você pode demonstrar carinho conversando, compartilhando experiências e buscando '
               'momentos juntos. Lembre-se de que cada pessoa mostra o que sente de um jeito diferente. Às vezes, '
               'alguém pode gostar muito de você mesmo sendo mais quieto ou precisando de um tempo sozinho.\n'
               'Procure escutar sem tentar preencher todo silêncio. Uma boa conversa acontece quando você pode se '
               'expressar e também conhecer o que a outra pessoa pensa e sente.\n'
               'Profissões que podem combinar com você\n'
               'Seu perfil pode combinar com atividades que envolvam comunicação, criatividade e contato com pessoas, '
               'como educação, comunicação, marketing, vendas, atendimento, produção de eventos, criação de conteúdo, '
               'relações públicas, artes, recursos humanos e empreendedorismo.\n'
               'Isso não significa que essas sejam as únicas profissões possíveis para você. Sua escolha também '
               'depende dos seus interesses, das habilidades que quer desenvolver, dos seus valores e das '
               'oportunidades disponíveis.\n'
               'Se você se reconhece nesse perfil, sua energia e sua facilidade para criar conexões podem abrir muitos '
               'caminhos. Use essas qualidades junto com a escuta, o planejamento e a persistência para levar suas '
               'ideias adiante.',
 'Integrador': 'Perfil integrador\n'
               'Se você tem um perfil integrador, provavelmente gosta de aproximar pessoas, ideias e pontos de vista. '
               'Você tende a perceber como cada pessoa pode contribuir e pode ajudar o grupo a encontrar um caminho em '
               'comum. Isso não significa que você precise concordar com todo mundo ou evitar qualquer conflito. '
               'Significa que costuma valorizar a colaboração e o respeito nas relações.\n'
               'Como você costuma agir\n'
               'Em um trabalho em grupo, por exemplo, você pode notar que duas pessoas têm ideias diferentes e ajudar '
               'cada uma a explicar o que está propondo. Depois, talvez encontre um jeito de juntar partes das duas '
               'ideias. Você também pode ser aquela pessoa que acolhe alguém novo, percebe quando uma pessoa ficou de '
               'fora ou pergunta ao grupo como todos podem participar.\n'
               'O que você costuma gostar\n'
               'Você pode gostar de:\n'
               '•\tTrabalhar em equipe e construir algo junto com outras pessoas.\n'
               '•\tConhecer diferentes opiniões e encontrar pontos em comum.\n'
               '•\tAjudar as pessoas a conversar e a se entender.\n'
               '•\tParticipar de ambientes respeitosos, acolhedores e cooperativos.\n'
               '•\tSentir que seu trabalho contribui para o bem-estar do grupo.\n'
               'O que pode incomodar você\n'
               'Talvez você se sinta desconfortável em ambientes muito competitivos, com discussões agressivas ou em '
               'que algumas pessoas não têm espaço para falar. Também pode achar difícil quando precisa escolher um '
               'lado em uma situação delicada.\n'
               'Ainda assim, diferenças e desacordos fazem parte da convivência. Nem sempre será possível deixar todos '
               'satisfeitos, e isso não significa que você falhou. É possível respeitar as pessoas e, ao mesmo tempo, '
               'defender uma decisão necessária.\n'
               'Sabotadores para observar\n'
               'Sua atenção às necessidades dos outros é uma qualidade, mas pode atrapalhar quando você:\n'
               '•\tConcorda com algo só para evitar uma discussão.\n'
               '•\tDeixa suas próprias necessidades sempre para depois.\n'
               '•\tTenta agradar a todos, mesmo quando isso não é possível.\n'
               '•\tAssume a responsabilidade por resolver conflitos que não dependem só de você.\n'
               '•\tDemora para tomar uma decisão por medo de desagradar alguém.\n'
               'Quando perceber isso, pergunte a si mesmo: “O que eu penso sobre essa situação?”, “O que é justo para '
               'mim e para as outras pessoas?” e “Posso expressar minha opinião com respeito?”. Colocar limites também '
               'é uma forma de cuidar das relações.\n'
               'Um conselho para sua vida profissional\n'
               'No trabalho, sua capacidade de colaborar e aproximar pessoas pode ser muito útil. Você pode contribuir '
               'em projetos coletivos, apoiar a comunicação entre equipes e ajudar a criar um ambiente em que as '
               'pessoas consigam participar. Lembre-se de que colaborar não significa fazer tudo pelos outros. Divida '
               'responsabilidades, expresse suas ideias e reconheça também o valor da sua contribuição.\n'
               'Um conselho para sua vida pessoal\n'
               'Nas relações pessoais, você pode ser alguém que oferece escuta, apoio e presença. Mas procure não '
               'esconder o que sente para manter a paz o tempo todo. Uma relação saudável permite que você escute e '
               'acolha os outros, mas também fale sobre o que precisa, pensa e sente.\n'
               'Você pode dizer, por exemplo: “Entendo o seu lado e também gostaria de explicar como me sinto”. Assim, '
               'abre espaço para o diálogo sem apagar a sua própria voz.\n'
               'Profissões que podem combinar com você\n'
               'Seu jeito pode combinar com áreas que envolvam colaboração, cuidado, diálogo e construção de relações, '
               'como educação, recursos humanos, mediação, serviço social, orientação profissional, atendimento, '
               'gestão de equipes, projetos comunitários, saúde e desenvolvimento de pessoas.\n'
               'Essas possibilidades não determinam sua escolha. Seus interesses, suas habilidades, seus valores e as '
               'oportunidades que encontrar também ajudam a escolher uma profissão que faça sentido para você.\n'
               'Se você se reconhece nesse perfil, sua habilidade para aproximar pessoas pode ser uma grande força. '
               'Continue construindo pontes, lembrando que a sua opinião e os seus limites também fazem parte de '
               'qualquer relação saudável.',
 'Analítico': 'Perfil analítico\n'
              'Se você tem um perfil analítico, provavelmente gosta de observar, entender e organizar as informações '
              'antes de tomar uma decisão. Você pode prestar atenção aos detalhes, comparar possibilidades e querer '
              'saber como as coisas funcionam. Isso não significa que você seja frio ou distante: talvez apenas '
              'prefira compreender bem uma situação antes de agir ou falar sobre ela.\n'
              'Como você costuma agir\n'
              'Quando recebe uma tarefa, você pode querer entender o objetivo, conferir as instruções e planejar cada '
              'etapa. Por exemplo, ao escolher um curso, talvez compare os conteúdos, os horários e as oportunidades '
              'que ele oferece. Em um trabalho em grupo, você pode perceber um dado que passou despercebido ou sugerir '
              'uma forma mais organizada de realizar a tarefa.\n'
              'O que você costuma gostar\n'
              'Você pode gostar de:\n'
              '•\tTer informações claras e instruções bem explicadas.\n'
              '•\tOrganizar dados, tarefas e ideias.\n'
              '•\tPesquisar, comparar opções e resolver problemas.\n'
              '•\tTer tempo para pensar antes de decidir.\n'
              '•\tFazer um trabalho cuidadoso e perceber que os detalhes estão corretos.\n'
              'O que pode incomodar você\n'
              'Talvez seja difícil trabalhar com informações confusas, mudanças de última hora ou decisões tomadas sem '
              'explicação. Você também pode se incomodar quando alguém ignora detalhes importantes ou pede uma '
              'resposta antes de você conseguir analisar a situação.\n'
              'Nem sempre, porém, será possível ter todas as informações ou esperar até sentir certeza total. Em '
              'alguns momentos, decidir com o que você já sabe e ajustar o caminho depois pode ser suficiente.\n'
              'Sabotadores para observar\n'
              'Seu cuidado e sua atenção aos detalhes são qualidades, mas podem atrapalhar quando você:\n'
              '•\tEspera ter certeza absoluta antes de começar.\n'
              '•\tRevê o mesmo trabalho muitas vezes por medo de cometer um erro.\n'
              '•\tAnalisa tantas possibilidades que acaba adiando a decisão.\n'
              '•\tDá mais atenção ao que está errado do que ao que já deu certo.\n'
              '•\tTem dificuldade para aceitar maneiras diferentes de fazer a mesma tarefa.\n'
              'Quando perceber isso, pergunte a si mesmo: “Tenho informações suficientes para dar o próximo passo?”, '
              '“Esse detalhe realmente muda o resultado?” e “O que posso aprender começando?”. Definir um prazo para '
              'analisar e outro para agir pode ajudar você a avançar.\n'
              'Um conselho para sua vida profissional\n'
              'No trabalho, sua capacidade de pesquisar, organizar e conferir informações pode fazer diferença. '
              'Procure tarefas em que possa analisar problemas, planejar processos, observar detalhes ou garantir '
              'qualidade. Também vale compartilhar suas conclusões de forma simples: explique o que encontrou, por que '
              'isso importa e qual passo sugere.\n'
              'Lembre-se de que um trabalho bem-feito não precisa ser perfeito em todos os detalhes. Combine critérios '
              'de qualidade com prazos e peça retorno quando isso puder ajudar você a seguir em frente.\n'
              'Um conselho para sua vida pessoal\n'
              'Nas relações, talvez você goste de pensar bastante antes de falar sobre o que sente. Tudo bem precisar '
              'de tempo, mas tente avisar as pessoas: “Quero pensar um pouco e depois conversamos”. Isso ajuda a '
              'evitar que seu silêncio pareça desinteresse.\n'
              'Também pode ser útil lembrar que nem toda conversa pede uma análise ou uma solução. Às vezes, a outra '
              'pessoa quer apenas ser ouvida. Você pode perguntar: “Você quer pensar comigo sobre uma solução ou '
              'prefere só me contar o que aconteceu?”.\n'
              'Profissões que podem combinar com você\n'
              'Seu jeito pode combinar com atividades que envolvam análise, investigação, organização e atenção aos '
              'detalhes, como pesquisa, tecnologia, contabilidade, finanças, engenharia, ciências, revisão de textos, '
              'controle de qualidade, planejamento e análise de dados.\n'
              'Essas são possibilidades para explorar, não uma lista que define seu futuro. Seus interesses, seus '
              'valores, suas habilidades e as experiências que deseja viver também ajudam você a escolher uma '
              'profissão.\n'
              'Se você se reconhece nesse perfil, sua atenção e seu jeito cuidadoso de pensar podem ajudar a encontrar '
              'soluções consistentes. Confie na sua capacidade de analisar e permita-se agir mesmo quando nem tudo '
              'estiver totalmente definido.'}

INTRODUCAO = 'A partir de agora vamos fazer alguns testes. Para cada uma das questões abaixo, você dispõe de duas alternativas. Dentre elas você deverá escolher a opção que mais se aproxima do seu modo de ser, mesmo que ela não descreva exatamente a sua forma de agir. Imagine, então, seu cotidiano e como você se comporta na maioria das vezes. Digite a letra que corresponde à alternativa. Vamos começar?'

# O PDF é montado em memória. Nenhum relatório é gravado em uma pasta pública.
def gerar_pdf(nome, idade, contagem, resultado, vencedores):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=45, leftMargin=45,
                            topMargin=54, bottomMargin=50, title="Relatório de Autoconhecimento")

    fonte = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    negrito = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    if fonte.exists() and negrito.exists():
        if "RelatorioSans" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("RelatorioSans", str(fonte)))
            pdfmetrics.registerFont(TTFont("RelatorioSans-Bold", str(negrito)))
        pdfmetrics.registerFontFamily("RelatorioSans", normal="RelatorioSans", bold="RelatorioSans-Bold")
        familia = "RelatorioSans"
        familia_bold = "RelatorioSans-Bold"
    else:
        # Alternativa com fonte embutida para ambientes que não têm DejaVu.
        familia, familia_bold = "Helvetica", "Helvetica-Bold"

    styles = {
        "titulo": ParagraphStyle("TituloRel", fontName=familia_bold, fontSize=18,
                                  leading=24, alignment=TA_CENTER, textColor=HexColor("#163D59"), spaceAfter=18),
        "subtitulo": ParagraphStyle("SubtituloRel", fontName=familia_bold, fontSize=12,
                                     leading=17, textColor=HexColor("#163D59"), spaceBefore=14, spaceAfter=7),
        "normal": ParagraphStyle("TextoRel", fontName=familia, fontSize=9.3,
                                  leading=15, spaceAfter=8),
    }
    story = [Paragraph("Relatório de Autoconhecimento", styles["titulo"]),
             Paragraph(f"<b>Participante:</b> {escape(str(nome))}", styles["normal"]),
             Paragraph(f"<b>Idade:</b> {idade} anos", styles["normal"]),
             Paragraph("Questionário comportamental de 13 questões", styles["normal"]),
             Paragraph("Contagem das alternativas", styles["subtitulo"])]
    story.append(Paragraph(" | ".join(f"{letra}: {contagem[letra]}" for letra in "CDEP"), styles["normal"]))
    story.append(Paragraph("Pontuação por perfil", styles["subtitulo"]))
    for perfil, valor in resultado.items():
        story.append(Paragraph(f"{escape(perfil)}: {valor} pontos", styles["normal"]))
    rotulo = "Perfil predominante" if len(vencedores) == 1 else "Perfis empatados na maior pontuação"
    story.append(Paragraph(rotulo + ": " + ", ".join(escape(v) for v in vencedores), styles["subtitulo"]))

    secoes = {"Como você costuma agir", "O que você costuma gostar", "O que pode incomodar você",
              "Sabotadores para observar", "Um conselho para sua vida profissional",
              "Um conselho para sua vida pessoal", "Profissões que podem combinar com você"}
    for perfil in vencedores:
        story.append(Paragraph(escape("Perfil " + perfil.lower()), styles["subtitulo"]))
        for linha in PERFIS[perfil].splitlines()[1:]:
            linha = linha.strip()
            if not linha:
                continue
            if linha in secoes:
                story.append(Paragraph(escape(linha), styles["subtitulo"]))
            else:
                # Texto de origem é texto puro; não interpretar marcação digitada por usuários.
                story.append(Paragraph(escape(linha).replace("\t", " "), styles["normal"]))

    story.append(Spacer(1, 16))
    story.append(Paragraph("Atividade de autoconhecimento, não um teste psicológico validado ou diagnóstico.",
                           styles["normal"]))
    story.append(Paragraph("Obrigado por chegar até aqui!", styles["normal"]))
    def rodape(canvas, doc_obj):
        canvas.setFont(familia, 8)
        canvas.setFillColor(HexColor("#667085"))
        canvas.drawRightString(A4[0]-45, 28, f"Página {doc_obj.page}")
    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    return buffer.getvalue()


def obter_config_email():
    # Na ausência dos Secrets, o download continua disponível.
    try:
        chave = st.secrets.get("RESEND_API_KEY", "")
        remetente = st.secrets.get("EMAIL_REMETENTE", "")
        return str(chave).strip(), str(remetente).strip()
    except (FileNotFoundError, KeyError):
        return "", ""


def enviar_pdf_por_email(destinatario, nome, pdf_bytes):
    chave, remetente = obter_config_email()
    if not chave or not remetente:
        raise ValueError("Envio por e-mail não configurado pelo responsável pelo aplicativo.")
    payload = {
        "from": remetente,
        "to": [destinatario],
        "subject": "Seu relatório de autoconhecimento",
        "html": (f"<p>Olá, {escape(nome)}!</p>"
                 "<p>Segue em anexo seu relatório de autoconhecimento em PDF.</p>"
                 "<p>Obrigado por participar!</p>"),
        "attachments": [{"filename": "relatorio_autoconhecimento.pdf",
                         "content": base64.b64encode(pdf_bytes).decode("ascii")}]
    }
    requisicao = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json",
                 "User-Agent": "AutoconhecimentoStreamlit/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(requisicao, timeout=20) as resposta:
        retorno = json.loads(resposta.read().decode("utf-8"))
    if not retorno.get("id"):
        raise RuntimeError("O serviço de e-mail não confirmou a solicitação.")
    return retorno["id"]


# Inicia uma conversa separada para cada visitante.
if "etapa" not in st.session_state:
    st.session_state.etapa = "nome"
    st.session_state.historico = [("assistant", "Olá, tudo bem? Qual é o seu nome?")]
    st.session_state.pontos = {"C": 0, "D": 0, "E": 0, "P": 0}
    st.session_state.indice = 0
    st.session_state.nome = ""
    st.session_state.idade = 0


def continuar(resposta, proxima_mensagem, nova_etapa):
    st.session_state.historico.append(("user", resposta))
    st.session_state.historico.append(("assistant", proxima_mensagem))
    st.session_state.etapa = nova_etapa
    st.rerun()


if st.button("🔄 Recomeçar a conversa"):
    for chave in list(st.session_state.keys()):
        del st.session_state[chave]
    st.rerun()

for autor, mensagem in st.session_state.historico:
    with st.chat_message(autor):
        st.write(mensagem)

etapa = st.session_state.etapa

if etapa == "nome":
    with st.form("form_nome"):
        nome = st.text_input("Seu nome", placeholder="Digite seu nome")
        ok = st.form_submit_button("Enviar")
    if ok:
        if nome.strip():
            st.session_state.nome = nome.strip()
            continuar(nome.strip(), f"Perfeito, {nome.strip()}! Vou te fazer umas perguntas, ok? Digite qualquer coisa para continuarmos.", "confirmacao")
        else:
            st.warning("Digite seu nome para prosseguir.")

elif etapa == "confirmacao":
    with st.form("form_confirmacao"):
        resposta = st.text_input("Sua resposta")
        ok = st.form_submit_button("Continuar")
    if ok:
        continuar(resposta or "Vamos lá!", "Diga-me a sua idade.", "idade")

elif etapa == "idade":
    with st.form("form_idade"):
        idade = st.number_input("Sua idade", min_value=1, max_value=120, step=1, value=18)
        ok = st.form_submit_button("Continuar")
    if ok:
        st.session_state.idade = idade
        continuar(str(idade), f"{st.session_state.nome}, {idade} anos.\n\n{INTRODUCAO}\n\n1) Sim\n\n2) Não", "inicio")

elif etapa == "inicio":
    with st.form("form_inicio"):
        resposta = st.radio("Deseja começar?", ["1) Sim", "2) Não"], index=None)
        ok = st.form_submit_button("Enviar")
    if ok:
        if resposta is None:
            st.warning("Selecione uma alternativa.")
        elif resposta.startswith("2"):
            continuar(resposta, "Quando estiver preparado, volte a me chamar. Até mais!", "encerrado")
        else:
            letra_a, texto_a = QUESTOES[0][0]
            letra_b, texto_b = QUESTOES[0][1]
            continuar(resposta, f"**Questão 01**\n\n**{letra_a}** — {texto_a}\n\n**{letra_b}** — {texto_b}", "perguntas")

elif etapa == "perguntas":
    indice = st.session_state.indice
    st.progress(indice / len(QUESTOES), text=f"Questão {indice + 1} de {len(QUESTOES)}")
    with st.form(f"form_questao_{indice}"):
        alternativas = QUESTOES[indice]
        escolha = st.radio("Qual alternativa combina mais com você?",
                           [f"{letra} — {descricao}" for letra, descricao in alternativas],
                           index=None)
        ok = st.form_submit_button("Responder e continuar")
    if ok:
        if escolha is None:
            st.warning("Selecione uma alternativa antes de continuar.")
        else:
            letra = escolha.split(" — ", 1)[0]
            st.session_state.pontos[letra] += 1
            st.session_state.indice += 1
            if st.session_state.indice == len(QUESTOES):
                continuar(escolha, "Obrigado por responder às 13 questões! Vamos conhecer seu resultado.", "resultado")
            else:
                proximo = st.session_state.indice
                (a, texto_a), (b, texto_b) = QUESTOES[proximo]
                continuar(escolha, f"**Questão {proximo+1:02d}**\n\n**{a}** — {texto_a}\n\n**{b}** — {texto_b}", "perguntas")

elif etapa == "resultado":
    contagem = st.session_state.pontos
    st.success(f"{st.session_state.nome}, você concluiu a avaliação!")
    st.subheader("Contagem de respostas")
    st.write(" | ".join(f"**{letra}:** {quantidade}" for letra, quantidade in contagem.items()))

    # Critério solicitado: somar as ocorrências das DUAS letras de cada perfil.
    resultado = {
        "Pragmático": contagem["C"] + contagem["D"],
        "Expressivo": contagem["D"] + contagem["E"],
        "Integrador": contagem["E"] + contagem["P"],
        "Analítico": contagem["P"] + contagem["C"],
    }
    maior_pontuacao = max(resultado.values())
    vencedores = [perfil for perfil, pontos in resultado.items() if pontos == maior_pontuacao]
    st.subheader("Pontuação por perfil")
    for perfil, pontos in resultado.items():
        st.write(f"**{perfil}:** {pontos} pontos")
    if len(vencedores) == 1:
        st.subheader(f"Seu perfil de maior pontuação: {vencedores[0]}")
    else:
        st.subheader("Empate entre perfis")
        st.write("Seus perfis com a maior pontuação foram: " + ", ".join(vencedores) + ".")
    for perfil in vencedores:
        st.divider()
        st.markdown(PERFIS[perfil])
    st.info("Este questionário é uma atividade de autoconhecimento e não um teste psicológico validado nem um diagnóstico.")
    st.write("**Obrigado por chegar até aqui!**")

    st.divider()
    st.subheader("📄 Seu relatório em PDF")
    pdf = gerar_pdf(st.session_state.nome, st.session_state.idade,
                    contagem, resultado, vencedores)
    st.download_button(
        "⬇️ Baixar meu relatório em PDF", data=pdf,
        file_name="relatorio_autoconhecimento.pdf", mime="application/pdf",
        use_container_width=True,
    )

    st.subheader("✉️ Receber o PDF por e-mail")
    chave, remetente = obter_config_email()
    if not (chave and remetente):
        st.info("O download já está disponível. O envio por e-mail será habilitado "
                "quando o responsável configurar o serviço de e-mail no Streamlit.")
    else:
        if st.session_state.get("email_enviado", False):
            st.success("Solicitação de envio recebida pelo serviço de e-mail. "
                       "Confira a caixa de entrada e o spam.")
        else:
            with st.form("form_enviar_email"):
                destinatario = st.text_input("Seu e-mail", placeholder="aluno@exemplo.com", max_chars=254)
                concorda = st.checkbox(
                    "Autorizo o envio do meu relatório comportamental para o e-mail informado."
                )
                enviar = st.form_submit_button("Enviar meu PDF por e-mail")
            if enviar:
                # Validação básica de endereço; entrega depende do provedor.
                valido = bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", destinatario.strip()))
                if not valido:
                    st.warning("Informe um endereço de e-mail válido.")
                elif not concorda:
                    st.warning("Marque a autorização para solicitar o envio.")
                else:
                    try:
                        with st.spinner("Solicitando o envio do relatório..."):
                            enviar_pdf_por_email(destinatario.strip(), st.session_state.nome, pdf)
                        st.session_state.email_enviado = True
                        st.success("Envio solicitado com sucesso! Confira sua caixa de entrada e spam.")
                    except urllib.error.HTTPError as erro:
                        st.error("Não foi possível solicitar o envio. Verifique com o responsável "
                                 "a configuração do remetente e do serviço de e-mail. "
                                 f"Código do serviço: {erro.code}.")
                    except (urllib.error.URLError, TimeoutError, ValueError, RuntimeError) as erro:
                        st.error("Não foi possível enviar o relatório por e-mail neste momento. "
                                 "Use o botão de download ou tente novamente mais tarde.")


elif etapa == "encerrado":
    st.info("A conversa foi encerrada. Use 'Recomeçar a conversa' quando quiser participar.")
