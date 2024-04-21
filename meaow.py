import nextcord
import asyncio
from nextcord.ext import commands
import os
import json 
from datetime import datetime
import requests as rq
from requests import post, Session , get
import requests 


with open('config.json', 'r', encoding='utf-8') as f:
    config_data = json.load(f)
bot = commands.Bot(command_prefix='mst!',help_command=None,intents=nextcord.Intents.all())
config = json.load(open('./config.json', 'r', encoding='utf-8'))



#
async def check_saved_data(user_id):
    user_data = []
    with open("./Databaseserver/info.json", "r") as file:
        for line in file:
            data_dict = json.loads(line.strip())
            if data_dict["user_id"] == user_id:
                user_data.append(data_dict)
    return user_data



class modalsell(nextcord.ui.Modal):
    def __init__(self, team_name):
        super().__init__(title="กรอกข้อมูล")
        self.team_name = team_name
        self.name = nextcord.ui.TextInput(label="ชื่อนักเตะ", custom_id="01", placeholder="ใส่ชื่อนักเตะตรงนี้ =", required=True)
        self.add_item(self.name)
        self.price = nextcord.ui.TextInput(label="ราคา", custom_id="02", placeholder="ใส่ราคาตรงนี้ =", required=True)
        self.add_item(self.price)
        self.note = nextcord.ui.TextInput(label="ข้อความ", placeholder="ใส่ Note ตรงนี้", custom_id="03", style=nextcord.TextInputStyle.paragraph, required=True, max_length=700)
        self.add_item(self.note)
    
    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            embed=nextcord.Embed(title=f"> ``✅`` | คุณส่งข้อมูลสำเร็จ", description="", color=0xD1EAF5, timestamp=datetime.now()),
            ephemeral=True
        )
        await bot.get_channel(int(config['sendinfo'])).send(f"{interaction.user.mention}")
        message = (
            f"``⚽``  ``|``  ทีมปัจจุบัน : ```{self.team_name}```\n"
            f"``📝``  ``|``  ชื่อนักเตะ : ```{self.name.value}```\n"
            f"``💰``  ``|``  ราคา : ```{self.price.value} ฿```\n"
            f"``📝``  ``|``  ข้อความ : ```{self.note.value}```"
        )
        embed = nextcord.Embed(description=message, color=0xFFB6C1, timestamp=datetime.now())
        await bot.get_channel(int(config['sendinfo'])).send(embed=embed)
        

        data = json.dumps({
            "team": self.team_name,
            "user_id": interaction.user.id,
            "name_play": self.name.value,
            "price": self.price.value,
            "note": self.note.value,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        with open("./Databaseserver/info.json", "a") as file:
            file.write(data + "\n")

class dropteam(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label='Buriram United', description="", emoji="<a:onlineping:1153299022061256796>"),
            nextcord.SelectOption(label='BG Pathum', description="", emoji="<a:onlineping:1153299022061256796> "),
            nextcord.SelectOption(label='True Bangkok United', description="", emoji="<a:onlineping:1153299022061256796>"),
            nextcord.SelectOption(label='Muangthong United', description="", emoji="<a:onlineping:1153299022061256796>"),
            nextcord.SelectOption(label='Sukothai FC', description="", emoji="<a:onlineping:1153299022061256796>"),
            nextcord.SelectOption(label='Chiangrai United', description="", emoji="<a:onlineping:1153299022061256796>"),
            nextcord.SelectOption(label='Port FC', description="", emoji="<a:onlineping:1153299022061256796>"),
            nextcord.SelectOption(label='Chonburi FC', description="", emoji="<a:onlineping:1153299022061256796>"),
        ]        
        super().__init__(
            custom_id='select-team',
            placeholder='เลือก ทีม ปัจจุบันของนักเตะ',
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )
    
    async def callback(self, interaction: nextcord.Interaction):
        selected_team = self.values[0]
        if selected_team in ['Buriram United', 'BG Pathum', 'True Bangkok United', 'Muangthong United', 'Sukothai FC', 'Chiangrai United', 'Port FC', 'Chonburi FC']: 
            await interaction.response.send_modal(modalsell(selected_team))


class Dropdownteam(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(dropteam())


class selectteam(nextcord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        

    @nextcord.ui.button(label='เลือกทีมที่จะขาย', style=nextcord.ButtonStyle.green, emoji="⚽", custom_id='teams', row=1)
    async def teams(self, button: nextcord.Button, interaction: nextcord.Interaction):
            await interaction.response.send_message(view=Dropdownteam(), ephemeral=True)
            


    @nextcord.ui.button(label='ตรวจสอบข้อมูลที่บันทึก', style=nextcord.ButtonStyle.blurple, emoji="📋", custom_id='check_data', row=1)
    async def check_data(self, button: nextcord.Button, interaction: nextcord.Interaction):
        user_data = await check_saved_data(interaction.user.id)
        if user_data:
            embed = nextcord.Embed(title="# ข้อมูลที่บันทึกของคุณ")
            embed.color = nextcord.Color.blue()
            for index, data in enumerate(user_data, start=1):
                embed.add_field(name=f"\n---ข้อมูลที่ {index}---", value="\n", inline=False)
                embed.add_field(name="ทีม :", value=f"```{data['team']}```", inline=True)
                embed.add_field(name="ราคา :", value=f"```{data['price']} บาท```", inline=True)
                embed.add_field(name="ชื่อนักเตะ :", value=f"```{data['name_play']}```", inline=True)
                embed.add_field(name="ข้อความ :", value=f"```{data['note']}```", inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(content="> ``❌``  ``|``  ``คุณยังไม่เคยบันทึกข้อมูล``", ephemeral=True)



@bot.event
async def on_ready():
    os.system('cls')
    bot.add_view(selectteam())
    competition_activity = nextcord.Activity(
        type=nextcord.ActivityType.competing,
        name=config['STATUS_NAME']
    )
    await bot.change_presence(status=nextcord.Status.online, activity=competition_activity)
    print(f'[ ✅ ] {bot.user.name} LOGIN SUCCESS!')



@bot.slash_command(
        name='setupsystem',
        description='📍︱ตั้งระบบเซ็ทอัพระบบ︱คำสั่งนี้สำหรับผู้ดูเเลระบบเท่านั้น',
        guild_ids=[config['serverids']]
)
async def setup(interaction: nextcord.Interaction):
    if interaction.user.id not in [config['ownerIds']]:
        return await interaction.response.send_message(content='[ ERROR ] เกิดข้อผิดพลาดในการใช้งานคำสั่งนี้ เพราะคุณไม่ใช่ผู้พัฒนาบอท', ephemeral=True)
    embed = nextcord.Embed()
    embed.set_author(name=f"{config['name_author']}", icon_url=bot.user.avatar.url)
    embed.description = f'''
>  # {config['Text_descriptions']}
'''
    embed.set_image(url=config['image_url'])
    embed.color = nextcord.Color.red()
    await interaction.channel.send(embed=embed, view=selectteam())
    await interaction.response.send_message(content='success', ephemeral=True)



bot.run(config['TOKENBOT'])