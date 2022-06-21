from replit import db

# db has a key for each user, containing a dictionary of user:amount
# recording total amount owed to each user.
# eg. db[user1][user2] returns the amount that user1 owes user2

def pay(user_paying, user_receiving, amt):
    ''' Marks that the user `user_paying` has paid an
    amount `amt` to `user_receiving`. '''
    user_paying = str(user_paying)
    user_receiving = str(user_receiving)

    # First check if there is a valid tab, if not then quit.
    if user_paying not in db.keys():
        return False
    if user_receiving not in db[user_paying].keys():
        return False

    db[user_paying][user_receiving] -= amt

    # if paid in full, remove from tab list
    if db[user_paying][user_receiving] <= 0:
        db[user_paying].pop(user_receiving)

    return True

def add_tab(user_owed, user_to_pay, amt):
    ''' Records that `user_to_pay` now owes `user_owed` the amount `amt`. '''
    user_to_pay = str(user_to_pay)
    user_owed = str(user_owed)

    if user_to_pay == user_owed:
        return False

    if user_to_pay not in db.keys():
        db[user_to_pay] = {}

    if user_owed not in db[user_to_pay].keys():
        db[user_to_pay][user_owed] = amt
    else:
        db[user_to_pay][user_owed] += amt
    cross_check(user_owed, user_to_pay)
    return True

def query(user):
    ''' Determines how much this user owes others. '''
    user = str(user)
    if user not in db.keys():
        return {}
    return db[user]

def cross_check(user1, user2):
    ''' Checks between the two users to see if any owed balances
    cancel out, and removes that balance. '''
    user1 = str(user1)
    user2 = str(user2)

    if user1 not in db.keys() or user2 not in db.keys():
        return
    user1_tab = query(user1)
    user2_tab = query(user2)

    if user1 not in user2_tab.keys() or user2 not in user1_tab.keys():
        return
    balance1 = user1_tab[user2] # amount user1 owes user2
    balance2 = user2_tab[user1] # amount user2 owes user1

    if abs(balance1-balance2) < 0.01 or user1 == user2:
        db[user1].pop(user2)
        db[user2].pop(user1)

    elif balance1 > balance2:
        # Subtract balance2 from balance1, set as user1's tab
        # set user2's tab to 0
        db[user1][user2] = balance1 - balance2
        db[user2].pop(user1)

    elif balance1 < balance2:
        # Subtract balance1 from balance2, set as user2's tab
        # set user1's tab to 0
        db[user2][user1] = balance2 - balance1
        db[user1].pop(user2)
    return

def clear_database():
    ''' Resets the database entirely. '''
    db.clear()
    return

def find_who_owes_me(user):
    ''' Given a user, find who owes this person and how much.
    Returns list of tuple [(user1, amount), ...] '''
    user = str(user)
    results = []
    for other in db.keys():
        if user in db[other].keys():
            results.append((other, db[other][user]))
    return results
