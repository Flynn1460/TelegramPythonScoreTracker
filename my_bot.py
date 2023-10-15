from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN: Final = 'YOUR TOKEN'
BOT_USERNAME: Final = '@BOT_NAME'

global score_expected
score_expected = False

# RESPOND TO NORMAL MESSAGES

def get_dependencies(text):
    variables = [""]
    curr_var = 0
    for i in range(len(text)):
        if text[i] == ' ':
            curr_var += 1
            variables.append("");

        else:
            variables[curr_var] += text[i]
    
    variables.remove(variables[0])

    return variables


def play_command():
    LOADED_SCORES = 10

    scoreFile = open("saved_info.txt", "r")
    scores = scoreFile.readlines()
    scoreFile.close()

    nums = []

    for i in range(len(scores)):
        nums.append([])
        for x in range(len(scores[i])):
            if scores[i][x] == ':':
                nums[i].append(str(scores[i][:x]))
                nums[i].append(int(scores[i][x+1:len(scores[i])-1]))

    new_nums = sorted(nums, key=lambda x: x[1], reverse=True)

    if (len(new_nums) > LOADED_SCORES):
        new_nums = new_nums[:LOADED_SCORES]

    display_text = ""

    for i in range(len(new_nums)):
        display_text += str(i+1) + ". " + str(new_nums[i][0]) + " - " + str(new_nums[i][1]) + "\n"

    display_text += "\nEnter your scores with '- SCORE NAME' to save your score on the table" 

    return display_text + "\n\nINSERT GAME HERE"

def add_score_command(text, user):
    variables = get_dependencies(text)
    
    filtered_vars = [variables[1], variables[0]]

    final_text = ""
    for i in range(len(filtered_vars)):
        final_text += str(i+1) + ". " + filtered_vars[i] + "\n"

    scoreFile = open("saved_info.txt", "a")
    scoreFile.write(filtered_vars[0] + ":" + filtered_vars[1] + "\n")
    scoreFile.close()

    final_text = 'Added Score - ' + filtered_vars[0] + ": " + filtered_vars[1] + "\n\nNew Standings \n\n " + play_command()

    return final_text

def process_response(text: str, user) -> str:
    processed: str = text.lower()

    if (processed[0:2] == "- "):
        return add_score_command(text, user)

    if processed[0:11] == "/play":
        score_expected = True

        return play_command()

    elif (processed[0] == '/' or processed[1] == '-'):
        return 'Im baffled by that'


def handle_response(message_type, text, user, group_direct_reff):
    if (bool(message_type == 'group') & bool(group_direct_reff)):
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            return process_response(new_text, user)
        
        else:
            return
    
    else:
        return process_response(text, user)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text
    user_id = update.message.chat.id
    user = update.message.from_user

    print(f' User {user_id} in {message_type}: "{text}"')

    response: str = handle_response(message_type, text, user, False)
    
    print('Bot : ', response)

    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print('Starting')
    app = Application.builder().token(TOKEN).build()

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)
    
    print('Checking')
    app.run_polling(poll_interval=1)