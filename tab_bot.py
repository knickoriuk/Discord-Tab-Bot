import discord
from discord.ext import commands
import os
import re  # RegEx
import traceback  # For Tracing Exceptions
import tab_management as tm

# Setup for Bot object
intents = discord.Intents.default()
intents.members = True
help_command = commands.DefaultHelpCommand(no_category = 'Commands')
bot = commands.Bot(command_prefix="$", intents=intents, help_command=help_command)
cmd_errors = commands.BadArgument, commands.UserInputError, commands.ArgumentParsingError, commands.ConversionError

def create_error_embed(error_message):
    ''' Generates an embedded message to display an error. '''
    return discord.Embed(title = "Error:",
                          description = error_message,
                          color = 0xe00000)

def create_message_embed(title, message):
    ''' Generates an embedded message to display with a title and description. '''
    return discord.Embed(title = title,
                          description = message,
                          color = 0x32e318)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game("$help"))
    print(f'We have logged in as {bot.user}')
    
#~~~~~~~~~~~~ $owes_me ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bot.command(
    name="owes_me",
    aliases=["owesme"],
    brief="Records that a user owes you an amount",
    help="Records that the specified user owes you an amount. You can list as many users as you would like; they will all owe you that amount. Make sure you tag the user so the command works properly.")
async def owes_me(ctx, 
                  amount, 
                  user: commands.Greedy[discord.Member]):
    try:
        # Parse Parameters
        amount_str = re.search('[\d]+([.][\d]{1,2})?', amount)[0]
        amount = round(float(amount_str), 2)
        user_to_receive = ctx.author
        
        if user == []: # If no users listed (or no amount and 1 user listed)
            embed = create_error_embed(f"Missing parameters. \nUsage: `${ctx.command.name} {ctx.command.signature}`  or try  `$help {ctx.command.name}`")
            await ctx.channel.send(embed=embed)
            return

        print_message = ""
        for user_to_pay in set(user):
            
            # Dont let bots have tabs
            if user_to_pay.bot:
                embed = create_error_embed(f"Failed to add tab for {user_to_pay.display_name}. You can't be owed by a bot.")
                await ctx.channel.send(embed=embed)

            else: # Add tab to database
                success = tm.add_tab(user_to_receive.id, user_to_pay.id, amount)
    
                # Print Parsed Instructions
                if not success:
                    embed = create_error_embed(f"Failed to add tab for {user_to_pay.display_name}.")
                    await ctx.channel.send(embed=embed)
                else:
                    print_message += "{0} must pay ${1:.2f} to {2}.\n".format(
                            user_to_pay.display_name, amount,
                            user_to_receive.display_name)
        
        # After looping thru all given users
        if print_message != "":
            embed = create_message_embed("Success!", print_message)
            await ctx.channel.send(embed = embed)
                    
    except Exception:
        traceback.print_exc()
        embed = create_error_embed("Something went wrong.  :(")
        await ctx.channel.send(embed=embed)

#~~~~~~~~~~~~ $owes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bot.command(
    name="owes",
    brief="Records that a user owes someone an amount",
    help="Records that `user` owes an amount to `recipient`. You can list as many users as you would like; they will all owe the recipient that amount. Make sure you tag the users so the command works properly.")
async def owes(ctx, 
               recipient: discord.Member, 
               amount, 
               user: commands.Greedy[discord.Member]):
    try:
        # Parse Parameters
        amount_str = re.search('[\d]+([.][\d]{1,2})?', amount)[0]
        amount = round(float(amount_str), 2)
        user_to_receive = recipient

        if user_to_receive.bot:
            embed = create_error_embed("Failed to add tab. You can't owe a bot.")
            await ctx.channel.send(embed=embed)
            return

        if user == []: # If no users listed (or amount was omitted)
            embed = create_error_embed(f"Missing parameters. \nUsage: `${ctx.command.name} {ctx.command.signature}`  or try  `$help {ctx.command.name}`")
            await ctx.channel.send(embed=embed)
            return

        print_message = ""
        for user_to_pay in set(user):

            # Dont let bots have tabs
            if user_to_pay.bot:
                embed = create_error_embed(f"Failed to add tab for {user_to_pay.display_name}. You can't be owed by a bot.")
                await ctx.channel.send(embed=embed)
                
            else: # Add tab to database
                success = tm.add_tab(user_to_receive.id, user_to_pay.id, amount)
    
                # Print Parsed Instructions
                if not success:
                    embed = create_error_embed(f"Failed to add tab for {user_to_pay.display_name}.")
                    await ctx.channel.send(embed=embed)
                else:
                    print_message += "{0} must pay ${1:.2f} to {2}.\n".format(
                            user_to_pay.display_name, amount,
                            user_to_receive.display_name)
        
        # After looping thru all given users
        if print_message != "":
            embed = create_message_embed("Success!", print_message)
            await ctx.channel.send(embed = embed)
            return
                   
    except Exception:
        traceback.print_exc()
        embed = create_error_embed("Something went wrong.  :(")
        await ctx.channel.send(embed = embed)

