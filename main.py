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
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class StarkIAApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("STARK IA")
        self.geometry("450x650+920+40")
        self.minsize(380, 500)
        self.configure(fg_color="#0F172A")

        self.attributes("-topmost", True)

        self.navegador = None
        self.ultimo_cargo = ""
        self.menu_lateral_aberto = False
        
        self.historico_conversas = []
        self.conversa_atual = []

        # ==================== LAYOUT PRINCIPAL (GRID) ====================
        self.grid_columnconfigure(0, weight=0)  # Menu Lateral
        self.grid_columnconfigure(1, weight=1)  # Painel do Chat
        self.grid_rowconfigure(0, weight=1)

        # ==================== PAINEL LATERAL (HISTÓRICO E COMANDOS) ====================
        self.sidebar_frame = ctk.CTkFrame(
            self, fg_color="#1E293B", corner_radius=0, width=320
        )
        self.sidebar_frame.grid_propagate(False)

        self.btn_nova_conversa = ctk.CTkButton(
            self.sidebar_frame,
            text="➕ Nova Conversa",
            fg_color="#2563EB",
            text_color="#FFFFFF",
            hover_color="#1D4ED8",
            corner_radius=8,
            height=38,
            font=("Segoe UI", 12, "bold"),
            command=self.criar_nova_conversa,
        )
        self.btn_nova_conversa.pack(pady=15, padx=15, fill="x")

        self.sidebar_scroll = ctk.CTkScrollableFrame(
            self.sidebar_frame,
            fg_color="#0F172A",
            corner_radius=12,
            border_color="#334155",
            border_width=1,
        )
        self.sidebar_scroll.pack(pady=(0, 15), padx=12, fill="both", expand=True)

        self.lbl_hist_titulo = ctk.CTkLabel(
            self.sidebar_scroll,
            text="🕒 Histórico de Conversas",
            text_color="#94A3B8",
            font=("Segoe UI", 12, "bold"),
        )
        self.lbl_hist_titulo.pack(pady=(10, 5), padx=5, anchor="w")

        self.frame_historico_lista = ctk.CTkFrame(self.sidebar_scroll, fg_color="transparent")
        self.frame_historico_lista.pack(fill="x", padx=0, pady=(0, 10))

        self.lbl_cmd_princ = ctk.CTkLabel(
            self.sidebar_scroll,
            text="⚡ Comandos Principais",
            text_color="#F8FAFC",
            font=("Segoe UI", 13, "bold"),
        )
        self.lbl_cmd_princ.pack(pady=(10, 5), padx=5, anchor="w")

        comandos_principais = [
            ("🔍 Vaga em São Paulo", "Quero procurar vaga de emprego em São Paulo"),
            ("💼 Estágio no Rio de Janeiro", "Quero procurar estágio em tecnologia no Rio de Janeiro"),
            ("🚀 Vaga Remota", "Quero procurar vaga remota"),
            ("🏢 Vaga em Curitiba", "Quero procurar vaga em grande empresa em Curitiba"),
            ("🎯 Vaga em Belo Horizonte", "Quero procurar vaga para júnior em Belo Horizonte"),
        ]

        for texto_btn, acao_texto in comandos_principais:
            btn_cmd = ctk.CTkButton(
                self.sidebar_scroll,
                text=texto_btn,
                fg_color="#2563EB",
                text_color="#FFFFFF",
                hover_color="#1D4ED8",
                anchor="w",
                corner_radius=8,
                height=36,
                font=("Segoe UI", 11, "bold"),
                command=lambda a=acao_texto: self.executar_comando_direto(a),
            )
            btn_cmd.pack(fill="x", pady=4, padx=4)

        self.lbl_cmd_gen = ctk.CTkLabel(
            self.sidebar_scroll,
            text="💡 Orientações e Dicas",
            text_color="#94A3B8",
            font=("Segoe UI", 13, "bold"),
        )
        self.lbl_cmd_gen.pack(pady=(15, 5), padx=5, anchor="w")

        comandos_genericos = [
            ("📝 Dicas para Entrevista", "Me dê dicas valiosas para ir bem em uma entrevista de emprego."),
            ("📄 Avaliar Perfil no Currículo", "Como posso destacar minhas habilidades no currículo para chamar atenção?"),
            ("🔄 Transição de Carreira Segura", "Como posso me planejar para fazer uma transição de carreira segura?"),
            ("📈 Habilidades em Alta no Mercado", "Quais são as competências profissionais mais exigidas pelo mercado atualmente?"),
        ]

        for texto_btn, acao_texto in comandos_genericos:
            btn_cmd = ctk.CTkButton(
                self.sidebar_scroll,
                text=texto_btn,
                fg_color="#334155",
                text_color="#F8FAFC",
                hover_color="#475569",
                anchor="w",
                corner_radius=8,
                height=36,
                font=("Segoe UI", 11),
                command=lambda a=acao_texto: self.executar_comando_direto(a),
            )
            btn_cmd.pack(fill="x", pady=4, padx=4)

        # ==================== PAINEL PRINCIPAL: CHAT ====================
        self.main_chat_frame = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=0)
        self.main_chat_frame.grid(row=0, column=1, sticky="nsew")

        self.header_frame = ctk.CTkFrame(
            self.main_chat_frame, fg_color="#1E293B", height=65, corner_radius=0
        )
        self.header_frame.pack(fill="x", side="top")

        self.btn_menu = ctk.CTkButton(
            self.header_frame,
            text="≡",
            width=40,
            height=35,
            fg_color="#334155",
            text_color="#F8FAFC",
            hover_color="#475569",
            corner_radius=6,
            font=("Segoe UI", 18, "bold"),
            command=self.alternar_menu,
        )
        self.btn_menu.pack(side="left", padx=15, pady=15)

        self.header_label = ctk.CTkLabel(
            self.header_frame,
            text="STARK IA",
            text_color="#F8FAFC",
            font=("Segoe UI", 16, "bold"),
        )
        self.header_label.pack(side="left", padx=5, pady=15)

        self.status_label = ctk.CTkLabel(
            self.header_frame,
            text="● Ativo",
            text_color="#10B981",
            font=("Segoe UI", 11, "bold"),
        )
        self.status_label.pack(side="right", padx=15, pady=15)

        self.chat_scroll = ctk.CTkScrollableFrame(
            self.main_chat_frame,
            fg_color="#1E293B",
            corner_radius=16,
            border_color="#334155",
            border_width=1,
        )
        self.chat_scroll.pack(pady=15, padx=15, fill="both", expand=True)

        self.input_frame = ctk.CTkFrame(
            self.main_chat_frame, fg_color="transparent"
        )
        self.input_frame.pack(fill="x", side="bottom", pady=15, padx=15)

        self.entry_msg = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Digite cargo e região (ex: Químico em São Paulo)...",
            placeholder_text_color="#94A3B8",
            fg_color="#1E293B",
            text_color="#F8FAFC",
            border_color="#334155",
            border_width=1.5,
            height=44,
            corner_radius=22,
            state="normal",
        )
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_msg.bind("<Return>", lambda event: self.enviar_mensagem())

        self.btn_enviar = ctk.CTkButton(
            self.input_frame,
            text="➤",
            width=44,
            height=44,
            fg_color="#2563EB",
            text_color="#FFFFFF",
            hover_color="#1D4ED8",
            corner_radius=22,
            font=("Segoe UI", 15, "bold"),
            command=self.enviar_mensagem,
            state="normal",
        )
        self.btn_enviar.pack(side="right")

        self.adicionar_balao_mensagem(
            "Olá! É um prazer ajudar você hoje. Como posso auxiliar na sua busca profissional?",
            is_user=False,
        )

    def alternar_menu(self):
        if self.menu_lateral_aberto:
            self.sidebar_frame.grid_forget()
            self.menu_lateral_aberto = False
        else:
            self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
            self.menu_lateral_aberto = True

    def criar_nova_conversa(self):
        if self.conversa_atual:
            titulo_resumo = self.conversa_atual[0][:22] + "..." if len(self.conversa_atual[0]) > 22 else self.conversa_atual[0]
            self.historico_conversas.append((titulo_resumo, list(self.conversa_atual)))
            self.atualizar_painel_historico()

        for widget in self.chat_scroll.winfo_children():
            widget.destroy()

        self.conversa_atual = []
        self.ultimo_cargo = ""
        self.adicionar_balao_mensagem("Nova conversa iniciada! Como posso ajudar você agora?", is_user=False)
        self.alternar_menu()

    def atualizar_painel_historico(self):
        for widget in self.frame_historico_lista.winfo_children():
            widget.destroy()

        for idx, (titulo, mensagens) in enumerate(reversed(self.historico_conversas)):
            btn_hist = ctk.CTkButton(
                self.frame_historico_lista,
                text=f"💬 {titulo}",
                fg_color="#334155",
                text_color="#CBD5E1",
                hover_color="#475569",
                anchor="w",
                corner_radius=6,
                height=30,
                font=("Segoe UI", 10),
                command=lambda m=mensagens: self.carregar_conversa_historico(m),
            )
            btn_hist.pack(fill="x", pady=2, padx=2)

    def carregar_conversa_historico(self, mensagens):
        for widget in self.chat_scroll.winfo_children():
            widget.destroy()

        self.conversa_atual = list(mensagens)
        for i, texto in enumerate(self.conversa_atual):
            is_u = (i % 2 == 0)
            self.adicionar_balao_mensagem_direta(texto, is_user=is_u)
        
        self.alternar_menu()

    def executar_comando_direto(self, acao):
        self.entry_msg.delete(0, "end")
        self.entry_msg.insert(0, acao)
        self.alternar_menu()
        self.enviar_mensagem()

    def adicionar_balao_mensagem_direta(self, texto, is_user=False):
        msg_container = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        msg_container.pack(fill="x", pady=6, padx=5)

        if is_user:
            balao = ctk.CTkFrame(msg_container, fg_color="#2563EB", corner_radius=16)
            balao.pack(side="right", anchor="e", padx=(45, 0))
            lbl_texto = ctk.CTkLabel(balao, text=texto, font=("Segoe UI", 12), text_color="#FFFFFF", wraplength=250, justify="left")
            lbl_texto.pack(anchor="e", padx=14, pady=10)
        else:
            balao = ctk.CTkFrame(msg_container, fg_color="#334155", corner_radius=16)
            balao.pack(side="left", anchor="w", padx=(0, 45))
            lbl_nome = ctk.CTkLabel(balao, text="STARK IA", font=("Segoe UI", 10, "bold"), text_color="#10B981")
            lbl_nome.pack(anchor="w", padx=14, pady=(8, 0))
            lbl_texto = ctk.CTkLabel(balao, text=texto, font=("Segoe UI", 12), text_color="#F8FAFC", wraplength=270, justify="left")
            lbl_texto.pack(anchor="w", padx=14, pady=(2, 10))
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def adicionar_balao_mensagem(self, texto, is_user=False):
        self.conversa_atual.append(texto)
        self.adicionar_balao_mensagem_direta(texto, is_user)
        return self.chat_scroll.winfo_children()[-1]

    def criar_balao_carregamento(self):
        container = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        container.pack(fill="x", pady=6, padx=5)

        balao = ctk.CTkFrame(container, fg_color="#334155", corner_radius=16)
        balao.pack(side="left", anchor="w", padx=(0, 45))

        lbl_nome = ctk.CTkLabel(
            balao,
            text="STARK IA",
            font=("Segoe UI", 10, "bold"),
            text_color="#94A3B8",
        )
        lbl_nome.pack(anchor="w", padx=14, pady=(8, 0))

        lbl_texto = ctk.CTkLabel(
            balao,
            text="✨ Buscando as melhores oportunidades...",
            font=("Segoe UI", 12, "italic"),
            text_color="#CBD5E1",
        )
        lbl_texto.pack(anchor="w", padx=14, pady=(2, 10))

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

    def processar_resposta_ia(self, mensagem):
        msg_raw = mensagem.strip()
        msg_lower = msg_raw.lower()
        time.sleep(0.3)

        if "entrevista" in msg_lower:
            resp = "Para ir bem em uma entrevista, pesquise bem sobre a empresa com antecedência, treine falar sobre suas principais conquistas profissionais com confiança e demonstre entusiasmo genuíno pela vaga!"
            self.adicionar_balao_mensagem(resp, is_user=False)
            return
        elif "currículo" in msg_lower or "curriculo" in msg_lower or "perfil" in msg_lower:
            resp = "Para destacar seu perfil, use verbos de ação nas suas experiências anteriores, coloque resultados numéricos alcançados e mantenha suas competências técnicas atualizadas de acordo com a vaga desejada."
            self.adicionar_balao_mensagem(resp, is_user=False)
            return
        elif "transição" in msg_lower or "transicao" in msg_lower:
            resp = "Uma transição segura envolve mapear as habilidades que você já tem (soft skills), estudar os requisitos da nova área e buscar cursos práticos ou projetos voluntários para construir portfólio."
            self.adicionar_balao_mensagem(resp, is_user=False)
            return
        elif "habilidades" in msg_lower or "competências" in msg_lower:
            resp = "Atualmente, o mercado valoriza muito a capacidade de adaptação rápida, inteligência emocional, resolução de problemas complexos e familiaridade com ferramentas tecnológicas modernas."
            self.adicionar_balao_mensagem(resp, is_user=False)
            return

        assuntos_proibidos = [
            "receita", "bolo", "futebol", "jogo", "fofoca",
            "filme", "piada", "musica", "música", "clima", "tempo",
            "historia", "história", "alemanha", "politica", "política", "presidente"
        ]
        if any(ap in msg_lower for ap in assuntos_proibidos):
            resp = "Desculpe, sou especializada em ajudar na busca por vagas de emprego e orientações de carreira. Como posso te ajudar nessa área?"
            self.adicionar_balao_mensagem(resp, is_user=False)
            return

        gatilhos_busca = ["procura", "procurar", "busca", "buscar", "vaga", "vagas", "emprego", "quero", "preciso", "estágio", "estagio", "ser"]
        tem_intencao_busca = any(g in msg_lower for g in gatilhos_busca)

        if not tem_intencao_busca and not self.ultimo_cargo:
            resp = "Com certeza! Pode me dizer qual cargo e região você gostaria de pesquisar."
            self.adicionar_balao_mensagem(resp, is_user=False)
            return

        locais_conhecidos = [
            "sao paulo", "são paulo", "sp", "rio de janeiro", "rj", "belo horizonte", "mg",
            "curitiba", "pr", "porto alegre", "rs", "salvador", "ba", "recife", "pe",
            "fortaleza", "ce", "manaus", "am", "brasilia", "brasília", "df", "goiania", "goiânia", "go",
            "florianopolis", "florianópolis", "sc", "vitoria", "vitória", "es", "cuiaba", "cuiabá", "mt",
            "campo grande", "ms", "belem", "belém", "pa", "santos", "campinas", "osasco", "sao bernardo", 
            "são bernardo", "santo andre", "santo andré", "niteroi", "niteroí", "zona sul", "zona leste", "zona norte", "zona oeste"
        ]

        regiao_encontrada = None
        for regiao in sorted(locais_conhecidos, key=len, reverse=True):
            padrao = r'(?:\b(?:em|no|na)\s+)?\b(' + re.escape(regiao) + r')\b'
            match = re.search(padrao, msg_lower)
            if match:
                regiao_encontrada = match.group(1).title()
                msg_lower = msg_lower.replace(match.group(0), "")
                break

        palavras_descartaveis = {
            "ola", "olá", "oi", "eai", "e ai", "salve", "suave", "fala", "hey",
            "opa", "mano", "cara", "velho", "bom", "dia", "boa", "tarde", "noite",
            "tudo", "bem", "ta", "tá", "beleza", "blz", "ok", "okay", "entendi", "certo",
            "pode", "ser", "sim", "massa", "top", "show", "perfeito", "obrigado", "obrigada",
            "valeu", "vlw", "agora", "quero", "querendo", "queria", "virar", "arrumar", "arranja",
            "busco", "buscar", "procurar", "procura", "pesquisar", "pesquisa", "achar", "encontrar",
            "preciso", "ver", "mostra", "mostre", "tem", "consigo", "vaga", "vagas", "emprego",
            "empregos", "oportunidade", "oportunidades", "trampo", "para", "em", "no", "na", "nos",
            "nas", "por", "hoje", "favor", "pfv", "porfavor", "ser",
            "um", "uma", "uns", "umas", "me", "mim", "pra", "pro", "ter", "como", "entao", "então", "estagio", "estágio", "grande", "empresa", "junior", "júnior"
        }

        cargos_curtos_validos = {"ti", "rh", "ui", "ux", "pr", "sem"}

        texto_limpo = re.sub(r"[^\w\s]", " ", msg_lower)
        tokens = texto_limpo.split()
        tokens_normalizados = [self.normalizar_palavra(word) for word in tokens]

        tokens_cargo = [
            word for word in tokens_normalizados
            if word not in palavras_descartaveis and (len(word) > 2 or word in cargos_curtos_validos)
        ]
        cargo_final = " ".join(tokens_cargo).strip()

        if not cargo_final and self.ultimo_cargo:
            cargo_final = self.ultimo_cargo
        elif cargo_final:
            self.ultimo_cargo = cargo_final

        if not cargo_final:
            resp = "Por favor, me informe qual cargo profissional você procura."
            self.adicionar_balao_mensagem(resp, is_user=False)
            return

        balao_loading = self.criar_balao_carregamento()
        self.executar_busca_na_pagina(cargo_final, regiao_encontrada, balao_loading)

    def executar_busca_na_pagina(self, cargo, regiao, balao_loading):
        try:
            if not self.navegador:
                opcoes = webdriver.ChromeOptions()
                opcoes.add_argument("--disable-blink-features=AutomationControlled")
                opcoes.add_experimental_option("excludeSwitches", ["enable-automation"])
                servico = Service(ChromeDriverManager().install())
                self.navegador = webdriver.Chrome(service=servico, options=opcoes)
                self.navegador.set_window_rect(x=50, y=50, width=950, height=950)

            # Abre o site da Catho
            self.navegador.get("https://www.catho.com.br/")
            self.aceitar_cookies()
            time.sleep(1.5)

            # Preenche o cargo
            try:
                input_cargo = WebDriverWait(self.navegador, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name*='q'], input#searchId, input[placeholder*='Cargo']"))
                )
                input_cargo.click()
                input_cargo.clear()
                for letra in cargo:
                    input_cargo.send_keys(letra)
                    time.sleep(0.03)
            except Exception:
                script_cargo = f"""
                    let inputCargo = document.querySelector("input[name*='q']") || document.querySelector("input#searchId") || document.querySelector("input[placeholder*='Cargo']");
                    if (inputCargo) {{
                        inputCargo.value = "{cargo}";
                        inputCargo.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                """
                self.navegador.execute_script(script_cargo)

            time.sleep(0.8)

            # Preenche a região e clica na sugestão da lista suspensa
            if regiao:
                try:
                    input_local = WebDriverWait(self.navegador, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name*='onde'], input#whereId, input[placeholder*='Localização']"))
                    )
                    input_local.click()
                    input_local.clear()
                    for letra in regiao:
                        input_local.send_keys(letra)
                        time.sleep(0.03)
                    
                    time.sleep(1.5)  # Aguarda a lista suspensa aparecer

                    # Clica na opção correta dentro da lista
                    sugestoes = self.navegador.find_elements(By.CSS_SELECTOR, "ul li, div[role='option'], .suggestion-item, .item-suggestion")
                    clicado = False
                    for sug in sugestoes:
                        if regiao.lower() in sug.text.lower():
                            sug.click()
                            clicado = True
                            break
                    if not clicado and sugestoes:
                        sugestoes[0].click()
                except Exception:
                    pass

            time.sleep(1.0)

            # >>> DISPARA A PESQUISA FORÇANDO VIA JAVASCRIPT O CLIQUE NO BOTÃO DE BUSCA DA PÁGINA <<<
            self.navegador.execute_script("""
                let botoes = document.querySelectorAll("button");
                for (let btn of botoes) {
                    let texto = btn.innerText.toLowerCase();
                    let aria = (btn.getAttribute('aria-label') || '').toLowerCase();
                    if (texto.includes("buscar") || texto.includes("vagas") || texto.includes("pesquisar") || aria.includes("buscar") || aria.includes("pesquisar")) {
                        btn.click();
                        return;
                    }
                }
                let form = document.querySelector("form");
                if (form) {
                    let submitBtn = form.querySelector("button[type='submit']");
                    if (submitBtn) { submitBtn.click(); return; }
                }
            """)

            time.sleep(2.5)
            self.aceitar_cookies()
            balao_loading.destroy()

            if regiao:
                self.adicionar_balao_mensagem(f"Prontinho! Pesquisei as vagas de '{cargo.title()}' em {regiao} e já exibi os resultados para você.", is_user=False)
            else:
                self.adicionar_balao_mensagem(f"Prontinho! Encontrei ótimas vagas para '{cargo.title()}' e já deixei a busca aberta na sua tela.", is_user=False)

        except Exception:
            balao_loading.destroy()
            self.adicionar_balao_mensagem("Tive uma pequena instabilidade ao abrir as vagas, mas já estou ajustando para você.", is_user=False)
            try:
                cargo_enc = urllib.parse.quote(cargo)
                self.navegador.get(f"https://www.catho.com.br/vagas/{cargo_enc}/")
            except Exception:
                self.navegador = None

    def aceitar_cookies(self):
        if not self.navegador:
            return
        try:
            time.sleep(1)
            self.navegador.execute_script("""
                let botoes = document.querySelectorAll("button");
                for (let btn of botoes) {
                    let texto = btn.innerText.toLowerCase();
                    if (texto.includes("aceitar") || texto.includes("permitir")) {
                        btn.click();
                        break;
                    }
                }
            """)
        except Exception:
            pass


if __name__ == "__main__":
    app = StarkIAApp()
    app.mainloop()