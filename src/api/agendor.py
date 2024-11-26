import json

import requests

import config

agendor_token = config.AGENDOR_TOKEN
agendor_base_url = "https://api.agendor.com.br/v3/"


def list_funnels() -> list:
    """
    List all funnels in Agendor
    :return: list of funnels
    """
    url = agendor_base_url + "funnels"

    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    data = (
        response.json().get("data", [])
        if response.status_code == 200
        else response.json()
    )

    return data


def get_funnel(funnel_name: str) -> dict:
    data = list_funnels()
    for entry in data:
        if entry["name"] == funnel_name:
            return entry

    return None


def get_deal_stage(deal_stages: list, deal_stage: str) -> int:
    for stage in deal_stages:
        if stage["name"] == deal_stage:
            return stage["sequence"]

    return None


def list_responsibles() -> list:
    """
    List all responsibles in Agendor
    :return: list of responsibles
    """
    url = agendor_base_url + "users"

    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    data = (
        response.json().get("data", [])
        if response.status_code == 200
        else response.json()
    )

    return data


def get_responsible_id(responsible_name: str) -> int:
    data = list_responsibles()
    for entry in data:
        if entry["name"] == responsible_name:
            return entry["id"]

    return 840560


def create_new_person(
    name: str,
    phone: str,
    responsible: str,
    cpf: str = None,
    organization: int = None,
    role: str = None,
    ranking: int = None,
    description: str = None,
    birthday: str = None,
    email: str = None,
    work: str = None,
    mobile: str = None,
    fax: str = None,
    facebook: str = None,
    twitter: str = None,
    instagram: str = None,
    linked_in: str = None,
    skype: str = None,
    postal_code: str = None,
    country: str = None,
    district: str = None,
    state: str = None,
    street_name: str = None,
    street_number: int = None,
    additional_info: str = None,
    city: int = None,
    leadOrigin: int = None,
    category: int = None,
    products: list = None,
    allowedUsers: list = None,
    allowToAllUsers: bool = None,
    customFields: dict = None,
) -> dict:
    """
    Create a new person in Agendor
    :param name: Name of the person (required)
    :param phone: Phone of the person (required)
    :param responsible: Name of the owner responsible for the person (required)
    :param cpf: CPF of the person (optional)
    :param organization: Organization ID (optional)
    :param role: Role of the person in their organization (optional)
    :param ranking: Ranking displayed as stars in the person's page (optional)
    :param description: Description of the person (optional)
    :param birthday: Birthdate of the person (optional)
    :param email: Email of the person (optional)
    :param work: Work contact (optional)
    :param mobile: Mobile contact (optional)
    :param fax: Fax contact (optional)
    :param facebook: Facebook contact (optional)
    :param twitter: Twitter contact (optional)
    :param instagram: Instagram contact (optional)
    :param linked_in: LinkedIn contact (optional)
    :param skype: Skype contact (optional)
    :param postal_code: Postal code of the address (optional)
    :param country: Country of the address (optional)
    :param district: District of the address (optional)
    :param state: State of the address (optional)
    :param street_name: Street name of the address (optional)
    :param street_number: Street number of the address (optional)
    :param additional_info: Additional information of the address (optional)
    :param city: City of the address (optional)
    :param leadOrigin: Lead origin ID (optional)
    :param category: Category ID (optional)
    :param products: List of product IDs (optional)
    :param allowedUsers: List of allowed user IDs (optional)
    :param allowToAllUsers: Boolean to allow to all users (optional)
    :param customFields: Dictionary of custom fields (optional)
    :return: New person data
    """
    url = agendor_base_url + "people"

    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }

    data = {"name": name, "ownerUser": responsible, "contact": {"whatsapp": phone}}

    if cpf:
        data["cpf"] = cpf
    if organization:
        data["organization"] = organization
    if role:
        data["role"] = role
    if ranking is not None:
        data["ranking"] = ranking
    if description:
        data["description"] = description
    if birthday:
        data["birthday"] = birthday

    contact = {}
    if email:
        contact["email"] = email
    if work:
        contact["work"] = work
    if mobile:
        contact["mobile"] = mobile
    if fax:
        contact["fax"] = fax
    if facebook:
        contact["facebook"] = facebook
    if twitter:
        contact["twitter"] = twitter
    if instagram:
        contact["instagram"] = instagram
    if linked_in:
        contact["linked_in"] = linked_in
    if skype:
        contact["skype"] = skype
    if contact:
        data["contact"].update(contact)

    address = {}
    if postal_code:
        address["postal_code"] = postal_code
    if country:
        address["country"] = country
    if district:
        address["district"] = district
    if state:
        address["state"] = state
    if street_name:
        address["street_name"] = street_name
    if street_number is not None:
        address["street_number"] = street_number
    if additional_info:
        address["additional_info"] = additional_info
    if city:
        address["city"] = city
    if address:
        data["address"] = address

    if leadOrigin:
        data["leadOrigin"] = leadOrigin
    if category:
        data["category"] = category
    if products:
        data["products"] = products
    if allowedUsers:
        data["allowedUsers"] = allowedUsers
    if allowToAllUsers is not None:
        data["allowToAllUsers"] = allowToAllUsers
    if customFields:
        data["customFields"] = customFields

    response = requests.post(url, headers=headers, json=data)
    response_data = response.json().get("data", {})
    return response_data


