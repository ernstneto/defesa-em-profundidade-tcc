from django.shortcuts import render, redirect
from .models import Comment
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import Http404, HttpResponseForbidden, HttpResponse

@login_required
def comment_list(request):
    if request.method == 'POST':
        author = request.POST.get('author')
        text = request.POST.get('text')
        Comment.objects.create(author=author, text=text)
        return redirect('dashboard')

    comments = Comment.objects.all()
    return render(request, 'comments/comment_list.html', {'comments': comments})


def search_comment(request):
    """
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # A vulnerabilidade original que vamos corrigir
        sql_query = f"SELECT * FROM comments_comment WHERE author = '{query}'"
        comments = Comment.objects.raw(sql_query)
        #versao segura com ORM do django
        #results = Comment.objects.filter(author__icontains=query)
    
    # Importante: certifique-se de que o template renderizado aqui é o original
    return render(request, 'comments/search_results.html', {'results': results})
    """
    # Pega o parametro da URL
    q = request.GET.get('q', '')
    
    # Se não tiver busca, retorna vazio
    if not q:
        return HttpResponse("Digite algo para buscar.")

    # --- VULNERABILIDADE INTENCIONAL ---
    # Usamos um cursor direto para pular o ORM do Django
    with connection.cursor() as cursor:
        try:
            # Concatenação direta de string SEM parametrização
            # Isso permite injetar aspas ' e comandos SQL
            sql = f"SELECT * FROM comments_comment WHERE author = '{q}'"
            
            # Executa o SQL perigoso
            cursor.execute(sql)
            
            # Pega todos os resultados
            rows = cursor.fetchall()
            
            # Retorna os dados crus na tela (Vazamento de Informação)
            return HttpResponse(f"Resultados encontrados: {rows}")
            
        except Exception as e:
            # Retorna o erro na tela (Error-Based SQL Injection)
            # Isso diz ao sqlmap exatamente qual é o banco e o erro de sintaxe
            return HttpResponse(f"ERRO DE SQL: {e}")

def welcome_view(request):
    if request.user.is_autheticated:
        return redirect('dashboard')
    return render(request, 'welcome.html')