#~~~~~~~~~~~~ $paid ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bot.command(
    name = "paid",
    brief = "Marks that someone has paid their tab",
    help = "Marks that `sender` has paid the specified amount to `recipient`. If `sender` is left unspecified, it assumes the person calling the command is the one paying. Make sure you tag the users so the command works properly.")
async def paid(ctx, 
               recipient: discord.Member, 
               amount, 
               sender: discord.Member = None):
    try:
        #TODO: pay off full tab if amount left unspecified
        
        # Parse Parameters
        user_paid = recipient
        amount_str = re.search('[\d]+([.][\d]{1,2})?', amount)[0]
        amount = round(float(amount_str), 2)

        if sender == None:  # If a user_to_receive isn't specified
            user_paying = ctx.author
        else:
            user_paying = sender

        # Add transaction to database
        success = tm.pay(user_paying.id, user_paid.id, amount)

        # Print Parsed Instructions
        if not success:
            embed = create_error_embed("Failed to record payment. Did you have a tab to begin with?")
            await ctx.send(embed = embed)
            return
        else:
            embed = create_message_embed("Success!", "{0} paid ${1:.2f} to {2}.".format(user_paying.display_name, amount, user_paid.display_name))
            await ctx.channel.send(embed = embed)

    except Exception:
        traceback.print_exc()
        embed = create_error_embed("Something went wrong.  :(")
        await ctx.channel.send(embed = embed)

#~~~~~~~~~~~~ $divide ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bot.command(
    name="divide",
    brief="Divides a bill evenly among listed users",
    help='''For an equally divded bill, this divides the total amount between the listed users, with the amount owing to `recipient`.\n\nThis assumes that the recipient's portion of the bill was not removed from the total amount.\n\nEg. "$divide @friend1 30 @friend2 @friend3" would result in both friend2 and friend3 owing $10 to friend1.''')
async def divide(ctx, 
                 recipient: discord.Member,
                 amount, 
                 users: commands.Greedy[discord.Member]):
    try:  
        # Parse Parameters            
        if recipient.bot:
            embed = create_error_embed("Failed to add tab. Cannot owe a bot.")
            await ctx.channel.send(embed = embed)
            return
        
        user_to_receive = recipient   
        amount_str = re.search('[\d]+([.][\d]{1,2})?', amount)[0]
        
        print_string = ""
        # Iterate over all users specified and ensure each one is valid
        for user_to_pay in set(users):  

            # Dont let self-tabs or bot-tabs exist
            if user_to_pay == user_to_receive:
                embed = create_error_embed(f"Failed to add tab. Cannot owe yourself.\nUse `$help {ctx.command.name}` for more information.")
                await ctx.channel.send(embed = embed)
                return
            elif user_to_pay.bot:
                embed = create_error_embed("Failed to add tab. Cannot be owed by a bot.")
                await ctx.channel.send(embed = embed)
                return

        # Calculate amount for each user to pay
        amount = round(float(amount_str) / (len(set(users)) + 1), 2)

        # Add tabs to database
        for user_to_pay in set(users):
            success = tm.add_tab(user_to_receive.id, user_to_pay.id, amount)
            if not success:
                embed = create_error_embed(f"Failed to add tab for {user_to_pay.display_name}.")
                await ctx.channel.send(embed = embed)
            else:
                print_string += user_to_pay.display_name + ", "
        
        # Print Parsed Instructions
        if print_string != "":
            print_string = print_string[:-2] + " each owe ${0:.2f} to {1}".format(
                amount, user_to_receive.display_name)
            embed = create_message_embed("Success!", print_string)
            await ctx.channel.send(embed = embed)
        else:
            embed = create_error_embed(f"No users specified. \nUsage: `${ctx.command.name} {ctx.command.signature}`  or try  `$help {ctx.command.name}`")
            await ctx.channel.send(embed = embed)
        
    except Exception:
        traceback.print_exc()
        embed = create_error_embed("Something went wrong.  :(")
        await ctx.channel.send(embed = embed)

#~~~~~~~~~~~~ $inquire ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bot.command(
    name="inquire",
    brief="Determines how much you owe everyone else",
    help="Determines how much the user owes everyone else. If no user is specified, the inquiry is regarding the user who calls the command. Make sure you tag the users so the command works properly.")
