#!/usr/bin/env python3

"""A Command Line Task Manager."""

import re
import pickle
from datetime import datetime as dt
from datetime import timedelta


def decide_action(command):
    """Decides which action the argument requires."""
    command_regex = re.search(r'^([-\w]*)\s?(.*)', command)
    command_main = command_regex.group(1).lower()
    command_extra = command_regex.group(2).lower()

    if command_main in ('ls','list'):
        if command_extra in ('t', 'today'):
            view_today()
        elif command_extra in ('o', 'overdue'):
            view_overdue()
        elif command_extra in ('tm', 'tomorrow'):
            view_tomorrow()
        elif command_extra in ('f', 'future'):
            view_tomorrow()
            view_future()
        elif command_extra in ('g', 'goals'):
            view_goals()
        elif command_extra in ('at', 'all-tasks'):
            view_overdue()
            view_today()
            view_tomorrow()
            view_future()
        elif command_extra in ('a', 'all'):
            view_goals()
            view_overdue()
            view_today()
            view_tomorrow()
            view_future()
        else:
            smart_display()

    elif command_main in ('a', 'add'):
        add_task(command_regex.group(2))

    elif command_main in ('ag', 'add-goal'):
        add_goal(command_regex.group(2))

    elif command_main in ('rm', 'remove'):
        if command_extra in ("all", 'a'):
            task_data.clear()
        else:
            delete_item(int(command_extra) - 1, deleted_tasks)

    elif command_main in ('rmg', 'remove-goal'):
        if command_extra in ("all", 'a'):
            goal_data.clear()
        else:
            delete_item(int(command_extra) - 1, deleted_goals)

    elif command_main in ('c', 'complete'):
        if 't' in command_extra or 'today' in command_extra:
            complete_today()
        else:
            complete_task(int(command_extra) - 1)

    elif command_main in ('cg', 'complete-goal'):
        complete_goal(int(command_extra) - 1)

    elif command_main in ('e', 'ed', 'edit'):
        edit_desc(command_regex.group(2))

    elif command_main in ('cd', 'change-date'):
        change_date(command_extra)

    elif command_main in ('ct', 'change-target'):
        change_target(command_extra)

    elif command_main in ('ar', 'add-repeat'):
        add_repeat(command_regex.group(2))

    elif command_main in ('rr', 'remove-repeat'):
        remove_repeat(int(command_extra) - 1)

    elif command_main in ('s', 'subtask'):
        add_sub(command_regex.group(2))

    elif command_main in ('cs', 'comp-subtask'):
        complete_sub(command_extra)

    elif command_main in ('rs', 'remove-subtask'):
        delete_sub(command_extra)

    elif command_main in ('es', 'edit-subtask'):
        edit_sub(command_regex.group(2))

    elif command.lower() in ('u', 'undo'):
        undo_action(deleted_tasks)

    elif command.lower() in ('uc', 'uncheck'):
        undo_action(completed_tasks)

    elif command.lower() in ('ug', 'undo-goal'):
        undo_action(deleted_goals)

    elif command.lower() in ('ucg', 'uncheck-goal'):
        undo_action(completed_goals)

    elif command.lower() in ('h', 'help'):
        show_help()


def view_today():
    """Prints all of today's tasks"""
    print()
    print('  ' + FONT_DICT['green'] + "TODAY'S TASKS" + FONT_DICT['end'])
    empty = True
    for task in task_data:
        if task[2] == current_date:
            print("   {}".format(task[0]).rjust(6) + "| {}".format(task[1]))
            # Check for Subtasks
            if task[4]:
                print_sub(int(task[0] - 1))
            empty = False
    if empty:
        print("    No Tasks Found")
    print()


