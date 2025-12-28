from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Property


def price_page_view(request):
    # 🔥 Retrieve data from database
    property_list = Property.objects.all().order_by('-id')

    # 🔥 Pagination (12 cards per page)
    paginator = Paginator(property_list, 9)
    page_number = request.GET.get('page')
    properties = paginator.get_page(page_number)

    context = {
        'page_title': 'Price Page',
        'properties': properties
    }
    return render(request, 'price_page/price_page.html', context)


def property_detail(request, slug):
    property = get_object_or_404(Property, slug=slug)
    return render(request, 'price_page/property_detail.html', {
        'property': property
    })
