import discord
from discord.ext import commands


class Misc():
    @commands.command()
    async def help(self, ctx, *args):
        '''This help message :D'''
        commands = {i for i in ctx.bot.all_commands.values()}

        if len(args) == 0:
            d = '**Bot help:**'

            for cmd in commands:
                d += '\n`{}{}`'.format(ctx.prefix, cmd.name)

                brief = cmd.brief
                if brief is None and cmd.help is not None:
                    brief = cmd.help.split('\n')[0]

                if brief is not None:
                    d += ' - {}'.format(brief)
        elif len(args) == 1:
            if args[0] not in ctx.bot.all_commands:
                d = 'Command not found.'
            else:
                cmd = ctx.bot.all_commands[args[0]]
                d = 'Help for command `{}`:\n'.format(cmd.name)
                d += '\n**Usage:**\n'

                params = list(cmd.clean_params.items())
                p_str = ''
                for p in params:
                    if p[1].default == p[1].empty:
                        p_str += ' [{}]'.format(p[0])
                    else:
                        p_str += ' <{}>'.format(p[0])

                d += '`{}{}{}`\n'.format(ctx.prefix, cmd.name, p_str)
                d += '\n**Description:**\n'
                d += '{}\n'.format('None' if cmd.help is None else cmd.help.strip())

                if cmd.checks:
                    d += '\n**Checks:**'
                    for check in cmd.checks:
                        d += '\n{}'.format(check.__qualname__.split('.')[0])
                    d += '\n'

                if cmd.aliases:
                    d += '\n**Aliases:**'
                    for alias in cmd.aliases:
                        d += '\n`{}{}`'.format(ctx.prefix, alias)

                    d += '\n'
        else:
            d = '**TWOWBot help:**'

            for i in args:
                if i in ctx.bot.all_commands:
                    cmd = ctx.bot.all_commands[i]
                    d += '\n`{}{}`'.format(ctx.prefix, i)

                    brief = cmd.brief
                    if brief is None and cmd.help is not None:
                        brief = cmd.help.split('\n')[0]

                    if brief is None:
                        brief = 'No description'

                    d += ' - {}'.format(brief)
                else:
                    d += '\n`{}{}` - Command not found'.format(ctx.prefix, i.replace('@', '@\u200b').replace('`', '`\u200b'))

        d += '\n*Made by hanss314#0128*'
        await ctx.bot.send_message(ctx.channel, d)
        
        
def setup(bot):
    bot.add_cog(Misc())
