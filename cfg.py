import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog
import os
from tkinter import ttk
from tkinter import filedialog
from tkinter import ttk

ARQUIVO = "agenda.txt"

def carregar_tarefas():
    if not os.path.exists(ARQUIVO):
        return []
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        linhas = f.readlines()
    tarefas = [linha.strip() for linha in linhas]
    return tarefas

def salvar_tarefas(tarefas):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        for t in tarefas:
            f.write(t + "\n")

def atualizar_lista():
    for item in lista.get_children():
        lista.delete(item)
    tarefas = carregar_tarefas()
    for t in tarefas:
        partes = t.split(";")
        nome = partes[0]
        caminho = partes[1]
        tipo = partes[2]
        agendamento = partes[3]
        status = "Ativo" if tipo != "desativado" else "Desativado"
        lista.insert("", tk.END, values=(nome, status, tipo, agendamento, caminho))

def adicionar_tarefa():
    def salvar(nova):
        tarefas = carregar_tarefas()
        tarefas.append(";".join(nova))
        salvar_tarefas(tarefas)
        atualizar_lista()

    abrir_formulario(adicionar=True, salvar_callback=salvar)

def editar_tarefa():
    selecao = lista.focus()
    if selecao:
        valores = lista.item(selecao)["values"]
        tarefas = carregar_tarefas()
        
        # Identifica o índice correspondente no arquivo original
        idx = next((i for i, t in enumerate(tarefas) if t.startswith(valores[0])), None)

        if idx is not None:
            partes = tarefas[idx].split(";")

            def salvar(nova):
                tarefas[idx] = ";".join(nova)
                salvar_tarefas(tarefas)
                atualizar_lista()

            abrir_formulario(adicionar=False, dados=partes, salvar_callback=salvar)
    else:
        messagebox.showwarning("Edição", "Selecione uma tarefa para editar.")

def remover_tarefa():
    selecao = lista.focus()
    if selecao:
        valores = lista.item(selecao)["values"]
        tarefas = carregar_tarefas()

        idx = next((i for i, t in enumerate(tarefas) if t.startswith(valores[0])), None)

        if idx is not None:
            confirmar = messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover a tarefa '{valores[0]}'?")
            if confirmar:
                del tarefas[idx]
                salvar_tarefas(tarefas)
                atualizar_lista()
    else:
        messagebox.showwarning("Remoção", "Selecione uma tarefa para remover.")

def abrir_formulario(adicionar=True, dados=None, salvar_callback=None):
    janela = tk.Toplevel()
    janela.title("Adicionar Tarefa" if adicionar else "Editar Tarefa")

    # Nome
    tk.Label(janela, text="Nome do processo:").grid(row=0, column=0, sticky="w")
    nome_var = tk.StringVar(value=dados[0] if dados else "")
    tk.Entry(janela, textvariable=nome_var, width=50).grid(row=0, column=1)

    # Caminho
    tk.Label(janela, text="Caminho do arquivo:").grid(row=1, column=0, sticky="w")
    caminho_var = tk.StringVar(value=dados[1] if dados else "")
    caminho_entry = tk.Entry(janela, textvariable=caminho_var, width=50)
    caminho_entry.grid(row=1, column=1)
    def selecionar_arquivo():
        caminho = filedialog.askopenfilename(title="Selecionar Script", filetypes=[("Arquivos BAT", "*.bat"), ("Todos os arquivos", "*.*")])
        if caminho:
            caminho_var.set(caminho)
    tk.Button(janela, text="Selecionar arquivo...", command=selecionar_arquivo).grid(row=1, column=2)

    # Tipo de agendamento
    tk.Label(janela, text="Tipo de agendamento:").grid(row=2, column=0, sticky="w")
    tipo_var = tk.StringVar()
    tipo_combo = ttk.Combobox(
        janela,
        textvariable=tipo_var,
        values=["horario", "intervalo", "desativado"],
        state="readonly"
    )
    tipo_combo.grid(row=2, column=1, sticky="w")
    tipo_combo.set(dados[2] if dados else "desativado")  # Define o padrão


    # Agendamento
    tk.Label(janela, text="Horários (HH:MM) ou intervalo (min):").grid(row=3, column=0, sticky="w")
    agendamento_var = tk.StringVar(value=dados[3] if dados else "")
    tk.Entry(janela, textvariable=agendamento_var, width=50).grid(row=3, column=1)

    # Botões
    def confirmar():
        nova = [nome_var.get(), caminho_var.get(), tipo_var.get(), agendamento_var.get()]
        resumo = ";".join(nova)
        if not all(nova[:3]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return
        if messagebox.askyesno("Confirmar", f"Deseja salvar esta tarefa?\n\n{resumo}"):
            salvar_callback(nova)
            janela.destroy()

    def cancelar():
        if messagebox.askyesno("Cancelar", "Deseja cancelar sem salvar?"):
            janela.destroy()

    tk.Button(janela, text="Salvar", command=confirmar).grid(row=4, column=1, pady=10)
    tk.Button(janela, text="Cancelar", command=cancelar).grid(row=4, column=2)

    janela.grab_set()  # bloqueia interação com a janela principal

def reiniciar_agendador():
    servico_nome = "VIVO_AGENDADOR"
    confirmar = messagebox.askyesno(
        "Reiniciar Serviço",
        f"Tem certeza que deseja reiniciar o serviço '{servico_nome}'?"
    )
    if confirmar:
        try:
            subprocess.run(["sc", "stop", servico_nome], check=True)
            subprocess.run(["sc", "start", servico_nome], check=True)
            messagebox.showinfo("Serviço Reiniciado", f"O serviço '{servico_nome}' foi reiniciado com sucesso.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erro", f"Falha ao reiniciar o serviço:\n{e}")

# Interface gráfica

root = tk.Tk()
root.title("Gerenciador de Tarefas")

colunas = ("nome", "status", "tipo", "agendamento", "caminho")
lista = ttk.Treeview(root, columns=colunas, show="headings", height=10)
lista.heading("nome", text="Nome")
lista.heading("status", text="Status")
lista.heading("tipo", text="Tipo")
lista.heading("agendamento", text="Agendamento")
lista.heading("caminho", text="Caminho")

# Largura das colunas
lista.column("nome", width=150)
lista.column("status", width=80)
lista.column("tipo", width=100)
lista.column("agendamento", width=150)
lista.column("caminho", width=250)

lista.pack(pady=10)

botao_add = tk.Button(root, text="Adicionar", command=adicionar_tarefa)
botao_add.pack(side=tk.LEFT, padx=10)

botao_edit = tk.Button(root, text="Editar", command=editar_tarefa)
botao_edit.pack(side=tk.LEFT, padx=10)

botao_del = tk.Button(root, text="Remover", command=remover_tarefa)
botao_del.pack(side=tk.LEFT, padx=10)

botao_reiniciar = tk.Button(root, text="Reiniciar Serviço", command=reiniciar_agendador)
botao_reiniciar.pack(side=tk.LEFT, padx=10)

atualizar_lista()
root.mainloop()