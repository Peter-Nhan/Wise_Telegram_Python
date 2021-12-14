#!/usr/local/bin/python3
import logging
import requests
from telegram import Update, message
from telegram.ext import Updater, CommandHandler, CallbackContext

AudUsdExchange = 1.00
tw_check_interval = 600
tw_token_headers = {'content-type': 'application/json', 'accept':'application/json', 'Authorization' : 'Bearer 1ae78624-e606-4444-b073-dfb52daf5e4c'}
tw_url = "https://api.sandbox.transferwise.tech/v1/rates?source=USD&target=AUD"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('*_Wise Bot_*', parse_mode='MarkdownV2')
    update.message.reply_text("Chat_id = {} ".format(update.message.chat_id))
    update.message.reply_text('Use /tw_on <AUD_USD target> - check exchange rate every '+str(tw_check_interval)+' seconds - if checked exchange rate is better or equal to the target exchange rate then Send Message')
    update.message.reply_text('Use /tw_off - turn off currency checks')
    update.message.reply_text('Use /tw_now - currency checks now')
    print("===> /start message ")

    if(update.message.chat.id < 0):
        print("Message Chat ID - Group: {}".format(update.message.chat.id))
        print("Message Chat Title: {}".format(update.message.chat.title))
    else:
        print("Message Chat ID: {}".format(update.message.chat.id))
        print("Message Chat Individual Name: {}".format(update.message.chat.first_name))

def tw_check(context: CallbackContext) -> None:
    """Send the tw_check message."""
    print("===> TransferWise - checking exchange rate now")
    global AudUsdExchange
    job = context.job
    response = requests.get(tw_url, headers=tw_token_headers)
    if (AudUsdExchange >= 1/response.json()[0]['rate']):
        context.bot.send_message(job.context, text='Current Rate: {} - Watch Rate: {}'.format(1/response.json()[0]['rate'],AudUsdExchange))
        print("===> TransferWise = Good exchange rates - Current Rate: {} - Watch Rate: {}".format(1/response.json()[0]['rate'],AudUsdExchange))
    else:
        print("===> TransferWise = Bad exchange rates - Current Rate: {} - Watch Rate: {}".format(1/response.json()[0]['rate'],AudUsdExchange))

def tw_on(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    print("===> TransferWise - turn ON regular checks")
    chat_id = update.message.chat_id
    global AudUsdExchange
    try:
        # args[0] should contain the time for the timer in seconds
        AudUsdExchange = float(context.args[0])
        if AudUsdExchange < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(tw_check, tw_check_interval, context=chat_id, name=str(chat_id))

        text = 'AUD_USD target check set - ' + str(AudUsdExchange)
        if job_removed:
            text += ' -> Old currency check was removed.'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /tw_on <AUD_USD target>')

def tw_off(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    print("===> TransferWise - turn OFF regular checks")
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Currency check cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)

def tw_now(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    print("===> TransferWise - check now")
    chat_id = update.message.chat_id
    response = requests.get(tw_url, headers=tw_token_headers)
    update.message.reply_text("Currency now - {}".format(1/response.json()[0]['rate']))

def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("2134933667:AAHl3Y9sb8ytlsU_Y0qKjWbpcXRZLOcMfTA")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("tw_on", tw_on))
    dispatcher.add_handler(CommandHandler("tw_off", tw_off))
    dispatcher.add_handler(CommandHandler("tw_now", tw_now))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()