def update_person(
    person_id: int,
    name: str = None,
    cpf: str = None,
    organization: int = None,
    role: str = None,
    ranking: int = None,
    description: str = None,
    birthday: str = None,
    ownerUser: int = None,
    email: str = None,
    work: str = None,
    mobile: str = None,
    fax: str = None,
    whatsapp: str = None,
    facebook: str = None,
    twitter: str = None,
    instagram: str = None,
    linked_in: str = None,
    skype: str = None,
    postal_code: str = None,
    country: str = None,
    district: str = None,
    state: str = None,
    street_name: str = None,
    street_number: int = None,
    additional_info: str = None,
    city: int = None,
    leadOrigin: int = None,
    category: int = None,
    products: list = None,
    allowedUsers: list = None,
    allowToAllUsers: bool = None,
    customFields: dict = None,
) -> dict:
    """
    Update a person in Agendor
    :param person_id: Person ID (required)
    :param name: Name of the person
    :param cpf: CPF of the person
    :param organization: Organization ID
    :param role: Role of the person
    :param ranking: Ranking of the person
    :param description: Description of the person
    :param birthday: Birthday of the person
    :param ownerUser: Owner user ID
    :param email: Email of the person
    :param work: Work contact
    :param mobile: Mobile contact
    :param fax: Fax contact
    :param whatsapp: WhatsApp contact
    :param facebook: Facebook contact
    :param twitter: Twitter contact
    :param instagram: Instagram contact
    :param linked_in: LinkedIn contact
    :param skype: Skype contact
    :param postal_code: Postal code of the address
    :param country: Country of the address
    :param district: District of the address
    :param state: State of the address
    :param street_name: Street name of the address
    :param street_number: Street number of the address
    :param additional_info: Additional info of the address
    :param city: City ID of the address
    :param leadOrigin: Lead origin ID
    :param category: Category ID
    :param products: List of product IDs
    :param allowedUsers: List of allowed user IDs
    :param allowToAllUsers: Boolean to allow to all users
    :param customFields: Dictionary of custom fields
    :return: Updated person data
    """
    url = agendor_base_url + f"people/{person_id}"

    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }

    # Construindo o dicionário de dados dinamicamente
    data = {}

    if name:
        data["name"] = name
    if cpf:
        data["cpf"] = cpf
    if organization:
        data["organization"] = organization
    if role:
        data["role"] = role
    if ranking is not None:
        data["ranking"] = ranking
    if description:
        data["description"] = description
    if birthday:
        data["birthday"] = birthday
    if ownerUser:
        data["ownerUser"] = ownerUser

    contact = {}
    if email:
        contact["email"] = email
    if work:
        contact["work"] = work
    if mobile:
        contact["mobile"] = mobile
    if fax:
        contact["fax"] = fax
    if whatsapp:
        contact["whatsapp"] = whatsapp
    if facebook:
        contact["facebook"] = facebook
    if twitter:
        contact["twitter"] = twitter
    if instagram:
        contact["instagram"] = instagram
    if linked_in:
        contact["linked_in"] = linked_in
    if skype:
        contact["skype"] = skype
    if contact:
        data["contact"] = contact

    address = {}
    if postal_code:
        address["postal_code"] = postal_code
    if country:
        address["country"] = country
    if district:
        address["district"] = district
    if state:
        address["state"] = state
    if street_name:
        address["street_name"] = street_name
    if street_number is not None:
        address["street_number"] = street_number
    if additional_info:
        address["additional_info"] = additional_info
    if city:
        address["city"] = city
    if address:
        data["address"] = address

    if leadOrigin:
        data["leadOrigin"] = leadOrigin
    if category:
        data["category"] = category
    if products:
        data["products"] = products
    if allowedUsers:
        data["allowedUsers"] = allowedUsers
    if allowToAllUsers is not None:
        data["allowToAllUsers"] = allowToAllUsers
    if customFields:
        data["customFields"] = customFields

    response = requests.put(url, headers=headers, json=data)
    response_data = (
        response.json().get("data", {})
        if response.status_code == 200
        else response.json()
    )
    return response_data


