from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import Http404
from .models import ShortLink
from .services import calculate_expiry, generate_random_code, validate_custom_alias


def home(request):
    if request.method == 'POST':
        original_url = request.POST.get('url')
        custom_alias = request.POST.get('alias', '').strip()
        
        if not original_url:
            messages.error(request, 'La URL es requerida')
            return render(request, 'home.html')
        
        if custom_alias:
            if not request.user.is_authenticated:
                messages.error(request, 'Debes iniciar sesión para usar alias personalizados')
                return render(request, 'home.html')
            
            valid, error_msg = validate_custom_alias(custom_alias)
            if not valid:
                messages.error(request, error_msg)
                return render(request, 'home.html')
            
            if ShortLink.objects.filter(short_code=custom_alias).exists():
                messages.error(request, 'Este alias ya está en uso')
                return render(request, 'home.html')
            
            short_code = custom_alias
        else:
            short_code = generate_random_code()
            while ShortLink.objects.filter(short_code=short_code).exists():
                short_code = generate_random_code()
        
        owner = request.user if request.user.is_authenticated else None
        expiry = calculate_expiry(user=owner)
        
        link = ShortLink.objects.create(
            original_url=original_url,
            short_code=short_code,
            owner=owner,
            expires_at=expiry
        )
        
        messages.success(request, f'URL creada: {request.build_absolute_uri("/" + link.short_code)}')
        return render(request, 'home.html', {'created_link': link})
    
    user_links = []
    if request.user.is_authenticated:
        user_links = ShortLink.objects.filter(owner=request.user)[:10]
    
    return render(request, 'home.html', {'user_links': user_links})


def redirect_link(request, short_code):
    link = get_object_or_404(ShortLink, short_code=short_code)
    
    if link.is_expired():
        raise Http404("Este enlace ha expirado")
    
    link.click_count += 1
    link.save(update_fields=['click_count'])
    
    return redirect(link.original_url)
