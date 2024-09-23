import config
import requests
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgendorApi:
    def __init__(self):
        token = config.AGENDOR_TOKEN
        self.agendor_base_url = "https://api.agendor.com.br/v3/"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        })
        self._responsible_cache = None
        self.funnels_cache = None

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        url = self.agendor_base_url + endpoint
        response = self.session.request(method, url, **kwargs)

        return self._handle_response(response)
    
    def _build_url(self, endpoint: str) -> str:
        return self.agendor_base_url + endpoint

    def _handle_response(self, response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()

        if not response.ok:
            error_message = data.get("errors", "Unknown error")
            raise Exception(f"Error {response.status_code}: {error_message}")

        return data
    
    # FUNNELS
    def list_funnels(self) -> list[Dict[str, Any]]:
        """
        Lista todos os funis disponíveis no Agendor.

        Returns:
            list[Dict[str, Any]]: Lista de dicionários contendo os dados de cada funil.

        Example:
            >>> funnels = agendor_api.list_funnels()
            >>> for funnel in funnels:
            ...     print(funnel['name'])
        """
        return self._request("GET", "funnels")
    
    def get_funnel(self, funnel_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém as informações de um funil específico pelo ID.

        Args:
            funnel_id (int): ID do funil a ser recuperado.

        Returns:
            Optional[Dict[str, Any]]: Um dicionário com os dados do funil ou None se não encontrado.

        Example:
            >>> funnel = agendor_api.get_funnel(12345)
            >>> if funnel:
            ...     print(funnel['name'])
        """

        data = self.list_funnels()
        for entry in data:
            if entry['id'] == funnel_id:
                return entry
        
        return None

    # RESPONSIBLES
    def list_responsibles(self) -> List[Dict[str, Any]]:
        """
        Lista todos os responsáveis no Agendor.

        Returns:
            List[Dict[str, Any]]: Lista de dicionários com os dados de cada responsável.

        Example:
            >>> responsibles = agendor_api.list_responsibles()
            >>> for responsible in responsibles:
            ...     print(responsible['name'])
        """

        if self._responsible_cache is None:
            self._responsible_cache = self._request("GET", "users")

        return self._responsible_cache

    def get_responsible_id(self, responsible_name: str) -> Optional[int]:
        """
        Obtém o ID de um responsável pelo nome.

        Args:
            responsible_name (str): Nome do responsável.

        Returns:
            Optional[int]: ID do responsável ou None se não encontrado.

        Example:
            >>> responsible_id = agendor_api.get_responsible_id('João Silva')
            >>> print(responsible_id)
        """
        responsibles = self.list_responsibles()
        for responsible in responsibles:
            if responsible['name'] == responsible_name:
                return responsible['id']
        
        return None

    # PERSONS
    def create_new_person(
        self,
        name: str,
        phone: str,
        responsible_id: int,
        cpf: Optional[str] = None,
        organization: Optional[int] = None,
        role: Optional[str] = None,
        ranking: Optional[int] = None,
        description: Optional[str] = None,
        birthday: Optional[datetime] = None,
        email: Optional[str] = None,
        work: Optional[str] = None,
        mobile: Optional[str] = None,
        fax: Optional[str] = None,
        facebook: Optional[str] = None,
        twitter: Optional[str] = None,
        instagram: Optional[str] = None,
        linked_in: Optional[str] = None,
        skype: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        street_name: Optional[str] = None,
        street_number: Optional[int] = None,
        additional_info: Optional[str] = None,
        city: Optional[int] = None,
        leadOrigin: Optional[int] = None,
        category: Optional[int] = None,
        products: Optional[List[int]] = None,
        allowedUsers: Optional[List[int]] = None,
        allowToAllUsers: Optional[bool] = None,
        customFields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Cria uma nova pessoa no Agendor.

        Args:
            name (str): Nome da pessoa.
            phone (str): Telefone da pessoa.
            responsible_id (int): ID do usuário responsável pela pessoa.
            cpf (str, optional): CPF da pessoa.
            organization (int, optional): ID da organização associada.
            role (str, optional): Cargo ou função da pessoa na organização.
            ranking (int, optional): Classificação da pessoa (0 a 5).
            description (str, optional): Descrição ou notas sobre a pessoa.
            birthday (datetime, optional): Data de nascimento.
            email (str, optional): Endereço de email.
            work (str, optional): Telefone comercial.
            mobile (str, optional): Telefone celular.
            fax (str, optional): Número de fax.
            facebook (str, optional): URL do perfil no Facebook.
            twitter (str, optional): URL do perfil no Twitter.
            instagram (str, optional): URL do perfil no Instagram.
            linked_in (str, optional): URL do perfil no LinkedIn.
            skype (str, optional): Nome de usuário no Skype.
            postal_code (str, optional): CEP do endereço.
            country (str, optional): País.
            district (str, optional): Bairro.
            state (str, optional): Estado (sigla).
            street_name (str, optional): Nome da rua.
            street_number (int, optional): Número do endereço.
            additional_info (str, optional): Informações adicionais do endereço.
            city (int, optional): ID da cidade.
            leadOrigin (int, optional): ID da origem do lead.
            category (int, optional): ID da categoria.
            products (List[int], optional): Lista de IDs de produtos associados.
            allowedUsers (List[int], optional): Lista de IDs de usuários com permissão.
            allowToAllUsers (bool, optional): Se verdadeiro, permite acesso a todos os usuários.
            customFields (Dict[str, Any], optional): Campos personalizados adicionais.

        Returns:
            Dict[str, Any]: Dados da pessoa criada retornados pela API do Agendor.

        Raises:
            ValueError: Se 'name', 'phone' ou 'responsible_id' não forem fornecidos.

        Example:
            >>> agendor_api.create_new_person(
            ...     name="Maria Silva",
            ...     phone="11999999999",
            ...     responsible_id=123456,
            ...     email="maria.silva@example.com"
            ... )

        """
        if not name or not phone or not responsible_id:
            raise ValueError("Name, phone and responsible ID are required")
        data = {
            "name": name,
            "ownerUser": responsible_id,
            "contact": {
                "whatsapp": phone
            }
        }

        if cpf:
            data["cpf"] = cpf
        if organization:
            data["organization"] = organization
        if role:
            data["role"] = role
        if ranking is not None:
            if not (0 <= ranking <= 5):
                raise ValueError("Ranking must be between 0 and 5")
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

        return self._request("POST", "people", json=data)

    def update_person(
        self,
        person_id: int,
        name: Optional[str] = None,
        cpf: Optional[str] = None,
        organization: Optional[int] = None,
        role: Optional[str] = None,
        ranking: Optional[int] = None,
        description: Optional[str] = None,
        birthday: Optional[datetime] = None,
        ownerUser: Optional[int] = None,
        email: Optional[str] = None,
        work: Optional[str] = None,
        mobile: Optional[str] = None,
        fax: Optional[str] = None,
        whatsapp: Optional[str] = None,
        facebook: Optional[str] = None,
        twitter: Optional[str] = None,
        instagram: Optional[str] = None,
        linked_in: Optional[str] = None,
        skype: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        street_name: Optional[str] = None,
        street_number: Optional[int] = None,
        additional_info: Optional[str] = None,
        city: Optional[int] = None,
        leadOrigin: Optional[int] = None,
        category: Optional[int] = None,
        products: Optional[List[int]] = None,
        allowedUsers: Optional[List[int]] = None,
        allowToAllUsers: Optional[bool] = None,
        customFields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Atualiza as informações de uma pessoa no Agendor.

        Args:
            person_id (int): ID da pessoa a ser atualizada.
            name (str, optional): Nome da pessoa.
            cpf (str, optional): CPF da pessoa.
            organization (int, optional): ID da organização associada.
            role (str, optional): Cargo ou função da pessoa.
            ranking (int, optional): Classificação da pessoa (0 a 5).
            description (str, optional): Descrição da pessoa.
            birthday (datetime, optional): Data de nascimento.
            ownerUser (int, optional): ID do usuário responsável pela pessoa.
            email (str, optional): Email da pessoa.
            mobile (str, optional): Número de celular.
            products (List[int], optional): Lista de IDs de produtos associados.
            allowedUsers (List[int], optional): Lista de IDs de usuários com permissão.
            allowToAllUsers (bool, optional): Se verdadeiro, permite acesso a todos os usuários.
            customFields (Dict[str, Any], optional): Campos personalizados adicionais.

        Returns:
            Dict[str, Any]: Dados da pessoa atualizados.

        Example:
            >>> agendor_api.update_person(person_id=12345, name="Maria Silva")
        """
        if not person_id:
            raise ValueError("'person_id' is required")
        
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
            if not (0 <= ranking <= 5):
                raise ValueError("'ranking' must be between 0 and 5")
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

        endpoint = f"people/{person_id}"

        return self._request("PUT", endpoint, json=data)

    def list_person(
        self, 
        page: int = 1, 
        per_page: int = 10, 
        name: Optional[str] = None, 
        category: Optional[int] = None, 
        leadOrigin: Optional[int] = None,
        products: Optional[List[int]] = None, 
        userOwner: Optional[int] = None, 
        role: Optional[str] = None, 
        cpf: Optional[str] = None, 
        organization: Optional[int] = None, 
        author: Optional[int] = None, 
        state: Optional[str] = None, 
        cityName: Optional[str] = None, 
        district: Optional[str] = None, 
        email: Optional[str] = None, 
        work_phone: Optional[str] = None, 
        mobile_phone: Optional[str] = None, 
        fax_phone: Optional[str] = None, 
        whatsapp: Optional[str] = None, 
        phone: Optional[str] = None, 
        createdAtGt: Optional[str] = None, 
        createdAtLt: Optional[str] = None, 
        updatedAtGt: Optional[str] = None, 
        updatedAtLt: Optional[str] = None, 
        withCustomFields: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Lista todas as pessoas no Agendor com os parâmetros de consulta especificados.

        Args:
            page (int, optional): Número da página dos resultados. Padrão é 1.
            per_page (int, optional): Número de resultados por página. Máximo de 100. Padrão é 10.
            name (str, optional): Prefixo do nome das pessoas.
            category (int, optional): ID da categoria das pessoas.
            leadOrigin (int, optional): ID da origem do lead.
            products (List[int], optional): Lista de IDs de produtos associados.
            userOwner (int, optional): ID do usuário responsável pelas pessoas.
            role (str, optional): Prefixo do cargo ou função das pessoas.
            cpf (str, optional): Prefixo do CPF das pessoas.
            organization (int, optional): ID da organização associada.
            author (int, optional): ID do autor do cadastro.
            state (str, optional): Sigla do estado.
            cityName (str, optional): Nome da cidade.
            district (str, optional): Nome do distrito ou bairro.
            email (str, optional): Prefixo do endereço de email.
            work_phone (str, optional): Prefixo do telefone comercial.
            mobile_phone (str, optional): Prefixo do telefone celular.
            fax_phone (str, optional): Prefixo do número de fax.
            whatsapp (str, optional): Prefixo do número de WhatsApp.
            phone (str, optional): Prefixo do telefone, buscando em todos os campos de telefone.
            createdAtGt (str, optional): Filtrar por pessoas criadas após essa data.
            createdAtLt (str, optional): Filtrar por pessoas criadas antes dessa data.
            updatedAtGt (str, optional): Filtrar por pessoas atualizadas após essa data.
            updatedAtLt (str, optional): Filtrar por pessoas atualizadas antes dessa data.
            withCustomFields (bool, optional): Retorna os campos personalizados das pessoas, se True.

        Returns:
            dict: Dicionário contendo os dados das pessoas retornadas pela API do Agendor.

        Example:
            >>> pessoas = agendor_api.list_person(page=1, per_page=5, name="Maria")
            >>> for pessoa in pessoas:
            ...     print(pessoa['name'])
        """
        if per_page > 100:
            per_page = 100

        params = {
            "page": page,
            "per_page": per_page
        }

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

        return self._request("GET", "people", params=params)

    def delete_person(self, person_id: int) -> Dict[str, Any]:
        """
        Deleta uma pessoa no Agendor.

        Args:
            person_id (int): ID da pessoa a ser deletada.

        Returns:
            Dict[str, Any]: Resposta da API após a exclusão.

        Example:
            >>> agendor_api.delete_person(person_id=12345)
        """

        if not person_id:
            raise ValueError("Person ID is required")
        
        endpoint = f"people/{person_id}"
        return self._request("DELETE", endpoint)

    # ORGANIZATIONS
    def list_organizations(
        self, 
        page: int = 1, 
        per_page: int = 10, 
        name: Optional[str] = None, 
        nameExact: Optional[str] = None, 
        category: Optional[int] = None,
        sector: Optional[int] = None, 
        leadOrigin: Optional[int] = None, 
        products: Optional[List[int]] = None, 
        userOwner: Optional[int] = None, 
        cnpj: Optional[str] = None,
        author: Optional[int] = None, 
        state: Optional[str] = None, 
        cityName: Optional[str] = None, 
        district: Optional[str] = None, 
        email: Optional[str] = None,
        work_phone: Optional[str] = None, 
        mobile_phone: Optional[str] = None, 
        fax_phone: Optional[str] = None, 
        whatsapp: Optional[str] = None, 
        phone: Optional[str] = None,
        createdAtGt: Optional[str] = None, 
        createdAtLt: Optional[str] = None, 
        updatedAtGt: Optional[str] = None, 
        updatedAtLt: Optional[str] = None, 
        withCustomFields: bool = False
    ) -> Dict[str, Any]:
        """
        Lista todas as organizações no Agendor com os parâmetros de consulta especificados.

        Args:
            page (int, optional): Número da página dos resultados. Padrão é 1.
            per_page (int, optional): Número de resultados por página. Máximo de 100. Padrão é 10.
            name (str, optional): Prefixo do nome da organização.
            nameExact (str, optional): Nome exato da organização.
            category (int, optional): ID da categoria da organização.
            sector (int, optional): ID do setor da organização.
            leadOrigin (int, optional): ID da origem do lead.
            products (List[int], optional): Lista de IDs de produtos associados à organização.
            userOwner (int, optional): ID do usuário responsável pela organização.
            cnpj (str, optional): Prefixo do CNPJ da organização.
            author (int, optional): ID do autor do cadastro.
            state (str, optional): Sigla do estado.
            cityName (str, optional): Nome da cidade.
            district (str, optional): Nome do distrito ou bairro.
            email (str, optional): Prefixo do endereço de email.
            work_phone (str, optional): Telefone comercial da organização.
            mobile_phone (str, optional): Telefone celular da organização.
            fax_phone (str, optional): Número de fax da organização.
            whatsapp (str, optional): Número de WhatsApp da organização.
            phone (str, optional): Número de telefone geral da organização.
            createdAtGt (str, optional): Filtrar por organizações criadas após essa data.
            createdAtLt (str, optional): Filtrar por organizações criadas antes dessa data.
            updatedAtGt (str, optional): Filtrar por organizações atualizadas após essa data.
            updatedAtLt (str, optional): Filtrar por organizações atualizadas antes dessa data.
            withCustomFields (bool, optional): Se verdadeiro, inclui campos personalizados nas respostas.

        Returns:
            Dict[str, Any]: Dicionário contendo os dados das organizações retornadas pela API do Agendor.

        Example:
            >>> orgs = agendor_api.list_organizations(name="Tech")
            >>> for org in orgs:
            ...     print(org['name'])
        """
        if per_page > 100:
            per_page = 100

        params = {
            "page": page,
            "per_page": per_page
        }

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

        return self._request("GET", "organizations", params=params)

    def create_organization(
        self,
        name: str,
        legalName: Optional[str] = None,
        cnpj: Optional[str] = None,
        description: Optional[str] = None,
        logo: Optional[str] = None,
        website: Optional[str] = None,
        ranking: Optional[int] = None,
        ownerUser: Optional[int] = None,
        email: Optional[str] = None,
        work: Optional[str] = None,
        mobile: Optional[str] = None,
        fax: Optional[str] = None,
        whatsapp: Optional[str] = None,
        facebook: Optional[str] = None,
        twitter: Optional[str] = None,
        instagram: Optional[str] = None,
        linked_in: Optional[str] = None,
        skype: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        street_name: Optional[str] = None,
        street_number: Optional[int] = None,
        additional_info: Optional[str] = None,
        city: Optional[int] = None,
        leadOrigin: Optional[int] = None,
        category: Optional[int] = None,
        sector: Optional[int] = None,
        products: Optional[List[int]] = None,
        allowedUsers: Optional[List[int]] = None,
        allowToAllUsers: bool = False,
        customFields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Cria uma nova organização no Agendor com os parâmetros especificados.

        Args:
            name (str): Nome fantasia da organização (obrigatório).
            legalName (str, opcional): Razão social da organização.
            cnpj (str, opcional): CNPJ da organização.
            description (str, opcional): Descrição da organização.
            logo (str, opcional): URL do logotipo da organização.
            website (str, opcional): URL do site da organização.
            ranking (int, opcional): Classificação da organização (0 a 5).
            ownerUser (int, opcional): ID ou email do proprietário da organização.
            email (str, opcional): Email de contato da organização.
            work (str, opcional): Telefone comercial da organização.
            mobile (str, opcional): Telefone celular da organização.
            fax (str, opcional): Número de fax da organização.
            whatsapp (str, opcional): Número do WhatsApp da organização.
            facebook (str, opcional): URL do perfil no Facebook.
            twitter (str, opcional): URL do perfil no Twitter.
            instagram (str, opcional): URL do perfil no Instagram.
            linked_in (str, opcional): URL do perfil no LinkedIn.
            skype (str, opcional): Nome de usuário no Skype.
            postal_code (str, opcional): CEP do endereço da organização.
            country (str, opcional): País do endereço.
            district (str, opcional): Bairro do endereço.
            state (str, opcional): Sigla do estado do endereço.
            street_name (str, opcional): Nome da rua do endereço.
            street_number (int, opcional): Número do endereço.
            additional_info (str, opcional): Informações adicionais do endereço.
            city (int, opcional): ID da cidade do endereço.
            leadOrigin (int, opcional): ID ou nome da origem do lead.
            category (int, opcional): ID ou nome da categoria.
            sector (int, opcional): ID ou nome do setor.
            products (List[int], opcional): Lista de IDs de produtos.
            allowedUsers (List[int], opcional): IDs de usuários permitidos a visualizar a organização.
            allowToAllUsers (bool, opcional): Se verdadeiro, permite acesso a todos os usuários.
            customFields (Dict[str, Any], opcional): Campos personalizados.

        Returns:
            Dict[str, Any]: Dados da organização criada.

        Example:
            >>> org = agendor_api.create_organization(
            ...     name="Tech Corp",
            ...     cnpj="12.345.678/0001-99",
            ...     email="contato@techcorp.com"
            ... )
        """
        if not name:
            raise ValueError("'name' is required")
        
        data = {
            "name": name
        }

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
            if not (0 <= ranking <= 5):
                raise ValueError("'ranking' must be between 0 and 5")
            data["ranking"] = ranking
        if ownerUser:
            data["ownerUser"] = ownerUser

        # Assemble contact information
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

        # Assemble address information
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

        return self._request("POST", "organizations", json=data)

    def update_organization(
        self,
        org_id: int,
        name: Optional[str] = None,
        legalName: Optional[str] = None,
        cnpj: Optional[str] = None,
        description: Optional[str] = None,
        logo: Optional[str] = None,
        website: Optional[str] = None,
        ranking: Optional[int] = None,
        ownerUser: Optional[int] = None,
        email: Optional[str] = None,
        work: Optional[str] = None,
        mobile: Optional[str] = None,
        fax: Optional[str] = None,
        whatsapp: Optional[str] = None,
        facebook: Optional[str] = None,
        twitter: Optional[str] = None,
        instagram: Optional[str] = None,
        linked_in: Optional[str] = None,
        skype: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        street_name: Optional[str] = None,
        street_number: Optional[int] = None,
        additional_info: Optional[str] = None,
        city: Optional[int] = None,
        leadOrigin: Optional[int] = None,
        category: Optional[int] = None,
        sector: Optional[int] = None,
        products: Optional[List[int]] = None,
        allowedUsers: Optional[List[int]] = None,
        allowToAllUsers: Optional[bool] = None,
        customFields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Atualiza uma organização no Agendor com os parâmetros especificados.

        Args:
            org_id (int): ID da organização a ser atualizada (obrigatório).
            name (str, opcional): Nome fantasia da organização.
            legalName (str, opcional): Razão social da organização.
            cnpj (str, opcional): CNPJ da organização.
            description (str, opcional): Descrição da organização.
            logo (str, opcional): URL do logotipo da organização.
            website (str, opcional): URL do site da organização.
            ranking (int, opcional): Classificação da organização (0 a 5).
            ownerUser (int, opcional): ID ou email do proprietário da organização.
            email (str, opcional): Email de contato da organização.
            work (str, opcional): Telefone comercial da organização.
            mobile (str, opcional): Telefone celular da organização.
            fax (str, opcional): Número de fax da organização.
            whatsapp (str, opcional): Número do WhatsApp da organização.
            facebook (str, opcional): URL do perfil no Facebook.
            twitter (str, opcional): URL do perfil no Twitter.
            instagram (str, opcional): URL do perfil no Instagram.
            linked_in (str, opcional): URL do perfil no LinkedIn.
            skype (str, opcional): Nome de usuário no Skype.
            postal_code (str, opcional): CEP do endereço da organização.
            country (str, opcional): País do endereço.
            district (str, opcional): Bairro do endereço.
            state (str, opcional): Sigla do estado do endereço.
            street_name (str, opcional): Nome da rua do endereço.
            street_number (int, opcional): Número do endereço.
            additional_info (str, opcional): Informações adicionais do endereço.
            city (int, opcional): ID da cidade do endereço.
            leadOrigin (int, opcional): ID ou nome da origem do lead.
            category (int, opcional): ID ou nome da categoria.
            sector (int, opcional): ID ou nome do setor.
            products (List[int], opcional): Lista de IDs de produtos.
            allowedUsers (List[int], opcional): IDs de usuários permitidos a visualizar a organização.
            allowToAllUsers (bool, opcional): Se verdadeiro, permite acesso a todos os usuários.
            customFields (Dict[str, Any], opcional): Campos personalizados.

        Returns:
            Dict[str, Any]: Dados da organização atualizados.

        Example:
            >>> org = agendor_api.update_organization(org_id=12345, name="New Corp Name")
        """
        if not org_id:
            raise ValueError("Organization ID is required.")
        
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
            if not (0 <= ranking <= 5):
                raise ValueError("Ranking must be between 0 and 5.")
            data["ranking"] = ranking
        if ownerUser:
            data["ownerUser"] = ownerUser

        # Assemble contact information
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

        # Assemble address information
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

        endpoint = f"organizations/{org_id}"
        
        return self._request("PUT", endpoint, json=data)

    # DEALS
    def get_deal_stage(deal_stages: list, deal_stage: int) -> int:
        for stage in deal_stages:
            if stage['id'] == deal_stage:
                return stage['sequence']

        return None

    def create_new_deal(
        self,
        entity_type: str,
        entity_id: int,
        title: str,
        dealStatusText: Optional[str] = None,
        description: Optional[str] = None,
        endTime: Optional[datetime] = None,
        products_entities: Optional[List[Dict[str, Any]]] = None,
        products: Optional[List[int]] = None,
        ranking: Optional[int] = None,
        startTime: Optional[datetime] = None,
        ownerUser: Optional[int] = None,
        funnel_id: Optional[int] = None,
        dealStage: Optional[int] = None,
        value: Optional[float] = None,
        allowedUsers: Optional[List[int]] = None,
        allowToAllUsers: Optional[bool] = None,
        customFields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Cria um novo negócio no Agendor.

        Args:
            entity_type (str): Tipo de entidade do negócio (deve ser "people" ou "organizations").
            entity_id (int): ID da entidade relacionada ao negócio.
            title (str): Título do negócio.
            dealStatusText (str, opcional): Status do negócio ("ongoing", "won", "lost").
            description (str, opcional): Descrição do negócio.
            endTime (datetime, opcional): Data de término do negócio.
            products_entities (List[Dict[str, Any]], opcional): Lista de produtos no negócio.
            products (List[int], opcional): Lista de IDs de produtos.
            ranking (int, opcional): Classificação do negócio (0 a 100).
            startTime (datetime, opcional): Data de início do negócio.
            ownerUser (int, opcional): ID do responsável pelo negócio.
            funnel_id (int, opcional): ID do funil de vendas.
            dealStage (int, opcional): Estágio do negócio no funil.
            value (float, opcional): Valor do negócio.
            allowedUsers (List[int], opcional): IDs de usuários com permissão de acesso.
            allowToAllUsers (bool, opcional): Se verdadeiro, permite acesso a todos os usuários.
            customFields (Dict[str, Any], opcional): Campos personalizados do negócio.

        Returns:
            Dict[str, Any]: Dados do negócio criado.

        Example:
            >>> deal = agendor_api.create_new_deal(
            ...     entity_type="people",
            ...     entity_id=12345,
            ...     title="Novo Negócio",
            ...     value=10000.0
            ... )
        """
        if entity_type not in ["people", "organizations"]:
            raise ValueError(f"Invalid entity_type. Must be one of: person, organization")
        
        if not entity_id or not title:
            raise ValueError("Entity ID and title are required")
        valid_statuses = ["ongoing", "won", "lost"]
        
        data = {
            "title": title,
        }

        if dealStatusText:
            if dealStatusText not in valid_statuses:
                raise ValueError(f"Invalid dealStatusText. Must be one of: {', '.join(valid_statuses)}")
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
            if not (0 <= ranking <= 100):
                raise ValueError("Ranking must be between 0 and 100")
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
        if funnel_id:
            data["funnel"] = funnel_id
            if dealStage:
                data["dealStage"] = dealStage

        endpoint = f"{entity_type}/{entity_id}/deals"
        return self._request("POST", endpoint, json=data)

    def list_deals(self, entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
        """
        Lista todos os negócios relacionados a uma entidade no Agendor.

        Args:
            entity_type (str): Tipo de entidade ("people" ou "organizations").
            entity_id (int): ID da entidade relacionada ao negócio.

        Returns:
            List[Dict[str, Any]]: Lista de negócios.

        Example:
            >>> deals = agendor_api.list_deals(entity_type="people", entity_id=12345)
            >>> for deal in deals:
            ...     print(deal['title'])
        """
        if entity_type not in ["people", "organizations"]:
            raise ValueError(f"Invalid entity_type. Must be one of: person, organization")

        endpoint = f"{entity_type}/{entity_id}/deals"
        return self._request("GET", endpoint)

    def update_deal(
        self,
        deal_id: int,
        value: Optional[float] = None,
        description: Optional[str] = None,
        startTime: Optional[datetime] = None,
        products_entities: Optional[List[Dict[str, Any]]] = None,
        products: Optional[List[str]] = None,
        ownerUser: Optional[int] = None,
        allowedUsers: Optional[List[int]] = None,
        allowToAllUsers: Optional[bool] = None,
        customFields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Atualiza as informações de um negócio no Agendor.

        Args:
            deal_id (int): ID do negócio a ser atualizado (obrigatório).
            value (float, opcional): Valor do negócio.
            description (str, opcional): Descrição do negócio.
            startTime (datetime, opcional): Data de início do negócio.
            products_entities (List[Dict[str, Any]], opcional): Lista de produtos no negócio.
            products (List[str], opcional): Lista de nomes de produtos.
            ownerUser (int, opcional): ID do responsável pelo negócio.
            allowedUsers (List[int], opcional): IDs de usuários com permissão de acesso.
            allowToAllUsers (bool, opcional): Se verdadeiro, permite acesso a todos os usuários.
            customFields (Dict[str, Any], opcional): Campos personalizados do negócio.

        Returns:
            Dict[str, Any]: Dados do negócio atualizado.

        Example:
            >>> updated_deal = agendor_api.update_deal(
            ...     deal_id=12345,
            ...     value=15000.0
            ... )
        """
        if not deal_id:
            raise ValueError("Deal ID is required")
        
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

        endpoint = f"deals/{deal_id}"
        return self._request("PUT", endpoint, json=data)

    def get_deal(self, deal_id: int) -> Dict[str, Any]:
        """
        Obtém os detalhes de um negócio no Agendor.

        Args:
            deal_id (int): ID do negócio.

        Returns:
            Dict[str, Any]: Dados do negócio.

        Example:
            >>> deal = agendor_api.get_deal(deal_id=12345)
            >>> print(deal['title'])
        """
        if not deal_id:
            raise ValueError("Deal ID is required")
        
        endpoint = f"deals/{deal_id}"
        return self._request("GET", endpoint)
    
    def update_deal_stage(self, deal_id: int, deal_stage: int, funnel_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Atualiza o estágio de um negócio no Agendor.

        Args:
            deal_id (int): ID do negócio.
            deal_stage (int): Novo estágio do negócio.
            funnel_id (int, opcional): Novo ID do funil de vendas.

        Returns:
            Dict[str, Any]: Dados do negócio atualizado.

        Example:
            >>> agendor_api.update_deal_stage(deal_id=12345, deal_stage=2)
        """
        if not deal_id or not deal_stage:
            raise ValueError("Deal ID and deal stage are required")
    
        data = {
            "dealStage": deal_stage
        }

        if funnel_id:
            data["funnel"] = funnel_id
        
        endpoint = f"deals/{deal_id}/stage"
        return self._request("PUT", endpoint, json=data)
    
    def update_deal_status(self, deal_id: int, deal_status_text: str) -> Dict[str, Any]:
        """
        Atualiza o status de um negócio no Agendor.

        Args:
            deal_id (int): ID do negócio.
            deal_status_text (str): Novo status do negócio ("ongoing", "won", "lost").

        Returns:
            Dict[str, Any]: Dados do negócio atualizado.

        Example:
            >>> agendor_api.update_deal_status(deal_id=12345, deal_status_text="won")
        """

        valid_statuses = ["ongoing", "won", "lost"]

        if deal_status_text not in valid_statuses:
            raise ValueError(f"Invalid deal status. Valid statuses are: {', '.join(valid_statuses)}")

        if not deal_id:
            raise ValueError("Deal ID is required")
        
        data = {
            "dealStatusText": deal_status_text
        }

        endpoint = f"deals/{deal_id}/status"
        return self._request("PUT", endpoint, json=data)
    
agendor = AgendorApi()