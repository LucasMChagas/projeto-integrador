"""
Módulo de Gerenciamento de Banco de Dados
Gerencia operações CRUD com arquivos Excel
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import threading
from typing import Optional, Dict, List, Any

class DatabaseManager:
    """Gerenciador de banco de dados baseado em Excel"""
    
    def __init__(self):
        self.lock = threading.Lock()  # Lock para operações concorrentes
        self._cache = {}  # Cache para leituras frequentes
    
    def get_user_path(self, user_hash: str) -> Path:
        """Retorna o caminho da pasta do usuário"""
        return Path("data/users") / user_hash
    
    # ==================== PRODUTOS ====================
    
    def get_produtos(self, user_hash: str) -> pd.DataFrame:
        """Retorna todos os produtos do usuário"""
        cache_key = f"{user_hash}_produtos"
        
        # Verificar cache
        if cache_key in self._cache:
            return self._cache[cache_key].copy()
        
        file_path = self.get_user_path(user_hash) / 'produtos.xlsx'
        
        if file_path.exists():
            df = pd.read_excel(file_path)
            self._cache[cache_key] = df.copy()
            return df
        
        return pd.DataFrame()
    
    def add_produto(self, user_hash: str, produto_data: Dict) -> tuple:
        """Adiciona um novo produto"""
        try:
            with self.lock:
                file_path = self.get_user_path(user_hash) / 'produtos.xlsx'
                df = pd.read_excel(file_path) if file_path.exists() else pd.DataFrame()
                
                # Verificar SKU único
                if 'sku' in produto_data and produto_data['sku'] in df['sku'].values:
                    return False, "SKU já existe!"
                
                # Adicionar metadados
                produto_data['id'] = len(df) + 1
                produto_data['data_cadastro'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                produto_data['ultima_atualizacao'] = produto_data['data_cadastro']
                
                # Adicionar campos customizados se existirem
                custom_fields = self.get_custom_fields(user_hash, 'produtos')
                for field in custom_fields:
                    if field not in produto_data:
                        produto_data[field] = None
                
                # Adicionar ao DataFrame
                new_row = pd.DataFrame([produto_data])
                df = pd.concat([df, new_row], ignore_index=True)
                
                # Salvar
                df.to_excel(file_path, index=False)
                
                # Limpar cache
                self._clear_cache(f"{user_hash}_produtos")
                
                # Registrar no histórico
                self.add_historico(user_hash, 'CREATE', 'produto', produto_data['id'], None, produto_data)
                
                return True, "Produto adicionado com sucesso!"
                
        except Exception as e:
            return False, f"Erro ao adicionar produto: {str(e)}"
    
    def update_produto(self, user_hash: str, produto_id: int, produto_data: Dict) -> tuple:
        """Atualiza um produto existente"""
        try:
            with self.lock:
                file_path = self.get_user_path(user_hash) / 'produtos.xlsx'
                df = pd.read_excel(file_path)
                
                if produto_id not in df['id'].values:
                    return False, "Produto não encontrado!"
                
                # Guardar valores antigos para histórico
                old_values = df[df['id'] == produto_id].to_dict('records')[0]
                
                # Atualizar valores
                produto_data['ultima_atualizacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                for key, value in produto_data.items():
                    if key != 'id':  # Não permitir alteração do ID
                        df.loc[df['id'] == produto_id, key] = value
                
                # Salvar
                df.to_excel(file_path, index=False)
                
                # Limpar cache
                self._clear_cache(f"{user_hash}_produtos")
                
                # Registrar no histórico
                self.add_historico(user_hash, 'UPDATE', 'produto', produto_id, old_values, produto_data)
                
                return True, "Produto atualizado com sucesso!"
                
        except Exception as e:
            return False, f"Erro ao atualizar produto: {str(e)}"
    
    def delete_produto(self, user_hash: str, produto_id: int) -> tuple:
        """Remove um produto"""
        try:
            with self.lock:
                file_path = self.get_user_path(user_hash) / 'produtos.xlsx'
                df = pd.read_excel(file_path)
                
                if produto_id not in df['id'].values:
                    return False, "Produto não encontrado!"
                
                # Guardar valores para histórico
                old_values = df[df['id'] == produto_id].to_dict('records')[0]
                
                # Remover produto
                df = df[df['id'] != produto_id]
                
                # Salvar
                df.to_excel(file_path, index=False)
                
                # Limpar cache
                self._clear_cache(f"{user_hash}_produtos")
                
                # Registrar no histórico
                self.add_historico(user_hash, 'DELETE', 'produto', produto_id, old_values, None)
                
                return True, "Produto removido com sucesso!"
                
        except Exception as e:
            return False, f"Erro ao remover produto: {str(e)}"
    
    # ==================== PLATAFORMAS ====================
    
    def get_plataformas(self, user_hash: str) -> pd.DataFrame:
        """Retorna todas as plataformas do usuário"""
        cache_key = f"{user_hash}_plataformas"
        
        if cache_key in self._cache:
            return self._cache[cache_key].copy()
        
        file_path = self.get_user_path(user_hash) / 'plataformas.xlsx'
        
        if file_path.exists():
            df = pd.read_excel(file_path)
            self._cache[cache_key] = df.copy()
            return df
        
        return pd.DataFrame()
    
    def add_plataforma(self, user_hash: str, plataforma_data: Dict) -> tuple:
        """Adiciona uma nova plataforma"""
        try:
            with self.lock:
                file_path = self.get_user_path(user_hash) / 'plataformas.xlsx'
                df = pd.read_excel(file_path) if file_path.exists() else pd.DataFrame()
                
                # Verificar nome único
                if 'nome' in plataforma_data and plataforma_data['nome'] in df['nome'].values:
                    return False, "Plataforma já existe!"
                
                # Adicionar metadados
                plataforma_data['id'] = len(df) + 1
                plataforma_data['ativa'] = plataforma_data.get('ativa', True)
                plataforma_data['data_cadastro'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                plataforma_data['ultima_atualizacao'] = plataforma_data['data_cadastro']
                
                # Adicionar ao DataFrame
                new_row = pd.DataFrame([plataforma_data])
                df = pd.concat([df, new_row], ignore_index=True)
                
                # Salvar
                df.to_excel(file_path, index=False)
                
                # Limpar cache
                self._clear_cache(f"{user_hash}_plataformas")
                
                # Registrar no histórico
                self.add_historico(user_hash, 'CREATE', 'plataforma', plataforma_data['id'], None, plataforma_data)
                
                return True, "Plataforma adicionada com sucesso!"
                
        except Exception as e:
            return False, f"Erro ao adicionar plataforma: {str(e)}"
    
    def update_plataforma(self, user_hash: str, plataforma_id: int, plataforma_data: Dict) -> tuple:
        """Atualiza uma plataforma existente"""
        try:
            with self.lock:
                file_path = self.get_user_path(user_hash) / 'plataformas.xlsx'
                df = pd.read_excel(file_path)
                
                if plataforma_id not in df['id'].values:
                    return False, "Plataforma não encontrada!"
                
                # Guardar valores antigos para histórico
                old_values = df[df['id'] == plataforma_id].to_dict('records')[0]
                
                # Atualizar valores
                plataforma_data['ultima_atualizacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                for key, value in plataforma_data.items():
                    if key != 'id':  # Não permitir alteração do ID
                        df.loc[df['id'] == plataforma_id, key] = value
                
                # Salvar
                df.to_excel(file_path, index=False)
                
                # Limpar cache
                self._clear_cache(f"{user_hash}_plataformas")
                
                # Registrar no histórico
                self.add_historico(user_hash, 'UPDATE', 'plataforma', plataforma_id, old_values, plataforma_data)
                
                return True, "Plataforma atualizada com sucesso!"
                
        except Exception as e:
            return False, f"Erro ao atualizar plataforma: {str(e)}"
    
    def delete_plataforma(self, user_hash: str, plataforma_id: int) -> tuple:
        """Remove uma plataforma e suas taxas associadas"""
        try:
            with self.lock:
                # Remover plataforma
                file_path = self.get_user_path(user_hash) / 'plataformas.xlsx'
                df = pd.read_excel(file_path)
                
                if plataforma_id not in df['id'].values:
                    return False, "Plataforma não encontrada!"
                
                # Guardar valores para histórico
                old_values = df[df['id'] == plataforma_id].to_dict('records')[0]
                
                # Remover plataforma
                df = df[df['id'] != plataforma_id]
                df.to_excel(file_path, index=False)
                
                # Remover taxas associadas
                taxas_path = self.get_user_path(user_hash) / 'taxas_plataforma.xlsx'
                if taxas_path.exists():
                    df_taxas = pd.read_excel(taxas_path)
                    df_taxas = df_taxas[df_taxas['plataforma_id'] != plataforma_id]
                    df_taxas.to_excel(taxas_path, index=False)
                
                # Limpar cache
                self._clear_cache(f"{user_hash}_plataformas")
                
                # Registrar no histórico
                self.add_historico(user_hash, 'DELETE', 'plataforma', plataforma_id, old_values, None)
                
                return True, "Plataforma removida com sucesso!"
                
        except Exception as e:
            return False, f"Erro ao remover plataforma: {str(e)}"
    
    # ==================== TAXAS ====================
    
    def get_taxas_plataforma(self, user_hash: str, plataforma_id: Optional[int] = None) -> pd.DataFrame:
        """Retorna as taxas de uma plataforma ou todas as taxas"""
        file_path = self.get_user_path(user_hash) / 'taxas_plataforma.xlsx'
        
        if file_path.exists():
            df = pd.read_excel(file_path)
            if plataforma_id:
                df = df[df['plataforma_id'] == plataforma_id]
            return df
        
        return pd.DataFrame()
    
    def add_taxa(self, user_hash: str, taxa_data: Dict) -> tuple:
        """Adiciona uma nova taxa a uma plataforma"""
        try:
            with self.lock:
                file_path = self.get_user_path(user_hash) / 'taxas_plataforma.xlsx'
                df = pd.read_excel(file_path) if file_path.exists() else pd.DataFrame()
                
                # Adicionar ID e metadados
                taxa_data['id'] = len(df) + 1
                taxa_data['ativa'] = taxa_data.get('ativa', True)
                
                # Adicionar ao DataFrame
                new_row = pd.DataFrame([taxa_data])
                df = pd.concat([df, new_row], ignore_index=True)
                
                # Salvar
                df.to_excel(file_path, index=False)
                
                return True, "Taxa adicionada com sucesso!"
                
        except Exception as e:
            return False, f"Erro ao adicionar taxa: {str(e)}"
    
    def update_taxa(self, user_hash: str, taxa_id: int, taxa_data: Dict) -> tuple:
        """Atualiza uma taxa existente"""
        try:
            with self.lock:
                file_path = self.get_user_path(user_hash) / 'taxas_plataforma.xlsx'
                df = pd.read_excel(file_path)
                
                if taxa_id not in df['id'].values:
                    return False, "Taxa não encontrada!"
                
                # Atualizar valores
                for key, value in taxa_data.items():
                    if key != 'id':
                        df.loc[df['id'] == taxa_id, key] = value
                
                # Salvar
                df.to_excel(file_path, index=False)
                
                return True, "Taxa atualizada com sucesso!"
                
        except Exception as e:
            return False, f"Erro ao atualizar taxa: {str(e)}"
    
    def delete_taxa(self, user_hash: str, taxa_id: int) -> tuple:
        """Remove uma taxa"""
        try:
            with self.lock:
                file_path = self.get_user_path(user_hash) / 'taxas_plataforma.xlsx'
                df = pd.read_excel(file_path)
                
                if taxa_id not in df['id'].values:
                    return False, "Taxa não encontrada!"
                
                # Remover taxa
                df = df[df['id'] != taxa_id]
                
                # Salvar
                df.to_excel(file_path, index=False)
                
                return True, "Taxa removida com sucesso!"
                
        except Exception as e:
            return False, f"Erro ao remover taxa: {str(e)}"
    
    # ==================== CAMPOS CUSTOMIZADOS ====================
    
    def add_custom_field(self, user_hash: str, entity: str, field_name: str, field_type: str = 'text') -> tuple:
        """Adiciona um campo customizado para produtos ou plataformas"""
        try:
            file_path = self.get_user_path(user_hash) / 'campos_custom.json'
            
            # Carregar campos existentes
            with open(file_path, 'r') as f:
                campos = json.load(f)
            
            # Adicionar novo campo
            if entity not in campos:
                campos[entity] = {}
            
            campos[entity][field_name] = {
                'type': field_type,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Salvar
            with open(file_path, 'w') as f:
                json.dump(campos, f, indent=2)
            
            # Adicionar coluna no Excel correspondente
            if entity == 'produtos':
                excel_path = self.get_user_path(user_hash) / 'produtos.xlsx'
            elif entity == 'plataformas':
                excel_path = self.get_user_path(user_hash) / 'plataformas.xlsx'
            else:
                return False, "Entidade inválida!"
            
            if excel_path.exists():
                df = pd.read_excel(excel_path)
                if field_name not in df.columns:
                    df[field_name] = None
                    df.to_excel(excel_path, index=False)
            
            return True, "Campo customizado adicionado com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao adicionar campo: {str(e)}"
    
    def get_custom_fields(self, user_hash: str, entity: str) -> List[str]:
        """Retorna lista de campos customizados de uma entidade"""
        file_path = self.get_user_path(user_hash) / 'campos_custom.json'
        
        if file_path.exists():
            with open(file_path, 'r') as f:
                campos = json.load(f)
            
            if entity in campos:
                return list(campos[entity].keys())
        
        return []
    
    # ==================== HISTÓRICO ====================
    
    def add_historico(self, user_hash: str, tipo_acao: str, entidade: str, 
                     id_entidade: int, valores_anteriores: Any, valores_novos: Any):
        """Adiciona entrada no histórico"""
        try:
            file_path = self.get_user_path(user_hash) / 'historico.xlsx'
            df = pd.read_excel(file_path) if file_path.exists() else pd.DataFrame()
            
            novo_registro = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'tipo_acao': tipo_acao,
                'entidade': entidade,
                'id_entidade': id_entidade,
                'valores_anteriores': json.dumps(valores_anteriores, default=str) if valores_anteriores else None,
                'valores_novos': json.dumps(valores_novos, default=str) if valores_novos else None,
                'usuario': user_hash
            }
            
            new_row = pd.DataFrame([novo_registro])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Manter apenas últimos 1000 registros
            if len(df) > 1000:
                df = df.tail(1000)
            
            df.to_excel(file_path, index=False)
            
        except Exception as e:
            print(f"Erro ao adicionar histórico: {str(e)}")
    
    def get_historico(self, user_hash: str, limit: int = 100) -> pd.DataFrame:
        """Retorna o histórico de ações do usuário"""
        file_path = self.get_user_path(user_hash) / 'historico.xlsx'
        
        if file_path.exists():
            df = pd.read_excel(file_path)
            return df.tail(limit)
        
        return pd.DataFrame()
    
    # ==================== UTILITÁRIOS ====================
    
    def _clear_cache(self, key: Optional[str] = None):
        """Limpa o cache"""
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()
    
    def export_produtos_excel(self, user_hash: str) -> Optional[bytes]:
        """Exporta produtos para Excel"""
        try:
            df = self.get_produtos(user_hash)
            if not df.empty:
                import io
                buffer = io.BytesIO()
                df.to_excel(buffer, index=False)
                return buffer.getvalue()
        except:
            pass
        return None
    
    def import_produtos_excel(self, user_hash: str, file_data: bytes) -> tuple:
        """Importa produtos de um Excel"""
        try:
            import io
            df_new = pd.read_excel(io.BytesIO(file_data))
            
            # Validar colunas obrigatórias
            required = ['sku', 'nome', 'custo']
            if not all(col in df_new.columns for col in required):
                return False, "Arquivo deve conter colunas: SKU, Nome, Custo"
            
            # Processar cada produto
            success = 0
            errors = []
            
            for _, row in df_new.iterrows():
                produto_data = row.to_dict()
                ok, msg = self.add_produto(user_hash, produto_data)
                if ok:
                    success += 1
                else:
                    errors.append(f"Linha {_ + 1}: {msg}")
            
            if errors:
                return True, f"Importados {success} produtos. Erros: {', '.join(errors[:5])}"
            
            return True, f"Importados {success} produtos com sucesso!"
            
        except Exception as e:
            return False, f"Erro na importação: {str(e)}"
    
    def save_precificacao(self, user_hash: str, data: Dict) -> tuple:
        """Salva uma precificação calculada"""
        print("\n" + "*" * 60)
        print("SAVE_PRECIFICACAO CHAMADO!")
        print(f"User: {user_hash}")
        print(f"Data keys: {data.keys()}")
        print("*" * 60 + "\n")
        
        try:
            # Caminho do arquivo
            file_path = self.get_user_path(user_hash) / 'precificacoes.xlsx'
            print(f"Caminho do arquivo: {file_path}")
            
            # Ler ou criar DataFrame
            if file_path.exists():
                print("Arquivo existe, lendo...")
                df = pd.read_excel(file_path)
                print(f"Lido com sucesso: {len(df)} registros existentes")
            else:
                print("Arquivo não existe, criando novo DataFrame")
                df = pd.DataFrame()
            
            # Adicionar dados
            data['id'] = len(df) + 1
            data['data_calculo'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"Adicionando registro com ID: {data['id']}")
            
            # Criar nova linha e adicionar
            new_row = pd.DataFrame([data])
            df = pd.concat([df, new_row], ignore_index=True)
            print(f"DataFrame agora tem {len(df)} registros")
            
            # SALVAR
            print(f"Salvando arquivo em: {file_path}")
            df.to_excel(file_path, index=False)
            print("to_excel executado")
            
            # Verificar se salvou
            if file_path.exists():
                print(f"SUCESSO! Arquivo existe: {file_path}")
                df_check = pd.read_excel(file_path)
                print(f"Verificação: arquivo tem {len(df_check)} registros")
                return True, f"Precificação salva! Total: {len(df_check)} registros"
            else:
                print(f"ERRO! Arquivo não existe após salvar: {file_path}")
                return False, "Arquivo não foi criado"
                
        except Exception as e:
            print(f"\nERRO EM save_precificacao: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False, f"Erro: {str(e)}"
    
    def get_precificacoes(self, user_hash: str) -> pd.DataFrame:
        """Retorna todas as precificações salvas"""
        cache_key = f"{user_hash}_precificacoes"
        
        # Verificar cache
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            file_path = self.get_user_path(user_hash) / 'precificacoes.xlsx'
            
            if file_path.exists():
                df = pd.read_excel(file_path)
                self._cache[cache_key] = df
                return df
            
            return pd.DataFrame()
            
        except Exception:
            return pd.DataFrame()
    
    def add_custom_field(self, user_hash: str, entity_type: str, field_name: str, field_type: str) -> tuple:
        """Adiciona campo customizado para produtos ou plataformas"""
        try:
            # Por enquanto, armazenar em arquivo de configuração
            config_path = self.get_user_path(user_hash) / 'custom_fields.xlsx'
            
            if config_path.exists():
                df = pd.read_excel(config_path)
            else:
                df = pd.DataFrame(columns=['entity_type', 'field_name', 'field_type'])
            
            # Adicionar novo campo
            new_field = pd.DataFrame([{
                'entity_type': entity_type,
                'field_name': field_name,
                'field_type': field_type
            }])
            
            df = pd.concat([df, new_field], ignore_index=True)
            df.to_excel(config_path, index=False)
            
            return True, f"Campo '{field_name}' adicionado com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao adicionar campo: {str(e)}"