def list_person(
    page: int = 1,
    per_page: int = 10,
    name: str = None,
    category: int = None,
    leadOrigin: int = None,
    products: list = None,
    userOwner: int = None,
    role: str = None,
    cpf: str = None,
    organization: int = None,
    author: int = None,
    state: str = None,
    cityName: str = None,
    district: str = None,
    email: str = None,
    work_phone: str = None,
    mobile_phone: str = None,
    fax_phone: str = None,
    whatsapp: str = None,
    phone: str = None,
    createdAtGt: str = None,
    createdAtLt: str = None,
    updatedAtGt: str = None,
    updatedAtLt: str = None,
    withCustomFields: bool = False,
) -> dict:
    """
    List all people in Agendor with specified query parameters.
    :param page: Page of results to fetch.
    :param per_page: Number of results to return per page.
    :param name: Name prefix.
    :param category: Category ID.
    :param leadOrigin: Lead origin ID.
    :param products: Array of product IDs.
    :param userOwner: Owner user ID.
    :param role: Role prefix.
    :param cpf: Document number (CPF) prefix.
    :param organization: Organization ID.
    :param author: Author user ID.
    :param state: Address state abbreviation.
    :param cityName: City name prefix.
    :param district: District name prefix.
    :param email: Contact email prefix.
    :param work_phone: Work phone number.
    :param mobile_phone: Mobile phone number.
    :param fax_phone: Fax number.
    :param whatsapp: WhatsApp phone number.
    :param phone: Use to search in any phone field (work, mobile, fax and WhatsApp).
    :param createdAtGt: Search for people created after this date.
    :param createdAtLt: Search for people created before this date.
    :param updatedAtGt: Search for people updated after this date.
    :param updatedAtLt: Search for people updated before this date.
    :param withCustomFields: Return custom fields of people.
    :return: Person data.
    """

    url = agendor_base_url + "people"

    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }
    if per_page > 100:
        per_page = 100

    params = {"page": page, "per_page": per_page}

    if name:
        params["name"] = name
    if category:
        params["category"] = category
    if leadOrigin:
        params["leadOrigin"] = leadOrigin
    if products:
        params["products"] = products
    if userOwner:
        params["userOwner"] = userOwner
    if role:
        params["role"] = role
    if cpf:
        params["cpf"] = cpf
    if organization:
        params["organization"] = organization
    if author:
        params["author"] = author
    if state:
        params["state"] = state
    if cityName:
        params["cityName"] = cityName
    if district:
        params["district"] = district
    if email:
        params["email"] = email
    if work_phone:
        params["work_phone"] = work_phone
    if mobile_phone:
        params["mobile_phone"] = mobile_phone
    if fax_phone:
        params["fax_phone"] = fax_phone
    if whatsapp:
        params["whatsapp"] = whatsapp
    if phone:
        params["phone"] = phone
    if createdAtGt:
        params["createdAtGt"] = createdAtGt
    if createdAtLt:
        params["createdAtLt"] = createdAtLt
    if updatedAtGt:
        params["updatedAtGt"] = updatedAtGt
    if updatedAtLt:
        params["updatedAtLt"] = updatedAtLt
    if withCustomFields:
        params["withCustomFields"] = withCustomFields

    response = requests.get(url, headers=headers, params=params)
    data = (
        response.json().get("data", [])
        if response.status_code == 200
        else response.json()
    )

    return data


