from discord.ext import commands
import discord

class Roles():
    @commands.command(aliases=['newrole'])
    async def new_role(self, ctx, name, colour: commands.ColourConverter):
        '''Creates a role'''
        try: role = await ctx.guild.create_role(name=name, colour=colour)
        except discord.Forbidden: return await ctx.send('Creation failed.')
        ctx.bot.ids['roles'].append(role.id)
        await ctx.send('Role created!')
        ctx.bot.save_data()
        
    @commands.command(aliases=['deleterole'])
    async def delete_role(self, ctx, role: commands.RoleConverter):
        '''Deletes a role'''
        if role.id not in ctx.bot.ids['roles']: return await ctx.send('You can\'t do that.')
        try: await role.delete()
        except discord.Forbidden: return await ctx.send('Deleting failed.')
        await ctx.send('Role deleted!')
        ctx.bot.ids['roles'].remove(role.id)
        ctx.bot.save_data()
        
    @commands.command(aliases=['giverole'])
    async def give_role(self, ctx, role: commands.RoleConverter, *members: commands.MemberConverter):
        '''Give role to members'''
        if role.id not in ctx.bot.ids['roles']: return await ctx.send('You can\'t do that.')
        success = []
        for member in members:
            try: await member.add_roles(role)
            except discord.Forbidden: pass
            else: success.append(member.name)
        if success: await ctx.send('Gave {} to {}.'.format(role, ', '.join(success)))
        else: await ctx.send('Adding roles failed.')
        
    @commands.command(aliases=['remrole'])
    async def rem_role(self, ctx, role: commands.RoleConverter, *members: commands.MemberConverter):
        '''Remove role from members'''
        if role.id not in ctx.bot.ids['roles']: return await ctx.send('You can\'t do that.')
        success = []
        for member in members:
            try: await member.remove_roles(role)
            except discord.Forbidden: pass
            else: success.append(member.name)
        
        if success: await ctx.send('Removed {} from {}.'.format(role, ', '.join(success)))
        else: await ctx.send('Removing roles failed.')
        
    @commands.command(aliases=['mention', 'ping'])
    async def announce(self, ctx, role: commands.RoleConverter, *, message = ''):
        '''Ping a role'''
        if role.id not in ctx.bot.ids['roles']: return await ctx.send('You can\'t do that.')
        await role.edit(mentionable=True)
        await ctx.send('{} {}'.format(role.mention, message))
        await role.edit(mentionable=False)
        try: await ctx.message.delete()
        except: pass
        
    @commands.command(aliases=['listroles'])
    async def list_roles(self, ctx):
        '''Remove role from members'''
        e = discord.Embed()
        e.title = 'Event team roles'
        m = ''
        roles = [(r.mention, r.id) for r in ctx.guild.roles if r.id in ctx.bot.ids['roles']]
        for r in roles: m += '{}: {}\n'.format(*r)
        e.description = m
        await ctx.send(embed=e)
        
def setup(bot):
    bot.add_cog(Roles())
