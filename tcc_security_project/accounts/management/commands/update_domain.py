from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
	help = 	'Atualiza o dominio do Site ID 1'

	def add_arguments(self, parser):
		parser.add_argument('domain', type=str, help='O novo domínio (sem https://)')

	def handle(self, *args, **kwargs):
		new_domain = kwargs['domain']

		clean_domain = new_domain.replace('https://', "").replace('http://', "").strip("/")

		try:
			site = Site.objects.get(pk=1)
			old_domain = site.domain
			site.domain = clean_domain
			site.name = "TCC CLoudflare Tunnel"
			site.save()
			self.stdout.write(self.style.SUCCESS(f"Sucesso! Site atualizado de '{old_domain}' para '{clean_domain}'"))
		except Site.DoesNotExist:
			self.stdout.write(self.style.ERROR('SITE ID 1 não encontrado.'))
