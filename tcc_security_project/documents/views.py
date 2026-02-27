# documents/views.py

import io
import ipaddress
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.files.base import ContentFile

# Importação dos modelos e formulários
from .models import Document, AccessLog
from .forms import DocumentUploadForm

# Bibliotecas para Marca D'água (PDF)
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color

# --- FUNÇÕES AUXILIARES ---

def get_client_ip(request):
    """Tenta descobrir o IP real do cliente (Cloudflare/Nginx)"""
    cf_ip = request.META.get('HTTP_CF_CONNECTING_IP')
    if cf_ip:
        return cf_ip
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def add_watermark(pdf_bytes, user, ip):
    """Aplica marca d'água com dados do usuário no PDF"""
    try:
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        timestamp = timezone.now().strftime("%d/%m/%Y %H:%M")
        
        # Texto: QUEM baixou, QUANDO e de ONDE
        text = f"RASTREADO: {user.username} | IP: {ip} | {timestamp}"
        
        can.setFillColor(Color(1, 0, 0, alpha=0.3)) # Vermelho transparente
        can.setFont("Helvetica-Bold", 12)
        # Desenha no rodapé e topo
        can.drawString(20, 20, text) 
        can.drawString(20, 800, text)
        can.save()
        packet.seek(0)
        
        watermark_pdf = PdfReader(packet)
        original_pdf = PdfReader(io.BytesIO(pdf_bytes))
        output = PdfWriter()

        for page in original_pdf.pages:
            page.merge_page(watermark_pdf.pages[0])
            output.add_page(page)
            
        output_stream = io.BytesIO()
        output.write(output_stream)
        return output_stream.getvalue()
    except Exception as e:
        print(f"Erro na marca d'água: {e}")
        return pdf_bytes # Se falhar, devolve original sem marca

# --- VIEWS PRINCIPAIS ---

@login_required
def document_list_view(request):
    user_ip = get_client_ip(request)
    is_secure_network = False
    try:
        # Considera seguro se for IP privado (VPN/LAN) ou localhost
        ip_obj = ipaddress.ip_address(user_ip)
        if ip_obj.is_private or user_ip == '127.0.0.1':
            is_secure_network = True
    except:
        pass

    # Filtra a lista baseada na rede
    if is_secure_network:
        docs = Document.objects.all().order_by('-upload_at')
    else:
        # Quem está fora da VPN não vê os confidenciais
        docs = Document.objects.exclude(classification='CONFIDENTIAL').order_by('-upload_at')

    return render(request, 'documents/list.html', {'docs': docs})

@login_required
def upload_document_view(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            
            # Lógica: Criar arquivo a partir de texto se não houver upload
            text_content = form.cleaned_data.get('text_content')
            
            if not doc.file and text_content:
                filename = f"{doc.title.replace(' ', '_')}.txt"
                doc.file.save(filename, ContentFile(text_content.encode('utf-8')), save=False)
            
            doc.save() # Dispara a criptografia no model
            return redirect('documents:list')
    else:
        form = DocumentUploadForm()
        
    return render(request, 'documents/upload.html', {'form': form})

@login_required
def secure_download_view(request, doc_id):
    doc = get_object_or_404(Document, pk=doc_id)
    ip = get_client_ip(request)
    allowed = True
    
    # 1. VERIFICAÇÃO DE SEGURANÇA (DLP)
    if doc.classification == 'CONFIDENTIAL':
        try:
            if not ipaddress.ip_address(ip).is_private and ip != '127.0.0.1':
                allowed = False
        except:
            allowed = False

    # Registro de Auditoria (AccessLog)
    AccessLog.objects.create(
        user=request.user,
        document=doc,
        action='DOWNLOAD_ATTEMPT',
        ip_address=ip,
        success=allowed
    )

    if not allowed:
        return HttpResponseForbidden("<h1>ACESSO NEGADO</h1><p>Documentos confidenciais só podem ser baixados via VPN.</p>")

    # 2. DESCRIPTOGRAFIA E ENTREGA
    try:
        file_content = doc.get_decrypted_content()
        
        # 3. MARCA D'ÁGUA (Se for PDF)
        filename = doc.file.name.split('/')[-1].replace('.enc', '')
        if filename.lower().endswith('.pdf'):
            file_content = add_watermark(file_content, request.user, ip)
            
        response = HttpResponse(file_content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        return HttpResponseForbidden(f"Erro ao processar arquivo: {e}")

@login_required
def audit_log_view(request):
    # Apenas Admins podem ver a auditoria
    if not request.user.is_staff:
        return HttpResponseForbidden("Acesso restrito a auditores.")

    logs = AccessLog.objects.all().select_related('user', 'document').order_by('-timestamp')[:50]
    return render(request, 'documents/audit_log.html', {'logs': logs})