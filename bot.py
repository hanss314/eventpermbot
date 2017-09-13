import traceback
import datetime
import logging
import sys
import re
import os
import base64

from discord.ext import commands
from discord.ext.commands.errors import CommandError, CommandNotFound
import ruamel.yaml as yaml
import discord

class CodeNamesBot(commands.Bot):
    class ErrorAlreadyShown(Exception): pass

    def __init__(self, log_file=None, *args, **kwargs):
        self.config = {}
        self.board = None
        self.yaml = yaml.YAML(typ='safe')
        
        with open('config.yml') as data_file:
            self.config = self.yaml.load(data_file)
            
        with open('ids.yml') as data_file:
            self.ids = self.yaml.load(data_file)
            
        logging.basicConfig(level=logging.INFO, format='[%(name)s %(levelname)s] %(message)s')
        self.logger = logging.getLogger('bot')

        super().__init__(
            command_prefix=self.config['prefix'],
            *args,
            **kwargs
        )
        
    def save_data(self):
        with open('ids.yml', 'w') as data_file:
            self.yaml.dump(self.ids, data_file)

    async def send_message(self, to, msg):
        try:
            if len(msg) > 2000:
                await to.send('Whoops! Discord won\'t let me send messages over 2000 characters.\nThe message started with: ```\n{}```'.format(msg[:1000].replace('`', '`\u200b')))
            else:
                await to.send(msg)
            pass
        except discord.errors.Forbidden:
            pass

    async def on_message(self, message):
        await self.process_commands(message)

    async def on_command_error(self, ctx: commands.Context, exception: Exception):
        if isinstance(exception, commands.CommandInvokeError):
            # all exceptions are wrapped in CommandInvokeError if they are not a subclass of CommandError
            # you can access the original exception with .original
            if isinstance(exception.original, discord.Forbidden):
                # permissions error
                try:
                    await ctx.send('Permissions error: `{}`'.format(exception))
                except discord.Forbidden:
                    # we can't send messages in that channel
                    return

            # Print to log then notify developers
            lines = traceback.format_exception(type(exception),
                                               exception,
                                               exception.__traceback__)

            self.logger.error(''.join(lines))

            return
        
        if isinstance(exception, commands.CheckFailure):
            await ctx.send('You can\'t do that.')
        elif isinstance(exception, commands.CommandNotFound):
            pass
        elif isinstance(exception, commands.UserInputError):
            error = ' '.join(exception.args)
            error_data = re.findall('Converting to \"(.*)\" failed for parameter \"(.*)\"\.', error)
            if not error_data:
                await ctx.send('Error: {}'.format(' '.join(exception.args)))
            else:
                await ctx.send('Got to say, I *was* expecting `{1}` to be an `{0}`..'.format(*error_data[0]))
        else:
            info = traceback.format_exception(type(exception), exception, exception.__traceback__, chain=False)
            self.logger.error('Unhandled command exception - {}'.format(''.join(info)))

    async def on_error(self, event_method, *args, **kwargs):
        info = sys.exc_info()
        if isinstance(info[1], self.ErrorAlreadyShown):
            return
        self.logger.error('Unhandled command exception - {}'.format(''.join(info)))

    async def on_ready(self):
        self.logger.info('Connected to Discord')
        self.logger.info('Guilds  : {}'.format(len(self.guilds)))
        self.logger.info('Users   : {}'.format(len(set(self.get_all_members()))))
        self.logger.info('Channels: {}'.format(len(list(self.get_all_channels()))))

    async def close(self):
        await super().close()

    def run(self):
        debug = any('debug' in arg.lower() for arg in sys.argv) or self.config.get('debug_mode', False)

        async def has_perms(ctx: commands.Context) -> bool:
            return bool(set([r.id for r in ctx.author.roles]) & set(ctx.bot.config['event_team']))
        
        self.add_check(has_perms)
        #self.remove_command("help")
        token = self.config['token']
        cogs = self.config.get('cogs', [])
        for cog in cogs:
            try:
                self.load_extension(cog)
            except Exception as e:
                self.logger.exception('Failed to load cog {}.'.format(cog))
            else:
                self.logger.info('Loaded cog {}.'.format(cog))

        self.logger.info('Loaded {} cogs'.format(len(self.cogs)))
        super().run(token)

if __name__ == '__main__':
    bot = CodeNamesBot()
    bot.run()
