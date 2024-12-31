import json
import math
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from .models import Client


# URLs and paths
urls = {
    "loginPage": "https://portal.unimedpalmas.coop.br/",
    "targetPage": "https://portal.unimedpalmas.coop.br/wheb_gridDet.jsp",
}

paths = {
    "outputFile": "guiasFaturar.csv",
}

# Retry settings
retry_settings = {
    "defaultTimeout": 10000,  # milliseconds
    "maxRetries": 3,
    "delayBetweenRetries": 5,  # seconds
}

# Data positions
data_positions = [1, 29, 2, 3, 17, 5, 16]


# Utility functions
def get_elapsed_time(start_time):
    time_in_seconds = math.floor((time.time() - start_time) / 1000)
    if time_in_seconds < 60:
        return f"{time_in_seconds} segundo{'s' if time_in_seconds != 1 else ''}"
    else:
        minutes = math.floor(time_in_seconds / 60)
        remaining_seconds = time_in_seconds % 60
        if remaining_seconds == 0:
            return f"{minutes} minuto{'s' if minutes != 1 else ''}"
        else:
            return (
                f"{minutes} minuto{'s' if minutes != 1 else ''} e "
                f"{remaining_seconds} segundo{'s' if remaining_seconds != 1 else ''}"
            )


def format_elapsed_time(elapsed_time):
    total_seconds = math.floor(elapsed_time / 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def is_a_month_older(date_string):
    day, month, year = date_string.split(";")[2].split(" ")[0].split("/")
    input_date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
    today = datetime.today()
    diff_in_days = (today - input_date).days
    return diff_in_days >= 32


def retry(fn):
    retries = retry_settings["maxRetries"]
    delay = retry_settings["delayBetweenRetries"] / 1000  # convert to seconds
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except Exception as e:
            if attempt < retries:
                print(f"Attempt {attempt} failed. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"All {retries} attempts failed.")
                raise


def get_nth_frame(page):
    return (
        page.frame_locator("iframe >> nth=0")
        .frame_locator("#principal")
        .frame_locator("td iframe")
        .frame_locator("frame >> nth=0")
    )


def get_principal_frame(page):
    return (
        page.frame_locator("iframe >> nth=0")
        .frame_locator("#principal")
        .frame_locator("td iframe")
        .frame_locator("#paginaPrincipal")
    )


def match_code(code):
    if len(str(code)) != 8:
        return None

    code_map = {
        20103131: "24,00",
        20103220: "8,09",
        20103344: "12,64",
        20103484: "6,72",
        20103492: "12,00",
        20103506: "6,72",
        20103514: "12,00",
        20103522: "25,28",
        20103646: "156,48",
        20103662: "11,38",
        50000144: "30,36",
        50000160: "12,64",
    }

    return code_map.get(code, None)


def login_auth(credentials, page):
    page.goto(urls["loginPage"], wait_until="domcontentloaded")
    frame = page.frame_locator("iframe >> nth=0").frame_locator("#principal")
    frame.locator("#tipoUsuario").select_option("P")
    frame.locator("#nmUsuario").fill(credentials["login"])
    frame.locator("#dsSenha").fill(credentials["password"])
    frame.get_by_role("button", name="Entrar").click()
    print("Login successful!")
    frame = navigate_executar_guia(page)
    return frame


def navigate_executar_guia(page):
    frame = (
        page.locator("iframe")
        .first.content_frame.locator("#principal")
        .content_frame.get_by_role("cell")
        .locator("iframe")
        .content_frame.locator("#menuLateral")
        .content_frame
    )
    frame.get_by_text("Execução da requisição").click()
    frame.get_by_text("» Executar requisição").click()
    frame = get_pagina_principal_frame(page)
    print("Navigation to target page successful!")
    return frame


def get_pagina_principal_frame(page):
    return (
        page.locator("iframe")
        .first.content_frame.locator("#principal")
        .content_frame.get_by_role("cell")
        .locator("iframe")
        .content_frame.locator("#paginaPrincipal")
        .content_frame
    )


def executar_guia(
    frame, codigo_beneficiario, nome_beneficiario, tipo_atendimento, quantidade
):

    print(f"Executando GUIA: {codigo_beneficiario} -  {nome_beneficiario}")
    frame.locator("#CD_USUARIO_PLANO").clear()
    frame.locator("#CD_USUARIO_PLANO").type(codigo_beneficiario)
    frame.get_by_role("button", name="Consultar").click()
    nomeBeneficiario = frame.locator("#NM_SEGURADO").input_value()

    if not nomeBeneficiario:
        print("Beneficiário não encontrado!")
        return None
    else:
        if get_extrato_guias(frame, codigo_beneficiario):
            frame.locator('input[type="checkbox"]').first.click()
            frame.get_by_role("button", name="Gerar guia").click()
            frame.locator("select").select_option(tipo_atendimento)
            frame.locator('input[type="text"]').fill(str(quantidade))
            frame.get_by_role("button", name="Confirmar geração de guias").click()
            frame.get_by_role("button", name="Voltar").click()
            return True
        else:
            return None


def get_extrato_guias(frame, codigo_beneficiario):
    try:
        frame.locator('role=cell[name="Procedimento"]').first.wait_for(timeout=2000)
    except Exception as e:
        total_requisicao = 0
        print(f"entrou extrato_guias {e}")
    else:
        total_requisicao = frame.get_by_role("cell", name="Procedimento").count()

    if total_requisicao == 0:
        client = Client.objects.filter(codigo_beneficiario=codigo_beneficiario)
        print(f"Client: {client}")
        client.update(active=False)
        client.save()
        return None
    else:
        try:
            codigo_requisicao = frame.get_by_role("cell").nth(23).inner_text()
            validade_guia = frame.get_by_role("cell").nth(25).inner_text()
            qtd_solicitada = frame.get_by_role("cell").nth(29).inner_text()
            qtd_aprovada = frame.get_by_role("cell").nth(29).inner_text()
            qtd_executada = frame.get_by_role("cell").nth(30).inner_text()
            qtd_restante = frame.get_by_role("cell").nth(31).inner_text()

            print(
                f"validade_guia: {validade_guia}, codigo_requisicao: {codigo_requisicao}, "
                f"qtd_solicitada: {qtd_solicitada}, qtd_aprovada: {qtd_aprovada}, "
                f"qtd_executada: {qtd_executada}, qtd_restante: {qtd_restante}, "
                f"total_requisicao: {total_requisicao}"
            )

            return (
                validade_guia,
                codigo_requisicao,
                qtd_solicitada,
                qtd_aprovada,
                qtd_executada,
                qtd_restante,
                total_requisicao,
            )
        except Exception as e:
            print(f"Error extracting details: {str(e)}")
            return None


def process_and_execute(clients, page):
    try:
        for client in clients:
            try:
                codigo_beneficiario = client["codigo_beneficiario"]
                nome_beneficiario = client["nome_beneficiario"]
                tipo_atendimento = client["tipo_atendimento"]
                quantidade = client["quantidade"]

                # Retrieve the main frame
                frame = get_pagina_principal_frame(page)

                # Execute the main action
                result = executar_guia(
                    frame,
                    codigo_beneficiario,
                    nome_beneficiario,
                    tipo_atendimento,
                    quantidade,
                )

                # Handle result and navigate back if necessary
                if result is None:
                    frame.get_by_role("button", name="Nova consulta").click()

            except Exception as e:
                print(f"Error processing client {codigo_beneficiario}: {e}")
                continue

    except Exception as e:
        print(f"Unexpected error during processing: {e}")


def login_and_navigate(credentials, clients):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.on(
            "dialog",
            lambda dialog: (
                print(f"DIALOG: {dialog.message}"),
                dialog.accept(),
            ),
        )

        # Event listener for popup
        page.on("popup", lambda popup: (popup.wait_for_load_state(), popup.close()))

        page.set_default_timeout(retry_settings["defaultTimeout"])
        login_auth(credentials, page)
        process_and_execute(clients, page)
        # input("Press Enter to close the browser...")
        browser.close()


def login(page, credentials, menu_option):
    page.goto(urls["loginPage"], wait_until="domcontentloaded")

    frame = page.frame_locator("iframe >> nth=0").frame_locator("#principal")
    frame.locator("#tipoUsuario").select_option("P")
    frame.locator("#nmUsuario").fill(credentials["login"])
    frame.locator("#dsSenha").fill(credentials["password"])
    frame.get_by_role("button", name="Entrar").click()
    print("Login successful!")
    frame = (
        page.locator("iframe")
        .first.content_frame.locator("#principal")
        .content_frame.get_by_role("cell")
        .locator("iframe")
        .content_frame.locator("#menuLateral")
        .content_frame
    )
    frame.get_by_text(menu_option).click()
    print("Navigation to target page successful!")
    return page, frame


def get_beneficiario_data(payload_json, codigo_beneficiario):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.on(
            "dialog",
            lambda dialog: (
                print(f"DIALOG: {dialog.message}"),
                dialog.accept(),
            ),
        )
        page.on("popup", lambda popup: (popup.wait_for_load_state(), popup.close()))

        page.set_default_timeout(retry_settings["defaultTimeout"])
        credentials = json.loads(payload_json)
        page, frame = login(page, credentials, "Dossiê beneficiário")
        frame = get_pagina_principal_frame(page)
        frame.locator("#CD_USUARIO_PLANO").clear()
        frame.locator("#CD_USUARIO_PLANO").type(codigo_beneficiario)
        frame.locator("#CD_USUARIO_PLANO").press("Tab")
        content = frame.locator("#tipoUsuario").all_inner_texts()
        print(content)
        input("Press Enter to close the browser...")


# browser.close()