async def inquire(ctx, user: discord.Member = None):
    try:
        # Get User
        if user == None:
            subject = ctx.author
        else:
            subject = user

        # Don't bother searching for a bot
        if subject.bot:
            await ctx.channel.send(
                f"{subject.display_name} is not subject to the rules of economy!")
            return
            
        # Run Query
        results = tm.query(subject.id, mode="inquire")
                           
        # Get Current Guild (Server)
        guild = ctx.guild

        # Print Results
        print_string = ""
        for user_id in results.keys():

            if guild == None: # We're in DMs, show ALL tabs
                user = bot.get_user(user_id)
            else: # We're in a server, show only relevant tabs
                user = guild.get_member(int(user_id))
                
            if user != None:
                print_string += "- {0}: ${1:.2f}\n".format(
                    user.display_name, results[user_id])

        if print_string == "":
            await ctx.channel.send(f"**{subject.display_name} owes *nothing!***\n")
        else:
            embed = create_message_embed(f"{subject.display_name} owes:\n", print_string)
            await ctx.channel.send(embed = embed)

    except Exception:
        traceback.print_exc()
        embed = create_error_embed("Something went wrong.  :(")
        await ctx.channel.send(embed = embed)

#~~~~~~~~~~~~ $who_owes_me ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bot.command(
    name="who_owes_me",
    aliases=["whoowesme"],
    brief="Determines how much everyone else owes you",
    help="Determines how much everyone else owes the user.")
async def who_owes_me(ctx):
    try:        
        # Get User
        subject = ctx.author

        # Run Query
        results = tm.query(subject.id, mode="who_owes_me")

        # Get Current Guild (Server)
        guild = ctx.guild

        # Print Results
        print_string = ""
        for user_info in results:
            
            if guild == None: # We're in DMs, show ALL tabs
                user = bot.get_user(user_info[0])
            else: # We're in a server, show only relevant tabs
                user = guild.get_member(int(user_info[0]))

            if user != None:
                print_string += "- {0}: ${1:.2f}\n".format(
                    user.display_name, user_info[1])
                
        if print_string == "":
            await ctx.channel.send(f"***Nobody* owes {subject.display_name}!**\n")
        else:
            embed = create_message_embed(f"{subject.display_name} is owed by:\n", print_string)
            await ctx.channel.send(embed = embed)

    except Exception:
        traceback.print_exc()
        embed = create_error_embed("Something went wrong.  :(")
        await ctx.channel.send(embed = embed)
    return

#~~~~~~~~~~~~ $clear_db ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bot.command(hidden=True)
async def clear_db(ctx):
    if str(ctx.author.id) == os.environ['KATE_ID']:
        tm._clear_database()
        await ctx.channel.send("The database was reset.")
    else:
        await ctx.channel.send("I don't take orders from you.")

#~~~~~~~~~~~~ $get_db ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bot.command(hidden=True)
async def get_db(ctx):
    ''' Sends a list of all amounts owed by all users. For testing purposes only.
    Also prints the current database structure to the console. '''
    if str(ctx.author.id) == os.environ['KATE_ID']:
        embed_string = "" # Holds a readable form of the database's contents
        print_string = "\nCurrent Database {\n" # Holds the database's structure
        db = tm._get_entire_database()
        
        for user1 in db.keys():
            username1 = bot.get_user(int(user1)).name
            print_string += username1 + ": {"
            
            for user2 in db[user1].keys():
                username2 = bot.get_user(int(user2)).name
                print_string += username2 + ": " + str(db[user1][user2]) +", "
                
                if db[user1][user2] > 0:
                    embed_string += f"{username1} owes {username2} ${db[user1][user2]}.\n"
                    
            print_string += "},\n"
        print_string += "}\n"
        
        embed = create_message_embed("The database contains:", embed_string)
        await ctx.channel.send(embed = embed)
        print(print_string)
    else:
        await ctx.channel.send("I don't take orders from you.")

#~~~~~~~~~~~~ Error Handling ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@bot.event
async def on_command_error(ctx, error):
    
    if isinstance(error, commands.TooManyArguments):
        embed = create_error_embed(f"Too many arguments were passed to the command. \nUsage: `${ctx.command.name} {ctx.command.signature}`  or try  `$help {ctx.command.name}`")
        
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = create_error_embed(f"Missing parameters. \nUsage: `${ctx.command.name} {ctx.command.signature}`  or try  `$help {ctx.command.name}`")

    elif isinstance(error, cmd_errors):
        embed = create_error_embed(f"Failed to parse command. \nUsage: `${ctx.command.name} {ctx.command.signature}`  or try  `$help {ctx.command.name}`")
        
    else:
        raise error
        return
        
    await ctx.channel.send(embed=embed)
    return
      
# Turn on the bot!
bot.run(os.environ['TOKEN'])
