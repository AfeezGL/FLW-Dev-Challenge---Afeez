import requests
import json
from django.shortcuts import render
from django.conf import settings

FLUTTERWAVE_SEC_KEY = settings.FLUTTERWAVE_SEC_KEY

# GET BRANCHES OF THE BENEFICIARY BANK


class Withdraw:
    def __init__(self, request, model, app, currency, bank=None, account_number=None, amount=None, reference=None, bank_code=None, branch_code=None, beneficiary_name=None, routing_number=None):
        self.request = request
        self.model = model
        self.app = app
        self.currency = currency
        self.bank = bank
        self.account_number = account_number
        self.amount = amount
        self.reference = reference
        self.bank_code = bank_code
        self.branch_code = branch_code
        self.beneficiary_name = beneficiary_name
        self.routing_number =routing_number
    

    def get_branches(self, run=False):
        if run == False:
            return None
        url = f"https://api.flutterwave.com/v3/banks/{self.bank}/branches"
        res = requests.get(url, headers = {"Authorization": FLUTTERWAVE_SEC_KEY})
        response = json.loads(res.content)
        branch_choices = response["data"]
        # PASS BRANCHES, AMOUNT, BANK AND ACCOUNT INTO THE TEMPLATE
        context = {
            "branch_choices": branch_choices,
            "amount": self.amount,
            "bank": self.bank,
            "account_number": self.account_number
        }
        template = f"{self.app}/withdrawOthers.html"
        # RETURN THE SPECIAL GHANAIAN WITHDRAWAL FORM
        return render(self.request, template, context)


    def send_withdrawal_form(self, run=False):
        if run == False:
            return None
        url = f"https://api.flutterwave.com/v3/banks/{self.model.country}"
        res = requests.get(url, headers = {"Authorization": FLUTTERWAVE_SEC_KEY})
        response= json.loads(res.content)
        bank_options = list(response["data"])
        template = f"{self.app}/initiateWithdrawal.html"
        context = {
            "bank_options": bank_options,
            "currency": self.currency
        }
        return render(self.request, template, context)


    def ngn_or_kes(self, run=False):
        if run == False:
            return None
        data = {
            "account_bank": self.bank,
            "account_number": self.account_number,
            "amount": self.amount,
            "narration": "jumga store withdrawal",
            "currency": self.currency,
            "reference": self.reference,
            "callback_url": "https://hooks.zapier.com/hooks/catch/9319455/o0es6km",
            "debit_currency": self.currency
        }
        res = requests.post("https://api.flutterwave.com/v3/transfers", json=data, headers={"Authorization": FLUTTERWAVE_SEC_KEY})
        response = json.loads(res.content)
        # IF WITHDRAWAL WAS SUCESSFUL, DEDUCT THE AMOUNT FROM THE USERS BALANCE
        if response["status"] == "success":
            self.model.balance -= self.amount
            print(self.model.balance)
            self.model.save()
        template = f"{self.app}/withdrawalResponse.html"
        context = {
            "status": response["status"],
            "message": response["message"]
        }
        return render(self.request, template, context)


    def withdraw_ghs(self, run=False):
        if run == False:
            return None
        data = {
            "account_bank": self.bank_code,
            "account_number": self.account_number,
            "amount": self.amount,
            "narration": "jumga store withdrawal",
            "currency": self.currency,
            "reference": self.reference,
            "callback_url": "https://hooks.zapier.com/hooks/catch/9319455/o0es6km",
            "destination_branch_code": self.branch_code,
            "beneficiary_name": self.beneficiary_name
        }
        res = requests.post("https://api.flutterwave.com/v3/transfers", json=data, headers={"Authorization": FLUTTERWAVE_SEC_KEY})
        response = json.loads(res.content)
        template = f"{self.app}/withdrawalResponse.html"
        if response["status"] == "success":
            self.model.balance -= self.amount
            print(self.model.balance)
            self.model.save()
        context = {
            "status": response["status"],
            "message": response["message"]
        }
        return render(self.request, template, context)

    def withdraw_uk(self, run=False):
        if run == False:
            return None
        data = {
            "amount": self.amount,
            "narration": "jumga store withdrawal",
            "currency": self.currency,
            "reference": self.reference,
            "beneficiary_name": self.beneficiary_name,
            "meta": [
                {
                "AccountNumber": self.account_number,
                "RoutingNumber": self.routing_number,
                "BeneficiaryName": self.beneficiary_name,
                "BeneficiaryCountry": "GB",
                }
            ]
        }

        res = requests.post("https://api.flutterwave.com/v3/transfers", json=data, headers={"Authorization": FLUTTERWAVE_SEC_KEY})
        response = json.loads(res.content)
        template = f"{self.app}/withdrawalResponse.html"
        if response["status"] == "success":
            self.model.balance -= self.amount
            print(self.model.balance)
            self.model.save()
        context = {
            "status": response["status"],
            "message": response["message"]
        }
        return render(self.request, template, context)