def view_tomorrow():
    """Prints all tasks due tomorrow"""
    print()
    print('  ' + FONT_DICT['orange'] + "TOMORROW'S TASKS" + FONT_DICT['end'])
    empty = True
    for task in task_data:
        if ((dt.strptime(task[2], '%Y-%m-%d')
             - dt.strptime(current_date, '%Y-%m-%d')).days) == 1:
            print("    {}".format(task[0]).rjust(6) + "| {}".format(task[1]))
            # Check for Subtasks
            if task[4]:
                print_sub(int(task[0] - 1))
            empty = False
    if empty:
        print("    No Tasks Found")
    print()


def view_overdue():
    """Prints all overdue tasks."""
    print()
    print('  ' + FONT_DICT['red'] + "OVERDUE TASKS" + FONT_DICT['end'])
    empty = True
    for task in task_data:
        if task[2] < current_date:
            over = ((dt.strptime(current_date, '%Y-%m-%d')
                     - dt.strptime(task[2], '%Y-%m-%d')).days)
            if over == 1:
                print("    {}".format(task[0]).rjust(6)
                      + "| {}[Due Yesterday]".format(task[1]))
            else:
                print("    {}".format(task[0]).rjust(6)
                      + "| {}[Due {} Days Ago]".format(task[1], over))
            # Check for Subtasks
            if task[4]:
                print_sub(int(task[0] - 1))
            empty = False
    if empty:
        print("    No Tasks Found")
    print()


def view_future():
    """Prints all future tasks to the terminal.."""
    print()
    print('  ' + FONT_DICT['blue'] + "FUTURE TASKS" + FONT_DICT['end'])
    empty = True
    for task in task_data:
        if task[2] > current_date:
            until = ((dt.strptime(task[2], '%Y-%m-%d')
                          - dt.strptime(current_date, '%Y-%m-%d')).days)
            if until > 1:
                print("    {}".format(task[0]).rjust(6)
                      + "| {} [Due in {} Days]".format(task[1], until))
            # Check for Subtasks
                if task[4]:
                    print_sub(int(task[0] - 1))
                empty = False
    if empty:
        print("    No Tasks Found")
    print()


def view_goals():
    """Prints all goals"""
    print()
    print('  ' + FONT_DICT['magenta'] + "GOALS" + FONT_DICT['end'], end='\n')
    if not goal_data:
        print("    No Goals Found")
        return
    for goal in goal_data:
        percent_done = int(goal[3]) // 5
        print("    {}".format(goal[0]).rjust(6), end='')
        if goal[2]:
            print("| {} [Target: {}]".format(goal[1].upper(), goal[2]).ljust(75),
                  end='')
        else:
            print("| {}".format(goal[1].upper().ljust(71)), end='')
        print("{}{}{}{}{}".format(FONT_DICT['green no u'], '+' * percent_done,
              FONT_DICT['red no u'], '-' * (20 - percent_done), FONT_DICT['end']),
              end='\n')
    print()


def add_task(command_extra):
    """Adds system argument task to the task list."""
    add_regex = re.search(r'^"(.*)"\s?(\S*)?\s?(.*)?', command_extra)
    task = add_regex.group(1)
    opt_date = add_regex.group(2)
    opt_repeat = add_regex.group(3)

    if opt_date:
        date = opt_date
    else:
        date = current_date

    if opt_repeat:
        if ',' in opt_repeat:
            repeat = opt_repeat.split(',')
        else:
            repeat = opt_repeat
    else:
        repeat = ''
    task_data.append([len(task_data) + 1, task, date, repeat, ''])
    update_order()


def add_goal(command_extra):
    """Adds a goal to the goal list."""
    gadd_regex = re.search(r'^"([^"]*)"\s?"?([^"]*)?"?\s?(.*)?', command_extra)
    goal = gadd_regex.group(1)
    opt_date = gadd_regex.group(2)
    opt_percent = gadd_regex.group(3)

    if opt_date:
        date = opt_date
    else:
        date = ''

    if opt_percent:
        percent = int(opt_percent)
    else:
        percent = 0

    goal_data.append([len(goal_data) + 1, goal, date, percent, ''])
    update_goal_order()
    view_goals()


