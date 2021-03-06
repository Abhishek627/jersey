"""List handling"""
import datetime
import pytz
import colorama
from trelloutil import backlog_board, format_due_date, CARD_ID_POSTFIX_COUNT
from label import label_name_with_color

def display_active_lists(label_name=None):
    """Display all active lists"""

    active_lists = ['doing', 'blocked', 'need_to_do']

    for active_list in active_lists:
        print(f'{colorama.Style.BRIGHT}{colorama.Fore.YELLOW}{active_list}')
        print(f'{colorama.Fore.RED}{"-" * len(active_list)}{colorama.Style.NORMAL}{colorama.Fore.RESET}')
        display_list(active_list, label_name=label_name)
        print()

def display_list(list_name, label_name=None):
    """Display a list of cards by list name"""

    board = backlog_board()

    lists = board.list_lists()
    input_list = [_ for _ in lists if _.name == list_name][0]

    for card in sorted(
            input_list.list_cards(),
            key=lambda card: str(card.due_date) if card.due_date else 'zzz'):
        if label_name:
            matched_labels = [label for label in card.labels if label.name == label_name]
            if not matched_labels:
                continue
        due_output = format_due_date(card)
        comments_count = len(card.get_comments())
        comments_output = f' {colorama.Fore.GREEN}({comments_count})' if comments_count > 0 else ''
        label_output = ' '.join([label_name_with_color(card_label) for card_label in card.labels])
        # pylint: disable=line-too-long
        print(f'{colorama.Fore.YELLOW}{card.id[-CARD_ID_POSTFIX_COUNT:]} {due_output} {colorama.Fore.RESET}{card.name}{comments_output} {label_output}')

def arg_list_cards_by_label(cli_args):
    """List all cards by label name"""

    display_active_lists(label_name=cli_args.label)

def arg_list(cli_args):
    """List a board card summary"""

    display_list(cli_args.list_name)

def sort_list(trello_list):
    """Sort the cards in a list"""
    cards = trello_list.list_cards()

    if not cards:
        return

    min_pos = min(cards, key=lambda card: card.pos).pos
    max_pos = max(cards, key=lambda card: card.pos).pos
    len_cards = len(cards)

    # no need to sort if there are no cards, or only 1
    if len_cards <= 1:
        return

    # pylint: disable=line-too-long
    for idx, card in enumerate(sorted(
            trello_list.list_cards(),
            key=lambda card: card.due_date if card.due_date else datetime.datetime.max.replace(tzinfo=pytz.UTC))):
        target_pos = min_pos + (idx * (max_pos - min_pos) / (len_cards - 1))
        if card.pos != target_pos:
            card.set_pos(target_pos)

def arg_sort(cli_args):
    """Sort all cards in board"""
    board = backlog_board()

    for trello_list in board.list_lists():
        if trello_list.name != 'done':
            sort_list(trello_list)
