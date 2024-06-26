import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QMessageBox, QTableWidgetItem, QTableWidget, QDialog, QFormLayout, QDialogButtonBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sqlite3

class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('SUPERMERCADO COM PYQT')
        self.setGeometry(100, 100, 800, 600)
        self.conexao = sqlite3.connect('produtos.db')
        self.criar_tabela()
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout_principal = QVBoxLayout()
        central_widget.setLayout(layout_principal)
        titulo_label = QLabel('CADASTRO DE PRODUTOS', self)
        titulo_label.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(titulo_label)
        botoes_layout = QHBoxLayout()

        self.botao_adicionar = QPushButton('ADICIONAR', self)
        self.botao_adicionar.clicked.connect(self.abrir_janela_adicionar)
        botoes_layout.addWidget(self.botao_adicionar)

        self.botao_editar = QPushButton('EDITAR', self)
        self.botao_editar.clicked.connect(self.editar_produto)
        botoes_layout.addWidget(self.botao_editar)

        self.botao_deletar = QPushButton('APAGAR', self)
        self.botao_deletar.clicked.connect(self.deletar_produto)
        botoes_layout.addWidget(self.botao_deletar)

        layout_principal.addLayout(botoes_layout)
        self.tabela_produtos = QTableWidget(self)
        self.tabela_produtos.setColumnCount(4)
        self.tabela_produtos.setHorizontalHeaderLabels(['ID', 'NOME', 'PREÇO', 'QUANTIDADE'])
        layout_principal.addWidget(self.tabela_produtos)
        self.carregar_dados()

    def criar_tabela(self):
        cursor = self.conexao.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          nome TEXT,
                          preco REAL,
                          quantidade INTEGER
                          )''')
        self.conexao.commit()

    def carregar_dados(self):
        self.tabela_produtos.setRowCount(0)
        cursor = self.conexao.cursor()
        cursor.execute('SELECT * FROM produtos')
        dados = cursor.fetchall()
        for row_number, row_data in enumerate(dados):
            self.tabela_produtos.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tabela_produtos.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def abrir_janela_adicionar(self):
        dialog = DialogoAdicionar(self)
        if dialog.exec_() == QDialog.Accepted:
            nome = dialog.nome.text()
            preco = dialog.preco.text()
            quantidade = dialog.quantidade.text()
            self.inserir_produto(nome, preco, quantidade)

    def inserir_produto(self, nome, preco, quantidade):
        cursor = self.conexao.cursor()
        cursor.execute('INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)', (nome, preco, quantidade))
        self.conexao.commit()
        self.carregar_dados()

    def editar_produto(self):
        if self.tabela_produtos.selectedItems():
            selected_row = self.tabela_produtos.currentRow()
            id = self.tabela_produtos.item(selected_row, 0).text()
            nome = self.tabela_produtos.item(selected_row, 1).text()
            preco = self.tabela_produtos.item(selected_row, 2).text()
            quantidade = self.tabela_produtos.item(selected_row, 3).text()
            dialog = DialogoEditar(self, id, nome, preco, quantidade)
            if dialog.exec_() == QDialog.Accepted:
                novo_nome = dialog.nome.text()
                novo_preco = dialog.preco.text()
                nova_quantidade = dialog.quantidade.text()
                self.atualizar_produto(id, novo_nome, novo_preco, nova_quantidade)

    def atualizar_produto(self, id, nome, preco, quantidade):
        cursor = self.conexao.cursor()
        cursor.execute('UPDATE produtos SET nome=?, preco=?, quantidade=? WHERE id=?', (nome, preco, quantidade, id))
        self.conexao.commit()
        self.carregar_dados()

    def deletar_produto(self):
        if self.tabela_produtos.selectedItems():
            selected_row = self.tabela_produtos.currentRow()
            id = self.tabela_produtos.item(selected_row, 0).text()
            mensagem_box = QMessageBox(QMessageBox.Question, 'Confirmar Exclusão', 'Tem certeza que deseja excluir este produto?', QMessageBox.Yes | QMessageBox.No, self)
            if mensagem_box.exec_() == QMessageBox.Yes:
                cursor = self.conexao.cursor()
                cursor.execute('DELETE FROM produtos WHERE id=?', (id,))
                self.conexao.commit()
                self.carregar_dados()

    def closeEvent(self, event):
        self.conexao.close()
        event.accept()

class DialogoAdicionar(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('ADICIONAR PRODUTO')
        self.setModal(True)

        layout = QFormLayout(self)

        self.nome = QLineEdit(self)
        self.nome.setPlaceholderText('Nome do Produto')
        layout.addRow('Nome:', self.nome)

        self.preco = QLineEdit(self)
        self.preco.setPlaceholderText('Preço do Produto')
        layout.addRow('Preço:', self.preco)

        self.quantidade = QLineEdit(self)
        self.quantidade.setPlaceholderText('Quantidade do Produto')
        layout.addRow('Quantidade:', self.quantidade)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        layout.addRow(botoes)

class DialogoEditar(DialogoAdicionar):
    def __init__(self, parent=None, id='', nome='', preco='', quantidade=''):
        super().__init__(parent)

        self.setWindowTitle('EDITAR PRODUTO')
        self.setModal(True)

        self.id = id
        self.nome.setText(nome)
        self.preco.setText(preco)
        self.quantidade.setText(quantidade)

    def accept(self):
        super().accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec_())
