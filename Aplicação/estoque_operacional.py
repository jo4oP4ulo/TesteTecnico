import sys

if len(sys.argv)!=3:
	print("""ERRO, OS ARQUIVOS DEVEM SER PASSADOS
  EX: "python3 estoque_operacional.py c1_vendas.txt c1_produtos.txt" """)
	sys.exit()

vendas_file, produtos_file = sys.argv[1:]

COD_CONFIRMADA  = [100, 102]

class Produto:
	"""
		produto: Código do Produto
		qt_co: Quantidade em estoque no início do período
		qt_min: Quantidade mínima que deve ser mantida no Centro Operacional
	"""

	def __init__(self, produto, qt_co, qt_min):
		self.produto = produto
		self.qt_co = qt_co
		self.qt_min = qt_min


class Venda:
	"""
		produto: Código do Produto
		qt_vendida: Quantidade vendida
		situacao: Situação da venda
			100: venda confirmada e com pagamento ok. 
			102: venda confirmada, mas com pagamento pendente 
			135: venda cancelada 
			190: venda não finalizada no canal de vendas 
			999: erro não identificado
		canal_venda: Canal de venda
			1: Representante comercial 
			2: Website 
			3: Aplicativo móvel Android 
			4: Aplicativo móvel iPhone
	"""

	def __init__(self, produto, qt_vendida, situacao, canal_venda):
		self.produto = produto
		self.qt_vendida = qt_vendida
		self.situacao = situacao
		self.canal_venda = canal_venda


class VendaTotal:

	class Balanco:
		def __init__(self, produto, qt_co, qt_min, t_venda, estoque):
			self.produto = produto
			self.qt_co = qt_co
			self.qt_min = qt_min
			self.t_venda = t_venda
			self.t_estoque = estoque

	def __init__(self):
		self.qt_vendas = {}
		
	def fazer_banlanco(self, venda, produto):
		if venda.situacao in COD_CONFIRMADA:
			if self.qt_vendas.get(venda.produto):
				self.qt_vendas[venda.produto].t_venda+=venda.qt_vendida
				self.qt_vendas[venda.produto].t_estoque-=venda.qt_vendida	
			else:
				self.qt_vendas[venda.produto] = self.Balanco(venda.produto, produto.qt_co, produto.qt_min, venda.qt_vendida, produto.qt_co-venda.qt_vendida)

	def balanco_total(self):
		f = open("transfere.txt",'w')
		
		f.write("Necessidade de Transferência Armazém para CO\n\n")
		f.write("Produto  QtCO  QtMin  QtVendas  Estq.após  Necess.  Transf. de\n")
		f.write("%41s%21s\n"%("Vendas","Arm p/ CO"))

		for produto in sorted(self.qt_vendas):
			necessidade = 0
			tranferencia = 0
			if (self.qt_vendas[produto].t_estoque < self.qt_vendas[produto].qt_min):
				necessidade = self.qt_vendas[produto].qt_min - self.qt_vendas[produto].t_estoque 
				tranferencia = necessidade
				if (necessidade>1 and necessidade<10):
					tranferencia = 10

			f.write("%2d%8d%7d%10d%11d%9d%12d\n"%(self.qt_vendas[produto].produto, self.qt_vendas[produto].qt_co, self.qt_vendas[produto].qt_min, self.qt_vendas[produto].t_venda, self.qt_vendas[produto].t_estoque, necessidade, tranferencia))
		f.close()		
		
def main():
	vendas = []
	produtos = {}

	with open(produtos_file) as produto_arq:
		for produto_todo in produto_arq:
			produto, qt_co, qt_min = produto_todo.strip().split(';')
			produto = int(produto)
			produtos[produto] = Produto(produto, int(qt_co), int(qt_min))
	
	with open(vendas_file) as vendas_arq:
		for venda in vendas_arq:
			produto, qt_vendida, situacao, canal_venda = venda.strip().split(';')
			vendas.append(Venda(int(produto), int(qt_vendida), int(situacao), int(canal_venda)))
	
	venda_total = VendaTotal()
	t_canal_venda = {
		1:0,
		2:0,
		3:0,
		4:0,
	}		

	f = open('DIVERGENCIAS.TXT', 'w')
	linha = 1
	for venda in vendas:
		if venda.produto in produtos:
			if venda.situacao == 999:
				f.write(f"Linha {linha} - Erro desconhecido. Acionar equipe de TI\n")
			if venda.situacao == 190:
				f.write(f"Linha {linha} - Venda não finalizada\n")
			if venda.situacao == 135:
				f.write(f"Linha {linha} - Venda cancelada\n")
			venda_total.fazer_banlanco(venda, produtos[venda.produto]);			
		else:
			if venda.situacao == 999:
				f.write(f"Linha {linha} - Erro desconhecido. Acionar equipe de TI\n")
			else:
				f.write(f"Linha {linha} - Código de Produto não encontrado {venda.produto}\n")

		if venda.situacao in COD_CONFIRMADA:
			t_canal_venda[venda.canal_venda]+=venda.qt_vendida	

		linha+=1
	
	f.close()

	venda_total.balanco_total()
	f = open("TOTCANAIS.TXT",'w')

	f.write("Quantidades de Vendas por canal\n\n")	
	f.write("""Canal                  QtVendas
1 - Representantes %12d
2 - Website        %12d
3 - App móvel Android %9d
4 - App móvel iPhone  %9d"""%(t_canal_venda[1], t_canal_venda[2], t_canal_venda[3], t_canal_venda[4]))
	f.close()

if __name__ == '__main__':
	main()