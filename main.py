import datetime
import re
import threading
import time
import urllib.parse
import customtkinter as ctk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class StarkIAApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Configurações da Janela principal
        self.title("STARK IA")
        self.geometry("400x600+920+100")
        self.resizable(False, False)
        self.configure(fg_color="#121212")

        # MANTÉM A JANELA DA IA SEMPRE POR CIMA
        self.attributes("-topmost", True)

        self.navegador = None
        self.ultimo_cargo = "" # Memória para guardar o último cargo pesquisado

        # Cabeçalho Dark Centralizado
        self.header_frame = ctk.CTkFrame(
            self, fg_color="#181818", height=60, corner_radius=0
        )
        self.header_frame.pack(fill="x", side="top")

        self.header_label = ctk.CTkLabel(
            self.header_frame,
            text="STARK IA",
            text_color="#FFFFFF",
            font=("Helvetica", 18, "bold"),
        )
        self.header_label.pack(pady=15)

        # Área de Scroll do Chat (Balões)
        self.chat_scroll = ctk.CTkScrollableFrame(
            self,
            width=370,
            height=440,
            fg_color="#1E1E1E",
            corner_radius=12,
        )
        self.chat_scroll.pack(pady=10, padx=15, fill="both", expand=True)

        # Entrada de mensagem
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", side="bottom", pady=15, padx=15)

        self.entry_msg = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Aguarde, inicializando o navegador...",
            placeholder_text_color="#888888",
            fg_color="#181818",
            text_color="#FFFFFF",
            border_color="#333333",
            border_width=1,
            height=42,
            width=300,
            corner_radius=20,  # Arredondado moderno
            state="disabled",  # Desativado de início
        )
        self.entry_msg.pack(side="left", padx=(0, 10))
        self.entry_msg.bind("<Return>", lambda event: self.enviar_mensagem())

        # BOTÃO REDONDO E AZUL
        self.btn_enviar = ctk.CTkButton(
            self.input_frame,
            text="➤",
            width=42,
            height=42,
            fg_color="#333333",
            text_color="#888888",
            hover_color="#444444",
            corner_radius=21,  # Formato circular
            font=("Helvetica", 14, "bold"),
            command=self.enviar_mensagem,
            state="disabled",  # Desativado de início
        )
        self.btn_enviar.pack(side="right")

        # Inicializa o navegador ao abrir o app
        threading.Thread(target=self.inicializar_navegador, daemon=True).start()

    def inicializar_navegador(self):
        try:
            opcoes = webdriver.ChromeOptions()
            opcoes.add_argument("--disable-blink-features=AutomationControlled")
            opcoes.add_experimental_option("excludeSwitches", ["enable-automation"])

            servico = Service(ChromeDriverManager().install())
            self.navegador = webdriver.Chrome(service=servico, options=opcoes)

            # Posiciona o navegador do lado esquerdo
            self.navegador.set_window_rect(x=50, y=100, width=860, height=620)
            self.navegador.get("https://www.catho.com.br/")

            self.aceitar_cookies()

            # Libera a entrada do usuário após o carregamento total
            self.entry_msg.configure(
                state="normal",
                placeholder_text="Converse comigo ou digite o cargo...",
            )
            self.btn_enviar.configure(
                state="normal",
                fg_color="#1F6AA5",  # Azul ao ativar
                text_color="#FFFFFF",
                hover_color="#144970",
            )

            # Mensagem de Boas-Vindas Inicial
            self.adicionar_balao_mensagem(
                "Olá! Eu sou a STARK IA, sua assistente automatizada para busca de empregos e desenvolvimento profissional. Como posso te ajudar hoje?",
                is_user=False,
            )

        except Exception as e:
            self.adicionar_balao_mensagem(
                f"Aviso: Não foi possível carregar o navegador ({e}).", is_user=False
            )

    def aceitar_cookies(self):
        """Procura e clica automaticamente em botões de aceitar cookies/LGPD via JavaScript para driblar bloqueios recentes."""
        if not self.navegador:
            return
        try:
            time.sleep(1)
            self.navegador.execute_script("""
                let botoes = document.querySelectorAll("button");
                for (let btn of botoes) {
                    let texto = btn.innerText.toLowerCase();
                    if (texto.includes("aceitar") || texto.includes("permitir") || texto.includes("ok")) {
                        btn.click();
                    }
                }
                // Tenta fechar especificamente o onetrust
                let onetrust = document.getElementById('onetrust-accept-btn-handler');
                if (onetrust) onetrust.click();
            """)
        except Exception:
            pass

    def adicionar_balao_mensagem(self, texto, is_user=False):
        """Cria e adiciona um balão de conversa visualmente formatado."""
        msg_container = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        msg_container.pack(fill="x", pady=4, padx=5)

        if is_user:
            # Balão do Usuário Compacto sem Nome
            balao = ctk.CTkFrame(
                msg_container,
                fg_color="#1F6AA5",  # Azul WhatsApp/Telegram
                corner_radius=14,
            )
            balao.pack(side="right", anchor="e", padx=(50, 0))

            lbl_texto = ctk.CTkLabel(
                balao,
                text=texto,
                font=("Helvetica", 12),
                text_color="#FFFFFF",
                wraplength=230,
                justify="left",
            )
            lbl_texto.pack(anchor="e", padx=12, pady=8)

        else:
            # Balão da IA com Nome da IA
            balao = ctk.CTkFrame(
                msg_container,
                fg_color="#2B2C2E",  # Cinza escuro elegante
                corner_radius=14,
            )
            balao.pack(side="left", anchor="w", padx=(0, 40))

            lbl_nome = ctk.CTkLabel(
                balao,
                text="STARK IA",
                font=("Helvetica", 10, "bold"),
                text_color="#00D26A",
            )
            lbl_nome.pack(anchor="w", padx=12, pady=(6, 0))

            lbl_texto = ctk.CTkLabel(
                balao,
                text=texto,
                font=("Helvetica", 12),
                text_color="#FFFFFF",
                wraplength=250,
                justify="left",
            )
            lbl_texto.pack(anchor="w", padx=12, pady=(2, 8))

        # Auto scroll para a última mensagem
        self.chat_scroll._parent_canvas.yview_moveto(1.0)
        return msg_container

    def criar_balao_carregamento(self):
        """Cria o balão cinza de carregamento com 3 pontinhos."""
        container = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        container.pack(fill="x", pady=4, padx=5)

        balao = ctk.CTkFrame(
            container,
            fg_color="#3A3B3C",  # Cinza
            corner_radius=14,
        )
        balao.pack(side="left", anchor="w", padx=(0, 40))

        lbl_nome = ctk.CTkLabel(
            balao,
            text="STARK IA",
            font=("Helvetica", 10, "bold"),
            text_color="#A0A0A0",
        )
        lbl_nome.pack(anchor="w", padx=12, pady=(6, 0))

        lbl_texto = ctk.CTkLabel(
            balao,
            text="Procurando vagas...",
            font=("Helvetica", 12, "italic"),
            text_color="#CCCCCC",
        )
        lbl_texto.pack(anchor="w", padx=12, pady=(2, 8))

        self.chat_scroll._parent_canvas.yview_moveto(1.0)
        return container

    def enviar_mensagem(self):
        if self.entry_msg.cget("state") == "disabled":
            return

        texto_usuario = self.entry_msg.get().strip()
        if not texto_usuario:
            return

        self.adicionar_balao_mensagem(texto_usuario, is_user=True)
        self.entry_msg.delete(0, "end")

        threading.Thread(
            target=self.processar_resposta_ia, args=(texto_usuario,), daemon=True
        ).start()

    def normalizar_palavra(self, palavra):
        return re.sub(r"(.)\1{2,}", r"\1", palavra)

    # =========================================================================
    # MOTOR INTELIGENTE DE ENTENDIMENTO DE LINGUAGEM E INTENÇÃO
    # =========================================================================
    def processar_resposta_ia(self, mensagem):
        msg_raw = mensagem.strip()
        msg_lower = msg_raw.lower()
        time.sleep(0.3)

        # 1. Filtro de Assuntos Fora de Escopo
        assuntos_proibidos = [
            "receita", "bolo", "futebol", "jogo", "fofoca", 
            "filme", "piada", "musica", "música", "clima", "tempo"
        ]
        if any(ap in msg_lower for ap in assuntos_proibidos):
            resposta = "Não é possível realizar esta ação, pois fui programada exclusivamente para te auxiliar na área profissional e busca de vagas de emprego."
            self.adicionar_balao_mensagem(resposta, is_user=False)
            return

        # 2. Pergunta de Data / Horário
        if any(d in msg_lower for d in ["dia de hoje", "data de hoje", "que dia e", "que dia é", "hoje"]) and not any(p in msg_lower for p in ["vaga", "emprego", "trabalho", "estagio", "quimico", "químico"]):
            data_atual = datetime.datetime.now().strftime("%d/%m/%Y")
            resposta = f"Hoje é dia {data_atual}. Qual oportunidade você gostaria de pesquisar hoje?"
            self.adicionar_balao_mensagem(resposta, is_user=False)
            return

        # 3. Pergunta sobre Identidade
        if "quem e voce" in msg_lower or "quem é você" in msg_lower or msg_lower == "stark":
            resposta = "Eu sou a STARK IA, sua assistente automatizada para busca de empregos e desenvolvimento profissional!"
            self.adicionar_balao_mensagem(resposta, is_user=False)
            return

        # 4. PALAVRAS A ELIMINAR (Adicionado 'entao', 'então', etc)
        palavras_descartaveis = {
            "ola", "olá", "oi", "eai", "e ai", "salve", "salvee", "suave", "fala", "hey",
            "opa", "opaa", "mano", "cara", "velho", "bom", "dia", "boa", "tarde", "noite",
            "tudo", "bem", "ta", "tá", "ta bem", "tá bem", "ta bom", "tá bom", "beleza",
            "blz", "ok", "okay", "entendi", "certo", "pode", "ser", "sim", "massa", "top",
            "show", "perfeito", "tmj", "obrigado", "obrigada", "valeu", "vlw", "agora",
            "quero", "querendo", "queria", "virar", "arrumar", "arranja", "busco", "buscar",
            "procurar", "procura", "pesquisar", "pesquisa", "achar", "encontrar", "preciso",
            "ver", "mostra", "mostre", "tem", "consigo", "vaga", "vagas", "emprego", "empregos",
            "oportunidade", "oportunidades", "trampo", "para", "em", "no", "na", "nos", "nas",
            "por", "sp", "sao", "paulo", "hoje", "favor", "pfv", "porfavor",
            "um", "uma", "uns", "umas", "me", "mim", "pra", "pro", "ter", "como", "entao", "então"
        }

        # Dicionário extra para mapear cidades conhecidas caso o usuário digite
        cidades_conhecidas = ["guaruja", "guarujá", "santos", "campinas", "osasco", "abc", "zona sul", "zona leste", "zona norte", "zona oeste"]
        cidade_identificada = None
        for cidade in cidades_conhecidas:
            if cidade in msg_lower:
                cidade_identificada = cidade.title()
                # Remove a cidade do texto para não ser lida como cargo
                msg_lower = msg_lower.replace(cidade, "")

        cargos_curtos_validos = {"ti", "rh", "ui", "ux", "pr", "sem"}

        texto_limpo = re.sub(r"[^\w\s]", " ", msg_lower)
        tokens = texto_limpo.split()
        tokens_normalizados = [self.normalizar_palavra(word) for word in tokens]

        tokens_cargo = [
            word for word in tokens_normalizados
            if word not in palavras_descartaveis and (len(word) > 2 or word in cargos_curtos_validos)
        ]
        cargo_final = " ".join(tokens_cargo).strip()

        # SISTEMA DE MEMÓRIA: Se não sobrou cargo, mas temos um cargo salvo e ele informou uma nova cidade (ex: "entao guaruja")
        if not cargo_final and self.ultimo_cargo and cidade_identificada:
            cargo_final = self.ultimo_cargo
        elif cargo_final:
            self.ultimo_cargo = cargo_final # Salva o cargo para a próxima interação

        if not cargo_final:
            resposta = "Perfeito! Quando quiser pesquisar alguma vaga, é só me dizer o cargo ou área profissional."
            self.adicionar_balao_mensagem(resposta, is_user=False)
            return

        # Define a região base (Se o usuário não falou cidade, vai pra Zona Sul padrão do código original)
        regiao_busca = cidade_identificada if cidade_identificada else "Zona Sul de SP"

        # Exibe o balão cinza de carregamento "Procurando vagas..."
        balao_loading = self.criar_balao_carregamento()

        # Executa a busca passando a região
        self.executar_busca_100_por_cento(cargo_final, regiao_busca, balao_loading)

    def executar_busca_100_por_cento(self, cargo, regiao, balao_loading):
        try:
            if not self.navegador:
                opcoes = webdriver.ChromeOptions()
                opcoes.add_argument("--disable-blink-features=AutomationControlled")
                servico = Service(ChromeDriverManager().install())
                self.navegador = webdriver.Chrome(service=servico, options=opcoes)
                self.navegador.set_window_rect(x=50, y=100, width=860, height=620)

            # 1. Carrega a página da Catho
            self.navegador.get("https://www.catho.com.br/")
            self.aceitar_cookies()
            time.sleep(1.5)

            # Ajusta o formato da string de busca de localização baseado no que foi pedido
            local_input = f"{regiao}, São Paulo - SP" if "SP" not in regiao and "São Paulo" not in regiao else regiao

            # 2. PREENCHIMENTO SEPARADO DOS CAMPOS (Lógica original mantida)
            preenchido_via_form = False
            try:
                inputs = self.navegador.find_elements(By.TAG_NAME, "input")
                campo_cargo = None
                campo_local = None

                for inp in inputs:
                    placeholder = (inp.get_attribute("placeholder") or "").lower()
                    if "cargo" in placeholder or "termo" in placeholder:
                        campo_cargo = inp
                    elif "localização" in placeholder or "cidade" in placeholder:
                        campo_local = inp

                if campo_cargo:
                    campo_cargo.click()
                    campo_cargo.send_keys(Keys.CONTROL + "a")
                    campo_cargo.send_keys(Keys.DELETE)
                    campo_cargo.send_keys(cargo)
                    time.sleep(0.3)

                if campo_local:
                    campo_local.click()
                    campo_local.send_keys(Keys.CONTROL + "a")
                    campo_local.send_keys(Keys.DELETE)
                    campo_local.send_keys(local_input)
                    time.sleep(0.4)
                    campo_local.send_keys(Keys.ENTER)
                    preenchido_via_form = True
                elif campo_cargo:
                    campo_cargo.send_keys(Keys.ENTER)
                    preenchido_via_form = True

            except Exception:
                preenchido_via_form = False

            # Se o preenchimento falhar, usa a URL direta
            if not preenchido_via_form:
                cargo_enc = urllib.parse.quote(cargo)
                local_enc = urllib.parse.quote(local_input)
                self.navegador.get(f"https://www.catho.com.br/vagas/{cargo_enc}/?q={cargo_enc}&onde={local_enc}")

            time.sleep(2)
            self.aceitar_cookies()

            # 3. LIMITADOR DE NO MÁXIMO 15 VAGAS (Lógica original)
            try:
                self.navegador.execute_script("""
                    let artigos = document.querySelectorAll('article');
                    if (artigos.length > 15) {
                        for (let i = 15; i < artigos.length; i++) {
                            artigos[i].remove();
                        }
                    }
                """)
            except Exception:
                pass

            self.navegador.execute_script("window.scrollTo(0, 500);")

            # Remove o balão cinza de carregamento antes de exibir a resposta final
            balao_loading.destroy()

            # 4. TRATAMENTO INTELIGENTE DAS LOCALIZAÇÕES (Lógica original adaptada para respeitar a cidade escolhida)
            vagas_encontradas = self.navegador.find_elements(By.TAG_NAME, "article")

            if not vagas_encontradas:
                self.adicionar_balao_mensagem(f"Não foram encontradas vagas para '{cargo.title()}' na região '{regiao}' no momento.", is_user=False)
                return

            # Se a região for Zona Sul, checa os bairros originais. Se for outra (ex: Guarujá), checa a própria cidade.
            if "zona sul" in regiao.lower():
                locais_alvo = ["zona sul", "santo amaro", "interlagos", "morumbi", "vila mariana", "moema", "jabaquara", "campo limpo", "campo grande", "brooklin", "pinheiros", "socorro", "grajau", "pedreira", "saude", "ipiranga", "aeroporto", "capao redondo", "jardim angela", "sacomã"]
            else:
                locais_alvo = [regiao.lower()]

            vagas_na_regiao_pedida = False
            outros_locais = set()

            for vaga in vagas_encontradas:
                texto_vaga = vaga.text.lower()
                if any(bairro in texto_vaga for bairro in locais_alvo):
                    vagas_na_regiao_pedida = True
                else:
                    linhas = vaga.text.split('\n')
                    for linha in linhas:
                        linha_limpa = linha.strip()
                        if ('sp' in linha_limpa.lower() or 'são paulo' in linha_limpa.lower() or '-' in linha_limpa) and not any(term in linha_limpa.lower() for term in ['r$', 'salário', 'mês', 'clt', 'pj']):
                            local_formatado = re.sub(r'^\d+\s*vagas?\s*-\s*', '', linha_limpa, flags=re.IGNORECASE)
                            if len(local_formatado) < 35:
                                outros_locais.add(local_formatado.title())

            if vagas_na_regiao_pedida:
                self.adicionar_balao_mensagem(f"Busca finalizada! Vagas para '{cargo.title()}' encontradas em {regiao} e exibidas no navegador.", is_user=False)
            else:
                locais_str = ", ".join(list(outros_locais)[:3]) if outros_locais else "outras regiões"
                self.adicionar_balao_mensagem(f"Aviso: Não foram encontradas vagas especificamente em {regiao} para '{cargo.title()}'. As vagas disponíveis foram encontradas em: {locais_str}.", is_user=False)

        except Exception:
            balao_loading.destroy()
            self.adicionar_balao_mensagem("Ocorreu uma oscilação na conexão com o navegador. Atualizando busca...", is_user=False)
            try:
                cargo_enc = urllib.parse.quote(cargo)
                self.navegador.get(f"https://www.catho.com.br/vagas/{cargo_enc}/")
                time.sleep(2)
                self.navegador.execute_script("window.scrollTo(0, 500);")
            except Exception:
                self.navegador = None

if __name__ == "__main__":
    app = StarkIAApp()
    app.mainloop()