def delete_person(person_id: int) -> dict:
    """
    Delete a person from Agendor
    :param person_id: Person ID
    :return: response
    """
    url = agendor_base_url + f"people/{person_id}"

    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }

    response = requests.delete(url, headers=headers)
    return response


def create_new_deal(
    person_id: int,
    person_name: str,
    dealStatusText: str = None,
    description: str = None,
    endTime: str = None,
    products_entities: list = None,
    products: list = None,
    ranking: int = None,
    startTime: str = None,
    ownerUser: str = None,
    funnel: int = None,
    dealStage: int = None,
    value: float = None,
    allowedUsers: list = None,
    allowToAllUsers: bool = None,
    customFields: dict = None,
) -> dict:
    """
    Create a new deal in Agendor
    :param person_id: Person ID (required)
    :param person_name: Person name (used as the title) (required)
    :param dealStatusText: Status of the deal, must be one of: "ongoing", "won", "lost"
    :param description: Description of the deal
    :param endTime: End time of the deal
    :param products_entities: List of product entities in the deal
        - id: Product entity ID
        - unitValue: Unit value of the product
        - discount: Discount of the product
        - quantity: Quantity of the product
    :param products: List of product names in the deal
    :param ranking: Ranking of the deal
    :param startTime: Start time of the deal
    :param ownerUser: Name of the owner responsible for the deal
    :param funnel: Funnel name
    :param dealStage: Deal stage name
    :param value: Value of the deal
    :param allowedUsers: List of allowed user IDs
    :param allowToAllUsers: Boolean to allow to all users
    :param customFields: Dictionary of custom fields
    :return: New deal data
    """
    url = agendor_base_url + f"organizations/{person_id}/deals"

    data = {
        "person": person_id,
        "title": person_name,
    }
    valid_statuses = ["ongoing", "won", "lost"]

    if dealStatusText:
        if dealStatusText not in valid_statuses:
            raise ValueError(
                f"Invalid dealStatusText. Must be one of: {', '.join(valid_statuses)}"
            )
        data["dealStatusText"] = dealStatusText
    if description:
        data["description"] = description
    if endTime:
        data["endTime"] = endTime
    if products_entities:
        data["products_entities"] = products_entities
    if products:
        data["products"] = products
    if ranking is not None:
        data["ranking"] = ranking
    if startTime:
        data["startTime"] = startTime
    if value is not None:
        data["value"] = value
    if allowedUsers:
        data["allowedUsers"] = allowedUsers
    if allowToAllUsers is not None:
        data["allowToAllUsers"] = allowToAllUsers
    if customFields:
        data["customFields"] = customFields

    # Tratamento especial para obter os IDs do funil e estágio do negócio, e do responsável
    if ownerUser:
        data["ownerUser"] = ownerUser
    if funnel:
        data["funnel"] = funnel
        data["dealStage"] = dealStage

    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    return response_data


