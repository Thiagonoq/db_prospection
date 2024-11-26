from src.models.analytics import GPTAvailableModels, Segments, Sources

not_purchase_options = {
    "Não gostei do produto": "deslike",
    "Não tenho redes sociais para compartilhar as artes": "no_has_social",
    "Achei o preço alto": "high_price",
    "Já tenho uma pessoa/empresa que faz esse serviço": "has_other_service",
    "Outro": "other",
}

feedback_after_30_medias = {
    "Muito ruim e quero parar de receber": "bad",
    "Precisa melhorar as artes": "improve",
    "Gosto, mas não posto ou compartilho as artes": "not_share",
    "Gosto muito e posto a maioria": "share",
    "Estou amando e posto sempre": "love",
}

sources = {
    "SMS": Sources.sms,
    "Site Video AI": Sources.site,
    "Indicação de amigos": Sources.indication,
    "Anúncio no Facebook": Sources.facebook,
    "Anúncio no Instagram": Sources.instagram,
    "Whatsapp": Sources.whatsapp,
    "Youtube": Sources.youtube,
    "Email": Sources.email,
    "Google": Sources.google_search,
    "Outros": Sources.other,
}

segments = {
    "Dentista": Segments.dentist,
    "Ótica": Segments.optics,
    "Material de Construção": Segments.construction_material,
    "Loja de Veículos": Segments.vehicle_store,
    "Hamburgueria": Segments.burger,
    "Pizzaria": Segments.pizzaria,
    "Restaurante": Segments.restaurant,
    "Roupas e Vestuário": Segments.clothing_and_apparel,
    "Hardware e Tecnologia": Segments.hardware_and_technology,
    "Smartphones e Acessórios": Segments.smartphone_and_accessories,
    "Imobiliária": Segments.real_estate,
    "Calçados": Segments.shoes,
    "Açougue": Segments.butchers,
    "Supermercado": Segments.supermarket,
    "Petshop": Segments.pet_shop,
    "Papelaria": Segments.stationery_shop,
    "Academia": Segments.academy,
    "Farmácia": Segments.pharmacy,
    "Relógios e Jóias": Segments.watches_and_jewelry,
    "Padaria": Segments.bakery,
    "Hortifruti": Segments.hortifruti,
    "Político": Segments.political,
    "Outros": Segments.others,
}

segments_reverse = {
    Segments.dentist: "Dentista",
    Segments.optics: "Ótica",
    Segments.construction_material: "Material de Construção",
    Segments.vehicle_store: "Loja de Veículos",
    Segments.burger: "Hamburgueria",
    Segments.pizzaria: "Pizzaria",
    Segments.restaurant: "Restaurante",
    Segments.clothing_and_apparel: "Roupas e Vestuário",
    Segments.hardware_and_technology: "Hardware e Tecnologia",
    Segments.smartphone_and_accessories: "Smartphones e Acessórios",
    Segments.real_estate: "Imobiliária",
    Segments.shoes: "Calçados",
    Segments.butchers: "Açougue",
    Segments.supermarket: "Supermercado",
    Segments.pet_shop: "Petshop",
    Segments.stationery_shop: "Papelaria",
    Segments.academy: "Academia",
    Segments.pharmacy: "Farmácia",
    Segments.watches_and_jewelry: "Relógios e Jóias",
    Segments.bakery: "Padaria",
    Segments.hortifruti: "Hortifruti",
    Segments.others: "Outros",
    Segments.political: "Político",
}

sources_reverse = {
    Sources.sms: "SMS",
    Sources.site: "Site Video AI",
    Sources.indication: "Indicação de amigos",
    Sources.facebook: "Anúncio no Facebook",
    Sources.instagram: "Anúncio no Instagram",
    Sources.whatsapp: "Whatsapp",
    Sources.youtube: "Youtube",
    Sources.email: "Email",
    Sources.google_search: "Google",
    Sources.other: "Outros",
}

input_pricing = {
    GPTAvailableModels.gpt_3_5_turbo_0125: 0.0005,
    GPTAvailableModels.gpt_3_5_turbo_1106: 0.001,
    GPTAvailableModels.gpt_4_1106_preview: 0.01,
    GPTAvailableModels.whisper: 0.006,
    GPTAvailableModels.gpt_4_vision_preview: 0.01085,
    GPTAvailableModels.gpt_4o: 0.005,
}

output_pricing = {
    GPTAvailableModels.gpt_3_5_turbo_0125: 0.0015,
    GPTAvailableModels.gpt_3_5_turbo_1106: 0.002,
    GPTAvailableModels.gpt_4_1106_preview: 0.03,
    GPTAvailableModels.whisper: 0.006,
    GPTAvailableModels.gpt_4_vision_preview: 0.03085,
    GPTAvailableModels.gpt_4o: 0.015,
}
