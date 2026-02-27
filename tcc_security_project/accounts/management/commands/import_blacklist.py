import requests
from django.core.management.base import BaseCommand
from django.core.validators import validate_ipv46_address
from django.core.exceptions import ValidationError
from accounts.models import BlockedIP

# URL de uma blacklist pública de exemplo (lista de IPs associados a scanners/bots)
# Existem muitas outras listas disponíveis online.
BLACKLIST_URL = "https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/firehol_level1.netset"

class Command(BaseCommand):
	help = 'Importa IPs de uma blacklist externa para o modeli BlockedIP.'

	def handle(self, *args, **options):
		self.stdout.write(self.style.NOTICE(f'Baixando blacklist de {BLACKLIST_URL}...'))

		try:
			response = requests.get(BLACKLIST_URL, timeout=30)
			response.raise_for_status() #levanta um erro se o download falhar
		except requests.ResquestException as e:
			self.stderr.write(self.style.ERROR(f'Erro ao baixar a blacklist: {e}'))
			return

		ips_added = 0
		ip_skipped = 0
		ips_invalid = 0

		#processa cada linha do arquivo baixado
		lines = response.text.splitlines()
		total_lines = len(lines)

		self.stdout.write(f'Processando {total_lines} linhas...')

		for line in lines:
			# ignora linhas comentadas (comecam com # ou vazias)
			ip_candidate = line.strip()
			if not ip_candidate or ip_candidate.startswith('#'):
				continue

			#valida se a linha é um endereço IP válido (IPv4 ou IPv6)
			try:
				validate_ipv46_address(ip_candidate)
				#tenta adicionar o IP ao banco.
				#get_or_create retorna o objeto e um booleano 'created'
				obj, created = BlockedIP.objects.get_or_create(ip_address=ip_candidate)

				if created:
					ips_added += 1
					#self.stdout.write(f'Adicionado: {ip_candidate}') #descomentar para log detalhado
				else:
					ips_skipped += 1 # IPjá existia na blacklist
			except ValidationError:
				ips_invalid += 1 # linha nao era um IP válido
			except Exception as e:
				self.stdout.write(self.style.ERROR(f'Erro ao processar IP {ip_candidate}: {e}'))

		# resumo
		self.stdout.write(self.style.SUCCESS(f'Importação concluída!'))
		self.stdout.write(f' - IPs adicionados: {ips_added}')
		self.stdout.write(f' - IPs já existentes (ignorados): {ip_skipped}')
