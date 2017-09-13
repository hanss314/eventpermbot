from discord.ext import commands
import discord
from discord.http import Route

class Channels():
    @commands.command(aliases=['newchannel'])
    async def new_channel(self, ctx, *, name):
        '''Creates a channel'''
        name = name.replace(' ','-')
        event_team = [r for r in ctx.guild.roles if r.id in ctx.bot.config['event_team']]
        overwrites = {
            r: discord.PermissionOverwrite(
                manage_channels=True,
                manage_roles=True,
                manage_messages=True,
                manage_webhooks=True
                ) for r in event_team
            }
        try: channel = await ctx.guild.create_text_channel(name, overwrites=overwrites)
        except discord.Forbidden: return await ctx.send('Creation failed.')
        ctx.bot.ids['channels'].append(channel.id)
        await ctx.send('Channel created!')
        ctx.bot.save_data()
        if 'channel_cat' in ctx.bot.config:
            cat = ctx.guild.get_channel(ctx.bot.config['channel_cat'])
            channel.edit(category=cat)

    @commands.command(aliases=['deletechannel'])
    async def delete_channel(self, ctx, channel: commands.TextChannelConverter):
        '''Deletes a channel'''
        if channel.id not in ctx.bot.ids['channels']: return await ctx.send('You can\'t do that.')
        try: await channel.delete()
        except discord.Forbidden: return await ctx.send('Deleting failed.')
        await ctx.send('Channel deleted!')
        ctx.bot.ids['channels'].remove(channel.id)
        ctx.bot.save_data()
        
def setup(bot):
    bot.add_cog(Channels())
