import os
import requests


TELEGRAM_API = "https://api.telegram.org/bot{}/sendMessage"


def send_telegram_message(
    bot_token,
    chat_id,
    message,
):
    """
    Send one E-AWARE fisher brief through Telegram.
    """

    url = TELEGRAM_API.format(
        bot_token
    )

    payload = {
        "chat_id": chat_id,
        "text": message,
    }

    response = requests.post(
        url,
        json=payload,
        timeout=20,
    )

    response.raise_for_status()

    return response.json()


def send_to_registered_fishers(
    message,
):
    """
    Send the daily brief to every registered
    Telegram chat ID stored in GitHub Secrets.

    TELEGRAM_CHAT_IDS format:

    123456789,987654321,555555555
    """

    bot_token = os.getenv(
        "TELEGRAM_BOT_TOKEN"
    )

    chat_ids = os.getenv(
        "TELEGRAM_CHAT_IDS"
    )

    if not bot_token:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is missing."
        )

    if not chat_ids:
        raise ValueError(
            "TELEGRAM_CHAT_IDS is missing."
        )

    ids = [
        item.strip()
        for item in chat_ids.split(",")
        if item.strip()
    ]

    results = []

    for chat_id in ids:

        result = send_telegram_message(
            bot_token,
            chat_id,
            message,
        )

        results.append(
            {
                "chat_id": chat_id,
                "success": result.get(
                    "ok",
                    False,
                ),
            }
        )

    return results


if __name__ == "__main__":

    from daily_brief import generate_daily_brief

    message = generate_daily_brief()

    results = send_to_registered_fishers(
        message
    )

    print(results)
