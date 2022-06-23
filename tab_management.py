from replit import db

# db has a key for each user, containing a dictionary of user:amount recording total amount owed to each user. 
# eg. frank owes bob $30, susie owes bob $19, frank owes susie $44
# db = {"frank": {"bob":30, "susie":44}, 
#       "bob":   {"frank":-30, "susie":-19}, 
#       "susie": {"bob":19, "frank":-44}}

def pay(user_paying, user_receiving, amount_paid):
    ''' (string, string, float) -> Bool
    Marks that the user `user_paying` has paid an amount `amount_paid` to
    `user_receiving`. Returns True if successful, False otherwise.
    '''
    user_paying = str(user_paying)
    user_receiving = str(user_receiving)

    # First check if there is a valid tab, if not then quit.
    if user_paying not in db.keys():
        return False
    if user_receiving not in db[user_paying].keys():
        return False

    amount_owed = db[user_paying][user_receiving] - amount_paid

    # if paid in full, remove from tab list
    if amount_owed < 0.01: # Prevent floating point errors from lingering
        db[user_paying].pop(user_receiving)
        db[user_receiving].pop(user_paying)

        # Also: remove user from database if there are no entries in db[user]
        if not db[user_paying]:
            db.pop(user_paying)
        if not db[user_receiving]:
            db.pop(user_receiving)
        
    # Otherwise update it to reflect new amount
    else:
        db[user_paying][user_receiving] = amount_owed
        db[user_receiving][user_paying] = -amount_owed
    return True

def add_tab(user_owed, user_to_pay, amount_owed):
    ''' (string, string, float) -> Bool
    Records that `user_to_pay` now owes `user_owed` the amount `amount_owed`. 
    Returns True if successful, False otherwise.
    '''
    user_to_pay = str(user_to_pay)
    user_owed = str(user_owed)

    if user_to_pay == user_owed:
        return False

    # Initialize people in database if not yet there
    if user_to_pay not in db.keys():
        db[user_to_pay] = {}
    if user_owed not in db.keys():
        db[user_owed] = {}

    # Add positive balance to `user_owed`
    if user_owed not in db[user_to_pay].keys():
        db[user_to_pay][user_owed] = amount_owed
    else:
        db[user_to_pay][user_owed] += amount_owed
        
    # Add negative balance to `user_to_pay`
    if user_to_pay not in db[user_owed].keys():
        db[user_owed][user_to_pay] = -amount_owed
    else:
        db[user_owed][user_to_pay] -= amount_owed
    
    return True

def query(user, mode=None):
    ''' (string, string) -> dictionary of {str: float}
    Determines how much this user owes others and is owed by others.
        - a negative balance implies the user IS OWED that amount,
        - a positive balance implies the user OWES that amount 
        
    Specify mode="inquire" to find only positive balances
    or mode="who_owes_me" to find only negative balances (which will
    be made positive). The default mode is None.
    '''
    user = str(user)
    if user not in db.keys():   
        return {}
    if mode != "inquire" and mode != "who_owes_me":
        return db[user]
    else:
        new_db = {}
        for other_user in db[user].keys():
            
            amount = db[user][other_user]
            if amount > 0 and mode == "inquire" : new_db[other_user] = amount 
            if amount < 0 and mode == "who_owes_me" : new_db[other_user] = -amount 
          
        return new_db

def _clear_database():
	''' Resets the database entirely. '''
	db.clear()
	return

def _get_entire_database():
    '''For debug purposes. '''
    return db

def _convert_db():
    '''A function to be ran once, converting the old format of db to
    the new format. '''
    for user1 in db.keys():
        for user2 in db[user1].keys():
            if user2 not in db.keys():
                db[user2] = {}
            db[user2][user1] = -db[user1][user2]
    return

def _clean_db():
    '''A function to be ran once, cleaning empty database entries. '''
    for user in db.keys():
        if not db[user]:
            db.pop(user)
    return