def list_deals(entity_type: str, entity_id: int) -> dict:
    """
    List all deals in Agendor
    :param person_id: Person ID
    :return: list of deals
    """
    endpoint = f"{entity_type}/{entity_id}/deals"
    url = agendor_base_url + endpoint
    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    data = response.json()
    
    return data


def update_deal(
    deal_id: int,
    value: int = None,
    description: str = None,
    startTime: str = None,
    products_entities: list = None,
    products: list = None,
    ownerUser: int = None,
    allowedUsers: list = None,
    allowToAllUsers: bool = None,
    customFields: dict = None,
) -> dict:
    """
    Update a deal's information in Agendor
    :param deal_id: ID of the deal to update (required)
    :param value: Value of the deal
    :param description: Description of the deal
    :param startTime: Start time of the deal
    :param products_entities: List of product entities in the deal
    :param products: List of product names in the deal
    :param ownerUser: Owner user ID
    :param allowedUsers: List of allowed user IDs
    :param allowToAllUsers: Boolean to allow to all users
    :param customFields: Dictionary of custom fields
    :return: Response from Agendor
    """
    url = agendor_base_url + f"deals/{deal_id}"

    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }

    data = {}

    if value is not None:
        data["value"] = value
    if description:
        data["description"] = description
    if startTime:
        data["startTime"] = startTime
    if products_entities:
        data["products_entities"] = products_entities
    if products:
        data["products"] = products
    if ownerUser is not None:
        data["ownerUser"] = ownerUser
    if allowedUsers:
        data["allowedUsers"] = allowedUsers
    if allowToAllUsers is not None:
        data["allowToAllUsers"] = allowToAllUsers
    if customFields:
        data["customFields"] = customFields

    response = requests.put(url, headers=headers, json=data)
    response_data = (
        response.json().get("data", {})
        if response.status_code == 200
        else response.json()
    )
    return response_data


def get_deal(deal_id: int) -> dict:
    """
    Get a deal from Agendor
    :param deal_id: Deal ID
    :return: deal data
    """
    url = agendor_base_url + f"deals/{deal_id}"

    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    data = (
        response.json().get("data", {})
        if response.status_code == 200
        else response.json()
    )
    return data


def update_deal_stage(deal_id: int, deal_stage: int, funnel: int) -> dict:
    """
    Update deal stage in Agendor
    :param deal_id: Deal ID
    :param deal_stage: New deal stage
    :return: deal updated data
    """
    url = agendor_base_url + f"deals/{deal_id}/stage"

    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }

    data = {"dealStage": deal_stage, "funnel": funnel}

    response = requests.put(url, headers=headers, json=data)

    return response.json()


def update_deal_status(deal_id: int, deal_status_text: str) -> dict:
    """
    Update deal status in Agendor
    :param deal_id: Deal ID
    :param deal_status_text: New deal status
    :return: deal updated data
    """
    valid_statuses = ["ongoing", "won", "lost"]

    if deal_status_text not in valid_statuses:
        raise ValueError(
            f"Invalid deal status. Valid statuses are: {', '.join(valid_statuses)}"
        )

    url = agendor_base_url + f"deals/{deal_id}/status"

    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }

    data = {"dealStatusText": deal_status_text}

    response = requests.put(url, headers=headers, json=data)
    data = (
        response.json().get("data", {})
        if response.status_code == 200
        else response.json()
    )
    return data


