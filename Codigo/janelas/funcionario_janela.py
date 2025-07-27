import customtkinter as ctk
from tkinter import *
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Codigo.bancoDeDados.bd import Banco_Dados

class Funcionario(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gerenciamento")
        ctk.set_appearance_mode("dark")
        self.geometry("720x600")
        self.bd = Banco_Dados("empresa.db")
        self.create_widgets()

    # Mapeamento dos labels para os nomes das colunas no banco
    COLUNA_MAP = {
        "nome": "nome",
        "telefone": "telefone",
        "email": "email",
        "cpf": "cpf",
        "matrícula": "matricula",
        "salário": "salario",
        "função": "funcao"
    }

    def create_widgets(self):
        frame = ctk.CTkFrame(self)
        frame.pack(pady=40, padx=40, fill="x")

        btn_cadastrar = ctk.CTkButton(frame, text="Cadastrar Funcionários", command=self.mostrar_formulario_cadastro)
        btn_cadastrar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        btn_editar = ctk.CTkButton(frame, text="Editar Funcionários", command=self.mostrar_formulario_editar)
        btn_editar.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        btn_buscar = ctk.CTkButton(frame, text="Buscar Funcionários", command=self.mostrar_formulario_busca)
        btn_buscar.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)

        self.form_frame = None  # Frame do formulário

    def mostrar_formulario_cadastro(self):
        if self.form_frame:
            self.form_frame.destroy()

        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=20, padx=40, fill="x")

        labels = list(self.COLUNA_MAP.keys())
        self.entries = {}

        for i, label in enumerate(labels):
            ctk.CTkLabel(self.form_frame, text=label.capitalize() + ":").grid(row=i, column=0, sticky="w", pady=5)
            entry = ctk.CTkEntry(self.form_frame)
            entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
            self.entries[label] = entry

        self.form_frame.grid_columnconfigure(1, weight=1)

        btn_salvar = ctk.CTkButton(self.form_frame, text="Salvar", command=self.salvar_funcionario)
        btn_salvar.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def salvar_funcionario(self):
        dados = {self.COLUNA_MAP[k]: v.get() for k, v in self.entries.items()}
        try:
            self.bd.cadastrar_funcionario(
                dados["nome"],
                dados["telefone"],
                dados["email"],
                dados["cpf"],
                dados["matricula"],
                float(dados["salario"]),
                dados["funcao"]
            )
            ctk.CTkLabel(self.form_frame, text="Funcionário cadastrado com sucesso!", text_color="green").grid(row=8, column=0, columnspan=2, pady=5)
        except Exception as e:
            ctk.CTkLabel(self.form_frame, text=f"Erro: {e}", text_color="red").grid(row=8, column=0, columnspan=2, pady=5)

    def mostrar_formulario_busca(self):
        if self.form_frame:
            self.form_frame.destroy()

        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=20, padx=40, fill="x")

        labels = list(self.COLUNA_MAP.keys())
        self.busca_entries = {}

        for i, label in enumerate(labels):
            ctk.CTkLabel(self.form_frame, text=label.capitalize() + ":").grid(row=i, column=0, sticky="w", pady=5)
            entry = ctk.CTkEntry(self.form_frame)
            entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
            self.busca_entries[label] = entry

        self.form_frame.grid_columnconfigure(1, weight=1)

        btn_buscar = ctk.CTkButton(self.form_frame, text="Buscar", command=self.buscar_funcionarios)
        btn_buscar.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def buscar_funcionarios(self):
        filtros = {self.COLUNA_MAP[k]: v.get() for k, v in self.busca_entries.items() if v.get().strip() != ""}
        if not filtros:
            resultados = self.bd.mostrar_todos("funcionarios")
        else:
            query = "SELECT * FROM funcionarios WHERE "
            params = []
            conds = []
            for coluna, valor in filtros.items():
                conds.append(f"{coluna} LIKE ?")
                params.append(f"%{valor}%")
            query += " AND ".join(conds)
            conn = self.bd.conectar()
            cursor = conn.cursor()
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            conn.close()

        if self.form_frame:
            self.form_frame.destroy()
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=20, padx=40, fill="both", expand=True)

        labels = list(self.COLUNA_MAP.keys())

        if not resultados:
            ctk.CTkLabel(self.form_frame, text="Nenhum funcionário encontrado.").pack(pady=10)
            return

        for idx, f in enumerate(resultados):
            card = ctk.CTkFrame(self.form_frame, border_width=2, border_color="#444444")
            card.grid(row=idx // 2, column=idx % 2, padx=10, pady=10, sticky="nsew")
            for i, (label, valor) in enumerate(zip(labels, f[1:])):  # f[1:] ignora o ID
                ctk.CTkLabel(card, text=f"{label.capitalize()}: {valor}", anchor="w").pack(anchor="w", padx=10, pady=2)
            self.form_frame.grid_rowconfigure(idx // 2, weight=1)
            self.form_frame.grid_columnconfigure(idx % 2, weight=1)

    def mostrar_formulario_editar(self):
        if self.form_frame:
            self.form_frame.destroy()

        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=20, padx=40, fill="x")

        labels = list(self.COLUNA_MAP.keys())
        self.editar_entries = {}

        for i, label in enumerate(labels):
            ctk.CTkLabel(self.form_frame, text=label.capitalize() + ":").grid(row=i, column=0, sticky="w", pady=5)
            entry = ctk.CTkEntry(self.form_frame)
            entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
            self.editar_entries[label] = entry

        self.form_frame.grid_columnconfigure(1, weight=1)

        btn_buscar = ctk.CTkButton(self.form_frame, text="Buscar", command=self.buscar_funcionarios_editar)
        btn_buscar.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def buscar_funcionarios_editar(self):
        filtros = {self.COLUNA_MAP[k]: v.get() for k, v in self.editar_entries.items() if v.get().strip() != ""}
        if not filtros:
            resultados = self.bd.mostrar_todos("funcionarios")
        else:
            query = "SELECT * FROM funcionarios WHERE "
            params = []
            conds = []
            for coluna, valor in filtros.items():
                conds.append(f"{coluna} LIKE ?")
                params.append(f"%{valor}%")
            query += " AND ".join(conds)
            conn = self.bd.conectar()
            cursor = conn.cursor()
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            conn.close()

        if self.form_frame:
            self.form_frame.destroy()
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=20, padx=40, fill="both", expand=True)

        labels = list(self.COLUNA_MAP.keys())

        if not resultados:
            ctk.CTkLabel(self.form_frame, text="Nenhum funcionário encontrado.").pack(pady=10)
            return

        for idx, f in enumerate(resultados):
            card = ctk.CTkFrame(self.form_frame, border_width=2, border_color="#444444")
            card.grid(row=idx // 2, column=idx % 2, padx=10, pady=10, sticky="nsew")
            for i, (label, valor) in enumerate(zip(labels, f[1:])):
                ctk.CTkLabel(card, text=f"{label.capitalize()}: {valor}", anchor="w").pack(anchor="w", padx=10, pady=2)
            card.bind("<Button-1>", lambda e, funcionario=f: self.mostrar_formulario_edicao(funcionario=f))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, funcionario=f: self.mostrar_formulario_edicao(funcionario=f))
            self.form_frame.grid_rowconfigure(idx // 2, weight=1)
            self.form_frame.grid_columnconfigure(idx % 2, weight=1)

    def mostrar_formulario_edicao(self, funcionario):
        if self.form_frame:
            self.form_frame.destroy()

        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=20, padx=40, fill="x")

        labels = list(self.COLUNA_MAP.keys())
        self.edicao_entries = {}

        for i, (label, valor) in enumerate(zip(labels, funcionario[1:])):
            ctk.CTkLabel(self.form_frame, text=label.capitalize() + ":").grid(row=i, column=0, sticky="w", pady=5)
            entry = ctk.CTkEntry(self.form_frame)
            entry.insert(0, str(valor))
            entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
            self.edicao_entries[label] = entry

        self.form_frame.grid_columnconfigure(1, weight=1)

        btn_salvar = ctk.CTkButton(
            self.form_frame,
            text="Salvar Alterações",
            command=lambda: self.salvar_edicao_funcionario(funcionario[0])
        )
        btn_salvar.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def salvar_edicao_funcionario(self, funcionario_id):
        dados = {self.COLUNA_MAP[k]: v.get() for k, v in self.edicao_entries.items()}
        try:
            for coluna, valor in dados.items():
                if coluna == "salario":
                    valor = float(valor)
                self.bd.editar_funcionario(funcionario_id, coluna, valor)
            ctk.CTkLabel(self.form_frame, text="Funcionário atualizado com sucesso!", text_color="green").grid(row=8, column=0, columnspan=2, pady=5)
        except Exception as e:
            ctk.CTkLabel(self.form_frame, text=f"Erro: {e}", text_color="red").grid(row=8, column=0, columnspan=2, pady=5)

if __name__ == "__main__":
    app = Funcionario()
    app.mainloop()