def delete_item(task_num, cache_list):
    """Removes an item from the task or goal list."""
    if cache_list is deleted_tasks:
        data_list = task_data
        undo_com = "'undo' or 'u'"
    elif cache_list is deleted_goals:
        data_list = goal_data
        undo_com = "'undo-goal' or 'ug'"
    cache_list.append(data_list.pop(task_num))
    print("  Item deleted. Enter {} to restore.".format(undo_com))

    if data_list == task_data:
        update_order()
    elif data_list == goal_data:
        update_goal_order()
        view_goals()



def complete_task(task_num):
    """Marks a task as complete."""
    repeat = task_data[task_num][3]
    if repeat != '':
        # Append copy of data so non-repeat date can be restored using 'Uncheck'
        data_copy = task_data[task_num][:]
        completed_tasks.append(data_copy)

        if type(repeat) is list:
            comp_list_rep(task_num, repeat)
            return

        old_date = dt.strptime(task_data[task_num][2], '%Y-%m-%d')
        new_date = old_date + timedelta(int(task_data[task_num][3]))
        task_data[task_num][2] = dt.strftime(new_date, '%Y-%m-%d')

        # Need to remove [Done] from completed subtasks
        if task_data[task_num][4] != '':
            reset_subs(task_num)
    else:
        completed_tasks.append(task_data.pop(task_num))
    print("  Task marked as complete. Enter 'uncheck' or 'uc' to restore.")
    update_order()


def complete_today():
    """Mark all of today's tasks as complete."""
    to_complete_list = []
    for task in task_data:
        if task[2] == current_date:
            to_complete_list.append(task[0] - 1)

    offset = 0
    for task_num in to_complete_list:
        complete_task(task_num - offset)
        offset += 1


def comp_list_rep(task_num, repeat):
    """Calculates the next day due in the repeat list and changes the due date."""
    # Find the name of the day the current due date is set to
    current_due = dt.strptime(task_data[task_num][2], '%Y-%m-%d')
    current_day = dt.strftime(current_due, '%a').lower()
    # Find the next day listed
    try:
        day_position = repeat.index(current_day)
    except ValueError:
        print("  Is the due date one of the named repeat days? If not, please "
              "change it to one of the repeat days and try again.")
        return

    if day_position == len(repeat) - 1:
        target_day = repeat[0]
    else:
        target_day = repeat[day_position + 1]
    # Cycle through days until the day matches
    checked_day = current_due
    while True:
        day_test = checked_day + timedelta(1)
        day_name = dt.strftime(day_test, '%a').lower()
        if day_name == target_day:
            new_date = day_test
            break
        else:
            checked_day = day_test

    task_data[task_num][2] = dt.strftime(new_date, '%Y-%m-%d')

    if task_data[task_num][4] != '':
        reset_subs(task_num)

    print("  Task marked as complete. Enter 'uncheck' or 'uc' to restore.")
    update_order()


def complete_goal(task_num):
    """Moves a goal to the completed cache."""
    completed_goals.append(goal_data.pop(task_num))
    print("  Goal marked as complete. Enter 'uncheck-goal' or 'ucg' to restore.")
    update_goal_order()
    view_goals()


def reset_subs(task_num):
    """Resets subtasks to non-completed status"""
    for num, subtask in enumerate(task_data[task_num][4]):
            task_data[task_num][4][num] = subtask.rstrip('[Done]')


def edit_desc(command_extra):
    """Updates a task's description."""
    edit_regex = re.search(r'^(\w*)\s?(.*)?', command_extra)
    task_num = int(edit_regex.group(1)) - 1

    if edit_regex.group(2):
        task_data[task_num][1] = edit_regex.group(2)
    else:
        print("  Editing: '{}'".format(task_data[task_num][1]))
        print("  Enter the new task description below:")
        new_desc = input("  ")
        task_data[task_num][1] = new_desc