def list_organizations(
    page: int = 1,
    per_page: int = 10,
    name: str = None,
    nameExact: str = None,
    category: int = None,
    sector: int = None,
    leadOrigin: int = None,
    products: list = None,
    userOwner: int = None,
    cnpj: str = None,
    author: int = None,
    state: str = None,
    cityName: str = None,
    district: str = None,
    email: str = None,
    work_phone: str = None,
    mobile_phone: str = None,
    fax_phone: str = None,
    whatsapp: str = None,
    phone: str = None,
    createdAtGt: str = None,
    createdAtLt: str = None,
    updatedAtGt: str = None,
    updatedAtLt: str = None,
    withCustomFields: bool = False,
) -> dict:
    """
    List all organizations in Agendor with specified query parameters.
    :param page: Page of results to fetch.
    :param per_page: Number of results to return per page.
    :param name: Name prefix.
    :param nameExact: Exact name match.
    :param category: Category ID.
    :param sector: Sector ID.
    :param leadOrigin: Lead origin ID.
    :param products: Array of product IDs.
    :param userOwner: Owner user ID.
    :param cnpj: Document number (CNPJ) prefix.
    :param author: Author user ID.
    :param state: Address state abbreviation.
    :param cityName: City name prefix.
    :param district: District name prefix.
    :param email: Contact email prefix.
    :param work_phone: Work phone number.
    :param mobile_phone: Mobile phone number.
    :param fax_phone: Fax number.
    :param whatsapp: WhatsApp phone number.
    :param phone: Use to search in any phone field (work, mobile, fax and WhatsApp).
    :param createdAtGt: Search for organizations created after this date.
    :param createdAtLt: Search for organizations created before this date.
    :param updatedAtGt: Search for organizations updated after this date.
    :param updatedAtLt: Search for organizations updated before this date.
    :param withCustomFields: Return custom fields of organizations.
    :return: Organization data.
    """

    url = agendor_base_url + "organizations"

    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }

    if per_page > 100:
        per_page = 100

    params = {"page": page, "per_page": per_page}

    if name:
        params["name"] = name
    if nameExact:
        params["nameExact"] = nameExact
    if category:
        params["category"] = category
    if sector:
        params["sector"] = sector
    if leadOrigin:
        params["leadOrigin"] = leadOrigin
    if products:
        params["products"] = products
    if userOwner:
        params["userOwner"] = userOwner
    if cnpj:
        params["cnpj"] = cnpj
    if author:
        params["author"] = author
    if state:
        params["state"] = state
    if cityName:
        params["cityName"] = cityName
    if district:
        params["district"] = district
    if email:
        params["email"] = email
    if work_phone:
        params["work_phone"] = work_phone
    if mobile_phone:
        params["mobile_phone"] = mobile_phone
    if fax_phone:
        params["fax_phone"] = fax_phone
    if whatsapp:
        params["whatsapp"] = whatsapp
    if phone:
        params["phone"] = phone
    if createdAtGt:
        params["createdAtGt"] = createdAtGt
    if createdAtLt:
        params["createdAtLt"] = createdAtLt
    if updatedAtGt:
        params["updatedAtGt"] = updatedAtGt
    if updatedAtLt:
        params["updatedAtLt"] = updatedAtLt
    if withCustomFields:
        params["withCustomFields"] = withCustomFields

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    return data


def create_organization(
    name: str,
    legalName: str = None,
    cnpj: str = None,
    description: str = None,
    logo: str = None,
    website: str = None,
    ranking: int = None,
    ownerUser: int = None,
    contact: dict = None,
    address: dict = None,
    leadOrigin: int = None,
    category: int = None,
    sector: int = None,
    products: list = None,
    allowedUsers: list = None,
    allowToAllUsers: bool = False,
    customFields: dict = None,
) -> dict:
    """
    Create a new organization in Agendor with specified parameters.
    :param name: Display name (Nome fantasia) - required.
    :param legalName: Legal name (Razão social).
    :param cnpj: Legal document number (CNPJ).
    :param description: Description of the organization.
    :param logo: Logo image URL.
    :param website: Homepage URL.
    :param ranking: Ranking displayed as stars in the organization page (0 to 5).
    :param ownerUser: User ID or email of the owner of this organization.
    :param contact: Contact information (as a dictionary).
    :param address: Address information (as a dictionary).
    :param leadOrigin: Lead origin ID or name.
    :param category: Category ID or name.
    :param sector: Sector ID or name.
    :param products: Array of product IDs.
    :param allowedUsers: Array of IDs of users that should be able to see this organization.
    :param allowToAllUsers: Set true if this organization should be visible to all users.
    :param customFields: Custom fields information.
    :return: The created organization data.
    """

    url = agendor_base_url + "organizations"

    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }

    data = {"name": name}

    if legalName:
        data["legalName"] = legalName
    if cnpj:
        data["cnpj"] = cnpj
    if description:
        data["description"] = description
    if logo:
        data["logo"] = logo
    if website:
        data["website"] = website
    if ranking is not None:
        data["ranking"] = ranking
    if ownerUser:
        data["ownerUser"] = ownerUser
    if contact:
        data["contact"] = contact
    if address:
        data["address"] = address
    if leadOrigin:
        data["leadOrigin"] = leadOrigin
    if category:
        data["category"] = category
    if sector:
        data["sector"] = sector
    if products:
        data["products"] = products
    if allowedUsers:
        data["allowedUsers"] = allowedUsers
    if allowToAllUsers:
        data["allowToAllUsers"] = allowToAllUsers
    if customFields:
        data["customFields"] = customFields

    response = requests.post(url, headers=headers, json=data)
    created_data = response.json() if response.status_code == 201 else response.json()

    return created_data


