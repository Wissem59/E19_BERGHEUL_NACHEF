from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import get_resolver, URLPattern, URLResolver
from .models import Section, Favorite_section


@login_required
@login_required
@login_required
def liste_favoris(request):
    """Display the list of the user's favorite sections."""
    favoris = Favorite_section.objects.filter(user=request.user)
    liste_favoris = []
    for favori in favoris:
        section_url = favori.section_url.url
        
        absolute_url = request.build_absolute_uri(section_url)

        if '/home' in absolute_url:
            absolute_url = absolute_url.replace('/home', '', 1)
        print(absolute_url)
        liste_favoris.append({
            'name': favori.section_url.name,
            'description': favori.section_url.description,
            'added_on': favori.added_on,
            'section_url': absolute_url,  # Pass the corrected URL to the template
            'user': favori.user,
            'id': favori.id
        })
    
    return render(request, 'favoris/liste_favoris.html', {'favoris': liste_favoris})


@login_required
def supprimer_favoris(request, section_id):
    # Fetch the favorite section by its ID for the current user
    favoris_instance = get_object_or_404(Favorite_section, user=request.user, id=section_id)

    if request.method == "POST":
        try:
            favoris_instance.delete()
            return redirect('favoris:liste_favoris')  # Redirect after deletion
        except Exception as e:
            # If deletion fails, show an error message on the list page
            return render(request, 'favoris/liste_favoris.html', {
                'error_message': 'Une erreur s\'est produite lors de la suppression.',
                'exception': str(e)
            })

    # Render the confirmation page before deletion
    return render(request, 'favoris/supprimer_favoris.html', {
        'favoris': favoris_instance  # Pass the favoris_instance to the template for display
    })



@login_required
def ajouter_favori(request, current_url):
    """Add a section to the user's favorites."""
    # Ensure the section exists in the database
    section, created = Section.objects.get_or_create(
        url=current_url,
        defaults={'name': current_url, 'description': f"Section for {current_url}"}
    )
    print('current_url')
    print(current_url)
    # Add the section to the user's favorites
    Favorite_section.objects.get_or_create(user=request.user, section_url=section)
    return redirect(request.META.get('HTTP_REFERER', '/home/'))

@login_required
def store_urls_in_sections(request):
    """Store all URL patterns in the `Section` model."""
    url_patterns = get_resolver().url_patterns
    process_url_patterns(url_patterns)
    return HttpResponse("URLs have been stored in the Sections model successfully!")

def process_url_patterns(url_patterns):
    """Helper to process nested URL patterns."""
    for pattern in url_patterns:
        if isinstance(pattern, URLPattern):
            name = pattern.name or str(pattern.pattern)
            description = f"Section for {name}"
            url = str(pattern.pattern)

            # Avoid overwriting existing `name` values
            Section.objects.update_or_create(
                url=url,
                defaults={'name': name, 'description': description}
            )
        elif isinstance(pattern, URLResolver):
            process_url_patterns(pattern.url_patterns)
