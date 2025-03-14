The game was inspired by Poeltl, the NBPA player guessing game (https://poeltl.nbpa.com/). Every day, one player is drawn from the NBA player's database, with data acquired from https://www.espn.com/ through web scraping. Your mission is to identify the player by guessing their full name until you find the correct one. 
The colors indicate how close you are to today's player. For example, if today's player is 23 years old and you guess a player who is 30, you will get a grey color, which means you're not close. However, you'll also see an arrow "↓" to indicate that today's player is younger than 30. 
If you guess a player who is 25, you'll get the same arrow, but the color will turn yellow, meaning you're very close to the correct age. The yellow color appears when the difference between the actual value and your guess is 3 or less. This feedback applies to numerical values such as age, 
jersey number, NBA experience, height, and weight. Other information includes the player's team, college, and position. This game may be more challenging than the original Poeltl guessing game because it lacks conference and division information, as I could not scrape that data. However, if you're an NBA expert, you should be fine!

----------------------------------------------------

Web scraping

I started by scraping URLs for each team.
```
def build_team_url():
    url = 'https://www.espn.com/nba/teams'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    r = requests.get(url, headers=headers)
    
    teams_source = r.text
    
    teams = dict(re.findall(r"www\.espn\.com/nba/team/_/name/(\w+)/(.+?)\",", teams_source))
    
    roster_urls = []
    
    for key in teams.keys():
        roster_urls.append("https://www.espn.com/nba/team/roster/_/name/" + key + '/' + teams[key])
        teams[key] = str(teams[key])

    return dict(zip(teams.values(),roster_urls))
```
The output provided a key for each team and its URL. For example, for the Boston Celtics.
```
rosters = build_team_url()
rosters
```
`'boston-celtics': 'https://www.espn.com/nba/team/roster/_/name/bos/boston-celtics'`

Then, I managed to print the players' data from a specific team after assigning the URL variable to the team's link.

```
url = "https://www.espn.com/nba/team/roster/_/name/gs/golden-state-warriors"
response = urllib.request.urlopen(url)
page_source = response.read().decode('utf-8')

data_regex = r'\{"shortName":.*?}'  
json_data_matches = re.findall(data_regex, page_source)

players = []
for match in json_data_matches:
    try:
        players.append(json.loads(match))  
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        continue  

players
```
`{'shortName': 'T. Armstrong',
  'name': 'Taran Armstrong',
  'href': 'https://www.espn.com/nba/player/_/id/4896850/taran-armstrong',
  'uid': 's:40~l:46~a:4896850',
  'guid': '761d5577-29c7-35f9-b9ed-c24ea9f0717f',
  'id': '4896850',
  'height': '6\' 6"',
  'weight': '190 lbs',
  'age': 23,
  'position': 'G',
  'birthDate': '01/15/02',
  'headshot': 'https://a.espncdn.com/combiner/i?img=/i/headshots/nophoto.png&w=200&h=146',
  'lastName': 'Taran Armstrong',
  'experience': 0,
  'college': 'California Baptist'},`

The next step was creating a function that prints information about players from a team by providing the function with the team's URL.

```
def get_players_info(roster_url):
    response = urllib.request.urlopen(roster_url)
    page_source = response.read().decode('utf-8')
    player_regex = r'\{"shortName":.*?}'
    json_data_matches = re.findall(player_regex, page_source)
    players = []
    for match in json_data_matches:
        try:
            players.append(json.loads(match))  
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            continue  
    
    players_dict = {player['name'].lower(): player for player in players}
    return players_dict
```
```
get_players_info('https://www.espn.com/nba/team/roster/_/name/mia/miami-heat')
```

`{'bam adebayo': {'shortName': 'B. Adebayo',
  'name': 'Bam Adebayo',
  'href': 'https://www.espn.com/nba/player/_/id/4066261/bam-adebayo',
  'uid': 's:40~l:46~a:4066261',
  'guid': '38b3edc5-57ff-d3ff-9aa2-2865f7f01a4c',
  'id': '4066261',
  'height': '6\' 9"',
  'weight': '255 lbs',
  'age': 27,
  'position': 'C',
  'jersey': '13',
  'salary': '$34,848,340',
  'birthDate': '07/18/97',
  'headshot': 'https://a.espncdn.com/i/headshots/nba/players/full/4066261.png',
  'lastName': 'Bam Adebayo',
  'experience': 7,
  'college': 'Kentucky'}`

I created a dictionary that prints information about players, so now you don't need to paste the entire URL—just the team's name.

```
all_players = dict()
for team in rosters.keys():
    print("Gathering player info for team: " + team)
    all_players[team] = get_players_info(rosters[team])
```
`Gathering player info for team: boston-celtics
Gathering player info for team: brooklyn-nets
Gathering player info for team: new-york-knicks
Gathering player info for team: philadelphia-76ers`

```
all_players['atlanta-hawks']
```
`{'dominick barlow': {'shortName': 'D. Barlow',
  'name': 'Dominick Barlow',
  'href': 'https://www.espn.com/nba/player/_/id/4870562/dominick-barlow',
  'uid': 's:40~l:46~a:4870562',
  'guid': 'b6f6857f-9a83-30a6-85a7-2e02c49d5ae5',
  'id': '4870562',
  'height': '6\' 8"',
  'weight': '215 lbs',
  'age': 21,
  'position': 'F',
  'jersey': '0',
  'salary': 0,
  'birthDate': '05/26/03',
  'headshot': 'https://a.espncdn.com/i/headshots/nba/players/full/4870562.png',
  'lastName': 'Dominick Barlow',
  'experience': 2}`

Next, I created a table from the players' data.
```
def any_roster_df(team):
    if team in all_players:
        team_df = pd.DataFrame.from_dict(all_players[team])
        team_df = team_df.T
        team_df['team'] = team
        team_df['name'] = team_df.index
        team_df = team_df.drop(['name','href','uid','guid','headshot','lastName','shortName'], axis=1)  
        team_df["salary"] = team_df["salary"].fillna("not specified")
        team_df["jersey"] = team_df["jersey"].fillna("not specified")
        team_df["college"] = team_df["college"].fillna("not specified")


        team_df = team_df.dropna(axis=1) 


        team_df.index = team_df.index.map(str.title)
        team_df.columns = team_df.columns.map(str.title)
        team_df.rename(columns={'Birthdate':'Birth date'}, inplace=True)
        team_df['Team'] = team_df['Team'].replace('-', ' ', regex=True).astype(object)
        team_df['Team'] = team_df['Team'].str.title()
        
    return team_df
```

```
any_roster_df('boston-celtics')
```

| Name              | Id       | Height | Weight  | Age | Position | Jersey | Salary        | Birth Date | Experience | College                 | Team            |
|-------------------|----------|--------|---------|-----|----------|--------|---------------|------------|------------|-------------------------|-----------------|
| Jaylen Brown      | 3917376  | 6' 6"  | 223 lbs | 28  | SG       | 7      | $49,205,800   | 10/24/96   | 8          | California              | Boston Celtics  |
| Torrey Craig      | 2528693  | 6' 5"  | 221 lbs | 34  | SF       | 12     | $2,845,342    | 12/19/90   | 7          | South Carolina Upstate  | Boston Celtics  |
| Jd Davison        | 4576085  | 6' 1"  | 195 lbs | 22  | SG       | 20     | 0             | 10/03/02   | 2          | Alabama                 | Boston Celtics  |
| Sam Hauser        | 4065804  | 6' 7"  | 217 lbs | 27  | SF       | 30     | $2,092,344    | 12/08/97   | 3          | Virginia                | Boston Celtics  |
| Jrue Holiday      | 3995     | 6' 4"  | 205 lbs | 34  | PG       | 4      | $30,000,000   | 06/12/90   | 15         | UCLA                   | Boston Celtics  |
| Al Horford        | 3213     | 6' 9"  | 240 lbs | 38  | C        | 42     | $9,500,000    | 06/03/86   | 17         | Florida                | Boston Celtics  |
| Luke Kornet       | 3064560  | 7' 1"  | 250 lbs | 29  | C        | 40     | $2,087,519    | 07/15/95   | 7          | Vanderbilt             | Boston Celtics  |
| Miles Norris      | 4397104  | 6' 7"  | 220 lbs | 24  | F        | 8      | not specified | 04/15/00   | 1          | UC Santa Barbara       | Boston Celtics  |
| Drew Peterson     | 4397689  | 6' 9"  | 205 lbs | 25  | F        | 13     | 0             | 11/09/99   | 1          | USC                    | Boston Celtics  |
| Kristaps Porzingis| 3102531  | 7' 2"  | 240 lbs | 29  | C        | 8      | $29,268,293   | 08/02/95   | 9          | not specified          | Boston Celtics  |
| Payton Pritchard  | 4066354  | 6' 1"  | 195 lbs | 27  | PG       | 11     | $6,696,429    | 01/28/98   | 4          | Oregon                 | Boston Celtics  |
| Neemias Queta     | 4397424  | 7' 0"  | 248 lbs | 25  | C        | 88     | $2,162,606    | 07/13/99   | 3          | Utah State             | Boston Celtics  |
| Baylor Scheierman | 4593841  | 6' 6"  | 205 lbs | 24  | F        | 55     | $2,494,320    | 09/26/00   | 0          | Creighton              | Boston Celtics  |
| Jayson Tatum      | 4065648  | 6' 8"  | 210 lbs | 27  | SF       | 0      | $34,848,340   | 03/03/98   | 7          | Duke                   | Boston Celtics  |
| Xavier Tillman    | 4277964  | 6' 7"  | 245 lbs | 26  | F        | 26     | $2,237,691    | 01/12/99   | 4          | Michigan State         | Boston Celtics  |
| Jordan Walsh      | 4683689  | 6' 6"  | 205 lbs | 21  | G        | 27     | $1,891,857    | 03/03/04   | 1          | Arkansas               | Boston Celtics  |
| Derrick White     | 3078576  | 6' 4"  | 190 lbs | 30  | PG       | 9      | $20,017,429   | 07/02/94   | 7          | Colorado               | Boston Celtics  |


Finally, I created a table containing information about every player.

```
all_players_df = pd.DataFrame()
# loop through each team, create a pandas DataFrame, and append
for team in all_players.keys():
    team_df = pd.DataFrame.from_dict(all_players[team], orient = "index")
    team_df['team'] = team
    team_df = team_df.drop(['name','href','uid','guid','headshot','lastName','shortName'], axis=1)  
    team_df["salary"] = team_df["salary"].fillna("not specified")
    team_df["jersey"] = team_df["jersey"].fillna("not specified")
    team_df["college"] = team_df["college"].fillna("not specified")


    team_df = team_df.dropna(axis=1) 

    team_df.index = team_df.index.map(str.title)
    team_df.columns = team_df.columns.map(str.title)
    team_df.rename(columns={'Birthdate':'Birth date'}, inplace=True)
    team_df['Team'] = team_df['Team'].replace('-', ' ', regex=True).astype(object)
    team_df['Team'] = team_df['Team'].str.title()
    
    all_players_df = all_players_df._append(team_df)
```

