"""
Módulo de Autenticação
Gerencia login, registro e autenticação de usuários
"""

import hashlib
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import os

class AuthManager:
    """Gerenciador de autenticação de usuários"""
    
    def __init__(self):
        self.base_path = Path("data/users")
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.users_file = self.base_path / "users_index.xlsx"
        self._initialize_users_index()
    
    def _initialize_users_index(self):
        """Cria o arquivo índice de usuários se não existir"""
        if not self.users_file.exists():
            df = pd.DataFrame(columns=[
                'email', 'password_hash', 'name', 'user_folder_hash', 
                'created_at', 'last_login'
            ])
            df.to_excel(self.users_file, index=False)
    
    def _hash_password(self, password: str) -> str:
        """Gera hash SHA256 da senha"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_user_folder_hash(self, email: str, password: str) -> str:
        """Gera hash único para pasta do usuário"""
        combined = f"{email}{password}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def register(self, email: str, password: str, name: str) -> tuple:
        """
        Registra um novo usuário
        
        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        try:
            # Verificar se usuário já existe
            df = pd.read_excel(self.users_file)
            if email in df['email'].values:
                return False, "Este email já está cadastrado!"
            
            # Criar hashes
            password_hash = self._hash_password(password)
            user_folder_hash = self._generate_user_folder_hash(email, password)
            
            # Criar pasta do usuário
            user_path = self.base_path / user_folder_hash
            user_path.mkdir(exist_ok=True)
            
            # Adicionar usuário ao índice
            new_user = pd.DataFrame([{
                'email': email,
                'password_hash': password_hash,
                'name': name,
                'user_folder_hash': user_folder_hash,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'last_login': None
            }])
            
            df = pd.concat([df, new_user], ignore_index=True)
            df.to_excel(self.users_file, index=False)
            
            # Criar estrutura inicial do usuário
            self._create_user_structure(user_folder_hash)
            
            return True, "Usuário registrado com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao registrar usuário: {str(e)}"
    
    def login(self, email: str, password: str) -> tuple:
        """
        Realiza login do usuário
        
        Returns:
            tuple: (sucesso: bool, dados_usuario: dict ou None)
        """
        try:
            df = pd.read_excel(self.users_file)
            password_hash = self._hash_password(password)
            
            # Verificar credenciais
            user = df[(df['email'] == email) & (df['password_hash'] == password_hash)]
            
            if user.empty:
                return False, None
            
            # Atualizar último login
            df.loc[df['email'] == email, 'last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df.to_excel(self.users_file, index=False)
            
            user_data = {
                'email': email,
                'name': user['name'].values[0],
                'hash': user['user_folder_hash'].values[0],
                'created_at': user['created_at'].values[0]
            }
            
            return True, user_data
            
        except Exception as e:
            print(f"Erro no login: {str(e)}")
            return False, None
    
    def _create_user_structure(self, user_hash: str):
        """Cria a estrutura inicial de arquivos para o usuário"""
        user_path = self.base_path / user_hash
        
        # Criar arquivo de produtos
        produtos_df = pd.DataFrame(columns=[
            'id', 'sku', 'nome', 'descricao', 'custo', 'frete', 
            'categoria', 'peso', 'dimensoes', 'plataforma',
            'preco_calculado', 'margem_liquida', 
            'data_cadastro', 'ultima_atualizacao'
        ])
        produtos_df.to_excel(user_path / 'produtos.xlsx', index=False)
        
        # Criar arquivo de plataformas
        plataformas_df = pd.DataFrame(columns=[
            'id', 'nome', 'ativa', 'data_cadastro', 'ultima_atualizacao'
        ])
        plataformas_df.to_excel(user_path / 'plataformas.xlsx', index=False)
        
        # Criar arquivo de taxas
        taxas_df = pd.DataFrame(columns=[
            'id', 'plataforma_id', 'nome_taxa', 'tipo_taxa', 
            'valor', 'condicao', 'prioridade', 'ativa'
        ])
        taxas_df.to_excel(user_path / 'taxas_plataforma.xlsx', index=False)
        
        # Criar arquivo de histórico
        historico_df = pd.DataFrame(columns=[
            'timestamp', 'tipo_acao', 'entidade', 'id_entidade',
            'valores_anteriores', 'valores_novos', 'usuario'
        ])
        historico_df.to_excel(user_path / 'historico.xlsx', index=False)
        
        # Criar arquivo de campos customizados
        campos_custom = {
            'produtos': {},
            'plataformas': {}
        }
        with open(user_path / 'campos_custom.json', 'w') as f:
            json.dump(campos_custom, f, indent=2)
    
    def get_user_path(self, user_hash: str) -> Path:
        """Retorna o caminho da pasta do usuário"""
        return self.base_path / user_hash
    
    def change_password(self, email: str, old_password: str, new_password: str) -> tuple:
        """
        Altera a senha do usuário
        
        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        try:
            df = pd.read_excel(self.users_file)
            old_hash = self._hash_password(old_password)
            
            # Verificar senha atual
            user = df[(df['email'] == email) & (df['password_hash'] == old_hash)]
            if user.empty:
                return False, "Senha atual incorreta!"
            
            # Atualizar senha
            new_hash = self._hash_password(new_password)
            df.loc[df['email'] == email, 'password_hash'] = new_hash
            df.to_excel(self.users_file, index=False)
            
            return True, "Senha alterada com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao alterar senha: {str(e)}"