def update_organization(
    org_id: int,
    name: str = None,
    legalName: str = None,
    cnpj: str = None,
    description: str = None,
    logo: str = None,
    website: str = None,
    ranking: int = None,
    ownerUser: int = None,
    contact: dict = None,
    address: dict = None,
    leadOrigin: int = None,
    category: int = None,
    sector: int = None,
    products: list = None,
    allowedUsers: list = None,
    allowToAllUsers: bool = None,
    customFields: dict = None,
) -> dict:
    """
    Update a specific organization by ID in Agendor with specified parameters.
    :param org_id: Organization ID - required.
    :param name: Display name (Nome fantasia).
    :param legalName: Legal name (Razão social).
    :param cnpj: Legal document number (CNPJ).
    :param description: Description of the organization.
    :param logo: Logo image URL.
    :param website: Homepage URL.
    :param ranking: Ranking displayed as stars in the organization page (0 to 5).
    :param ownerUser: User ID or email of the owner of this organization.
    :param contact: Contact information (as a dictionary).
    :param address: Address information (as a dictionary).
    :param leadOrigin: Lead origin ID or name.
    :param category: Category ID or name.
    :param sector: Sector ID or name.
    :param products: Array of product IDs.
    :param allowedUsers: Array of IDs of users that should be able to see this organization.
    :param allowToAllUsers: Set true if this organization should be visible to all users.
    :param customFields: Custom fields information.
    :return: The updated organization data.
    """

    url = agendor_base_url + f"organizations/{org_id}"

    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }

    data = {}

    if name:
        data["name"] = name
    if legalName:
        data["legalName"] = legalName
    if cnpj:
        data["cnpj"] = cnpj
    if description:
        data["description"] = description
    if logo:
        data["logo"] = logo
    if website:
        data["website"] = website
    if ranking is not None:
        data["ranking"] = ranking
    if ownerUser:
        data["ownerUser"] = ownerUser
    if contact:
        data["contact"] = contact
    if address:
        data["address"] = address
    if leadOrigin:
        data["leadOrigin"] = leadOrigin
    if category:
        data["category"] = category
    if sector:
        data["sector"] = sector
    if products:
        data["products"] = products
    if allowedUsers:
        data["allowedUsers"] = allowedUsers
    if allowToAllUsers is not None:
        data["allowToAllUsers"] = allowToAllUsers
    if customFields:
        data["customFields"] = customFields

    response = requests.put(url, headers=headers, json=data)
    updated_data = response.json() if response.status_code == 200 else response.json()

    return updated_data


def list_organization_deals(organization_id: int) -> dict:
    """
    List all deals in Agendor
    :param organization_id: Organization ID
    :return: list of deals
    """
    url = agendor_base_url + f"organizations/{organization_id}/deals"

    headers = {
        "Authorization": f"Token {agendor_token}",
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)

    try:
        data = response.json()
    except json.JSONDecodeError:
        data = {}

    return data
