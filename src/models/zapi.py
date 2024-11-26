from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, RootModel


class BaseMessage(BaseModel):
    phone: str
    isEdit: bool = False
    isGroup: bool = False
    messageId: Optional[str] = None
    referenceMessageId: Optional[str] = None
    productReferenceId: Optional[str] = None


class TextModel(BaseModel):
    message: str


class ReferencedMessageModel(BaseModel):
    messageId: str
    fromMe: bool
    phone: str
    participant: Any


class ListResponseMessageModel(BaseModel):
    message: str
    title: str
    selectedRowId: str


class ImageModel(BaseModel):
    imageUrl: str
    thumbnailUrl: str
    caption: str
    mimeType: str
    viewOnce: bool
    width: int
    height: int


class AudioModel(BaseModel):
    ptt: bool
    seconds: int
    audioUrl: str
    mimeType: str
    viewOnce: bool


class ExternalAdReply(BaseModel):
    title: str
    body: str
    mediaType: int
    thumbnailUrl: str
    mediaUrl: str
    sourceType: str
    sourceId: str
    sourceUrl: str
    containsAutoReply: bool


class ProductForward(BaseModel):
    productImage: str
    businessOwnerJid: str
    currencyCode: str
    productId: str
    description: Any
    productImageCount: int
    price: int
    url: str
    retailerId: str
    firstImageId: str
    title: str


class ExternalAdText(BaseModel):
    message: str


class ReactionReferencedMessage(BaseModel):
    messageId: str
    fromMe: bool
    phone: str
    participant: Any


class Reaction(BaseModel):
    value: str
    time: int
    reactionBy: str
    referencedMessage: ReactionReferencedMessage


class ReactionMessage(BaseMessage):
    reaction: Reaction


class Product(BaseModel):
    name: str


class Order(BaseModel):
    products: list[Product]


class Document(BaseModel):
    caption: Any
    documentUrl: Any
    mimeType: str
    title: str
    pageCount: int
    fileName: str


class ExternalAdModel(BaseMessage):
    externalAdReply: ExternalAdReply
    text: ExternalAdText


class TextMessage(BaseMessage):
    text: TextModel


class ListMessage(BaseMessage):
    listResponseMessage: ListResponseMessageModel


class ImageMessage(BaseMessage):
    image: ImageModel


class AudioMessage(BaseMessage):
    audio: AudioModel


class OrderMessage(BaseMessage):
    order: Order


class DocumentMessage(BaseMessage):
    document: Document


class ProductMessage(BaseMessage):
    product: ProductForward
    text: Optional[TextModel] = TextModel(message="")


class WaitingForMessage(BaseMessage):
    waitingMessage: bool


MessageTypes = (
    ListMessage
    | ImageMessage
    | AudioMessage
    | TextMessage
    | ExternalAdModel
    | ReactionMessage
    | OrderMessage
    | DocumentMessage
    | ProductMessage
)


class RootMessageTypes(RootModel):
    root: MessageTypes
