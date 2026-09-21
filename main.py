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
        self.configure(fg_color="#090D16")  # Fundo geral ainda mais escuro

        # Configuração do ícone personalizado da aplicação
        try:
            self.iconbitmap("stark_logo.ico")
        except Exception:
            pass

        self.attributes("-topmost", True)

        self.navegador = None
        self.ultimo_cargo = ""
        
        self.historico_conversas = []
        self.conversa_atual = []

        # ==================== LAYOUT PRINCIPAL (GRID) ====================
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==================== PAINEL PRINCIPAL: CHAT ====================
        self.main_chat_frame = ctk.CTkFrame(self, fg_color="#090D16", corner_radius=0)
        self.main_chat_frame.grid(row=0, column=0, sticky="nsew")

        # Cabeçalho com título centralizado e tom escuro
        self.header_frame = ctk.CTkFrame(
            self.main_chat_frame, fg_color="#0D1322", height=65, corner_radius=0
        )
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            self.header_frame,
            text="● Ativo",
            text_color="#10B981",
            font=("Segoe UI", 11, "bold"),
        )
        self.status_label.pack(side="right", padx=15, pady=15)

        self.header_label = ctk.CTkLabel(
            self.header_frame,
            text="STARK IA",
            text_color="#F8FAFC",
            font=("Segoe UI", 16, "bold"),
        )
        self.header_label.pack(side="top", pady=18)

        # Área de mensagens com tom escuro profundo
        self.chat_scroll = ctk.CTkScrollableFrame(
            self.main_chat_frame,
            fg_color="#0D1322",
            corner_radius=16,
            border_color="#1E293B",
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
            placeholder_text_color="#64748B",
            fg_color="#0D1322",
            text_color="#F8FAFC",
            border_color="#1E293B",
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

    def adicionar_balao_mensagem_direta(self, texto, is_user=False):
        msg_container = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        msg_container.pack(fill="x", pady=6, padx=5)

        if is_user:
            balao = ctk.CTkFrame(msg_container, fg_color="#1D4ED8", corner_radius=16)
            balao.pack(side="right", anchor="e", padx=(45, 0))
            lbl_texto = ctk.CTkLabel(balao, text=texto, font=("Segoe UI", 12), text_color="#FFFFFF", wraplength=250, justify="left")
            lbl_texto.pack(anchor="e", padx=14, pady=10)
        else:
            balao = ctk.CTkFrame(msg_container, fg_color="#161F33", corner_radius=16)
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

        balao = ctk.CTkFrame(container, fg_color="#161F33", corner_radius=16)
        balao.pack(side="left", anchor="w", padx=(0, 45))

        lbl_nome = ctk.CTkLabel(
            balao,
            text="STARK IA",
            font=("Segoe UI", 10, "bold"),
            text_color="#64748B",
        )
        lbl_nome.pack(anchor="w", padx=14, pady=(8, 0))

        lbl_texto = ctk.CTkLabel(
            balao,
            text="Buscando as melhores oportunidades...",
            font=("Segoe UI", 12, "italic"),
            text_color="#94A3B8",
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

        gatilhos_busca = ["procura", "procurar", "busca", "buscar", "vaga", "vagas", "emprego", "quero", "preciso", "estágio", "estagio", "ser", "trabalhar", "trampar"]
        tem_intencao_busca = any(g in msg_lower for g in gatilhos_busca)

        if not tem_intencao_busca and not self.ultimo_cargo and len(msg_lower.split()) < 2:
            resp = "Com certeza! Pode me dizer qual cargo e região você gostaria de pesquisar."
            self.adicionar_balao_mensagem(resp, is_user=False)
            return

        # ==================== DICIONÁRIO COMPLETO DE ESTADOS E CAPITAIS ====================
        mapeamento_regioes = {
            "sao paulo": "sao-paulo-sp", "são paulo": "sao-paulo-sp", "sp": "sao-paulo-sp",
            "rio de janeiro": "rio-de-janeiro-rj", "rj": "rio-de-janeiro-rj",
            "belo horizonte": "belo-horizonte-mg", "minas gerais": "belo-horizonte-mg", "mg": "belo-horizonte-mg",
            "vitoria": "vitoria-es", "vitória": "vitoria-es", "espirito santo": "vitoria-es", "espírito santo": "vitoria-es", "es": "vitoria-es",
            "curitiba": "curitiba-pr", "parana": "curitiba-pr", "paraná": "curitiba-pr", "pr": "curitiba-pr",
            "florianopolis": "florianopolis-sc", "florianópolis": "florianopolis-sc", "santa catarina": "florianopolis-sc", "sc": "florianopolis-sc",
            "porto alegre": "porto-alegre-rs", "rio grande do sul": "porto-alegre-rs", "rs": "porto-alegre-rs",
            "salvador": "salvador-ba", "bahia": "salvador-ba", "ba": "salvador-ba",
            "recife": "recife-pe", "pernambuco": "recife-pe", "pe": "recife-pe",
            "fortaleza": "fortaleza-ce", "ceara": "fortaleza-ce", "ceará": "fortaleza-ce", "ce": "fortaleza-ce",
            "sao luis": "sao-luis-ma", "são luís": "sao-luis-ma", "maranhao": "sao-luis-ma", "maranhão": "sao-luis-ma", "ma": "sao-luis-ma",
            "natal": "natal-rn", "rio grande do norte": "natal-rn", "rn": "natal-rn",
            "joao pessoa": "joao-pessoa-pb", "joão pessoa": "joao-pessoa-pb", "paraiba": "joao-pessoa-pb", "paraíba": "joao-pessoa-pb", "pb": "joao-pessoa-pb",
            "maceio": "maceio-al", "maceió": "maceio-al", "alagoas": "maceio-al", "al": "maceio-al",
            "aracaju": "aracaju-se", "sergipe": "aracaju-se", "se": "aracaju-se",
            "teresina": "teresina-pi", "piaui": "teresina-pi", "piauí": "teresina-pi", "pi": "teresina-pi",
            "manaus": "manaus-am", "amazonas": "manaus-am", "am": "manaus-am",
            "belem": "belem-pa", "belém": "belem-pa", "para": "belem-pa", "pará": "belem-pa", "pa": "belem-pa",
            "porto velho": "porto-velho-ro", "rondonia": "porto-velho-ro", "rondônia": "porto-velho-ro", "ro": "porto-velho-ro",
            "rio branco": "rio-branco-ac", "acre": "rio-branco-ac", "ac": "rio-branco-ac",
            "macapa": "macapa-ap", "macapá": "macapa-ap", "amapa": "macapa-ap", "amapá": "macapa-ap", "ap": "macapa-ap",
            "boa vista": "boa-vista-rr", "roraima": "boa-vista-rr", "rr": "boa-vista-rr",
            "palmas": "palmas-to", "tocantins": "palmas-to", "to": "palmas-to",
            "brasilia": "brasilia-df", "brasília": "brasilia-df", "df": "brasilia-df", "distrito federal": "brasilia-df",
            "goiania": "goiania-go", "goiânia": "goiania-go", "goias": "goiania-go", "goiás": "goiania-go", "go": "goiania-go",
            "cuiaba": "cuiaba-mt", "cuiabá": "cuiaba-mt", "mato grosso": "cuiaba-mt", "mt": "cuiaba-mt",
            "campo grande": "campo-grande-ms", "mato grosso do sul": "campo-grande-ms", "ms": "campo-grande-ms",
            "campinas": "campinas-sp", "santos": "santos-sp", "osasco": "osasco-sp",
            "niteroi": "niteroi-rj", "niteroí": "niteroi-rj", "londrina": "londrina-pr"
        }

        regiao_encontrada = None
        for regiao in sorted(mapeamento_regioes.keys(), key=len, reverse=True):
            padrao = r'(?:\b(?:em|no|na)\s+)?\b(' + re.escape(regiao) + r')\b'
            match = re.search(padrao, msg_lower)
            if match:
                regiao_encontrada = regiao
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
            "empregos", "oportunidade", "oportunidades", "trampo", "trabalhar", "trabalho", "trampar",
            "para", "em", "no", "na", "nos", "nas", "por", "hoje", "favor", "pfv", "porfavor",
            "um", "uma", "uns", "umas", "me", "mim", "pra", "pro", "ter", "como", "entao", "então", 
            "estagio", "estágio", "grande", "empresa", "junior", "júnior", "ser", "como",
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
        self.executar_busca_na_pagina(cargo_final, regiao_encontrada, mapeamento_regioes, balao_loading)

    def executar_busca_na_pagina(self, cargo, regiao_chave, mapeamento_regioes, balao_loading):
        try:
            if not self.navegador:
                opcoes = webdriver.ChromeOptions()
                opcoes.add_argument("--disable-blink-features=AutomationControlled")
                opcoes.add_experimental_option("excludeSwitches", ["enable-automation"])
                servico = Service(ChromeDriverManager().install())
                self.navegador = webdriver.Chrome(service=servico, options=opcoes)
                self.navegador.set_window_rect(x=50, y=50, width=950, height=950)

            cargo_url = cargo.lower().strip()
            cargo_url = (cargo_url.replace("á", "a").replace("à", "a").replace("ã", "a").replace("â", "a")
                                  .replace("é", "e").replace("ê", "e").replace("í", "i")
                                  .replace("ó", "o").replace("ô", "o").replace("õ", "o")
                                  .replace("ú", "u").replace("ç", "c"))
            cargo_url = re.sub(r'[^a-z0-9\s]', '', cargo_url)
            cargo_url = cargo_url.replace(" ", "-")

            if regiao_chave:
                regiao_url = mapeamento_regioes.get(regiao_chave)
                url_busca = f"https://www.catho.com.br/vagas/{cargo_url}/{regiao_url}/"
                self.navegador.get(url_busca)
                time.sleep(2.0)
            else:
                self.navegador.get("https://www.catho.com.br/")
                self.aceitar_cookies()
                time.sleep(1.5)

                script_cargo = f"""
                    let inputCargo = document.querySelector("input[name*='q']") || document.querySelector("input#searchId") || document.querySelector("input[placeholder*='Cargo']");
                    if (inputCargo) {{
                        inputCargo.focus();
                        inputCargo.value = "";
                        inputCargo.value = "{cargo}";
                        inputCargo.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        inputCargo.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                """
                self.navegador.execute_script(script_cargo)
                time.sleep(0.8)

                self.navegador.execute_script("""
                    let form = document.querySelector("form");
                    if (form) {
                        let submitBtn = form.querySelector("button[type='submit']") || form.querySelector("button");
                        if (submitBtn) { submitBtn.click(); }
                    }
                """)
                time.sleep(2.5)

            self.aceitar_cookies()
            balao_loading.destroy()

            if regiao_chave:
                self.adicionar_balao_mensagem(f"Prontinho! Pesquisei as vagas de '{cargo.title()}' em {regiao_chave.title()} e já exibi os resultados filtrados.", is_user=False)
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