def undo_action(cache_list):
    """Restores the last deleted or completed task to the task list."""
    if cache_list is (completed_tasks or deleted_tasks):
        data_list = task_data
    elif cache_list is (completed_goals or deleted_goals):
        data_list = goal_data

    # Check for a repeat flag. If found delete matching task before restoring
    if cache_list == completed_tasks and completed_tasks[-1][3] != '':
        description = completed_tasks[-1][1]
        for task in task_data:
            if description == task[1]:
                del task_data[int(task[0]) - 1]
                break
    data_list.append(cache_list.pop(-1))
    if data_list is task_data:
        update_order()
    elif data_list is goal_data:
        update_goal_order()
        view_goals()

def change_date(command_extra):
    """Changes the due date of a task."""
    date_regex = re.search(r'^(\w*)\s?(.*)?', command_extra)
    task_num = int(date_regex.group(1)) - 1
    if date_regex.group(2):
        if date_regex.group(2) == 't':
            task_data[task_num][2] = current_date
        else:
            task_data[task_num][2] = date_regex.group(2)
    else:
        print("  Enter New Due Date For {}: (YYYY-MM-DD)".format(task_data[task_num][1]))
        new_date = input("  ")
        task_data[task_num][2] = new_date
    update_order()


def change_target(command_extra):
    """Changes the target date of a goal."""
    target_regex = re.search(r'^(\w*)\s?(.*)?', command_extra)
    goal_num = int(target_regex.group(1)) - 1
    if target_regex.group(2):
        new_target = target_regex.group(2)
    else:
        print("  Enter New Target For {}:".format(goal_data[goal_num][1]))
        new_target = input("  ")
    goal_data[goal_num][2] = new_target
    update_goal_order()
    view_goals()


def add_repeat(command_extra):
    """Flags a task with the repeat flag so it auto-renews on completion."""
    repeat_regex = re.search(r'^(\w*)\s?(.*)?', command_extra)
    command_step = repeat_regex.group(2)
    print(command_step)
    if command_step:
        if ',' in command_step:
            step = command_step.split(',')
        else:
            step = command_step
    else:
        print("  Enter your repeat length in number of days or "
              "a list of days seperated by a comma (mon,wed,sat): ")
        unsorted_step = input("  ").lower()
        if ',' in unsorted_step:
            step = unsorted_step.split(',')
        else:
            step = unsorted_step

    task_data[int(repeat_regex.group(1)) - 1][3] = step


def remove_repeat(task_num):
    """Removes the repeat flag from a task."""
    task_data[task_num][3] = ''


def update_order():
    """Updates the numbering of the tasks."""
    task_data.sort(key=lambda x: x[2])
    count = 1
    for task in task_data:
        task[0] = count
        count += 1

def update_goal_order():
    """Updates the Numbering of the Goals."""
    for num, goal in enumerate(goal_data, 1):
        goal[0] = num


def add_sub(command_extra):
    """Adds subtask to a task."""
    sub_regex = re.search(r'^(\w*)\s?(.*)?', command_extra)
    task_num = int(sub_regex.group(1)) - 1
    subtask = sub_regex.group(2)
    if not subtask:
        print("  Enter Subtask:")
        subtask = input("  ")
    if task_data[task_num][4] == '':
        task_data[task_num][4] = [subtask]
    else:
        task_data[task_num][4].append(subtask)


def complete_sub(command_extra):
    """Marks a subtask as complete."""
    subcom_regex = re.search(r'^(\w*)\s?(.*)?', command_extra)
    task_num = int(subcom_regex.group(1)) - 1
    if subcom_regex.group(2):
        sub_num = int(subcom_regex.group(2)) - 1
    else:
        sub_num = int(input("  Enter the number of the subtask")) - 1
    task_data[task_num][4][sub_num] = task_data[task_num][4][sub_num] + " [Done]"


