from django.shortcuts import render, redirect
from django.views import View
from .forms import CategoryForm, TransactionForm
from .models import Category, Transaction
from django.db import transaction 
from django.contrib import messages
from .filters import TransactionFilter
from accounts.models import Transfer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.template.loader import render_to_string



class TransactionMainView(View):
    def get(self, request, form=None):
        queryset = Transaction.objects.filter(user=request.user).order_by('-date')
        
        f = TransactionFilter(request.GET, queryset=queryset, request=request)
        filtered_qs = f.qs         #f.qs - bu filtrdan o'tgan natijalar

        if request.GET.get("export") == "pdf":
            html_string = render_to_string(
                "transactions_list_pdf.html", {"transactions": filtered_qs}
            )

            try:
                from weasyprint import HTML
            except Exception as e:
                return HttpResponse(
                    f"PDF export is unavailable because WeasyPrint dependencies are not installed/configured on this system. Import error: {e}",
                    status=500,
                )

            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = '''attachment; filename="tranzaksiyalar_hisoboti.pdf"'''

            HTML(string=html_string, base_url=request.build_absolute_uri("/")).write_pdf(response)
            return response
        
        items_per_page = 10
        paginator = Paginator(filtered_qs, items_per_page)
        page_number = request.GET.get('page')
        
        try:
            page_obj = paginator.get_page(page_number)
        except (PageNotAnInteger, EmptyPage):
            page_obj = paginator.page(1)

        query_params = request.GET.copy()
        query_params.pop("page", None)

        context = {
            'page_obj': page_obj,
            "categories": Category.objects.filter(user=request.user),
            "transactions": page_obj,
            "filter_form": f.form,
            "t_form": form if form else TransactionForm(user=request.user),
            "c_form": CategoryForm(),
            "querystring_no_page": query_params.urlencode(),
        }
        return render(request, 'main_page.html', context)

    def post(self, request):
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                new_t = form.save(commit=False)
                new_t.user = request.user
                account = new_t.account

                if new_t.type == 'xarajat' and account.balance < new_t.amount:
                    form.add_error('amount', f"Mablag' yetarli emas! Balans: {account.balance}")
                    return self.get(request, form=form)

                if new_t.type == 'daromad':
                    account.balance += new_t.amount
                else:
                    account.balance -= new_t.amount
                
                new_t.save()
                account.save()
                messages.success(request, "Tranzaksiya muvaffaqiyatli bajarildi!")
                return redirect('transaction_main')
        
        return self.get(request, form=form)

class CategoryCreatePostView(View):
    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data.get("name").strip().lower()
            category_type = form.cleaned_data.get("type")

            category, created = Category.objects.get_or_create(
                user=request.user, 
                name=category_name, 
                defaults={'type': category_type}
            )

            if not created:
                messages.warning(request, f"'{category_name}' kategoriyasi allaqachon mavjud.")
            else:
                messages.success(request, "Kategoriya qo'shildi.")
        
        return redirect('transaction_main')
