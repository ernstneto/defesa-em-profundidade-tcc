from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
	help = 'Crai os grupos de segurança padrão (Níveis de acesso)'

	def handle(self, *args, **kwargs):
		groups = {
			'Nivel_1_Basico': 'Acesso apenas ao site web. Sem VPN.',
			'Nivel_2_Avançado': 'Acesso à VPN (Rota LAN). Funcionários remotos.',
			'Nivel_3_Admin': 'Acesso Total (VPN + Admin). Administradores de sistema.'
		}

		for name, desc in groups.items():
			group, created = Group.objects.get_or_create(name=name)
			if created:
				self.stdout.write(self.style.SUCCESS(f'Grupo criado: {name}'))
			else:
				self.stdout.write(f'Gupo ja existe: {name}')

		self.stdout.write(self.style.SUCCESS('--- Configuração de Grupos Concluida ---'))