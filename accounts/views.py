from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import AccountCreateForm, TransferCreateForm
from .models import Account, Transfer
from django.db.models import Prefetch, Q
from transactions.models import Transaction
from shared.utils import get_exchange_rates, convert_currency
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.http import HttpResponse



class AccountListView(LoginRequiredMixin, View):
    def get(self, request):
        accounts = Account.objects.filter(user = request.user)
        return render(request, "accounts_list.html", {"accounts":accounts})
    

class AccountCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = AccountCreateForm()
        return render(request, "account_create.html", {"form": form})
    
    def post(self, request):
        form = AccountCreateForm(request.POST)
        if form.is_valid():
            account = form.save(commit = False)
            account.user = request.user
            account.save()
            return redirect("accounts-list")
        return render(request, "account_create.html", {"form":form})
    

class AccountDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        tr_queryset = Transaction.objects.select_related('category').order_by('-date')

        queryset = Account.objects.prefetch_related(
            Prefetch('account_transactions', queryset=tr_queryset)
        ).filter(user=request.user)

        account = get_object_or_404(queryset, pk=pk)
        return render(request, "account_detail.html", {"account": account})
    
class AccountUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk): 
        account = get_object_or_404(Account, pk = pk, user = request.user)
        form  = AccountCreateForm(instance = account)
        return render(request, "account_update.html", {"form":form, "account":account})
    
    def post(self, request, pk):
        account = get_object_or_404(Account, pk = pk, user = request.user)
        form = AccountCreateForm(request.POST, instance = account)
        if form.is_valid():
            account = form.save(commit = False)
            account.user = request.user
            account.save()
            return redirect("account-detail", pk)
        return render(request, "account_update.html", {"form":form, "account":account})
    

class AccountDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        account = get_object_or_404(Account, pk = pk, user = request.user)
        return render(request, "account_delete.html", {"account":account})
    
    def post(self, request, pk):
        account = get_object_or_404(Account, pk = pk, user = request.user)
        account.delete()
        return redirect("accounts-list")


class TransferListView(LoginRequiredMixin, View):
    def get(self, request):
        transfers = (
            Transfer.objects.filter(Q(from_account__user=request.user) | Q(to_account__user=request.user))
            .all()
            .order_by("-date")
        )

        min_summa = request.GET.get("min_summa")
        max_summa = request.GET.get("max_summa")
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")

        if min_summa:
            transfers = transfers.filter(amount__gte=min_summa)
        if max_summa:
            transfers = transfers.filter(amount__lte=max_summa)
        if from_date:
            transfers = transfers.filter(date__gte=from_date)
        if to_date:
            transfers = transfers.filter(date__lte=to_date)

        if request.GET.get("export") == "pdf":
            html_string = render_to_string(
                "transfer_list_pdf.html", {"transfers": transfers}
            )

            try:
                from weasyprint import HTML
            except Exception as e:
                return HttpResponse(
                    f"PDF export is unavailable because WeasyPrint dependencies are not installed/configured on this system. Import error: {e}",
                    status=500,
                )

            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = '''attachment; filename="o'tkazmalar_hisoboti.pdf"'''

            HTML(string=html_string, base_url=request.build_absolute_uri("/")).write_pdf(response)
            return response

        items_per_page = 10
        paginator = Paginator(transfers, items_per_page)
        
        # hozirgi urldan page number ni olamiz
        page_number = request.GET.get('page')
        
        try:
            # Tanlangan page-ni objectlarini qaytaramiz
            transfers = paginator.get_page(page_number)
        except PageNotAnInteger:
            transfers = paginator.page(1)                           
        except EmptyPage:
            transfers = paginator.page(paginator.num_pages) # bizda yuq sahifani surasa oxirgi sahifani qaytaramiz
        

        query_params = request.GET.copy()
        query_params.pop("page", None)

        return render(request, "transfer_list.html", {"transfers": transfers, "querystring_no_page": query_params.urlencode()})



class MakeTransafer(LoginRequiredMixin, View):
    def get(self, request):
        user_accounts = Account.objects.filter(user=request.user)
        form = TransferCreateForm()
        return render(request, "create_transfer.html", {"form": form, "user_accounts": user_accounts})

    def post(self, request):
        user_accounts = Account.objects.filter(user=request.user) 
        form = TransferCreateForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data['amount']
            from_id = request.POST.get("from_account_id")
            to_id = request.POST.get("to_account_id")

            from_account = get_object_or_404(Account, pk=from_id, user=request.user)
            to_account = get_object_or_404(Account, pk=to_id, user=request.user)

  
            if from_account.currency == 'usd' and not amount > 1:
                print("hshshshshshs")
                messages.error(request, "Dollar hisobi uchun minimal o'tkazma $1")
           
            elif from_account.currency == 'uzs' and amount < 1000:
                messages.error(request, "So'm hisobi uchun minimal o'tkazma 1000 so'm")

            elif from_account == to_account:
                messages.error(request, "Transfer uchun boshqa hisobni tanlang!")
            elif from_account.balance < amount:
                messages.error(request, "Balans yetarli emas")
            else:
                try:
                    with transaction.atomic():
                        rates = get_exchange_rates()
                        converted_summa = convert_currency(amount, from_account.currency, to_account.currency, rates)

                        from_account.balance -= amount
                        to_account.balance += converted_summa

                        from_account.save()
                        to_account.save()
                        Transfer.objects.create(from_account=from_account, to_account=to_account, amount=amount)
                    
                    messages.success(request, "Transfer amalga oshirildi")
                    return redirect("transfer_list")
                except Exception as e:
                    messages.error(request, f"Xatolik yuz berdi: {e}")

        return render(request, "create_transfer.html", {
            "form": form, 
            "user_accounts": user_accounts
        })
