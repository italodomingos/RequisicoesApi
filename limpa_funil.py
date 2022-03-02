import logging

import requests

data = {
    "filter": {
        "CATEGORY_ID": "9"
    },
    "select": ["ID"]
}
# request = requests.post("https://bambui.bitrix24.com.br/rest/57/twhlofvidecl4w63/crm.deal.list", headers=headers,
#                         data=data)

while True:
    try:
        request = requests.post("https://bambui.bitrix24.com.br/rest/57/twhlofvidecl4w63/crm.deal.list", json=data)
        cards_funil_results = request.json()
        cards_funil = cards_funil_results['result']
        print(cards_funil_results)

        for card in cards_funil:

            delete_params = {

                "ID": card['ID']
            }
            request = requests.post("https://bambui.bitrix24.com.br/rest/57/twhlofvidecl4w63/crm.deal.delete",
                                    json=delete_params)

            print(f"Card com o ID: {card['ID']} removido")

        if cards_funil_results['next']:
            data['start'] = cards_funil_results['next']

        else:
            break

    except Exception as e:
        logging.exception(e)
        break