def delete_sub(command_extra):
    """Removes a subtask."""
    delcom_regex = re.search(r'^(\w*)\s?(.*)?', command_extra)
    task_num = int(delcom_regex.group(1)) - 1
    if delcom_regex.group(2):
        sub_num = int(delcom_regex.group(2)) - 1
    else:
        sub_num = input("  Enter the number of the subtask")
    del task_data[task_num][4][sub_num]


def edit_sub(command_extra):
    """Updates a subtask's description."""
    edits_regex = re.search(r'^(\w*)\s(\w)\s?(.*)?', command_extra)
    task_num = int(edits_regex.group(1)) - 1
    sub_num = int(edits_regex.group(2)) - 1
    print("  Editing: '{}'".format(task_data[task_num][4][sub_num]))
    if edits_regex.group(3):
        task_data[task_num][4][sub_num] = edits_regex.group(3)
    else:
        print("  Enter the new subtask description below:")
        new_desc = input("  ")
        task_data[task_num][4][sub_num] = new_desc


def print_sub(task_num):
    """Prints a tasks subtasks."""
    for subtask in task_data[task_num][4]:
        if subtask[-6:] == '[Done]':
            undone = subtask.rstrip(' [Done]')
            subtask = strike_text(undone)
        print("        +) {}".format(subtask))
    print()


def strike_text(text):
    """Adds a strikethtough effect to text."""
    striked = ''
    for char in text:
        striked = striked + char + '\u0336'
    return striked

# MISC FUNCTIONS
def save_changes():
    """Writes changes to file."""
    with open ('data.pickle', 'wb') as fp:
        pickle.dump(task_data, fp)
        pickle.dump(goal_data, fp)


def smart_display():
    """Checks if Overdue/Tomorrow lists have tasks before printing with Today."""
    if not task_data:
        print()
        print(FONT_DICT['red no u'] + "  NO TASKS TO DISPLAY" + FONT_DICT['end'])
        return
    if task_data[0][2] < current_date:
        view_overdue()
    view_today()
    for task in task_data:
        if ((dt.strptime(task[2], '%Y-%m-%d')
            - dt.strptime(current_date, '%Y-%m-%d')).days) == 1:
            view_tomorrow()
            break


def show_help():
    """Prints Taskian usage instructions to the screen."""
    print()
    with open('help.txt') as f:
        for line in f.readlines():
            print(line, end='')


# A dictionary of ANSI escapse sequences for font effects.
FONT_DICT = {
   'blue':  '\033[4;94m',
   'green':  '\033[4;92m',
   'green no u':  '\033[1;92m',
   'orange': '\033[4;93m',
   'red':  '\033[4;91m',
   'red no u':  '\033[1;91m',
   'magenta':  '\033[4;95m',
   'end':  '\033[0m',
}


with open('data.pickle', 'rb') as fp:
    task_data = pickle.load(fp)
    goal_data = pickle.load(fp)

# Cache Lists
deleted_tasks = []
completed_tasks = []
deleted_goals = []
completed_goals = []

current_date = dt.now().strftime('%Y-%m-%d')

# Initial display
if goal_data:
    view_goals()
smart_display()
print('\n')

while True:
    action = input("  ENTER COMMAND ('q' to quit): ")
    if action.lower() == "q":
        break
    else:
        try:
            decide_action(action)
            print('\n')
        except IndexError:
            print()
            print("  No Item Found at that Position in the list or Cache - "
                  "Try Again or Enter 'h' or 'help' for Usage Instructions.")
        except ValueError:
            print()
            print("  Did You Forget A Number For The Item/Subitem in Your Command? - "
                  "Try Again or Enter 'h' or 'help' for Usage Instructions.")

        if action[:2] != 'ls' and action[:1] != 'h' and action[:4] != 'help':
            smart_display()
            save_changes()
