from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class OrderStatus(str, Enum):
    free = "free"
    paid = "paid"
    ended = "ended"
    unpaid = "unpaid"
    created = "created"
    refused = "refused"

    trialing = "trialing"
    refunded = "refunded"
    chargedback = "chargedback"
    waitingPayment = "waitingPayment"


class PaymentMethod(str, Enum):
    pix = "pix"
    boleto = "boleto"
    paypal = "paypal"
    credit_card = "credit_card"
    two_credit_cards = "two_credit_cards"


class OrderUpdatesModel(BaseModel):
    status: Optional[OrderStatus] = OrderStatus.created
    old_status: Optional[OrderStatus] = OrderStatus.created

    created_at: Optional[str] = ""
    updated_at: Optional[str] = ""


class ClientOrderModel(BaseModel):
    uf: Optional[str] = ""
    name: Optional[str] = ""
    city: Optional[str] = ""
    email: Optional[str] = ""
    street: Optional[str] = ""
    number: Optional[str] = ""
    zipcode: Optional[str] = ""
    document: Optional[str] = ""
    cpf: Optional[str] = ""
    cnpj: Optional[str] = ""
    cpf_cnpj: Optional[str] = ""
    cellphone: Optional[str] = ""
    complement: Optional[str] = ""
    neighborhood: Optional[str] = ""


class SaleModel(BaseModel):
    amount: Optional[float] = 0
    installments: Optional[int] = 1
    payment_method: Optional[PaymentMethod] = PaymentMethod.credit_card


class OrderModel(BaseModel):
    id: int
    status: OrderStatus = OrderStatus.created
    client: ClientOrderModel = ClientOrderModel()
    sale: SaleModel = SaleModel()

    created_at: datetime
    updated_at: datetime

    end_date: Optional[datetime] = None


class LeadModel(BaseModel):
    product_id: int
    client: ClientOrderModel
